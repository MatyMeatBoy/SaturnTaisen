"""Pair Saturn full-screen pictures (IC, OMAKE, LOAD) with PC pictures by content (T96).

These names do not follow the BG rule (IC01.BIN is IC0100.SPR), so each Saturn picture is compared with every
large PC picture of ICATCH, TITLE, ENDING, SYSTEM, WALL and CG (normalised correlation of 32x16 grey
signatures, tools/match_hd_all.py). Tiers: `content` when the best correlation is >= 0.95 and the runner-up is
at least 0.10 lower; otherwise `candidate` (an eye check is needed). Data only: names, hashes, scores.

  python tools/match_hd_screens.py --pc ROOT --iso "local/prepared/disc1/Track 01.iso" --out config/hd-screen-map.json
"""
import argparse
import glob
import hashlib
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402
import decode_spred  # noqa: E402
import match_hd_all as match  # noqa: E402

FOLDERS = ('SAKURA1/ICATCH', 'SAKURA1/TITLE', 'SAKURA1/ENDING', 'SAKURA1/SYSTEM', 'SAKURA3/CG', 'SAKURA1/WALL')
PREFIXES = ('IC', 'OMAKE', 'LOAD')


def pc_signatures(path):
    raw = Path(path).read_bytes()
    try:
        pictures = decode_spred.decode(raw)
    except Exception:
        return []
    return [{'sig': match.signature(p.convert('RGB')), 'index': i, 'size': list(p.size),
             'sha256': hashlib.sha256(raw).hexdigest(), 'path': str(path)}
            for i, p in pictures if p.width >= 300 and p.height >= 200]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pc', type=Path, required=True)
    parser.add_argument('--iso', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--folder', default='SAKURA1')
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    paths = [p for sub in FOLDERS for p in sorted(glob.glob(str(args.pc / sub / '*.SPR')))]
    with ProcessPoolExecutor(args.workers) as pool:
        pcs = [x for part in pool.map(pc_signatures, paths, chunksize=4) for x in part]
    iso = saturn.Iso(args.iso)
    pairs = []
    for name, extent in iso.files(args.folder):
        prefix = re.match(r'[A-Z_]+', name)
        if not (prefix and prefix.group(0) in PREFIXES and name.endswith('.BIN')):
            continue
        data = iso.content(extent)
        image = saturn.decode(data)
        if image is None:
            continue
        sig = match.signature(image)
        ranked = sorted(((match.correlation(sig, p['sig']), p) for p in pcs), key=lambda t: -t[0])
        best, second = ranked[0], ranked[1]
        rel = Path(best[1]['path']).resolve().relative_to(args.pc.resolve()).as_posix()
        other = Path(second[1]['path']).resolve().relative_to(args.pc.resolve()).as_posix()
        firm = best[0] >= 0.95 and best[0] - second[0] >= 0.10
        pairs.append({'saturn_file': f'{args.folder}/{name}', 'size': list(image.size),
                      'cells_sha256': hashlib.sha256(saturn.picture_bytes(data)).hexdigest(),
                      'palette_fnv': '%016X' % saturn.palette_fingerprint(data),
                      'pc_file': rel, 'pc_image_index': best[1]['index'], 'pc_sha256': best[1]['sha256'],
                      'pc_size': best[1]['size'], 'correlation': round(best[0], 3),
                      'runner_up': other, 'runner_up_correlation': round(second[0], 3),
                      'tier': 'content' if firm else 'candidate'})
    summary = {t: sum(p['tier'] == t for p in pairs) for t in ('content', 'candidate')}
    args.out.write_text(json.dumps({'schema': 1, 'scope': 'Saturn IC/OMAKE/LOAD pictures to PC pictures by content; data only.',
                                    'summary': summary, 'pairs': pairs}, indent=1) + '\n', encoding='utf-8')
    print(len(pairs), summary)


if __name__ == '__main__':
    main()
