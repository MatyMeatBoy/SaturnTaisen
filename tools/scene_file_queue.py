"""Export one HD work item per unique PC scene file, with its Saturn references."""

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENE_FOLDERS = (
    'SAKURA1/BG', 'SAKURA2/BG', 'SAKURA2/EVENT', 'SAKURA3/CG',
    'SAKURA1/ENDING', 'SAKURA1/TITLE', 'SAKURA1/ICATCH',
)
PRIORITY = {
    'wired-unverified': 0, 'paired-not-wired': 1, 'unsupported-size': 2,
    'unpaired': 3, 'unknown': 4, 'hd': 5,
}
EVENT_REFERENCE = re.compile(r'^\s*MAP:\s*(\d+)\s+NPCID:\s*(\d+)\s+(EVENT\\[^\s]+\.SPR)\b', re.IGNORECASE)


def extra_family(path):
    if path.startswith('SAKURA2/EVENT/'):
        return 'EVENT'
    if path.startswith('SAKURA3/CG/'):
        return 'CG'
    return None


def event_references(text, files):
    names = {path.casefold(): path for path in files if path.startswith('SAKURA2/EVENT/')}
    references = defaultdict(set)
    for line in text.splitlines():
        if match := EVENT_REFERENCE.match(line):
            map_id, npc_id, path = match.groups()
            key = ('SAKURA2/' + path.replace('\\', '/')).casefold()
            if key not in names:
                raise ValueError(f'EVENTANM referencia un SPR ausente: {path}')
            references[names[key]].add((int(map_id), int(npc_id)))
    return references


def work_items(pc_root, register, census):
    files = {
        path.relative_to(pc_root).as_posix()
        for folder in SCENE_FOLDERS for path in (pc_root / folder).rglob('*')
        if path.is_file() and path.suffix.lower() == '.spr'
    }
    groups = [set(group) for group in census['groups']]
    aliases = {path for group in groups for path in group}
    if len(files) != census['candidates'] or not aliases <= files:
        raise ValueError('El directorio PC no coincide con el censo completo de archivos de escena.')
    groups.extend({path} for path in files - aliases)
    events = event_references((pc_root / 'SAKURA2/EVENTANM.TAB').read_text(encoding='cp932'), files)

    statuses = defaultdict(set)
    references = defaultdict(set)
    for resources in [register['unassigned'], *(chapter['resources'] for chapter in register['chapters'])]:
        for key, row in resources['scene-pictures'].items():
            if path := row.get('pc'):
                statuses[path].add(row['status'])
                references[path].add(key)

    linked = {path for path, states in statuses.items() if 'hd' in states}
    excluded = {path for path, states in statuses.items() if 'excluded' in states} - linked
    items = []
    for group in groups:
        candidates = group - excluded
        if not candidates:
            continue
        canonical = min(candidates, key=lambda path: (
            extra_family(path) is not None, path not in linked, path))
        has_link = bool(candidates & linked)
        states = set().union(*(statuses[path] for path in candidates))
        state = 'hd' if has_link else min(
            (status for status in states if status in PRIORITY), key=PRIORITY.get, default='unknown')
        keys = set().union(*(references[path] for path in candidates))
        event_keys = set().union(*(events[path] for path in candidates))
        items.append((canonical, state, len(keys), '; '.join(sorted(candidates - {canonical})),
                      '; '.join(sorted(keys)),
                      '; '.join(f'MAP{map_id:02d}/NPC{npc_id}' for map_id, npc_id in sorted(event_keys))))
    return sorted(items, key=lambda row: (PRIORITY[row[1]], row[0]))


def event_shards(items):
    """Assign each EVENT identity to one route, retaining every original reference."""
    by_map = defaultdict(set)
    without_route = []
    for row in items:
        if not row[0].startswith('SAKURA2/EVENT/'):
            continue
        routes = {reference.split('/')[0] for reference in row[5].split('; ') if reference}
        if not routes:
            without_route.append(row)
        for route in routes:
            by_map[route].add(row)

    assigned = set()
    if 'MAP02' in by_map:
        first = by_map.pop('MAP02')
        assigned.update(first)
        yield from (('MAP02', *row) for row in sorted(first))
    while by_map:
        route = min(by_map, key=lambda key: (-len(by_map[key] - assigned), key))
        fresh = by_map.pop(route) - assigned
        assigned.update(fresh)
        yield from ((route, *row) for row in sorted(fresh))
    yield from (('SIN_REFERENCIA_PC', *row) for row in sorted(without_route))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pc-root', type=Path, required=True, help='directorio con SAKURA1, SAKURA2 y SAKURA3')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--event-shards', action='store_true',
                        help='exporta solo EVENT y asigna cada donante a una ruta táctica')
    parser.add_argument('--scope', choices=('all', 'core', 'extras'), default='all',
                        help='limita el CSV al mod principal o a los extras EVENT/CG')
    args = parser.parse_args()
    if args.event_shards and args.scope == 'core':
        parser.error('--event-shards requiere un alcance que incluya EVENT')
    config = ROOT / 'config'
    register = json.loads((config / 'hd-chapter-coverage.json').read_text(encoding='utf-8'))
    census = json.loads((config / 'hd-scene-file-duplicates.json').read_text(encoding='utf-8'))
    try:
        items = work_items(args.pc_root, register, census)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    with args.output.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        columns = ('archivo_pc', 'estado', 'referencias_saturn', 'archivos_pc_equivalentes',
                   'claves_saturn', 'referencias_eventanm_pc')
        if args.event_shards:
            shards = list(event_shards(items))
            writer.writerow(('ruta_principal', *columns))
            writer.writerows(shards)
            print(f'{len(shards)} donantes EVENT únicos en la cola')
            return
        writer.writerow(columns)
        if args.scope != 'all':
            items = [item for item in items
                     if bool(extra_family(item[0])) == (args.scope == 'extras')]
        writer.writerows(items)
    linked = sum(state == 'hd' for _, state, *_ in items)
    print(f'{linked}/{len(items)} enlazados; {len(items) - linked} pendientes')


if __name__ == '__main__':
    main()
