"""Find the frame sizes of the eye and mouth strips that follow an NC body (T19).

After the body bitmap of an NC*.BIN come runs of equally sized frames (eyes, then mouths for most files), and
the PC NC*.SPR holds the matching parts in the same order, also in runs of equal size. The Saturn frame sizes are
not in the file, but for two runs the byte count gives an exact condition: n1*E + n2*M = bytes after the body, with
E = w1*h1 and M = w2*h2 (widths in multiples of 8, the VDP1 rule). Each candidate is scored by how well its first
frame of every run correlates with the first PC part of the same run (both on mid-grey, 24x24 grey signature).

  python tools/solve_nc_strips.py --pc ROOT --iso "local/prepared/disc1/Track 01.iso" --out config/hd-body-strips.json

Only files whose best solution is clear (score >= 0.55 on both runs and a margin over the next solution) are
written; the rest are listed as unsolved. Data only: sizes, offsets and scores.
"""
import argparse
import json
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402
import decode_spred  # noqa: E402

SIG = (24, 24)
ROOT = Path(__file__).resolve().parents[1]


def signature(image):
    rgba = image.convert('RGBA')
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if a and r < 24 and g > 232 and b < 24:
                pixels[x, y] = (0, 0, 0, 0)
    grey = Image.new('RGB', rgba.size, (128, 128, 128))
    grey.paste(rgba, mask=rgba.split()[3])
    values = list(grey.convert('L').resize(SIG, Image.BILINEAR).getdata())
    mean = sum(values) / len(values)
    centred = [v - mean for v in values]
    norm = sum(v * v for v in centred) ** 0.5 or 1.0
    return [v / norm for v in centred]


