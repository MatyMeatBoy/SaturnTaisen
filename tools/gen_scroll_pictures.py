#!/usr/bin/env python3
"""Derive the scroll-picture table (config/hd-scroll-pictures.json and the C++ rows) offline.

Rule (see docs/research/scroll-table.md): the Saturn shows a 288x144 window of a larger NBG picture; the PC art is the same
picture at 2x. The window slides along one axis (the larger one). The PC crop is therefore
  scroll axis: 2 * saturn_offset, length 576 (horizontal) / 288 (vertical)... i.e. 2 * window length
  cross axis : centred, (pc_cross - 2 * window_cross) / 2
Everything below is derived from the Saturn BIN and the PC SPR only; there is no in-game input.
Only hashes, sizes and dimensions are written (no pixels).
"""
import argparse, json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from decode_saturn_bg import Iso, decode, _variant_b_layout, palette_fingerprint  # noqa: E402
from match_hd_all import correlation, signature  # noqa: E402
from PIL import Image  # noqa: E402
from decode_spred import decode as decode_pc  # noqa: E402

WINDOW = (288, 144)
CELL_BYTES = 41472
MIN_CORRELATION = 0.90


def fnv(raw):
    h = 0xcbf29ce484222325
    for b in raw:
        h = ((h ^ b) * 1099511628211) & 0xffffffffffffffff
    return h


