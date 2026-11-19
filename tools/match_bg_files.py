"""Pair Saturn `BG*.BIN` scene backgrounds with PC `BG*.SPR` images by content (T67/T76-T711).

The Saturn pictures come from `tools/decode_saturn_bg.py` (288x144, 8 bpp cells). The PC pictures are
576x320 SPRED images (`tools/decode_spred.py`). The PC picture is twice the Saturn width and 16
native rows taller, so the Saturn picture is compared with the PC picture's top and bottom 288 rows
(the best of the two alignments) on a small luminance signature.

A pair is only reported as `firm` when the best score is clearly better than the runner-up
(margin >= 0.25 relative) and the score itself is low. Everything else is `ambiguous` and must be
confirmed by eye before it goes to config/hd-scene-bg-pairs.json. Lighting variants (BG1119 day /
BG1120 night) share structure and usually land in `ambiguous`.

Usage:
  python tools/match_bg_files.py ISO PC_BG_DIR OUT.json [--cache DIR]
Output is identifiers and scores only (no pixels).
"""
import argparse
import hashlib
import json
import pickle
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402
import decode_spred  # noqa: E402

SIG = (48, 24)


def signature(image):
    return image.convert('L').resize(SIG, Image.BILINEAR)


def pc_signatures(directory, cache):
    path = cache / 'pc-signatures.pkl' if cache else None
    if path and path.is_file():
        return pickle.loads(path.read_bytes())
    out = {}
    for spr in sorted(directory.glob('*.SPR')):
        data = spr.read_bytes()
        try:
            images = decode_spred.decode(data)
        except Exception:
            continue
        for index, image in images:
            if image.size != (576, 320):
                continue
            rgb = image.convert('RGB')
            top = signature(rgb.crop((0, 0, 576, 288)))
            bottom = signature(rgb.crop((0, 32, 576, 320)))
            out[(spr.name, index)] = (hashlib.sha256(data).hexdigest(), top, bottom)
    if path:
        cache.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps(out))
    return out


def score(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 255.0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('iso', type=Path)
    parser.add_argument('pc_bg', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--cache', type=Path)
    parser.add_argument('--folder', default='SAKURA1')
    args = parser.parse_args()
    pc = pc_signatures(args.pc_bg, args.cache)
    iso = saturn.Iso(args.iso)
    results = []
    for name, extent in iso.files(args.folder):
        if not (name.startswith('BG') and name.endswith('.BIN')):
            continue
        image = saturn.decode(iso.content(extent))
        if image is None:
            continue
        sig = signature(image)
        ranked = sorted(
            (min(score(sig, top), score(sig, bottom)), key) for key, (_, top, bottom) in pc.items())
        best, second = ranked[0], ranked[1]
        margin = (second[0] - best[0]) / second[0] if second[0] else 0.0
        results.append({
            'saturn_file': f'{args.folder}/{name}',
            'pc_file': best[1][0], 'pc_image_index': best[1][1], 'pc_sha256': pc[best[1]][0],
            'score': round(best[0], 4), 'runner_up': second[1][0], 'runner_up_score': round(second[0], 4),
            'margin': round(margin, 3),
            'status': 'firm' if margin >= 0.25 and best[0] < 0.08 else 'ambiguous',
        })
    args.output.write_text(json.dumps(results, indent=1), encoding='utf-8')
    firm = sum(r['status'] == 'firm' for r in results)
    print(f'{len(results)} Saturn backgrounds, {firm} firm, {len(results) - firm} ambiguous')


if __name__ == '__main__':
    main()
