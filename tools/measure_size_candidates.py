#!/usr/bin/env python3
"""Offline measurement of crop candidates for the `unsupported-size` scroll/battle pictures (TP2a-size).

For each picture the native image (decode_saturn_bg) is compared with the PC subimage 0 under every crop box of the
"free" row style: any scale (separate x/y), any position. The best per-window score is a ceiling: if its minimum over
the windows is below the 0.90 floor of tools/gen_scroll_pictures.py, no row style (affine or otherwise) can pass.
Only numbers are printed/written. Needs the prepared discs and the extracted PC BG folder (never committed).
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from decode_saturn_bg import Iso, decode  # noqa: E402
from decode_spred import decode as decode_pc  # noqa: E402
from match_hd_all import correlation, signature  # noqa: E402

FLOOR = 0.90
WIN = (288, 144)


def grey(img):
    return np.asarray(img.convert('L'), dtype=np.float32)


def ncc_search(tpl, big):
    """Best zero-mean NCC of `tpl` inside `big` (all integer positions). Returns (score, x, y)."""
    th, tw = tpl.shape
    bh, bw = big.shape
    if bh < th or bw < tw:
        return -1.0, 0, 0
    t = tpl - tpl.mean()
    tn = np.sqrt((t * t).sum()) or 1.0
    from numpy.lib.stride_tricks import sliding_window_view
    v = sliding_window_view(big, (th, tw))
    best = (-1.0, 0, 0)
    for y in range(v.shape[0]):
        row = v[y].reshape(v.shape[1], -1)
        m = row - row.mean(axis=1, keepdims=True)
        n = np.sqrt((m * m).sum(axis=1)); n[n == 0] = 1.0
        s = (m @ t.ravel()) / (n * tn)
        x = int(s.argmax())
        if s[x] > best[0]:
            best = (float(s[x]), x, y)
    return best


def best_box(native_win, pc, scales_x, scales_y, work=0.5):
    """Search PC boxes for one native window. Returns (sig correlation, box)."""
    tpl = grey(native_win.resize((int(native_win.width * work), int(native_win.height * work)), Image.BOX))
    best = (-1.0, None)
    for sy in scales_y:
        for sx in scales_x:
            w = max(8, round(pc.width / sx * work)); h = max(8, round(pc.height / sy * work))
            big = grey(pc.resize((w, h), Image.BOX))
            s, x, y = ncc_search(tpl, big)
            if s > best[0]:
                best = (s, (x, y, sx, sy))
    s, (x, y, sx, sy) = best
    x0 = x / work * sx; y0 = y / work * sy
    box = (round(x0), round(y0), round(x0 + native_win.width * sx), round(y0 + native_win.height * sy))
    box = (max(0, box[0]), max(0, box[1]), min(pc.width, box[2]), min(pc.height, box[3]))
    got = pc.crop(box).resize(native_win.size, Image.Resampling.BOX)
    return correlation(signature(native_win), signature(got)), box


def refine_box(native, pc, sx, sy, span_x=0.25, span_y=0.3):
    """Coarse-to-fine search of the free box (scale in both axes and position) for a whole picture."""
    best = (-1.0, None)
    for work, steps, shrink in ((0.25, 9, 1.0), (0.5, 7, 0.3), (1.0, 5, 0.12)):
        sxs = [sx + span_x * shrink * (i / (steps - 1) * 2 - 1) for i in range(steps)]
        sys_ = [sy + span_y * shrink * (i / (steps - 1) * 2 - 1) for i in range(steps)]
        best = best_box(native, pc, sxs, sys_, work=work)
        box = best[1]
        sx, sy = (box[2] - box[0]) / native.width, (box[3] - box[1]) / native.height
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prepared', default=str(ROOT / 'local/prepared'))
    ap.add_argument('--pc', required=True, help='root holding SAKURA1/BG and SAKURA2/BG')
    ap.add_argument('--out')
    ap.add_argument('--stride', type=int, default=24)
    a = ap.parse_args()
    discs = {1: Iso(str(Path(a.prepared) / 'disc1' / 'Track 01.iso')), 2: Iso(str(Path(a.prepared) / 'disc2' / 'Track 01.iso'))}
    plan = json.loads((ROOT / 'config/hd-wide-bg-plan.json').read_text())['entries']
    todo = [r for r in plan if Path(r['saturn_file']).stem in
            {'BG1257', 'BG1280', 'BG2093', 'BG2247', 'BG2290', 'BG2338', 'BBG238', 'BBG239', 'BBG240', 'BBG241', 'BBG242', 'BBG243', 'BBG300'}]
    result = {}
    for r in todo:
        name = Path(r['saturn_file']).stem
        disc = 2 if r['saturn_file'].startswith('SAKURA2') else 1
        e = discs[disc].find('/' + r['saturn_file'])
        raw = discs[disc].content(e)
        native = decode(raw)
        pcp = Path(a.pc) / r['pc_file']
        pc = dict(decode_pc(pcp.read_bytes()))[0].convert('RGB')
        nw, nh = native.size
        if r['class'] == 'full_screen' or (nw, nh) == (320, 160):
            wins = [(0, 0, nw, nh)]
            sxs = [pc.width / nw * k for k in (0.9, 0.94, 0.97, 1.0, 1.03, 1.06, 1.1)]
            sys_ = [pc.height / nh * k for k in (0.85, 0.9, 0.95, 1.0, 1.05, 1.1)]
            if r['class'] == 'full_screen':
                sys_ += [pc.width / nw * k for k in (0.94, 0.97, 1.0, 1.03, 1.06)]  # near-uniform scale with vertical crop
        elif nw > WIN[0]:
            wins = [(o, 0, o + WIN[0], WIN[1]) for o in range(0, nw - WIN[0] + 1, a.stride)] + [(nw - WIN[0], 0, nw, WIN[1])]
        else:
            wins = [(0, o, WIN[0], o + WIN[1]) for o in range(0, nh - WIN[1] + 1, a.stride)] + [(0, nh - WIN[1], WIN[0], nh)]
        if r['class'] != 'full_screen' and (nw, nh) != (320, 160):
            base = pc.width / nw if nw > WIN[0] else pc.height / nh
            sxs = sorted({round(base * k, 3) for k in (0.8, 0.9, 1.0, 1.1, 1.2)})
            sys_ = sorted({round(pc.height / nh * k, 3) for k in (0.85, 0.9, 0.95, 1.0)}) if nw > WIN[0] else sxs
            if nw <= WIN[0]:
                sxs = sorted({round(pc.width / nw * k, 3) for k in (0.9, 0.95, 1.0, 1.05)})
        scores = []
        for w in wins:
            win = native.crop(w).convert('RGB')
            sc, box = best_box(win, pc, sxs, sys_)
            if r['class'] == 'full_screen':
                sc, box = refine_box(win, pc, 2.0, 2.1)
            scores.append((round(sc, 4), w[0] if nw > WIN[0] else w[1], box))
        vals = [s for s, _, _ in scores]
        result[name] = {'native': [nw, nh], 'pc': [pc.width, pc.height], 'pc_file': r['pc_file'], 'windows': len(vals),
                        'min': min(vals), 'mean': round(sum(vals) / len(vals), 4), 'max': max(vals),
                        'passes_floor': min(vals) >= FLOOR,
                        'offsets_below_floor': [o for sc, o, _ in scores if sc < FLOOR] if len(scores) > 1 else [],
                        'best_boxes': [list(b) for sc, o, b in scores][:1] if len(scores) == 1 else []}
        print(name, result[name], flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
