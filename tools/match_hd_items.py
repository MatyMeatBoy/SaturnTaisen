"""Pair the Saturn item pictures (ITEMnn.BIN) with the PC item pictures by content (T23/T54).

ITEMnn.BIN (13,056 bytes) is a 112x112 picture at 8 bits per pixel, stored line by line after a 256-word RGB555
big-endian palette; palette index 0 is the transparent key. The PC pictures (SAKURA1/ITEM/*.SPR, SPRED with
alpha) have another size and aspect, so both are put on mid-grey, reduced to a 32x32 grey signature and compared
by normalised correlation against every PC picture.

  python tools/match_hd_items.py --pc ROOT --iso "local/prepared/disc1/Track 01.iso" --out config/hd-item-map.json

Tiers: `content` when the best correlation is >= 0.90 and the runner-up is at least 0.05 lower; otherwise
`candidate`. Data only: names, hashes and scores.
"""
import argparse
import glob
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402
import decode_spred  # noqa: E402

SIG = (32, 32)


def decode_item(data):
    """Return a 112x112 RGBA picture (index 0 transparent) or None."""
    if len(data) != 512 + 112 * 112:
        return None
    words = struct.unpack_from('>256H', data, 0)
    palette = [(((w & 31) * 255 // 31), ((w >> 5) & 31) * 255 // 31, ((w >> 10) & 31) * 255 // 31) for w in words]
    image = Image.new('RGBA', (112, 112))
    pixels = image.load()
    for i, index in enumerate(data[512:]):
        pixels[i % 112, i // 112] = (0, 0, 0, 0) if index == 0 else palette[index] + (255,)
    return image


def signature(image):
    grey = Image.new('RGB', image.size, (128, 128, 128))
    grey.paste(image.convert('RGBA'), mask=image.convert('RGBA').split()[3])
    values = list(grey.convert('L').resize(SIG, Image.BILINEAR).getdata())
    mean = sum(values) / len(values)
    centred = [v - mean for v in values]
    norm = sum(v * v for v in centred) ** 0.5 or 1.0
    return [v / norm for v in centred]


def correlation(a, b):
    return sum(x * y for x, y in zip(a, b))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pc', type=Path, required=True)
    parser.add_argument('--iso', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    pcs = []
    for path in sorted(glob.glob(str(args.pc / 'SAKURA1/ITEM/*.SPR'))):
        raw = Path(path).read_bytes()
        try:
            pictures = decode_spred.decode(raw)
        except Exception:
            continue
        for index, picture in pictures:
            pcs.append({'file': Path(path).resolve().relative_to(args.pc.resolve()).as_posix(), 'index': index,
                        'size': list(picture.size), 'sha256': hashlib.sha256(raw).hexdigest(), 'sig': signature(picture)})
    iso = saturn.Iso(args.iso)
    pairs = []
    for name, extent in iso.files('SAKURA1'):
        if not re.match(r'ITEM\d+\.BIN$', name):
            continue
        data = iso.content(extent)
        image = decode_item(data)
        if image is None:
            continue
        sig = signature(image)
        ranked = sorted(((correlation(sig, p['sig']), p) for p in pcs), key=lambda t: -t[0])
        best, second = ranked[0], ranked[1]
        firm = best[0] >= 0.90 and best[0] - second[0] >= 0.05
        pairs.append({'saturn_file': f'SAKURA1/{name}', 'palette_fnv': '%016X' % saturn_fnv(data[:512]),
                      'pc_file': best[1]['file'], 'pc_image_index': best[1]['index'], 'pc_sha256': best[1]['sha256'],
                      'pc_size': best[1]['size'], 'correlation': round(best[0], 3),
                      'runner_up': second[1]['file'], 'runner_up_correlation': round(second[0], 3),
                      'tier': 'content' if firm else 'candidate'})
    summary = {t: sum(p['tier'] == t for p in pairs) for t in ('content', 'candidate')}
    args.out.write_text(json.dumps({'schema': 1, 'scope': 'Saturn ITEMnn.BIN to PC item pictures by content; data only.',
                                    'summary': summary, 'pairs': pairs}, indent=1) + '\n', encoding='utf-8')
    print(len(pairs), summary, 'PC pictures', len(pcs))


def saturn_fnv(palette):
    value = 14695981039346656037
    for byte in palette:
        value = ((value ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value


if __name__ == '__main__':
    main()
