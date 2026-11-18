"""Menu text strips: sequences of 16x16 4 bpp tiles holding rendered words.

A strip is n tiles in file order; as an image it is (16*n) x 16 palette indices.
Words are located by background gaps; a Spanish word must stay inside the pixel
range of the English word it replaces so the game's placement code is untouched.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from red_lz import compress, decompress  # noqa: E402
from decodificar import Disc  # noqa: E402

T = 16


def strip_from(data: bytes, offset: int, n: int):
    """Return rows: list of 16 lists of palette indices, width 16*n."""
    rows = [[0] * (T * n) for _ in range(T)]
    for t in range(n):
        base = offset + t * 128
        for y in range(T):
            for x in range(T):
                b = data[base + y * 8 + x // 2]
                rows[y][t * T + x] = (b >> 4) if x % 2 == 0 else (b & 15)
    return rows


def strip_into(data: bytearray, offset: int, rows):
    n = len(rows[0]) // T
    for t in range(n):
        base = offset + t * 128
        for y in range(T):
            for x in range(0, T, 2):
                data[base + y * 8 + x // 2] = (rows[y][t * T + x] << 4) | rows[y][t * T + x + 1]


def words(rows, background: int, min_gap: int = 4):
    """Pixel column ranges [x0, x1) holding ink, split by gaps >= min_gap."""
    width = len(rows[0])
    ink = [any(rows[y][x] != background for y in range(T)) for x in range(width)]
    spans, x = [], 0
    while x < width:
        if not ink[x]:
            x += 1
            continue
        start = x
        gap = 0
        while x < width and gap < min_gap:
            gap = 0 if ink[x] else gap + 1
            x += 1
        spans.append((start, x - gap))
    return spans


def stream(disc: Disc, name: str, offset: int):
    raw = disc.read(name)
    return raw, decompress(raw[offset:])
