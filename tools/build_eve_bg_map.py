"""Build config/hd-eve-bg-map.json: EVE event pictures and scrolling variant-B pictures the runtime recognises (T105).

Usage: python tools/build_eve_bg_map.py DISC1_ISO DISC2_ISO PC_ROOT config/hd-eve-bg-map.json

Reads the discs and the PC pictures (local, read only); the output is numbers only (palette fingerprints, file
names, crop windows). An EVE picture is `enabled` only when a presented-frame witness exists (T105e: EVE0101 and EVE202,
palette seen on the active layer 5). The window is where the Saturn 288x144 picture sits inside the PC picture
(PC pixels, may overhang the PC picture: the overhang is black, like the black bars of the Saturn picture). It was fitted
by normalised correlation of the luminance at 288x144 (`fit`), so it is an estimate, not an exact match: the Saturn art
is a reframed, slightly stretched version of the PC art. Scrolling pictures are listed for recognition only: none is
drawn (BG2252 failed the alignment check, T105c; the others have no witness).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402

PC_FOR = {'EVE002': 'BBG002', 'EVE0101': 'BBG001', 'EVE0116': 'BBG201', 'EVE0118': 'BBG101', 'EVE102': 'BBG102',
          'EVE105': 'BBG105', 'EVE202': 'BBG202', 'EVE205': 'BBG205', 'EVE207': 'BBG207'}
# Fitted windows [x, y, w, h] in PC pixels and the correlation they reached; only the witnessed identities are enabled.
WINDOW = {'EVE0101': ([-16, -16, 648, 346], 0.911), 'EVE202': ([-8, 12, 576, 310], 0.885)}
WITNESS = {'EVE0101': 'battle-entry-ref-3000', 'EVE202': 'chapter-2 cold-native finish'}


def files(iso, folder):
    return {name: iso.content(extent) for name, extent in iso.files(folder)}


def main():
    disc1, disc2, pc_root, out = (Path(a) for a in sys.argv[1:5])
    iso1, iso2 = saturn.Iso(disc1), saturn.Iso(disc2)
    eve = {}
    for number, iso in (('1', iso1), ('2', iso2)):
        for name, data in files(iso, 'SAKURA2').items():
            if name.startswith('EVE') and name.endswith('.BIN'):
                eve.setdefault(name[:-4], {})[number] = '%016X' % saturn.palette_fingerprint(data)
    entries = []
    for name in sorted(eve):
        prints = set(eve[name].values())
        assert len(prints) == 1, name
        window, score = WINDOW.get(name, (None, None))
        entries.append({'eve': name, 'discs': sorted(eve[name]), 'palette': prints.pop(),
                        'pc_file': 'SAKURA2/BG/%s.SPR' % PC_FOR[name], 'pc_image_index': 0,
                        'window': window, 'fit': score, 'enabled': name in WITNESS,
                        'witness': WITNESS.get(name)})
    plan = json.loads((Path(__file__).resolve().parents[1] / 'config/hd-wide-bg-plan.json').read_text(encoding='utf-8'))
    on_disc = files(iso1, 'SAKURA1')
    scroll = []
    for item in plan['entries']:
        if item['class'] not in ('wide_scroll', 'tall_scroll') or not item['saturn_file'].startswith('SAKURA1/'):
            continue
        data = on_disc.get(item['saturn_file'].split('/')[-1])
        fp = None if data is None else saturn.palette_fingerprint(data)
        if fp is None:
            continue
        scroll.append({'file': item['saturn_file'], 'class': item['class'], 'size': item['size'],
                       'palette': '%016X' % fp, 'draw': False,
                       'reason': 'PC redraw failed the scene alignment check (T105c)' if item['saturn_file'].endswith('BG2252.BIN')
                       else 'no per-identity transform and no gameplay scroll witness (T105c2)'})
    scroll.sort(key=lambda e: (e['palette'], e['file']))
    out.write_text(json.dumps({'schema': 1, 'scope': 'EVE pictures and scrolling variant-B pictures recognised by the runtime (T105)',
                               'eve': entries, 'scroll': scroll}, indent=1) + '\n', encoding='utf-8')
    print(len(entries), 'EVE,', len(scroll), 'scroll,', sum(e['enabled'] for e in entries), 'enabled')


if __name__ == '__main__':
    main()
