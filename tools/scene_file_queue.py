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
        canonical = min(candidates, key=lambda path: (path not in linked, path))
        states = set().union(*(statuses[path] for path in candidates))
        state = 'hd' if canonical in linked else min(
            (status for status in states if status in PRIORITY), key=PRIORITY.get, default='unknown')
        keys = set().union(*(references[path] for path in candidates))
        event_keys = set().union(*(events[path] for path in candidates))
        items.append((canonical, state, len(keys), '; '.join(sorted(candidates - {canonical})),
                      '; '.join(sorted(keys)),
                      '; '.join(f'MAP{map_id:02d}/NPC{npc_id}' for map_id, npc_id in sorted(event_keys))))
    return sorted(items, key=lambda row: (PRIORITY[row[1]], row[0]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pc-root', type=Path, required=True, help='directorio con SAKURA1, SAKURA2 y SAKURA3')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = ROOT / 'config'
    register = json.loads((config / 'hd-chapter-coverage.json').read_text(encoding='utf-8'))
    census = json.loads((config / 'hd-scene-file-duplicates.json').read_text(encoding='utf-8'))
    try:
        items = work_items(args.pc_root, register, census)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    with args.output.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('archivo_pc', 'estado', 'referencias_saturn', 'archivos_pc_equivalentes',
                         'claves_saturn', 'referencias_eventanm_pc'))
        writer.writerows(items)
    linked = sum(state == 'hd' for _, state, *_ in items)
    print(f'{linked}/{len(items)} enlazados; {len(items) - linked} pendientes')


if __name__ == '__main__':
    main()
