"""Build the remaining HD batches from the canonical inventory and local witnesses."""

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import stat

from build_hd_progress import ROOT, apply_register
from gen_tactical_ground_table import fnv1a64
from hd_census import all_rows
from scene_file_queue import extra_family, work_items


CONFIG = ROOT / 'config'
REGISTER = CONFIG / 'hd-chapter-coverage.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def state_index(roots, signatures):
    """Read only the VDP2 page from each distinct v9 snapshot."""
    hits = defaultdict(list)
    scanned = 0
    seen = set()
    for root in roots:
        for directory, children, names in os.walk(root, followlinks=False):
            children[:] = sorted(child for child in children if not (
                getattr((Path(directory) / child).lstat(), 'st_file_attributes', 0)
                & stat.FILE_ATTRIBUTE_REPARSE_POINT))
            for name in sorted(names):
                if not (name.endswith('.state') or
                        (name.startswith('state-') and name.endswith('.bin'))):
                    continue
                path = Path(directory) / name
                info = path.stat()
                if info.st_size != 4257356:
                    continue
                identity = (info.st_dev, info.st_ino) if info.st_ino else path.resolve()
                if identity in seen:
                    continue
                seen.add(identity)
                with path.open('rb') as stream:
                    if stream.read(4) != b'TSRS':
                        continue
                    stream.seek(0x3c0064)
                    fingerprint = f'{fnv1a64(stream.read(8192)):016X}'
                scanned += 1
                if fingerprint in signatures:
                    hits[fingerprint].append(str(path.resolve()))
    return scanned, {key: sorted(paths) for key, paths in hits.items()}


def make_queue(pc_root, state_roots, batch_size):
    register = load(REGISTER)
    progress = load(CONFIG / 'hd-progress.json')
    apply_register(progress, REGISTER)
    categories = {row['id']: row for row in progress['categories']}
    expected = {name: categories[name]['total'] - categories[name]['integrated']
                for name in ('scene-images', 'hud-menus')}
    grounds = progress['tactical_grounds']
    expected['tactical-grounds'] = grounds['total'] - grounds['integrated']
    batches = defaultdict(list)
    scene_review = load(CONFIG / 'hd-scene-bg-review.json')
    rejected = scene_review['rejected']
    shared_keys = scene_review['shared_cell_choice']

    for path, status, _, aliases, references, _ in work_items(
            pc_root, register, load(CONFIG / 'hd-scene-file-duplicates.json')):
        if status == 'hd' or extra_family(path):
            continue
        family = str(Path(path).parent).replace('\\', '/')
        item = {
            'donor': path, 'aliases': aliases.split('; ') if aliases else [],
            'saturn': references.split('; ') if references else [],
        }
        if status == 'unknown' and family == 'SAKURA1/BG':
            name = Path(path).stem
            if name in rejected:
                status = 'reviewed-hold'
                item['review'] = rejected[name]
            elif name in shared_keys and shared_keys[name] != name:
                status = 'shared-native-key'
                item['other_donor'] = f'{family}/{shared_keys[name]}.SPR'
        batches['scene-images', status, family].append(item)

    rows = [row for _, _, row in all_rows(register, 'menus-hud')]
    integrated = {(row['pc'], row['pc_image_index']) for row in rows
                  if row['status'] == 'hd' and row.get('pc') and 'pc_image_index' in row}
    excluded = {row['pc'] for row in rows if row['status'] == 'excluded'
                and row.get('images')}
    families = load(CONFIG / 'hd-menu-open-classification.json')['families']
    reviewed = {file_id: {'family': family, 'method': row['connect'], 'note': row['note']}
                for family, row in families.items() for file_id in row['files']}
    menu_inventory = load(ROOT / 'docs/research/pc-menu-hud-inventory.json')['menus']
    for entry in menu_inventory:
        path = entry['pc_path']
        if path in excluded:
            continue
        review = reviewed.get(entry['id'])
        method = review['method'] if review else 'system'
        for image in entry['images']:
            ordinal = image['index']
            if (path, ordinal) not in integrated:
                batches['hud-menus', method, path].append({
                    'donor': path, 'ordinal': ordinal,
                    'size': [image['width'], image['height']],
                    'review': review,
                })
    items = defaultdict(set)
    for item in load(CONFIG / 'hd-item-map.json')['pairs']:
        items[item['pc_file'], item['pc_image_index']].add(item['saturn_file'])
    for (path, ordinal), references in sorted(items.items()):
        if (path, ordinal) not in integrated:
            batches['hud-menus', 'item', 'SAKURA1/ITEM'].append({
                'donor': path, 'ordinal': ordinal, 'saturn': sorted(references),
            })

    maps = [row for row in load(CONFIG / 'hd-tactical-ground-table.json')['maps']
            if row['status'] != 'hd']
    scanned, witnesses = state_index(state_roots, {row.get('signature') for row in maps})
    for row in maps:
        checkpoints = witnesses.get(row.get('signature'), [])
        # A resident page identifies a replay candidate, never a visible draw.
        priority = 'resident' if checkpoints and row['status'] == 'candidate' else row['status']
        batches['tactical-grounds', priority, row['layout']].append({
            'map': row['map'], 'donor': row['pc_ground'], 'saturn': row['saturn'],
            'signature': row.get('signature'), 'resident_checkpoints': checkpoints,
        })

    actual = {name: sum(len(items) for key, items in batches.items() if key[0] == name)
              for name in expected}
    if actual != expected:
        raise ValueError(f'Pending identities differ from the progress register: {actual} != {expected}')
    order = ('resident', 'wired-unverified', 'paired-not-wired', 'item', 'candidate',
             'witness', 'witness+mechanism', 'system', 'unsupported-size',
             'needs-assembler', 'unpaired', 'unknown', 'shared-native-key', 'reviewed-hold', 'native')
    ranked = sorted(batches, key=lambda key: (order.index(key[1]), -len(batches[key]), key))
    queue = []
    for category, status, family in ranked:
        items = batches[category, status, family]
        for offset in range(0, len(items), batch_size):
            queue.append({'category': category, 'status': status, 'family': family,
                          'items': items[offset:offset + batch_size]})
    return {'pending': actual, 'states_scanned': scanned, 'batches': queue}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pc-root', type=Path, required=True)
    parser.add_argument('--states', type=Path, action='append', default=[])
    parser.add_argument('--batch-size', type=int, default=8)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error('--batch-size must be positive')
    if not all(root.is_dir() for root in args.states):
        parser.error('each --states path must be a directory')
    try:
        queue = make_queue(args.pc_root, args.states, args.batch_size)
        args.output.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f'{sum(queue["pending"].values())} pending identities in {len(queue["batches"])} batches. '
          f'{queue["states_scanned"]} states indexed.')


if __name__ == '__main__':
    main()
