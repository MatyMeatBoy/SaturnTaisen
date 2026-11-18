"""Reuse the English patch's own painted letters to compose Spanish labels.

segment(): split a label region into glyphs at background columns.
compose(): place glyph pixel blocks (with their original spacing rules) centred in a box.
Only the pixels that differ from the background are copied, so outlines/shading survive.
"""
from __future__ import annotations


def segment(rows, box, is_bg, min_gap=1):
    """Return list of (x0, x1) column runs with ink inside box=(x,y,w,h)."""
    x, y, w, h = box
    ink = [any(not is_bg(rows[yy][xx]) for yy in range(y, y + h)) for xx in range(x, x + w)]
    runs, i = [], 0
    while i < w:
        if not ink[i]:
            i += 1
            continue
        s = i
        while i < w and ink[i]:
            i += 1
        runs.append((x + s, x + i))
    return runs


def cut(rows, box, x0, x1, is_bg):
    _, y, _, h = box
    return [[None if is_bg(rows[yy][xx]) else rows[yy][xx] for xx in range(x0, x1)] for yy in range(y, y + h)]


def mirror(glyph):
    return [list(reversed(r)) for r in glyph]


def compose(rows, box, glyphs, spacing, bg_fill, keep=lambda v: False, align='center'):
    """Clear box (except keep(v)) to bg_fill and draw glyphs separated by spacing (int or list)."""
    x, y, w, h = box
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if not keep(rows[yy][xx]):
                rows[yy][xx] = bg_fill
    gaps = spacing if isinstance(spacing, list) else [spacing] * len(glyphs)
    total = sum(len(g[0]) for g in glyphs) + sum(gaps[:len(glyphs) - 1])
    if total > w:
        raise SystemExit(f'composición de {total}px no cabe en {w}px')
    cx = x + (w - total) // 2 if align == 'center' else x
    for i, g in enumerate(glyphs):
        for yy, r in enumerate(g):
            for xx, v in enumerate(r):
                if v is not None:
                    rows[y + yy][cx + xx] = v
        cx += len(g[0]) + (gaps[i] if i < len(glyphs) - 1 else 0)
    return total
