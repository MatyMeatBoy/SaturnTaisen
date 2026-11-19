"""Mass pairing of Saturn `BG*.BIN`/`BBG*.BIN` backgrounds with PC `.SPR` pictures, all discs and layouts (T76-T711).

One command replaces the screenshot-by-screenshot work: every Saturn picture the decoder understands
(`tools/decode_saturn_bg.py`, three layouts) is paired with the PC picture of the same file number and the
pair is checked against ALL PC pictures, in parallel. Output is data only (names, hashes, scores).

  python tools/match_hd_all.py --pc ROOT_OF_EXTRACTED_PC --out config/hd-scene-bg-map.json \\
      --disc "local/prepared/disc1/Track 01.iso:SAKURA1" --disc "local/prepared/disc2/Track 01.iso:SAKURA2"

The PC picture is the whole scene (576x320), not a crop of it: it is stretched onto the Saturn picture
rectangle (288x144 or the picture's own size). Colours differ between the two renderings, so the score is
the normalised correlation of 32x16 grey signatures (brightness and contrast independent). Tiers:
  content   the same-number PC picture is the best of all PC pictures and correlates >= 0.80
  number    same number only (a lighting/palette variant, or another crop): needs an eye check
  missing   no PC picture with that number
`rank` is the position of the same-number PC picture among all PC pictures (1 = best) and `best_other` the
strongest different picture, so a reviewer can see how decisive the match is.
"""
import argparse
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402
import decode_spred  # noqa: E402

SIG = (32, 16)


def signature(image):
    grey = image.convert('L').resize(SIG, Image.BILINEAR)
    values = list(grey.getdata())
    mean = sum(values) / len(values)
    centred = [v - mean for v in values]
    norm = sum(v * v for v in centred) ** 0.5 or 1.0
    return [v / norm for v in centred]


def correlation(a, b):
    return sum(x * y for x, y in zip(a, b))


def pc_signature(path, image_index=None):
    raw = Path(path).read_bytes()
    try:
        pictures = decode_spred.decode(raw)
    except Exception:
        return None
    if not pictures:
        return None
    if image_index is None:
        index, picture = max(pictures, key=lambda p: p[1].width * p[1].height)
    else:
        selected = next((item for item in pictures if item[0] == image_index), None)
        if selected is None:
            return None
        index, picture = selected
    return {'name': Path(path).name, 'rel': None, 'index': index, 'size': list(picture.size),
            'sha256': hashlib.sha256(raw).hexdigest(), 'sig': signature(picture.convert('RGB'))}


# The standard PC search uses the same file number. BG2338's artwork is
# a subimage of BG2238.SPR, as reviewed in docs/research/saturn-bg-format.md.
REVIEWED_ALTERNATE_STILLS = {'SAKURA1/BG2338.BIN': ('SAKURA1/BG/BG2238.SPR', 17)}


def reviewed_alternate(sat, pc_root):
    candidate = REVIEWED_ALTERNATE_STILLS.get(sat['saturn_file'])
    if candidate is None:
        return None
    relative, image_index = candidate
    path = pc_root / relative
    if not path.is_file():
        return None
    image = pc_signature(path, image_index)
    if image is None:
        return None
    score = correlation(sat['sig'], image['sig'])
    if score < 0.92:
        return None
    return {'pc_file': relative, 'pc_image_index': image_index, 'pc_sha256': image['sha256'],
            'pc_size': image['size'], 'correlation': round(score, 3), 'tier': 'content',
            'pair_method': 'visual-cross-number'}


def saturn_signature(task):
    iso_path, folder, name, extent = task
    data = saturn.Iso(iso_path).content(extent)
    image = saturn.decode(data)
    if image is None:
        return {'saturn_file': f'{folder}/{name}', 'decoded': False}
    return {'saturn_file': f'{folder}/{name}', 'decoded': True, 'size': list(image.size), 'folder': folder,
            'cells_sha256': hashlib.sha256(saturn.picture_bytes(data)).hexdigest(),
            'palette_fnv': '%016X' % saturn.palette_fingerprint(data), 'sig': signature(image)}


def pc_files(root, folder):
    for directory in (root / folder / 'BG', root / folder):
        if directory.is_dir():
            yield from sorted(directory.glob('*.SPR'))
            return


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pc', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--disc', action='append', required=True, help='ISO:FOLDER, repeatable')
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    tasks, folders = [], []
    for spec in args.disc:
        iso_path, _, folder = spec.rpartition(':')
        folders.append(folder)
        for name, extent in saturn.Iso(iso_path).files(folder):
            if name.startswith(('BG', 'BBG')) and name.endswith('.BIN'):
                tasks.append((iso_path, folder, name, extent))
    paths = [p for folder in folders for p in pc_files(args.pc, folder)]
    with ProcessPoolExecutor(args.workers) as pool:
        pcs = [x for x in pool.map(pc_signature, paths, chunksize=8)]
        sats = list(pool.map(saturn_signature, tasks, chunksize=8))
    index = {}
    for path, item in zip(paths, pcs):
        if item:
            item['rel'] = path.relative_to(args.pc).as_posix()
            index.setdefault((path.parent.parent.name if path.parent.name == 'BG' else path.parent.name, path.name), item)
    everything = list(index.values())
    pairs = []
    for sat in sats:
        if not sat['decoded']:
            pairs.append(sat)
            continue
        name = sat['saturn_file'].split('/')[-1][:-4] + '.SPR'
        own = index.get((sat['folder'], name))
        entry = {k: sat[k] for k in ('saturn_file', 'decoded', 'size', 'cells_sha256', 'palette_fnv')}
        alternate = reviewed_alternate(sat, args.pc)
        if alternate is not None:
            entry.update(alternate)
            pairs.append(entry)
            continue
        if own is None:
            entry['tier'] = 'missing'
            pairs.append(entry)
            continue
        scores = sorted(((correlation(sat['sig'], other['sig']), other['rel']) for other in everything), reverse=True)
        value = correlation(sat['sig'], own['sig'])
        rank = 1 + sum(1 for s, _ in scores if s > value)
        other = next(s for s in scores if s[1] != own['rel'])
        entry.update({'pc_file': own['rel'], 'pc_image_index': own['index'], 'pc_sha256': own['sha256'],
                      'pc_size': own['size'], 'correlation': round(value, 3), 'rank': rank,
                      'best_other': other[1], 'best_other_correlation': round(other[0], 3),
                      'tier': 'content' if rank == 1 and value >= 0.80 else 'number'})
        pairs.append(entry)
    decoded = [p for p in pairs if p['decoded']]
    summary = {t: sum(p.get('tier') == t for p in decoded) for t in ('content', 'number', 'missing')}
    keys = [p['cells_sha256'] for p in decoded]
    out = {'schema': 2,
           'scope': 'Saturn BG*.BIN/BBG*.BIN to PC .SPR by shared file number, checked against every PC picture '
                    '(normalised correlation of 32x16 grey signatures) with reviewed cross-number exceptions; data only. cells_sha256 identifies the native '
                    'picture; tier `number` needs an eye check before drawing.',
           'summary': summary, 'duplicate_cell_hashes': len(keys) - len(set(keys)),
           'undecoded': [p['saturn_file'] for p in pairs if not p['decoded']],
           'pairs': decoded}
    args.out.write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    print(len(decoded), 'decoded', summary, 'undecoded', len(out['undecoded']), 'duplicate keys', out['duplicate_cell_hashes'])


if __name__ == '__main__':
    main()
