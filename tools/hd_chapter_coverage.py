"""Join local Saturn scene evidence with tracked HD catalogs using asset metadata only."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = range(1, 11)
CATEGORIES = (
    'scene-pictures', 'bodies', 'portraits', 'film',
    'tactical-maps', 'tactical-units', 'menus-hud',
)
BG_REPORT = 'docs/research/bg-matching-progress.md'
BODY_REPORT = 'docs/research/saturn-bg-format.md'
PORTRAIT_REPORT = 'docs/research/portrait-animation-coverage.md'
SWEEP_REPORT = 'docs/research/chapter-sweep.md'
EVE_PAIRS = {
    'EVE002': 'BBG002', 'EVE0101': 'BBG001', 'EVE0116': 'BBG201',
    'EVE0118': 'BBG101', 'EVE102': 'BBG102', 'EVE105': 'BBG105',
    'EVE202': 'BBG202', 'EVE205': 'BBG205', 'EVE207': 'BBG207',
}
# The documented draws include partial native faces and conditional fallbacks.
BODY_DRAWS = {'NC11', 'NC20', 'NC30', 'NC55', 'NC82', 'NC97'}
# Exact file witnesses with a documented chapter. Shared disc residency and
# the sequence of files in a cold run are insufficient for chapter placement.
CHAPTER_WITNESSES = {
    (1, '/SAKURA1/BG1119.BIN'): (1, BG_REPORT),
    (1, '/SAKURA1/NC20.BIN'): (1, BODY_REPORT),
    (1, '/SAKURA1/NC30.BIN'): (1, BODY_REPORT),
    (1, '/SAKURA2/EVE0101.BIN'): (1, BODY_REPORT),
    (1, '/SAKURA2/EVE202.BIN'): (2, BODY_REPORT),
}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def disc_for(chapter):
    return 1 if chapter <= 7 else 2


def asset_category(path):
    name = Path(path).name
    for pattern, category in (
        (r'(?:BG\d+|BBG\d+|EVE\d+|(?!LIPS_)\w+_CG|CG\d+|TITLE\d+|IC\d+)\.BIN', 'scene-pictures'),
        (r'NC\d+\.BIN', 'bodies'),
        (r'\d{4}FCE\.BIN', 'portraits'),
        (r'MAP\d+\.BIN', 'tactical-maps'),
        (r'UNIT\d+\.BIN', 'tactical-units'),
        (r'(?:WKL\d+|WALL\d+|ITEM\d+|LOAD|OMAKE|TMAP|LIPS_CG)\.BIN', 'menus-hud'),
    ):
        if re.fullmatch(pattern, name):
            return category
    return None


def indexed_chapter(path):
    name = Path(path).name
    atlas = re.fullmatch(r'(\d{2})\d{2}(?:FCE|TBL)\.BIN', name)
    title = re.fullmatch(r'TITLE(\d+)\.BIN', name)
    if atlas or title:
        chapter = int((atlas or title)[1])
        if chapter in CHAPTERS:
            return chapter
    return None


def film_key(resource, offset):
    return resource['disc'], 150 + resource['lba'] + offset // 2048


def pairs(data):
    return {'/' + row['saturn_file']: row for row in data['pairs']}


def runtime_bg_entries(root):
    with TemporaryDirectory() as temp:
        header = Path(temp) / 'scene_bg.h'
        subprocess.run([
            sys.executable, str(root / 'tools/gen_scene_bg_table.py'),
            str(root / 'config/hd-scene-bg-map.json'), str(header),
        ], check=True, capture_output=True, text=True)
        return set(re.findall(r'\{0x([0-9A-F]+)ull,"([^"]+)",(\d+)\}',
                              header.read_text(encoding='utf-8')))


def build(root, index_dir, portrait_audit):
    def config(name):
        return load(root / 'config' / (name + '.json'))

    inventory = load(index_dir / 'resource-inventory.json')
    index = load(index_dir / 'scene-index.json')
    portrait_report = load(portrait_audit)
    if portrait_report.get('errors'):
        raise ValueError('The portrait audit reports errors')
    portraits = portrait_report['rows']
    recipes = {r['id']: r['pc_index'] for r in config('hd-portrait-recipe')['portraits']}
    films = {(r['disc'], r['fad']): r for r in config('film-fad-map')['streams']}
    bg = pairs(config('hd-scene-bg-map'))
    bg_review = config('hd-scene-bg-review')
    bg_table = runtime_bg_entries(root)
    screens = pairs(config('hd-screen-map'))
    bodies = pairs(config('hd-body-map'))
    body_review = config('hd-body-review')
    # Bodies in the runtime table: content pairs or eye-confirmed candidates, not rejected (the filter of tools/gen_body_table.py).
    body_runtime = {
        Path(path).stem for path, pair in bodies.items()
        if Path(path).stem not in body_review['rejected']
        and (pair['tier'] == 'content' or Path(path).stem in body_review['eye_confirmed_candidates'])
    }
    items = pairs(config('hd-item-map'))
    item_review = pairs(config('hd-item-review'))
    cold_bg = {
        '/' + row['pc_file'].replace('/BG/', '/').replace('.SPR', '.BIN'): row['evidence_frame']
        for row in config('hd-scene-bg-pairs')['pairs']
    }
    chapters = {
        n: {'chapter': n, 'disc': disc_for(n), 'resources': {c: {} for c in CATEGORIES}}
        for n in CHAPTERS
    }
    unassigned = {c: {} for c in CATEGORIES}
    by_id = {r['resource_id']: r for r in inventory}

    # Explicit runtime observations can identify a resource or establish RAM
    # residency. Selection shots establish the chapter, not an asset identity.
    observed = {}
    resident = {}
    for row in index:
        if row['certainty'] != 'observed':
            continue
        chapter = row.get('observed_episode')
        report = SWEEP_REPORT
        if chapter is None and row['scene_id'] == '1:observation:intermission-pause':
            chapter = 1
            report = 'docs/research/chapter1-wide-transitions.md'
        if chapter not in CHAPTERS:
            continue
        if row['disc'] != disc_for(chapter):
            raise ValueError(f"Observed episode {chapter} on unexpected disc {row['disc']}")
        key = (row.get('resource_id'), row.get('stream_offset'))
        if key[0] is not None:
            observed[key] = (chapter, report)
        for resource_id in row.get('resident_resource_ids', []):
            if asset_category(by_id[resource_id]['iso_path']):
                resident[resource_id] = (chapter, report)

    def add(category, key, row, chapter=None, association='unknown', evidence=None):
        item = dict(row, association=association)
        if evidence:
            item['evidence'] = evidence
        target = chapters[chapter]['resources'] if chapter else unassigned
        target[category][key] = item

    for resource in inventory:
        disc, path, ident = (resource[k] for k in ('disc', 'iso_path', 'resource_id'))
        kind = asset_category(path)
        name = Path(path).stem
        chapter, report = observed.get((ident, None), (None, None))
        association = 'observed' if chapter else 'unknown'
        if ident in resident and chapter is None:
            chapter, report = resident[ident]
            association = 'resident'
        if chapter is None:
            candidate = indexed_chapter(path)
            if candidate and disc == disc_for(candidate):
                chapter, association = candidate, 'inferred'
        if (disc, path) in CHAPTER_WITNESSES:
            chapter, report = CHAPTER_WITNESSES[(disc, path)]
            association = 'observed'
        row = {'status': 'unknown'}
        if path in bg:
            pair = bg[path]
            accepted = name not in bg_review['rejected'] and (
                pair.get('tier') == 'content' or name in bg_review['eye_confirmed_number_tier']
            )
            if accepted:
                key = (pair['palette_fnv'], pair['pc_file'], str(pair['pc_image_index']))
                row = {'status': 'hd' if key in bg_table else 'paired-not-wired',
                       'pc': pair['pc_file']}
                if key not in bg_table:
                    if name[2:3] in '34' or name == 'BG0000':
                        # Character cut-outs on a key colour and the blank picture are never replaced (tools/gen_scene_bg_table.py).
                        row['status'] = 'excluded'
                        row['reason'] = 'cut-out on a key colour or blank picture, not replaced by design'
                    elif pair.get('size') != [288, 144] or not path.startswith(('/SAKURA1/', '/SAKURA2/EVE')):
                        # The runtime draws a 288x144 picture only; wide and tall ones need scroll support (T105c).
                        row['status'] = 'unsupported-size'
                        row['reason'] = 'size %s, the runtime draws 288x144 pictures only' % (pair.get('size'),)
                    else:
                        row['reason'] = 'palette shared with a picture that maps to another PC file (ambiguous)'
            elif name in bg_review['rejected'] or pair.get('tier') == 'missing':
                row['status'] = 'unpaired'
        elif path in screens and screens[path]['tier'] == 'content':
            row = {'status': 'paired-not-wired', 'pc': screens[path]['pc_file']}
        elif name in EVE_PAIRS:
            row = {'status': 'paired-not-wired', 'pc': 'SAKURA2/BG/' + EVE_PAIRS[name] + '.SPR'}
        elif path in bodies:
            pair = bodies[path]
            if name in body_review['rejected']:
                row['status'] = 'unpaired'
            elif pair['tier'] == 'content' or name in body_review['eye_confirmed_candidates']:
                row = {'status': 'hd' if name in BODY_DRAWS else 'wired-unverified' if name in body_runtime else 'paired-not-wired',
                       'pc': 'SAKURA1/NC/' + (pair['best_pc'] if pair['tier'] == 'content' else pair['same_name_pc'])}
                if name in BODY_DRAWS:
                    row['native_face_fallback'] = True
                    row['runtime_evidence'] = BODY_REPORT
        elif path in items:
            pair = items[path]
            if pair['tier'] == 'content' or item_review.get(path, {}).get('verdict') == 'confirmed':
                row = {'status': 'paired-not-wired', 'pc': pair['pc_file']}
            elif path in item_review:
                row['status'] = 'unpaired'
        if path in cold_bg and disc == 1:
            row['cold_run_frame'] = cold_bg[path]
        if kind:
            add(kind, f'{disc}:{path}', row, chapter, association, report)

        for stream in resource['video_streams']:
            offset = stream['offset']
            _, fad = film_key(resource, offset)
            film = films.get((disc, fad))
            row = {'status': 'unknown', 'fad': fad}
            if film and film['file'] == path:
                row['status'] = 'unpaired'
                if movie := film.get('movie'):
                    row.update(status='paired-not-wired' if film['alternate_cut'] else 'hd',
                               pc=movie, alternate_cut=film['alternate_cut'])
            chapter, report = observed.get((ident, offset), (None, None))
            if disc == 1 and row.get('pc') == 'MOVIE001' and path == '/SAKURA4':
                chapter, report = 1, 'docs/PENDIENTES.md#list'
            add('film', f'{disc}:{path}+{offset}', row, chapter,
                'observed' if chapter else 'unknown', report)
    for portrait in portraits:
        ident = portrait['id']
        if not re.fullmatch('[0-9a-f]{4}', ident):
            raise ValueError(f'Invalid portrait identity {ident!r}')
        sources = sorted(portrait.get('chapter1_sources', []))
        for source in sources:
            disc, _, path = source.partition(':')
            if disc not in ('1', '2') or indexed_chapter(path) != 1:
                raise ValueError(f'Invalid chapter 1 portrait source for {ident}')
        row = {'status': 'hd', 'pc_index': recipes[ident]} if ident in recipes else {'status': 'unpaired'}
        if sources:
            row['atlases'] = sources
        add('portraits', ident, row, 1 if sources else None,
            'inferred' if sources else 'unknown', PORTRAIT_REPORT if sources else None)

    add('tactical-maps', '1:STAGE01', {
        'status': 'unknown', 'extension': 'STAGE01-right-v1.png',
    }, 1, 'observed', 'docs/research/pixelgen-v1.md')

    return {
        'schema': 1,
        'status': {
            'hd': 'Runtime supports this substitution or a documented partial draw. Scene occurrence and full replay verification are separate.',
            'wired-unverified': 'The runtime table holds this body and tries to draw it when it appears; no in-game observation is recorded yet (hd means a documented draw).',
            'paired-not-wired': 'Accepted counterpart that is genuinely not in the runtime table (for example an ambiguous palette) or an alternate film cut, which stays native. Not a to-do list: check `reason` first.',
            'excluded': 'Paired but never replaced by design (key-colour character cut-outs, the blank picture).',
            'unsupported-size': 'Accepted counterpart whose size the runtime cannot draw yet (not 288x144): needs scroll or size support (T105c).',
            'unpaired': 'The catalog records a rejected or absent counterpart.',
            'unknown': 'Pairing or integration is not established by the input catalogs.',
        },
        'association': {
            'observed': 'The resource is identified in runtime evidence for this chapter.',
            'resident': 'The resource matches in RAM during the chapter, without evidence it was drawn.',
            'inferred': 'Episode file numbering or chapter 1 atlas membership provides a candidate.',
            'unknown': 'No chapter attribution in the inputs.',
        },
        'chapters': list(chapters.values()),
        'unassigned': unassigned,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, required=True, help='directory generated by build_scene_index.py')
    parser.add_argument('--portrait-audit', type=Path, required=True, help='portrait-coverage.json from audit_portrait_coverage.py')
    parser.add_argument('--output', type=Path, default=ROOT / 'config/hd-chapter-coverage.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        result = build(ROOT, args.index, args.portrait_audit)
        expected = json.dumps(result, indent=2, sort_keys=True) + '\n'
        if args.check:
            if args.output.read_text(encoding='utf-8') != expected:
                parser.exit(1, 'Regenerate the HD chapter coverage JSON.\n')
        else:
            args.output.write_text(expected, encoding='utf-8', newline='\n')
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
