"""Classify the non-standard Saturn backgrounds of config/hd-scene-bg-map.json for the scrolling work (T105).

Reads only the committed pair map (no game data). For every pair whose Saturn picture is not the common
288x144 it records the Saturn and PC sizes, the PC/Saturn scale on each axis and a class:
  wide_scroll  Saturn wider than the 288-pixel window (variant B scrolling scenes)
  tall_scroll  Saturn taller than 144 pixels at width 288 (vertical scroll)
  full_screen  320x224 pictures
  other
`scale_match` is true when both axes scale by the same factor within 2 %: only those can be drawn by a plain
stretch; the rest need a per-file crop/offset decision (eye review). Writes config/hd-wide-bg-plan.json.
Usage: python tools/plan_wide_bg.py [--map FILE] [--out FILE] [--check]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINDOW = (288, 144)


def classify(size):
    w, h = size
    if (w, h) == (320, 224):
        return 'full_screen'
    if w > WINDOW[0]:
        return 'wide_scroll'
    if w == WINDOW[0] and h > WINDOW[1]:
        return 'tall_scroll'
    return 'other'


def plan(pair_map):
    entries = []
    for p in pair_map['pairs']:
        if not p.get('decoded') or list(p['size']) == list(WINDOW):
            continue
        entry = {'saturn_file': p['saturn_file'], 'size': p['size'], 'class': classify(p['size']),
                 'tier': p['tier'], 'pc_file': p.get('pc_file'), 'pc_size': p.get('pc_size'),
                 'cells_sha256': p['cells_sha256']}
        if p.get('pc_size'):
            sx, sy = p['pc_size'][0] / p['size'][0], p['pc_size'][1] / p['size'][1]
            entry['scale'] = [round(sx, 3), round(sy, 3)]
            entry['scale_match'] = abs(sx - sy) / sy <= 0.02
        entries.append(entry)
    counts = {}
    for e in entries:
        key = '%s/%s' % (e['class'], 'scale_match' if e.get('scale_match') else 'needs_review')
        counts[key] = counts.get(key, 0) + 1
    return {'schema': 1, 'scope': 'non-288x144 decoded Saturn backgrounds (T105)', 'counts': counts,
            'entries': sorted(entries, key=lambda e: e['saturn_file'])}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--map', type=Path, default=ROOT / 'config' / 'hd-scene-bg-map.json')
    ap.add_argument('--out', type=Path, default=ROOT / 'config' / 'hd-wide-bg-plan.json')
    ap.add_argument('--check', action='store_true', help='fail when --out is not what the map yields')
    args = ap.parse_args()
    result = json.dumps(plan(json.loads(args.map.read_text('utf-8'))), indent=1) + '\n'
    if args.check:
        return 0 if args.out.read_text('utf-8') == result else 1
    args.out.write_text(result, 'utf-8')
    print(args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
