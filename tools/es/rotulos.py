"""Replace text painted into indexed menu graphics (8 or 4 bpp, linear).

Spanish text is rendered with antialiasing and mapped to the nearest colour among
the palette entries already used in the edited area, so the result keeps the
original look (ink, shading, optional outline) and introduces no new colours.
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from decodificar import palette  # noqa: E402

FONTS = r'C:\Windows\Fonts'


def read_indices(data, off, w, h, bpp):
    if bpp == 8:
        return [list(data[off + y * w: off + y * w + w]) for y in range(h)]
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            b = data[off + (y * w + x) // 2]
            row.append(b >> 4 if x % 2 == 0 else b & 15)
        rows.append(row)
    return rows


def write_indices(data, off, rows, bpp):
    h, w = len(rows), len(rows[0])
    for y in range(h):
        for x in range(w):
            if bpp == 8:
                data[off + y * w + x] = rows[y][x]
            elif x % 2 == 0:
                data[off + (y * w + x) // 2] = (rows[y][x] << 4) | rows[y][x + 1]


def text_mask(text, face, size, box_w, box_h, squeeze=1.0, bold_px=0):
    """Coverage mask (0..255) of text centred in box, squeezed until it fits box_w."""
    f = ImageFont.truetype(os.path.join(FONTS, face), size * 4)
    while True:
        l, t, r, b = f.getbbox(text)
        tw, th = r - l, b - t
        big = Image.new('L', (tw + 8, th + 8), 0)
        ImageDraw.Draw(big).text((4 - l, 4 - t), text, font=f, fill=255)
        if bold_px:
            big = big.filter(ImageFilter.MaxFilter(bold_px * 4 + 1))
        w = max(1, round(big.width / 4 * squeeze))
        h = max(1, round(big.height / 4))
        small = big.resize((w, h), Image.LANCZOS)
        bbox = small.getbbox() or (0, 0, 1, 1)
        small = small.crop(bbox)
        if small.width <= box_w or squeeze < 0.55:
            break
        squeeze -= 0.03
    if small.width > box_w or small.height > box_h:
        raise SystemExit(f'{text!r}: {small.size} no cabe en {box_w}x{box_h}')
    mask = Image.new('L', (box_w, box_h), 0)
    mask.paste(small, ((box_w - small.width) // 2, (box_h - small.height) // 2))
    return mask, squeeze


def nearest(pal, rgb, allowed):
    return min(allowed, key=lambda i: sum((pal[i][k] - rgb[k]) ** 2 for k in range(3)))


def replace_text(rows, pal, box, text, face, size, ink, bg, outline=None, allowed=None, squeeze=1.0, bold_px=0,
                 keep=None):
    """box=(x,y,w,h). ink/bg/outline are palette indices. Clears box to bg first (keep: indices left untouched)."""
    x0, y0, bw, bh = box
    if allowed is None:
        allowed = sorted({rows[y][x] for y in range(y0, y0 + bh) for x in range(x0, x0 + bw)})
    for y in range(y0, y0 + bh):
        for x in range(x0, x0 + bw):
            if keep is None or rows[y][x] not in keep:
                rows[y][x] = bg
    mask, sq = text_mask(text, face, size, bw - (2 if outline is not None else 0), bh - (2 if outline is not None else 0),
                         squeeze, bold_px)
    if outline is not None:
        full = Image.new('L', (bw, bh), 0)
        full.paste(mask, (1, 1))
        mask = full
        ring = mask.point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(3))
    px = mask.load()
    bgc, inkc = pal[bg], pal[ink]
    for y in range(bh):
        for x in range(bw):
            c = px[x, y] / 255
            if outline is not None and ring.getpixel((x, y)) and c < 0.5:
                rows[y0 + y][x0 + x] = outline
                continue
            if c < 0.12:
                continue
            base = pal[outline] if outline is not None else bgc
            rgb = tuple(round(base[k] * (1 - c) + inkc[k] * c) for k in range(3))
            rows[y0 + y][x0 + x] = nearest(pal, rgb, allowed)
    return sq


def to_image(rows, pal, scale=3):
    h, w = len(rows), len(rows[0])
    im = Image.new('RGB', (w, h))
    im.putdata([tuple(pal[v]) for r in rows for v in r])
    return im.resize((w * scale, h * scale), Image.NEAREST)


def load_palette(spec, bpp):
    return [tuple(c) for c in palette(spec, 1 << bpp)]
