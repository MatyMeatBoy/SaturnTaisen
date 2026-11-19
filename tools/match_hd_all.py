"""Mass pairing of Saturn `BG*.BIN` backgrounds with PC `.SPR` pictures, all discs and both layouts (T76-T711).

One command replaces the screenshot-by-screenshot work: every Saturn picture the decoder understands
(`tools/decode_saturn_bg.py`, both variants) is paired with the PC picture of the same file number and
scored on content, in parallel, and the pairs are written as data (no pixels).

  python tools/match_hd_all.py --pc ROOT_OF_EXTRACTED_PC --out config/hd-scene-bg-map-all.json \\
      --disc "local/prepared/disc1/Track 01.iso:SAKURA1" --disc "local/prepared/disc2/Track 01.iso:SAKURA2"

`--disc ISO:FOLDER` can repeat. PC pictures are looked up as ROOT/FOLDER/BG/<name>.SPR, then
ROOT/FOLDER/<name>.SPR. Comparison: both pictures are reduced to a 48x24 luminance signature; when the
PC picture is taller than the Saturn aspect (the PC pictures carry 16 extra native rows) its top and bottom
crops are both tried and the best score wins. Tiers:
  content   score <= 0.10 (the same-number PC picture looks like the Saturn one)
  number    same number but the content differs (other crop, lighting or palette): needs an eye check
  missing   no PC picture with that number
Never commit decoded pictures; the output only has names, hashes and scores.
"""
import argparse
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402
import decode_spred  # noqa: E402

SIG = (48, 24)


def signature(image):
    return image.convert('L').resize(SIG, Image.BILINEAR)


def score(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 255.0


def pc_path(root, folder, name):
    for candidate in (root / folder / 'BG' / name, root / folder / name):
        if candidate.is_file():
            return candidate
    return None


def best_score(sat_image, pc_image):
    sat_sig = signature(sat_image)
    aspect = sat_image.width / sat_image.height
    rgb = pc_image.convert('RGB')
    crop_h = round(rgb.width / aspect)
    crops = [rgb] if crop_h >= rgb.height else [
        rgb.crop((0, 0, rgb.width, crop_h)), rgb.crop((0, rgb.height - crop_h, rgb.width, rgb.height))]
    return min(score(sat_sig, signature(c)) for c in crops)


def work(task):
    iso_path, folder, name, extent, pc_root = task
    iso = saturn.Iso(iso_path)
    data = iso.content(extent)
    image = saturn.decode(data)
    entry = {'saturn_file': f'{folder}/{name}', 'decoded': image is not None}
    if image is None:
        return entry
    body = saturn.picture_bytes(data)
    entry['cells_sha256'] = hashlib.sha256(body).hexdigest()
    entry['size'] = [image.width, image.height]
    spr = pc_path(Path(pc_root), folder, name[:-4] + '.SPR')
    if spr is None:
        entry['tier'] = 'missing'
        return entry
    raw = spr.read_bytes()
    try:
        pictures = decode_spred.decode(raw)
    except Exception:
        entry['tier'] = 'missing'
        return entry
    if not pictures:
        entry['tier'] = 'missing'
        return entry
    index, picture = max(pictures, key=lambda p: p[1].width * p[1].height)
    value = best_score(image, picture)
    entry.update({'pc_file': spr.relative_to(pc_root).as_posix(), 'pc_image_index': index,
                  'pc_sha256': hashlib.sha256(raw).hexdigest(), 'pc_size': list(picture.size),
                  'content_score': round(value, 4), 'tier': 'content' if value <= 0.10 else 'number'})
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pc', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--disc', action='append', required=True, help='ISO:FOLDER, repeatable')
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    tasks = []
    for spec in args.disc:
        iso_path, _, folder = spec.rpartition(':')
        iso = saturn.Iso(iso_path)
        for name, extent in iso.files(folder):
            if name.startswith(('BG', 'BBG')) and name.endswith('.BIN'):
                tasks.append((iso_path, folder, name, extent, str(args.pc)))
    with ProcessPoolExecutor(args.workers) as pool:
        entries = list(pool.map(work, tasks, chunksize=8))
    pairs = [e for e in entries if e.get('decoded')]
    summary = {t: sum(e.get('tier') == t for e in pairs) for t in ('content', 'number', 'missing')}
    keys = [e['cells_sha256'] for e in pairs]
    out = {'schema': 1,
           'scope': 'Saturn BG*.BIN to PC .SPR by shared file number with a content score; data only (names, hashes, scores). '
                    'cells_sha256 identifies the native picture at runtime. Tier `number` needs an eye check before drawing.',
           'summary': summary, 'duplicate_cell_hashes': len(keys) - len(set(keys)),
           'undecoded': [e['saturn_file'] for e in entries if not e.get('decoded')], 'pairs': pairs}
    args.out.write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    print(len(pairs), 'decoded', summary, 'undecoded', len(out['undecoded']), 'duplicate keys', out['duplicate_cell_hashes'])


if __name__ == '__main__':
    main()
