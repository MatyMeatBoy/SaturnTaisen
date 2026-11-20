#!/usr/bin/env python3
"""THD21: classify the open menu/HUD PC images by family and by what connects them.

Offline and read-only: it reads docs/research/pc-menu-hud-inventory.json (names, sizes, counts) and the
drawn set SYSTEM_HUD_DRAWS in tools/hd_chapter_coverage.py. No pixels, no runtime.
  python tools/menu_open_classification.py            write config/hd-menu-open-classification.json
  python tools/menu_open_classification.py --check    fail if the file is stale
"""
import argparse, collections, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import hd_chapter_coverage as cov  # noqa: E402

OUT = ROOT / 'config' / 'hd-menu-open-classification.json'
CENSUS = ROOT / 'docs' / 'research' / 'pc-menu-hud-inventory.json'
# connect: 'data' = a table row is enough (witnessed call already guarded); 'witness' = needs a saved state or
# trace of the Saturn draw; 'mechanism' = needs a new compositor; 'native' = keep native by decision.
FAMILIES = {
    'system-frames': ('witness+mechanism', ['SISTEM', 'SIS_BG', 'SIS_BG2', 'SIS_BG3', 'OPTION', 'WINDOW', 'EXIT_W', 'BURO_W', 'TUIKA_W'],
        'Frames and tab panels. The 0197-0213 patches draw rails from VDP1/VDP2 ownership per menu; the rest has no VDP1 texture witness. Needs the menu open in a state to read which layer draws it.'),
    'disc-icons': ('witness', ['SIS_ICON'],
        'CD-1/CD-2 pink done (0112, 0146). Blue selected variants need a selected-slot state; CD-3/CD-4 never appear on a two-disc Saturn; System RAM and cartridge stay native.'),
    'title-logo': ('witness+mechanism', ['TITLE', 'SEGALOGO', 'REDLOGO', 'TL_BG0', 'TL_ROGO0', 'CAUTION', 'NOWLOAD'],
        'Title/logo/caution screens at 640x480 with baked Japanese or PC-only text; Saturn builds them from LOGO.SH2 16x16 tiles. Needs one witnessed frame per screen and a text decision.'),
    'extra-menu': ('witness+mechanism', ['KARAOKE', 'OMKMOV_W', 'OMKSND_W', 'MINISAKU', 'MSTAFF'],
        'Extra (omake) menu labels and panels; no pointer table and no witnessed draw call. Needs an extra-menu saved state.'),
    'steam': ('witness', ['JYOUKI'], 'Steam animation; no native sequence identified.'),
    'keep-native': ('native', ['R_HARI', 'SHADE_WB', 'OP_WIN', 'SHADE_WA'],
        'Kept native by decision (aspect, clock face, baked Japanese labels) or no native texture (SHADE_WA).'),
}


def build():
    census = json.loads(CENSUS.read_text(encoding='utf-8'))
    done = set(cov.SYSTEM_HUD_DRAWS)
    fam_of = {m: f for f, (_, names, _) in FAMILIES.items() for m in names}
    rows = collections.defaultdict(lambda: collections.defaultdict(list))
    for m in census['menus']:
        if m['id'] == 'KAO':
            continue
        for img in m['images']:
            if (m['pc_path'], img['index']) in done:
                continue
            rows[fam_of[m['id']]][m['id']].append({'index': img['index'], 'size': [img['width'], img['height']]})
    families = {}
    for f, (connect, _, note) in FAMILIES.items():
        files = rows.get(f, {})
        families[f] = {'connect': connect, 'note': note, 'open': sum(len(v) for v in files.values()),
                       'files': {k: {'open': len(v), 'images': v} for k, v in sorted(files.items())}}
    total = sum(v['open'] for v in families.values())
    return {'schema': 1,
            'scope': 'THD21 offline classification of open SYSTEM images (no KAO); the ten open item pictures are listed separately',
            'open_system_images': total,
            'open_item_pictures': 10,
            'open_total': total + 10,
            'connectable_by_data_alone': 0,
            'item_pictures': 'ITEM09 full card plus nine compact icons: the card path needs a full-card counterpart; the 40 unpaired Saturn ITEM BINs have no PC card in hd-item-review.json',
            'families': families}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    text = json.dumps(build(), indent=1, ensure_ascii=False) + '\n'
    if a.check:
        if not OUT.exists() or OUT.read_text(encoding='utf-8') != text:
            print('stale: run tools/menu_open_classification.py'); return 1
        return 0
    OUT.write_text(text, encoding='utf-8'); print('wrote', OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
