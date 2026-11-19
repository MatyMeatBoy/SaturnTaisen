"""Join local Saturn scene evidence with tracked HD catalogs using asset metadata only."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import gen_item_table  # noqa: E402
CHAPTERS = range(1, 11)
CATEGORIES = (
    'scene-pictures', 'bodies', 'portraits', 'film',
    'tactical-maps', 'tactical-units', 'menus-hud',
)
BODY_REPORT = 'docs/research/saturn-bg-format.md'
CAMPAIGN_REPORT = 'docs/research/coverage-campaign-v026.md'
PORTRAIT_REPORT = 'docs/research/portrait-animation-coverage.md'

RESIDUAL_PORTRAIT_REPORT = PORTRAIT_REPORT + '#residual-portraits-00a1-and-0169'
RESIDUAL_PORTRAIT_REVIEWS = {
    '00a1': {
        'status': 'paired-not-wired',
        'pc_index': 160,
        'reason': 'The same Iris expression needs the two PC strips reversed. Both strip commands still need in-game validation.',
    },
    '0169': {
        'status': 'unpaired',
        'candidate_pc_indices': [348, 360],
        'reason': 'The PC emblem changes the artwork and framing, and its strips do not reproduce the repeated Saturn base region.',
    },
}
SWEEP_REPORT = 'docs/research/chapter-sweep.md'
BG1285_REPORT = 'docs/research/bg1285-pan.md'
BG1207_REPORT = 'docs/research/bg1207-pan.md'
BG2248_REPORT = 'docs/research/bg2248-pan.md'
SCROLL_REPORT = 'docs/research/scroll-table.md'
STAGE01_REPORT = 'docs/research/stage01-pc-ground.md'
CHAPTER1_ROUTE_REPORT = 'docs/research/hd-chapter-1.md#observations-from-the-full-cold-route'
# The replay identifies active donors. BG2004 shares native cells and palette
# with other variants, so this trace cannot attribute its BIN.
CHAPTER1_ROUTE_SCENES = (
    'BG1001 BG1002 BG1006 BG1007 BG1011 BG1012 BG1017 BG1021 BG1030 BG1045 BG1046 '
    'BG1058 BG1070 BG1116 BG1119 BG1193 BG1209 BG1216 BG2034 BG2039 BG2159 BG2173 '
    'BG2250 BG2251 BG2535'
).split()
CHAPTER1_ROUTE_BODIES = (
    'NC10 NC11 NC12 NC20 NC21 NC25 NC30 NC3004 NC32 NC3250 NC50 NC51 NC55 NC56 '
    'NC81 NC82 NC95 NC96 NC97'
).split()
CHAPTER1_ROUTE_PORTRAITS = (
    '0001 0002 0003 0004 0005 0006 0007 0009 000a 000b 000f 0013 0014 0015 0016 '
    '0017 0018 001a 001c 001d 0023 0040 0041 0043 0045 0047 004a 0064 0065 006e '
    '0091 0092 0093 0094 0095 0096 009b 009c 00e2 00e3 00e4 00e5 00e9 0134 0136 '
    '013a 013c 0142 0148 0149 015e 015f 0161 0163 0166 0168 0176 0177 0179 017a '
    '017b 017c'
).split()
CHAPTER1_ROUTE_FILMS = {23695360: 'MOVIE001', 45410304: 'MOVIE002', 56039424: 'MOVIE003'}
STAGE01_MAP = (1, '/SAKURA2/MAP01.BIN')
TH2_GROUND = (1, '/SAKURA2/MAP02.BIN')
TH2_UNITS = (1, '/SAKURA2/UNIT02.BIN')
TH2_REPORT = 'docs/research/hd-chapter-2.md'
STAGE21_REPORT = 'docs/research/stage21-pc-ground.md'
STAGE21_MAP = (1, '/SAKURA2/MAP21.BIN')
CHAPTER4_TACTICAL_REPORT = 'docs/research/hd-chapter-4.md#first-tactical-map-and-work-ram'
STAGE06_MAP = (1, '/SAKURA2/MAP06.BIN')
CHAPTER_FILE_RESIDENCIES = {
    '1:/SAKURA2/WKL06.BIN:f9306a073a1c603658e7b6c132b6ef36e889086e990f2c8856e056db1c14af4b':
        (4, CHAPTER4_TACTICAL_REPORT),
    '1:/SAKURA2/WKL21.BIN:60fed250c11dab1d28df048763315fc62b159a0cee502a73b473a63cef2734f3':
        (4, CHAPTER4_TACTICAL_REPORT),
}
BBG204_INSET = (1, '/SAKURA2/BBG204.BIN')
BBG204_REPORT = 'docs/research/bbg204-tactical-inset.md'
BBG_INSET_REPORT = 'docs/research/disc1-battle-insets.md'
BBG_INSET_PAIRS = {'BBG002', 'BBG003', 'BBG004', 'BBG005', 'BBG006', 'BBG007', 'BBG008', 'BBG103', 'BBG104', 'BBG106', 'BBG205', 'BBG235'}
EVE002_REPORT = 'docs/research/eve002-tactical-inset.md'
EVE0116_REPORT = 'docs/research/eve0116-tactical-inset.md'
EVE0118_REPORT = 'docs/research/eve0118-tactical-inset.md'
EVE_PAIRS = {
    'EVE002': 'BBG002', 'EVE0101': 'BBG001', 'EVE0116': 'BBG201',
    'EVE0118': 'BBG101', 'EVE102': 'BBG102', 'EVE105': 'BBG105',
    'EVE202': 'BBG202', 'EVE205': 'BBG205', 'EVE207': 'BBG207',
}
# Menu/HUD pictures the runtime draws from the SYSTEM census (docs/research/pc-menu-hud-inventory.json), as
# (PC file, image index): evidence. Only pieces whose table or patch was read are listed; everything else stays open.
MENU_REPORT = 'docs/research/pc-menu-hud-inventory.md'
SYSTEM_HUD_DRAWS = {
    ('SAKURA1/SYSTEM/FONT_CSL.SPR', 0): ('patch 0093, port/system_brackets.h: left inventory bracket', MENU_REPORT + '#t110a-inventory-brackets-in-game'),
    ('SAKURA1/SYSTEM/FONT_CSL.SPR', 1): ('patch 0093, port/system_brackets.h: right inventory bracket', MENU_REPORT + '#t110a-inventory-brackets-in-game'),
    ('SAKURA1/SYSTEM/SIS_ICON.SPR', 2): ('patch 0112, port/load_disc_icon.h: CD-1 load emblem', MENU_REPORT + '#t110b-cd-1-emblem-in-the-load-menu'),
}
# SYSTEM files that belong to another category and must not be counted twice in hud-menus.
SYSTEM_HUD_EXCLUDED = {
    'SAKURA1/SYSTEM/KAO.SPR': 'portrait atlas (394 faces): counted in the portraits category through the FCE recipe and portrait pack',
}
MENU_CENSUS = 'docs/research/pc-menu-hud-inventory.json'
# The documented draws include partial native faces and conditional fallbacks.
BODY_DRAWS = {'NC10', 'NC11', 'NC20', 'NC25', 'NC30', 'NC50', 'NC55', 'NC82', 'NC97', 'NC3250'}  # NC10, NC50, NC3250: docs/research/coverage-campaign-v026.md
# Draw evidence applies to the exact disc, resource, and chapter observed.
SCENE_DRAWS = {
    BBG204_INSET: (4, BBG204_REPORT),
    **{(1, f'/SAKURA1/BG{number}.BIN'): (1, BODY_REPORT) for number in (1011, 1012, 1017)},
    **{(1, f'/SAKURA1/BG{number}.BIN'): (1, CAMPAIGN_REPORT) for number in (1001, 1006, 1045, 1209, 2159, 2250, 2251)},
    (1, '/SAKURA1/BG1119.BIN'): (1, CHAPTER1_ROUTE_REPORT),
    (1, '/SAKURA1/BG1216.BIN'): (1, CHAPTER1_ROUTE_REPORT),
    (2, '/SAKURA1/BG2159.BIN'): (8, 'docs/research/bg2159-disc2-visual.md'),
    (2, '/SAKURA1/BG2238.BIN'): (9, 'docs/research/bg2238-still.md'),
}
# Exact file witnesses with a documented chapter. Shared disc residency and
# the sequence of files in a cold run are insufficient for chapter placement.
CHAPTER_WITNESSES = {
    (1, '/SAKURA1/BG1198.BIN'): (3, 'docs/research/th3-native-attribution.md'),
    (1, '/SAKURA1/TITLE3.BIN'): (3, 'docs/research/th3-native-attribution.md'),
    (1, '/SAKURA1/BG1022.BIN'): (3, 'docs/research/th3-native-attribution.md'),
    (1, '/SAKURA1/BG1008.BIN'): (3, 'docs/research/th3-native-attribution.md'),
    (1, '/SAKURA2/MAP04.BIN'): (3, 'docs/research/th3-native-attribution.md'),
    (1, '/SAKURA2/UNIT04.BIN'): (3, 'docs/research/th3-native-attribution.md'),
    **{(1, f'/SAKURA1/{name}.BIN'): (1, CHAPTER1_ROUTE_REPORT)
       for name in CHAPTER1_ROUTE_SCENES + CHAPTER1_ROUTE_BODIES},
    **SCENE_DRAWS,
    (1, '/SAKURA1/NC20.BIN'): (1, BODY_REPORT),
    (1, '/SAKURA1/NC30.BIN'): (1, BODY_REPORT),
    (2, '/SAKURA1/BG1285.BIN'): (10, BG1285_REPORT),
    (1, '/SAKURA1/BG1207.BIN'): (1, BG1207_REPORT),
    (1, '/SAKURA1/BG2248.BIN'): (1, BG2248_REPORT),
    (1, '/SAKURA1/BG2533.BIN'): (5, 'docs/research/bg2533-pan.md'),
    (1, '/SAKURA2/EVE0101.BIN'): (1, BODY_REPORT),
    (1, '/SAKURA2/EVE0116.BIN'): (1, EVE0116_REPORT),
    (1, '/SAKURA2/EVE0118.BIN'): (1, EVE0118_REPORT),
    (1, '/SAKURA2/EVE202.BIN'): (2, BODY_REPORT),
    (1, '/SAKURA2/EVE002.BIN'): (2, EVE002_REPORT),
    STAGE01_MAP: (1, STAGE01_REPORT),
    TH2_GROUND: (2, TH2_REPORT),
    TH2_UNITS: (2, TH2_REPORT),
    STAGE21_MAP: (4, STAGE21_REPORT),
    STAGE06_MAP: (4, CHAPTER4_TACTICAL_REPORT),
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
        text = header.read_text(encoding='utf-8')
        first = set(re.findall(r'\{0x([0-9A-F]+)ull,"([^"]+)",(\d+)\}', text))
        cells = {(palette, fnv): (file, index) for palette, fnv, file, index in re.findall(
            r'\{0x([0-9A-F]+)ull,0x([0-9A-F]+)ull,"([^"]+)",(\d+)\}', text)}
        return first, cells


def fce_atlas_row(identities, recipes):
    """TP6: attribute an FCE atlas file to the portrait identities it holds."""
    uncovered = [i for i in identities if i not in recipes]
    if not identities:
        return {'status': 'excluded', 'identities': [],
                'reason': 'empty atlas (160-byte zero header): no portrait identity to replace',
                'evidence': PORTRAIT_REPORT}
    row = {'status': 'hd' if not uncovered else 'unknown', 'identities': identities,
           'evidence': 'config/hd-portrait-recipe.json'}
    if uncovered:
        row['uncovered'] = uncovered
        row['reason'] = ('every other identity is in the runtime portrait table; the listed identities '
                         'have no accepted PC pair (tracked as their own portrait rows, T52)')
    return row


def build(root, index_dir, portrait_audit):
    def config(name):
        return load(root / 'config' / (name + '.json'))

    inventory = load(index_dir / 'resource-inventory.json')
    index = load(index_dir / 'scene-index.json')
    portrait_report = load(portrait_audit)
    if portrait_report.get('errors'):
        raise ValueError('The portrait audit reports errors')
    portraits = portrait_report['rows']
    fce_atlases = portrait_report.get('fce_atlases', {})
    recipes = {r['id']: r['pc_index'] for r in config('hd-portrait-recipe')['portraits']}
    films = {(r['disc'], r['fad']): r for r in config('film-fad-map')['streams']}
    bg = pairs(config('hd-scene-bg-map'))
    bg_review = config('hd-scene-bg-review')
    scroll_rows = {row['name'] for row in config('hd-scroll-pictures')['rows']}
    bg_table, bg_cell_table = runtime_bg_entries(root)
    donor_hashes = {
        (row['pc_file'], str(row['pc_image_index'])): row.get('pc_sha256')
        for row in bg.values() if row.get('pc_file') and 'pc_image_index' in row
    }
    screens = pairs(config('hd-screen-map'))
    endings = pairs(config('hd-ending-bank-map'))
    bodies = pairs(config('hd-body-map'))
    body_review = config('hd-body-review')
    # Match tools/gen_body_table.py, including reviewed cut-outs with a candidate-tier pair.
    confirmed_bodies = set(body_review['eye_confirmed_candidates']) | set(body_review.get('cutout', {}))
    body_runtime = {
        Path(path).stem for path, pair in bodies.items()
        if Path(path).stem not in body_review['rejected']
        and (pair['tier'] == 'content' or Path(path).stem in confirmed_bodies)
    }
    items = pairs(config('hd-item-map'))
    item_review = pairs(config('hd-item-review'))
    # Same selection as tools/gen_item_table.py: the palettes that the runtime item-card table (patch 0090) holds.
    item_runtime = {palette for palette, _ in gen_item_table.build_rows(
        config('hd-item-map'), config('hd-item-review')['pairs'])} & set(config('hd-item-texture-fingerprints'))
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
        if chapter is None:
            residency = resident.get(ident) or CHAPTER_FILE_RESIDENCIES.get(ident)
            if residency:
                chapter, report = residency
                association = 'resident'
        if chapter is None:
            candidate = indexed_chapter(path)
            if candidate and disc == disc_for(candidate):
                chapter, association = candidate, 'inferred'
        if (disc, path) in CHAPTER_WITNESSES:
            chapter, report = CHAPTER_WITNESSES[(disc, path)]
            association = 'observed'
        row = {'status': 'unknown'}
        if (disc, path) == STAGE01_MAP:
            row = {
                'status': 'hd',
                'pc': 'SAKURA2/MAP/MAP01/MAP01_A.SPR',
                'scope': 'source-4 ground only',
                'extension': 'STAGE01-right-v1.png',
            }
        elif (disc, path) == TH2_GROUND:
            row = {
                'status': 'paired-not-wired',
                'pc': 'SAKURA2/MAP/MAP02/MAP02_A.SPR',
                'scope': 'source-4 ground only',
            }
        elif (disc, path) == STAGE21_MAP:
            row = {
                'status': 'hd',
                'pc': 'SAKURA2/MAP/MAP21/MAP21_A.SPR',
                'scope': 'source-4 ground only',
                'verified_in_game': True,
                'runtime_evidence': STAGE21_REPORT,
            }
        elif (disc, path) == STAGE06_MAP:
            row = {
                'status': 'paired-not-wired',
                'pc': 'SAKURA2/MAP/MAP06/MAP06_A.SPR',
                'scope': 'ground only',
                'reason': 'The PC ground aligns across three cameras. A layer guard and runtime sampling remain to be verified.',
                'pairing_evidence': CHAPTER4_TACTICAL_REPORT,
            }
        elif (disc, path) == BBG204_INSET:
            row = {'status': 'hd', 'pc': 'SAKURA2/BG/BBG204.SPR',
                   'verified_in_game': True, 'runtime_evidence': BBG204_REPORT}
        elif title := re.fullmatch(r'/SAKURA1/(TITLE[1-9])\.BIN', path):
            row = {
                'status': 'excluded',
                'pc': f'SAKURA1/TITLE/{title[1]}.SPR',
                'reason': 'Japanese lettering is baked into the PC image. The approved episode cards use localized centers.',
                'decision_evidence': 'docs/research/episode-title-pc-pairings.md',
            }
        elif disc == 1 and name in BBG_INSET_PAIRS and path == f'/SAKURA2/{name}.BIN':
            row = {'status': 'hd', 'pc': f'SAKURA2/BG/{name}.SPR', 'pairing_evidence': BBG_INSET_REPORT}
        elif path in endings:
            bank = endings[path]
            row = {
                'status': 'paired-not-wired',
                'pc': bank['pc_file'],
                'pc_image_indices': [record['pc_image_index'] for record in bank['records']],
                'scope': 'ending-bank subimages',
                'reason': 'Requires ending-layer composition and viewport evidence.',
                'decision_evidence': 'docs/research/ending-bank-pairs.md',
            }
        elif path in bg:
            pair = bg[path]
            accepted = name not in bg_review['rejected'] and (
                pair.get('tier') == 'content' or name in bg_review['eye_confirmed_number_tier']
            )
            if accepted:
                key = (pair['palette_fnv'], pair['pc_file'], str(pair['pc_image_index']))
                donor = bg_cell_table.get((pair['palette_fnv'], pair.get('cells_fnv')))
                same_image = donor == key[1:] or (
                    donor is not None and pair.get('pc_sha256') and donor[1] == key[2] and
                    donor_hashes.get(donor) == pair['pc_sha256'] and pair['size'] == [288, 144] and
                    path.startswith(('/SAKURA1/', '/SAKURA2/EVE', '/SAKURA2/BBG')) and name[2:3] not in '34') or (
                    donor is not None and name in bg_review.get('shared_cell_choice', {}) and pair['size'] == [288, 144])
                row = {'status': 'hd' if key in bg_table or same_image else 'paired-not-wired',
                       'pc': donor[0] if same_image else pair['pc_file']}
                if (disc, path) == (1, '/SAKURA1/BG2533.BIN'):
                    row['status'] = 'hd'
                    row['runtime_evidence'] = 'docs/research/bg2533-pan.md'
                elif path == '/SAKURA1/BG2295.BIN' or name in bg_review.get('guarded_viewport', []):
                    row['status'] = 'hd'
                elif path == '/SAKURA1/BG1285.BIN':
                    row['status'] = 'hd'
                    if disc == 2:
                        row.update(verified_in_game=True, runtime_evidence=BG1285_REPORT)
                elif path == '/SAKURA1/BG1207.BIN':
                    row['status'] = 'hd'
                    if disc == 1:
                        row.update(verified_in_game=True, runtime_evidence=BG1207_REPORT)
                elif path == '/SAKURA1/BG2248.BIN':
                    row['status'] = 'hd'
                    if disc == 1:
                        row.update(verified_in_game=True, runtime_evidence=BG2248_REPORT)
                elif path == '/SAKURA1/BG2238.BIN':
                    row['status'] = 'hd'
                    if (disc, path) in SCENE_DRAWS:
                        row.update(verified_in_game=True, runtime_evidence=SCENE_DRAWS[(disc, path)][1])
                elif name in scroll_rows:
                    # TP2: a row of the scroll-picture table (config/hd-scroll-pictures.json) is drawn by the runtime's table path.
                    row['status'] = 'hd'
                    row.setdefault('runtime_evidence', SCROLL_REPORT)
                elif row['status'] == 'hd' and (disc, path) in SCENE_DRAWS:
                    row['verified_in_game'] = True
                    row['runtime_evidence'] = SCENE_DRAWS[(disc, path)][1]
                elif (disc, path) == (1, '/SAKURA2/EVE0116.BIN'):
                    row.update(status='hd', verified_in_game=True, runtime_evidence=EVE0116_REPORT)
                elif (disc, path) == (1, '/SAKURA2/EVE002.BIN'):
                    row.update(status='hd', verified_in_game=True, runtime_evidence=EVE002_REPORT)
                elif (disc, path) == (1, '/SAKURA2/EVE0118.BIN'):
                    row.update(status='hd', verified_in_game=True, runtime_evidence=EVE0118_REPORT)
                elif row['status'] != 'hd':
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
            if path == '/SAKURA1/IC01.BIN':
                row['status'] = 'hd'
                row['verified_in_game'] = disc == 1
                if disc == 1:
                    row['runtime_evidence'] = 'docs/research/ic01-hd-intermission.md'
            else:
                row['reason'] = ('no saved state or route reaches this intermission, so its palette key, '
                                 'menu layers, darkening and anchor are unwitnessed; see docs/research/ic01-hd-intermission.md')
        elif name in EVE_PAIRS:
            row = {'status': 'paired-not-wired', 'pc': 'SAKURA2/BG/' + EVE_PAIRS[name] + '.SPR'}
        elif kind == 'bodies' and name in body_review.get('paired_not_wired', {}):
            row = {
                'status': 'paired-not-wired',
                'pc': f'SAKURA1/NC/{name}.SPR',
                'reason': body_review['paired_not_wired'][name],
                'pairing_evidence': 'docs/research/saturn-bg-format.md#tp5a-bounded-body-crops',
            }
        elif path in bodies:
            pair = bodies[path]
            if name in body_review['rejected']:
                row['status'] = 'unpaired'
            elif name in body_runtime:
                row = {'status': 'hd',
                       'pc': 'SAKURA1/NC/' + (pair['best_pc'] if pair['tier'] == 'content' else pair['same_name_pc'])}
                row['verified_in_game'] = name in BODY_DRAWS
                if name in BODY_DRAWS:
                    row['native_face_fallback'] = True
                    row['runtime_evidence'] = BODY_REPORT
        elif path in items:
            pair = items[path]
            if pair['tier'] == 'content' or item_review.get(path, {}).get('verdict') == 'confirmed':
                row = {'status': 'paired-not-wired', 'pc': pair['pc_file'], 'pc_image_index': pair['pc_image_index']}
                if pair['palette_fnv'].upper() in item_runtime:
                    row.update(status='hd', runtime_evidence=MENU_REPORT + '#item-detail-sprite-witness-t109')
            elif path in item_review:
                row['status'] = 'unpaired'
        if kind == 'portraits' and f'{disc}:{path}' in fce_atlases and row['status'] == 'unknown':
            row.update(fce_atlas_row(fce_atlases[f'{disc}:{path}'], recipes))
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
                    row.update(status='excluded' if film['alternate_cut'] else 'hd',
                               pc=movie, alternate_cut=film['alternate_cut'])
                    if film['alternate_cut']:
                        row['reason'] = 'alternate PC edit stays native to preserve the Saturn timing'
                elif path == '/SAKURA1/OPSAKURA.CPK' and 0 < film.get('duration', 0) < 0.5:
                    row.update(status='excluded', reason='short native transition without a PC clip')
            chapter, report = observed.get((ident, offset), (None, None))
            if (disc == 1 and path == '/SAKURA4' and offset in CHAPTER1_ROUTE_FILMS
                    and row.get('pc') == CHAPTER1_ROUTE_FILMS[offset]):
                chapter, report = 1, CHAPTER1_ROUTE_REPORT
            add('film', f'{disc}:{path}+{offset}', row, chapter,
                'observed' if chapter else 'unknown', report)
    census = load(root / MENU_CENSUS)
    for file in census['menus']:
        name = file['pc_path']
        if name in SYSTEM_HUD_EXCLUDED:
            unassigned['menus-hud']['pc:' + name] = {
                'status': 'excluded', 'pc': name, 'images': len(file['images']), 'association': 'unknown',
                'reason': SYSTEM_HUD_EXCLUDED[name]}
        for image in file['images']:
            if (name, image['index']) in SYSTEM_HUD_DRAWS:
                note, evidence = SYSTEM_HUD_DRAWS[(name, image['index'])]
                unassigned['menus-hud'][f"pc:{name}#{image['index']}"] = {
                    'status': 'hd', 'pc': name, 'pc_image_index': image['index'], 'association': 'unknown',
                    'draw': note, 'runtime_evidence': evidence}
    hud_census = {
        'system_images': sum(len(file['images']) for file in census['menus']),
        'item_images': len({(p['pc_file'], p['pc_image_index']) for p in config('hd-item-map')['pairs']}),
    }
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
        if ident not in recipes and ident in RESIDUAL_PORTRAIT_REVIEWS:
            row.update(RESIDUAL_PORTRAIT_REVIEWS[ident], pairing_evidence=RESIDUAL_PORTRAIT_REPORT)
        if sources:
            row['atlases'] = sources
        if ident in CHAPTER1_ROUTE_PORTRAITS:
            add('portraits', ident, row, 1, 'observed', CHAPTER1_ROUTE_REPORT)
        else:
            add('portraits', ident, row, 1 if sources else None,
                'inferred' if sources else 'unknown', PORTRAIT_REPORT if sources else None)

    return {
        'schema': 1,
        'status': {
            'hd': 'Implemented: the runtime table holds it and the runtime draws it when it appears (for a body, a documented draw sets verified_in_game). Seeing it in a replay is separate.',
            'wired-unverified': 'Reserved: in a table but not drawn by the runtime. Bodies in the runtime table are `hd` now; `verified_in_game` says whether a draw was observed.',
            'paired-not-wired': 'Accepted counterpart that is genuinely not in the runtime table (for example an ambiguous palette). Check `reason` first.',
            'excluded': 'Native by design (key-colour cut-outs, blank pictures, alternate film edits or native transitions).',
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
        'hud_census': hud_census,
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
