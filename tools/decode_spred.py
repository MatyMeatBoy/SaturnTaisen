"""Read-only decoder for PC SPRED (.SPR) images, ported from patch 0013 (port/pc_sprites.h).

Usage: python tools/decode_spred.py FILE.SPR OUTDIR   (writes one PNG per image, local use only)
Never commit decoded output: the images are the owner's PC assets.
"""
import struct
import sys
from pathlib import Path
from PIL import Image

BITS = (4, 4, 8, 8, 8, 16, 24, 32)


def _lz(comp, need):
    ring = bytearray(4096); write = 0xFEE; flags = left = cursor = 0; raw = bytearray()
    while len(raw) < need:
        if not left:
            flags = comp[cursor]; cursor += 1; left = 8
        literal = flags & 1; flags >>= 1; left -= 1
        if literal:
            v = comp[cursor]; cursor += 1
            raw.append(v); ring[write] = v; write = (write + 1) & 4095
        else:
            a, b = comp[cursor], comp[cursor + 1]; cursor += 2
            read = a | ((b >> 4) << 8); length = (b & 15) + 3
            if length > need - len(raw):
                raise ValueError('SPRED match exceeds output')
            for _ in range(length):
                v = ring[read]; read = (read + 1) & 4095
                raw.append(v); ring[write] = v; write = (write + 1) & 4095
    return bytes(raw)


def decode(data):
    if len(data) < 32 or data[:10] != b'SEGA SPRED':
        raise ValueError('unknown SPRED signature')
    word = lambda at: struct.unpack_from('>H', data, at)[0]
    long_ = lambda at: struct.unpack_from('>I', data, at)[0]
    palette = bitmaps = None
    at = 16
    while at + 16 <= len(data):
        offset, size, index = long_(at), long_(at + 4), long_(at + 8)
        if not offset or not size:
            break
        if offset > len(data) or size > len(data) - offset or index >= 14:
            raise ValueError('invalid chunk extent')
        if index == 1: palette = (offset, size)
        if index == 2: bitmaps = (offset, size)
        at += 16
        if at >= offset:
            break
    if not bitmaps or bitmaps[1] < 16:
        raise ValueError('missing image table')
    count = word(bitmaps[0]); table = 16 + count * 16
    colors = []
    if palette and palette[1] >= 16:
        wide = word(palette[0] + 2) == 4; step = 4 if wide else 2
        for p in range(palette[0] + 16, palette[0] + palette[1] - step + 1, step):
            if wide:
                colors.append((data[p + 1], data[p + 2], data[p + 3], data[p]))
            else:
                c = word(p)
                colors.append(((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31, 255))
        if colors:
            colors[0] = colors[0][:3] + (0,)
    images = []
    for n in range(count):
        p = bitmaps[0] + 16 + n * 16
        w, h, fmt, bank = word(p), word(p + 2), word(p + 4), word(p + 6)
        rel, size = long_(p + 8), long_(p + 12)
        if not w or not h or not size:
            continue
        bpp = BITS[fmt & 15]; need = (w * h * bpp + 7) // 8
        start = bitmaps[0] + table + rel
        comp = data[start:start + size]
        raw = _lz(comp, need) if fmt >> 4 else comp[:need]
        px = bytearray()
        for i in range(w * h):
            if bpp in (4, 8):
                v = raw[i] if bpp == 8 else (raw[i // 2] >> (0 if i & 1 else 4)) & 15
                px += bytes(colors[bank * (16 if bpp == 4 else 256) + v])
            elif bpp == 16:
                c = raw[i * 2] | (raw[i * 2 + 1] << 8)
                px += bytes((((c >> 10) & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, (c & 31) * 255 // 31, 255))
            else:
                raise ValueError('24/32-bit direct SPRED needs verified channel mapping')
        images.append((n, Image.frombytes('RGBA', (w, h), bytes(px))))
    return images


if __name__ == '__main__':
    src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    for n, image in decode(src.read_bytes()):
        image.save(out / f'{src.stem}_{n}.png')
