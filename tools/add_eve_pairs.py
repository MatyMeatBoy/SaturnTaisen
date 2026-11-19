"""Adds the reviewed EVE event pictures to config/hd-scene-bg-map.json so the scene-picture table wires them (TW2, T105b).

Each `SAKURA2/EVE*.BIN` is 288x144 like a BG picture and was matched by eye to a PC `SAKURA2/BG/BBG*.SPR` (576x320, the same whole-scene
layout as the BG pictures, so the T74 draw stretches it the same way). Only pairs whose content score is 0.80 or more are added: EVE0101
(0.673) and EVE105 (0.594) show the same artwork at a different framing and would be drawn misframed; they stay native.
Data only (names, hashes, scores). Reads the disc 1 image.

    python tools/add_eve_pairs.py --disc "local/prepared/disc1/Track 01.iso" --pc local/work/v02-pc-game/_t_@_C__
"""
import argparse, hashlib, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402
from add_cells_fnv import fnv64  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
# name -> (PC file, content correlation recorded in docs/research/saturn-bg-format.md, what the picture is)
PAIRS = {
    'EVE002': ('BBG002', 0.824), 'EVE0116': ('BBG201', 0.923), 'EVE0118': ('BBG101', 0.828), 'EVE102': ('BBG102', 0.807),
    'EVE202': ('BBG202', 0.895), 'EVE205': ('BBG205', 0.915), 'EVE207': ('BBG207', 0.999),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--disc', required=True)
    ap.add_argument('--pc', type=pathlib.Path, required=True)
    ap.add_argument('--map', type=pathlib.Path, default=ROOT / 'config/hd-scene-bg-map.json')
    ap.add_argument('--review', type=pathlib.Path, default=ROOT / 'config/hd-scene-bg-review.json')
    a = ap.parse_args()
    iso = saturn.Iso(a.disc)
    files = dict(iso.files('SAKURA2'))
    data = json.loads(a.map.read_text(encoding='utf-8'))
    review = json.loads(a.review.read_text(encoding='utf-8'))
    have = {p['saturn_file'] for p in data['pairs']}
    added = []
    for name, (pc, score) in PAIRS.items():
        key = 'SAKURA2/%s.BIN' % name
        if key in have:
            continue
        content = iso.content(files[name + '.BIN'])
        image = saturn.decode(content)
        cells = saturn.picture_bytes(content)
        pc_path = a.pc / 'SAKURA2' / 'BG' / (pc + '.SPR')
        data['pairs'].append({
            'saturn_file': key, 'decoded': True, 'size': list(image.size),
            'cells_sha256': hashlib.sha256(cells).hexdigest(), 'palette_fnv': '%016X' % saturn.palette_fingerprint(content),
            'pc_file': 'SAKURA2/BG/%s.SPR' % pc, 'pc_image_index': 0, 'pc_sha256': hashlib.sha256(pc_path.read_bytes()).hexdigest(),
            'pc_size': [576, 320], 'correlation': score, 'tier': 'number', 'cells_fnv': '%016X' % fnv64(cells)})
        if name not in review['eye_confirmed_number_tier']:
            review['eye_confirmed_number_tier'].append(name)
        added.append(name)
    review['eye_confirmed_number_tier'].sort()
    a.map.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    a.review.write_text(json.dumps(review, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print('added', added)


if __name__ == '__main__':
    main()