def frame_image(data, palette, offset, width, height):
    image = Image.new('RGBA', (width, height))
    pixels = image.load()
    for i in range(width * height):
        index = data[offset + i]
        pixels[i % width, i // width] = (0, 0, 0, 0) if index == 0 else palette[index] + (255,)
    return image


def runs(parts):
    out = []
    for index, size in parts:
        if out and out[-1]['size'] == size:
            out[-1]['indices'].append(index)
        else:
            out.append({'size': size, 'indices': [index]})
    return out


def divisors(total):
    for w in range(8, 257, 8):
        if total % w == 0 and 4 <= total // w <= 128:
            yield w, total // w


def roughness(data, offset, nbytes, width):
    """Mean difference between a pixel and the one a row below, over pairs where either pixel is not transparent.
    The true width of a raster makes this small (a wrong one shears the picture)."""
    total = count = 0
    end = min(offset + nbytes, len(data))
    for i in range(offset, end - width, 2):
        a, b = data[i], data[i + width]
        if a or b:
            total += abs(a - b)
            count += 1
    return total / count if count > 40 else 999.0


def best_width(data, offset, nbytes, total_frame_bytes):
    """The (width, height) of one frame whose area is total_frame_bytes and whose raster is smoothest."""
    best = None
    for w, h in divisors(total_frame_bytes):
        score = roughness(data, offset, nbytes, w)
        if best is None or score < best[0]:
            best = (score, w, h)
    return best


def solve(data, stride, pc_images):
    palette = [(((w & 31) * 255 // 31), ((w >> 5) & 31) * 255 // 31, ((w >> 10) & 31) * 255 // 31)
               for w in struct.unpack_from('>256H', data, 0x410)]
    start = 0x610 + stride * 144
    rest = len(data) - start
    body = max(pc_images, key=lambda t: t[1].width * t[1].height)[0]
    parts = [(i, im.size, im) for i, im in pc_images if i != body and im.size != (16, 16)]
    groups = runs([(i, sz) for i, sz, _ in parts])
    if not groups or len(groups) > 2:
        return None, '%d runs (only 1 or 2 are solved)' % len(groups)
    by_index = {i: im for i, _, im in parts}
    counts = [len(g['indices']) for g in groups]
    ref = [signature(by_index[g['indices'][0]]) for g in groups]
    options = []
    if len(groups) == 1:
        if rest % counts[0]:
            return None, 'no integer solution'
        options = [((rest // counts[0]),)]
    else:
        n1, n2 = counts
        for e_bytes in range(64, rest // n1, 8):
            remainder = rest - n1 * e_bytes
            if remainder > 0 and remainder % n2 == 0:
                options.append((e_bytes, remainder // n2))
    scored = []
    for sizes in options:
        offset, total, choice = start, 0.0, []
        for r, frame_bytes in enumerate(sizes):
            rough = best_width(data, offset, counts[r] * frame_bytes, frame_bytes)
            if rough is None:
                total = 999.0
                break
            total += rough[0]
            choice.append((rough[1], rough[2]))
            offset += counts[r] * frame_bytes
        if total < 999.0:
            scored.append((total / len(sizes), tuple(choice)))
    if not scored:
        return None, 'no integer solution'
    scored.sort()
    best = scored[0]
    # Options that only change the heights give almost the same raster; a real rival has other widths.
    widths = tuple(w for w, _ in best[1])
    rivals = [sc for sc, ch in scored[1:] if tuple(w for w, _ in ch) != widths]
    margin = (rivals[0] - best[0]) if rivals else 99.0
    offset, check, runs_out = start, [], []
    for r, (w, h) in enumerate(best[1]):
        check.append(sum(x * y for x, y in zip(signature(frame_image(data, palette, offset, w, h)), ref[r])))
        runs_out.append({'width': w, 'height': h, 'count': counts[r], 'offset': offset,
                         'pc_indices': groups[r]['indices'], 'pc_size': list(groups[r]['size'])})
        offset += counts[r] * w * h
    if best[0] > 40 or margin < 2.5:
        return None, 'unclear (roughness %.1f, margin %.1f)' % (best[0], margin)
    return {'body_end': start, 'runs': runs_out, 'roughness': round(best[0], 2), 'margin': round(margin, 2),
            'correlation': round(min(check), 3)}, None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pc', type=Path, required=True)
    parser.add_argument('--iso', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--only', help='comma separated NC names, for a quick check')
    args = parser.parse_args()
    review = json.loads((ROOT / 'config/hd-body-review.json').read_text(encoding='utf-8'))
    body_map = json.loads((ROOT / 'config/hd-body-map.json').read_text(encoding='utf-8'))
    confirmed, rejected = set(review['eye_confirmed_candidates']), set(review['rejected'])
    names = [p['saturn_file'].split('/')[-1][:-4] for p in body_map['pairs']
             if (p['tier'] == 'content' or p['saturn_file'].split('/')[-1][:-4] in confirmed)
             and p['saturn_file'].split('/')[-1][:-4] not in rejected]
    if args.only:
        names = [n for n in names if n in args.only.split(',')]
    iso = saturn.Iso(args.iso)
    files = dict(iso.files('SAKURA1'))
    solved, unsolved = {}, {}
    for name in names:
        data = iso.content(files[name + '.BIN'])
        stride = saturn.nc_stride(data)
        try:
            images = decode_spred.decode((args.pc / 'SAKURA1/NC' / (name + '.SPR')).read_bytes())
        except Exception as error:
            unsolved[name] = 'PC file unreadable: %s' % error
            continue
        result, why = solve(data, stride, images)
        if result:
            result['stride'] = stride
            solved[name] = result
        else:
            unsolved[name] = why
    args.out.write_text(json.dumps({'schema': 1, 'scope': 'Saturn NC face strip sizes solved from the byte count and '
                                    'the PC parts; data only.', 'solved': solved, 'unsolved': unsolved}, indent=1) + '\n',
                        encoding='utf-8')
    print(len(solved), 'solved,', len(unsolved), 'unsolved')


if __name__ == '__main__':
    main()
