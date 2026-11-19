"""Pair the Saturn large-character bodies (NC*.BIN) with the PC NC pictures by content (T19).

`tools/decode_saturn_bg.py decode_nc` reads the body bitmap of each NC*.BIN (176-ish x 144, face left blank: the
eyes and mouth are separate strips). The PC `SAKURA1/NC/*.SPR` hold the body as the first and largest picture
(for example 326x320) with the face drawn in. Both are put on mid-grey, reduced to a 32x32 grey signature
(aspect ignored: the PC picture is not a plain 2x of the Saturn one) and compared by normalised correlation
against every PC body. Tiers: `content` when the same-named PC file is the best match and correlates >= 0.75,
otherwise `candidate`. Data only: names, hashes and scores.

  python tools/match_hd_bodies.py --pc ROOT --iso "local/prepared/disc1/Track 01.iso" --out config/hd-body-map.json
"""
import argparse
import glob
import hashlib
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402
import decode_spred  # noqa: E402

SIG = (32, 32)


def key_out(image):
    """PC NC pictures sit on a chroma background (green, or cyan for the NC30xx set) instead of alpha."""
    rgba = image.convert('RGBA')
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if a and r < 24 and g > 232 and b in range(0, 24) or a and r < 24 and g > 232 and b > 232:
                pixels[x, y] = (0, 0, 0, 0)
    return rgba


def signature(image):
    rgba = key_out(image)
    grey = Image.new('RGB', rgba.size, (128, 128, 128))
    grey.paste(rgba, mask=rgba.split()[3])
    values = list(grey.convert('L').resize(SIG, Image.BILINEAR).getdata())
    mean = sum(values) / len(values)
    centred = [v - mean for v in values]
    norm = sum(v * v for v in centred) ** 0.5 or 1.0
    return [v / norm for v in centred]


def correlation(a, b):
    return sum(x * y for x, y in zip(a, b))


def pc_body(path):
    raw = Path(path).read_bytes()
    try:
        pictures = decode_spred.decode(raw)
    except Exception:
        return None
    if not pictures:
        return None
    index, picture = max(pictures, key=lambda p: p[1].width * p[1].height)
    return {'file': Path(path).name, 'path': str(path), 'index': index, 'size': list(picture.size),
            'sha256': hashlib.sha256(raw).hexdigest(), 'sig': signature(picture)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pc', type=Path, required=True)
    parser.add_argument('--iso', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    paths = sorted(glob.glob(str(args.pc / 'SAKURA1/NC/*.SPR')))
    with ProcessPoolExecutor(args.workers) as pool:
        pcs = [p for p in pool.map(pc_body, paths, chunksize=4) if p]
    by_name = {p['file']: p for p in pcs}
    iso = saturn.Iso(args.iso)
    pairs, undecoded = [], []
    for name, extent in iso.files('SAKURA1'):
        if not re.match(r'NC\d+\.BIN$', name):
            continue
        data = iso.content(extent)
        image = saturn.decode_nc(data)
        if image is None:
            undecoded.append(f'SAKURA1/{name}')
            continue
        sig = signature(image)
        ranked = sorted(((correlation(sig, p['sig']), p) for p in pcs), key=lambda t: -t[0])
        own = by_name.get(name[:-4] + '.SPR')
        value = correlation(sig, own['sig']) if own else None
        best = ranked[0]
        entry = {'saturn_file': f'SAKURA1/{name}', 'size': list(image.size),
                 'palette_fnv': '%016X' % saturn_fnv(data[0x410:0x610]),
                 'same_name_pc': own['file'] if own else None,
                 'same_name_correlation': round(value, 3) if value is not None else None,
                 'best_pc': best[1]['file'], 'best_correlation': round(best[0], 3),
                 'pc_sha256': (own or best[1])['sha256'], 'pc_size': (own or best[1])['size']}
        entry['tier'] = 'content' if own and best[1]['file'] == own['file'] and value >= 0.75 else 'candidate'
        pairs.append(entry)
    summary = {t: sum(p['tier'] == t for p in pairs) for t in ('content', 'candidate')}
    args.out.write_text(json.dumps({'schema': 1, 'scope': 'Saturn NC*.BIN bodies to PC NC pictures by content; data only.',
                                    'summary': summary, 'undecoded': undecoded, 'pairs': pairs}, indent=1) + '\n', encoding='utf-8')
    print(len(pairs), summary, 'undecoded', len(undecoded), 'PC bodies', len(pcs))


def saturn_fnv(palette):
    value = 14695981039346656037
    for byte in palette:
        value = ((value ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value


if __name__ == '__main__':
    main()