def derive(name, discs, pc_root):
    entries = {d: iso.find(f'/SAKURA1/{name}.BIN') for d, iso in discs.items()}
    entries = {d: e for d, e in entries.items() if e}
    if not entries:
        return None, 'not on the prepared discs'
    files = {d: discs[d].content(e) for d, e in entries.items()}
    raw = next(iter(files.values()))
    if len(set(files.values())) != 1:
        return None, 'native bytes differ between discs'
    layout = _variant_b_layout(raw)
    if not layout:
        return None, 'native layout is not the variant-B name table'
    w8, h8, tiles_at, names = layout
    w, h = w8 * 8, h8 * 8
    counts = Counter(x & 0x7fff for x in names)
    counts[0] += 4096 - len(names)
    unique = [k for k, v in counts.items() if v == 1]
    if not unique:
        return None, 'no uniquely named cell'
    cell_at = min(unique) * 32
    tiles = raw[tiles_at:]
    if cell_at + CELL_BYTES > len(tiles):
        return None, 'cell key would read past the picture tile pool'
    pc_file = pc_root / f'{name}.SPR'
    if not pc_file.exists():
        return None, 'PC file missing'
    pc = pc_file.read_bytes()
    parts = dict(decode_pc(pc))
    if 0 not in parts:
        return None, 'PC subimage 0 missing'
    pw, ph = parts[0].size
    if w > WINDOW[0] and h == WINDOW[1]:
        axis = 'x'
    elif h > WINDOW[1] and w == WINDOW[0]:
        axis = 'y'
    else:
        return None, f'native {w}x{h} does not scroll along one axis of the 288x144 window'
    # PC art is 2x along the scroll axis; the cross axis is centred.
    cross_ok = (ph - 2 * WINDOW[1]) % 2 == 0 and ph >= 2 * WINDOW[1] if axis == 'x' else (pw - 2 * WINDOW[0]) % 2 == 0 and pw >= 2 * WINDOW[0]
    scroll_ok = pw == 2 * w if axis == 'x' else ph == 2 * h
    if not (cross_ok and scroll_ok):
        return None, f'PC {pw}x{ph} is not 2x of native {w}x{h}'
    native = decode(raw).convert('RGB')
    art = parts[0].convert('RGB')
    cross = (ph - 2 * WINDOW[1]) // 2 if axis == 'x' else (pw - 2 * WINDOW[0]) // 2
    scores = []
    for at in range(0, (w - WINDOW[0] if axis == 'x' else h - WINDOW[1]) + 1, 8):
        if axis == 'x':
            wanted, got = native.crop((at, 0, at + 288, 144)), art.crop((2 * at, cross, 2 * at + 576, cross + 288))
        else:
            wanted, got = native.crop((0, at, 288, at + 144)), art.crop((cross, 2 * at, cross + 576, 2 * at + 288))
        scores.append(correlation(signature(wanted), signature(got.resize((288, 144), Image.Resampling.BOX))))
    if min(scores) < MIN_CORRELATION:
        return None, f'PC art does not follow the native picture (min crop correlation {min(scores):.3f})'
    return {
        'min_crop_correlation': round(min(scores), 4),
        'name': name, 'axis': axis, 'width': w, 'height': h,
        'native_bytes': len(raw), 'native_fnv': f'{fnv(raw):016X}',
        'palette': f'{palette_fingerprint(raw):016X}', 'cells': f'{fnv(tiles[cell_at:cell_at + CELL_BYTES]):016X}',
        'pc_file': f'SAKURA1/BG/{name}.SPR', 'pc_bytes': len(pc), 'pc_fnv': f'{fnv(pc):016X}',
        'pc_width': pw, 'pc_height': ph,
        'crop_cross': ((ph - 2 * WINDOW[1]) // 2) if axis == 'x' else ((pw - 2 * WINDOW[0]) // 2),
    }, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prepared', default=str(ROOT / 'local/prepared'))
    ap.add_argument('--pc', required=True, help='PC game root holding SAKURA1/BG')
    ap.add_argument('--header', help='write the C++ rows (port/scroll_picture_rows.h)')
    ap.add_argument('--out', default=str(ROOT / 'config/hd-scroll-pictures.json'))
    a = ap.parse_args()
    inventory = json.loads((ROOT / 'config/hd-wide-bg-plan.json').read_text())['entries']
    coverage = json.loads((ROOT / 'config/hd-chapter-coverage.json').read_text())
    groups = [coverage['unassigned'], *(chapter['resources'] for chapter in coverage['chapters'])]
    excluded = {Path(path.split(':', 1)[-1]).stem for group in groups
                for path, row in group['scene-pictures'].items() if row['status'] == 'excluded'}
    # Geometry is an inventory property. Its candidates stay the same when an asset becomes HD.
    still_viewports = {'BG1306', 'BG2238', 'BG2260'}
    names = {Path(row['saturn_file']).stem for row in inventory} - excluded - still_viewports
    discs = {d: Iso(str(Path(a.prepared) / f'disc{d}' / 'Track 01.iso')) for d in (1, 2)}
    pc_root = Path(a.pc) / 'SAKURA1' / 'BG'
    rows, skipped = [], {}
    for n in sorted(x for x in names if x.startswith('BG') and not x.startswith('BBG')):
        row, why = derive(n, discs, pc_root)
        if row:
            rows.append(row)
        else:
            skipped[n] = why
    for n in sorted(x for x in names if x.startswith('BBG')):
        skipped[n] = 'battle background: full 320x224 frame, not a 288x144 scroll window (TP2b)'
    Path(a.out).write_text(json.dumps({'window': list(WINDOW), 'rows': rows, 'skipped': skipped}, indent=1) + '\n', encoding='utf-8', newline='\n')
    if a.header:
        lines = ['// Generated by tools/gen_scroll_pictures.py from config/hd-scroll-pictures.json. Do not edit by hand.',
                 '// name, axis, native w x h, native bytes/fnv, VDP2 palette key, first-cell key (0: palette only), PC file/bytes/fnv, PC w x h, style']
        for r in rows:
            style = {'BG1207': 'ScrollStyle::ActorForeground', 'BG2533': 'ScrollStyle::EdgeRamp'}.get(r['name'], 'ScrollStyle::Plain')
            cells = '0' if r['name'] == 'BG2533' else f"0x{r['cells']}ull"  # BG2533 was pinned by palette alone (patch 0098)
            axis = 'ScrollAxis::Horizontal' if r['axis'] == 'x' else 'ScrollAxis::Vertical'
            lines.append(f"{{\"{r['name']}\", {axis}, {r['width']}, {r['height']}, {r['native_bytes']}, 0x{r['native_fnv']}ull,\n"
                         f" 0x{r['palette']}ull, {cells}, \"{r['pc_file']}\", {r['pc_bytes']}, 0x{r['pc_fnv']}ull, {r['pc_width']}, {r['pc_height']},\n"
                         f" {style}}},")
        Path(a.header).write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    for r in rows:
        print(r['name'], r['axis'], r['width'], r['height'], r['pc_width'], r['pc_height'])
    for k, v in skipped.items():
        print('skip', k, v)


if __name__ == '__main__':
    main()
