"""Adds `cells_fnv` (FNV-1a 64 of the cell data the game copies to VDP2) to every pair of config/hd-scene-bg-map.json (TW1).

The palette fingerprint alone cannot tell apart pictures that share a palette. The cell data hash is the second key: the runtime hashes
the same bytes from VDP2 VRAM (`decode_saturn_bg.picture_bytes` is exactly what the game copies) and looks the pair up by (palette, cells).
Data only (hashes). The disc images are read, nothing is written out of them.

    python tools/add_cells_fnv.py --disc "local/prepared/disc1/Track 01.iso:SAKURA1" --disc "local/prepared/disc2/Track 01.iso:SAKURA2"
"""
import argparse, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]


def fnv64(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', type=pathlib.Path, default=ROOT / 'config/hd-scene-bg-map.json')
    ap.add_argument('--disc', action='append', required=True, help='ISO:FOLDER, repeatable (the folder picks the disc of its pairs)')
    a = ap.parse_args()
    sources = {}
    for spec in a.disc:
        path, _, folder = spec.rpartition(':')
        iso = saturn.Iso(path)
        sources[folder] = (iso, dict(iso.files(folder)))
    data = json.loads(a.map.read_text(encoding='utf-8'))
    added = missing = 0
    for pair in data['pairs']:
        folder, _, name = pair['saturn_file'].partition('/')
        if folder not in sources or not pair.get('decoded'):
            continue
        iso, files = sources[folder]
        if name not in files:
            missing += 1
            continue
        cells = saturn.picture_bytes(iso.content(files[name]))
        if cells is None:
            missing += 1
            continue
        pair['cells_fnv'] = '%016X' % fnv64(cells)
        added += 1
    a.map.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print('cells_fnv added to', added, 'pairs;', missing, 'not found')


if __name__ == '__main__':
    main()
