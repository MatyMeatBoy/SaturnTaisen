"""Render menu words like the English patch did: TrueType text, antialiased,
quantized to the 15-step ink ramp (index 1 = full ink ... 14 = faint, 0 = background).
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

FONTS = r'C:\Windows\Fonts'


def font(name: str, size: int):
    return ImageFont.truetype(f'{FONTS}\\{name}', size)


LEVELS = None  # optional subset of ink indices (e.g. [1, 4, 8, 12]) to keep strips compressible


def render(text: str, face: str, size: int, baseline: int, squeeze: float = 1.0, height: int = 16,
           threshold: int = 24, gamma: float = 1.0):
    """Return (rows, width): palette-index rows of the word, cropped horizontally."""
    f = font(face, size)
    left, top, right, bottom = f.getbbox(text)
    ascent = f.getmetrics()[0]
    w = right - left + 4
    scale = 4  # supersample for better coverage, like a smooth TrueType raster
    big = Image.new('L', (w * scale, height * scale), 0)
    fb = font(face, size * scale)
    ImageDraw.Draw(big).text((-left * scale + 2 * scale, (baseline - ascent) * scale), text, font=fb, fill=255)
    tw = max(1, round(w * squeeze))
    im = big.resize((tw, height), Image.LANCZOS)
    px = im.load()
    rows = [[0] * tw for _ in range(height)]
    for y in range(height):
        for x in range(tw):
            c = px[x, y]
            if c > threshold:
                c = (c / 255) ** gamma
                v = max(1, min(14, round(15 - c * 14)))
                rows[y][x] = min(LEVELS, key=lambda L: abs(L - v)) if LEVELS else v
    cols = [x for x in range(tw) if any(rows[y][x] for y in range(height))]
    if not cols:
        return rows, 0
    a, b = cols[0], cols[-1] + 1
    return [r[a:b] for r in rows], b - a


def fit(text: str, face: str, size: int, baseline: int, width: int, **kw):
    """Largest horizontal squeeze (>= 0.72) so the word fits width pixels."""
    rows, w = render(text, face, size, baseline, **kw)
    squeeze = 1.0
    while w > width and squeeze > 0.72:
        squeeze -= 0.02
        rows, w = render(text, face, size, baseline, squeeze=squeeze, **kw)
    if w > width:
        raise ValueError(f'{text!r} needs {w}px, slot has {width}px')
    return rows, w, squeeze
