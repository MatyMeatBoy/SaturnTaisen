"""Read-only decoder for the Saturn scene backgrounds `BG*.BIN` (T67).

Format (verified on SAKURA1/BG1001.BIN, the theatre lobby):

  0x0000  header, 0x50 bytes (starts 00 01 00 01, rest zero in every file checked)
  0x0050  288x144 picture, 8 bits per pixel, stored as 36x18 cells of 8x8 pixels
          (64 bytes per cell, cells in row-major order, rows inside a cell in order)
  0xA250  palette, 256 big-endian RGB555 words (Saturn layout: bits 0-4 R, 5-9 G, 10-14 B)
  0xA450  trailing data (not needed to draw the picture; 45,120-byte files are zero padded)

Variant B (marker `00 01 00 02`, 30 files) stores a two-word VDP2 pattern-name table:

  0x0000  marker, cells wide (u16 BE), cells high (u16 BE), declared tile count (u16 BE)
  0x0010  palette, 256 big-endian RGB555 words
  0x0610  row-major pattern names, one u32 BE per cell
  after   contiguous 64-byte 8 bpp tiles, starting immediately after the pattern names

In the file, the low bits of each pattern name give a 32-byte character number (twice the tile
index). Bit 30 flips horizontally and bit 31 vertically. The complete tile bytes in the file
bound all reads because BG4302 declares more tiles than its file contains.

The mini-game files (BGHANA, BGSLOT, ...) start with a palette and are not decoded here.

Usage:
  python tools/decode_saturn_bg.py DISC_TRACK01.iso OUTDIR [--prefix SAKURA1/BG]
Writes one PNG per file for local comparison. Never commit the output: it is the game's art.
"""
import argparse
import struct
from pathlib import Path

from PIL import Image

HEADER = 0x50
CELLS_W, CELLS_H = 36, 18
PICTURE = CELLS_W * CELLS_H * 64
PALETTE_AT = HEADER + PICTURE
SIZE = 45120
VARIANT_B = b'\x00\x01\x00\x02'
VARIANT_B_MAP_AT = 0x610
CHARACTER_NUMBER = 0x7FFF
FLIP_HORIZONTAL = 1 << 30
FLIP_VERTICAL = 1 << 31


def decode(data):
    """Return an RGB Pillow image (288x144 for the common variant), or None when `data` is not a known layout."""
    if data[:4] == VARIANT_B:
        layout = _variant_b_layout(data)
        return _variant_b_image(data, *layout) if layout else None
    table = _table(data)
    if table:
        return _mapped(data, *table)
    screen = _screen(data)
    if screen is not None:
        return screen
    if len(data) != SIZE or data[:4] != b'\x00\x01\x00\x01':
        return None
    return _cells(data, PALETTE_AT, HEADER, CELLS_W, CELLS_H)


def _variant_b_layout(data):
    if len(data) < VARIANT_B_MAP_AT:
        return None
    cells_w, cells_h = struct.unpack_from('>HH', data, 4)
    cell_count = cells_w * cells_h
    picture_at = VARIANT_B_MAP_AT + cell_count * 4
    if not cell_count or picture_at >= len(data):
        return None
    tile_count, remainder = divmod(len(data) - picture_at, 64)
    if remainder:
        return None
    names = struct.unpack_from(f'>{cell_count}I', data, VARIANT_B_MAP_AT)
    # These files use only the two flip flags and an even 15-bit character number.
    supported_bits = FLIP_HORIZONTAL | FLIP_VERTICAL | (CHARACTER_NUMBER & ~1)
    if any(name & ~supported_bits or (name & CHARACTER_NUMBER) // 2 >= tile_count for name in names):
        return None
    return cells_w, cells_h, picture_at, names


def _variant_b_image(data, cells_w, cells_h, picture_at, names):
    words = struct.unpack_from('>256H', data, 0x10)
    palette = [((w & 31) * 255 // 31, ((w >> 5) & 31) * 255 // 31, ((w >> 10) & 31) * 255 // 31)
               for w in words]
    image = Image.new('RGB', (cells_w * 8, cells_h * 8))
    pixels = image.load()
    for cell, name in enumerate(names):
        base = picture_at + (name & CHARACTER_NUMBER) * 32
        left, top = (cell % cells_w) * 8, (cell // cells_w) * 8
        flip_x = 7 if name & FLIP_HORIZONTAL else 0
        flip_y = 7 if name & FLIP_VERTICAL else 0
        for y in range(8):
            row_at = base + (y ^ flip_y) * 8
            for x in range(8):
                pixels[left + x, top + y] = palette[data[row_at + (x ^ flip_x)]]
    return image


def _screen_ok(data):
    if not 76000 <= len(data) <= 77000:
        return False
    first = struct.unpack_from('>4I', data, 512)
    # The table counts up by 2 per cell; IC/KABE/OMAKE/LOAD start at 0, TITLE* at 2 (one more cell in the file).
    return first[0] in (0, 2) and first[1:] == (first[0] + 2, first[0] + 4, first[0] + 6)


def _screen(data):
    """Variant D: full-screen pictures (IC, OMAKE, LOAD, KABE, TITLE): 256 palette words, a table of 40x28 big-endian
    u32 entries (2 x cell number), then the 8x8 8 bpp cells. 320x224."""
    if not _screen_ok(data):
        return None
    entries = struct.unpack_from('>1120I', data, 512)
    tiles = (len(data) - 512 - 4480) // 64
    words = struct.unpack_from('>256H', data, 0)
    palette = [((w & 31) * 255 // 31, ((w >> 5) & 31) * 255 // 31, ((w >> 10) & 31) * 255 // 31) for w in words]
    image = Image.new('RGB', (320, 224))
    pixels = image.load()
    for cell, entry in enumerate(entries):
        tile = entry >> 1
        if tile >= tiles:
            continue
        base = 512 + 4480 + tile * 64
        left, top = (cell % 40) * 8, (cell // 40) * 8
        for y in range(8):
            row = data[base + y * 8: base + y * 8 + 8]
            for x in range(8):
                pixels[left + x, top + y] = palette[row[x]]
    return image


def _cells(data, palette_at, picture_at, cells_w, cells_h):
    words = struct.unpack_from('>256H', data, palette_at)
    palette = [((w & 31) * 255 // 31, ((w >> 5) & 31) * 255 // 31, ((w >> 10) & 31) * 255 // 31) for w in words]
    image = Image.new('RGB', (cells_w * 8, cells_h * 8))
    pixels = image.load()
    for cell in range(cells_w * cells_h):
        base = picture_at + cell * 64
        left, top = (cell % cells_w) * 8, (cell // cells_w) * 8
        for y in range(8):
            row = data[base + y * 8: base + y * 8 + 8]
            for x in range(8):
                pixels[left + x, top + y] = palette[row[x]]
    return image


def picture_bytes(data):
    """The cell data the game copies to VDP2 (hash key for runtime recognition), or None."""
    if data[:4] == VARIANT_B:
        layout = _variant_b_layout(data)
        return data[layout[2]:] if layout else None
    table = _table(data)
    if table:
        return data[table[0]:table[0] + table[1]]
    if _screen_ok(data):
        return data[512 + 4480:]
    if len(data) == SIZE and data[:4] == b'\x00\x01\x00\x01':
        return data[HEADER:PALETTE_AT]
    return None


def _mapped(data, picture_at, picture_size, map_at, map_size, palette_at):
    """Variant C picture: unique 8x8 tiles plus a map (u16 per cell = 2 x tile number, VDP2 pattern names)."""
    entries = map_size // 2
    dims = {648: (36, 18), 1120: (40, 28)}.get(entries)
    if dims is None:
        return None
    cells_w, cells_h = dims
    words = struct.unpack_from('>256H', data, palette_at)
    palette = [((w & 31) * 255 // 31, ((w >> 5) & 31) * 255 // 31, ((w >> 10) & 31) * 255 // 31) for w in words]
    image = Image.new('RGB', (cells_w * 8, cells_h * 8))
    pixels = image.load()
    names = struct.unpack_from('>%dH' % entries, data, map_at)
    tiles = picture_size // 64
    for cell, name in enumerate(names):
        tile = (name & 0x3FFF) >> 1
        if tile >= tiles:
            continue
        base = picture_at + tile * 64
        left, top = (cell % cells_w) * 8, (cell // cells_w) * 8
        for y in range(8):
            row = data[base + y * 8: base + y * 8 + 8]
            for x in range(8):
                pixels[left + x, top + y] = palette[row[x]]
    return image


def palette_bytes(data):
    """The 256 palette words (512 bytes) the game loads into colour RAM for this picture, or None."""
    if data[:4] == VARIANT_B and len(data) >= 0x210:
        return data[0x10:0x210]
    table = _table(data)
    if table:
        return data[table[4]:table[4] + 512]
    if _screen_ok(data):
        return data[:512]
    if len(data) == SIZE and data[:4] == bytes([0, 1, 0, 1]):
        return data[PALETTE_AT:PALETTE_AT + 512]
    return None


def palette_fingerprint(data):
    """FNV-1a 64 over the palette bytes: what `Renderer::BackgroundPaletteFingerprint` computes from colour RAM."""
    palette = palette_bytes(data)
    if palette is None:
        return None
    value = 14695981039346656037
    for byte in palette:
        value = ((value ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value


def _table(data):
    """Variant C (disc 2 battle backgrounds `BBG*.BIN`): big-endian (offset, size) pairs from 0x00, ended by a
    zero pair: the unique tiles, the map (1296 or 2240 bytes) and the 512-byte palette.
    Returns (picture_at, picture_size, map_at, map_size, palette_at) or None."""
    pairs = []
    for at in range(0, 64, 8):
        if at + 8 > len(data):
            return None
        offset, size = struct.unpack_from('>II', data, at)
        if not offset and not size:
            break
        if offset + size > len(data):
            return None
        pairs.append((offset, size))
    if len(pairs) != 3 or pairs[0][0] != 0x18 or pairs[2][1] != 512 or pairs[1][1] not in (1296, 2240):
        return None
    return pairs[0][0], pairs[0][1], pairs[1][0], pairs[1][1], pairs[2][0]


def nc_records(data):
    """The (type, x1, y1, x2, y2) records of an NC*.BIN: nine bytes each from 0x11, type 0x3C-0x3F."""
    records, at = [], 0x11
    while at + 9 <= 0x410 and data[at] in (0x3C, 0x3D, 0x3E, 0x3F):
        records.append((data[at],) + struct.unpack_from('>4H', data, at + 1))
        at += 9
    return records


def nc_stride(data):
    """Row stride of the body bitmap at 0x610: the lag with the smallest mean difference between a pixel and the
    one a row below, counting only pairs where either pixel is not the transparent index 0 (the body is mostly
    transparent, so plain differences prefer wrong, longer lags). Searched from 60 to 419; None if the file is short."""
    segment = data[0x610:0x610 + 16000]
    if len(segment) < 3000:
        return None
    best, best_score = None, None
    for w in range(60, 420):
        total = count = 0
        for i in range(0, len(segment) - w, 3):
            a, b = segment[i], segment[i + w]
            if a or b:
                total += abs(a - b)
                count += 1
        if count > 150 and (best_score is None or total / count < best_score):
            best, best_score = w, total / count
    return best


def decode_nc(data):
    """The large-character body of an NC*.BIN as an RGBA picture (palette at 0x410, bitmap at 0x610, index 0 clear).

    The face is blank: the eyes and mouth are separate strips that follow the body. Width is the detected
    stride, height is 144."""
    if len(data) < 0x610 + 6000 or data[:2] != bytes([0, 2]):
        return None
    records = nc_records(data)
    width = nc_stride(data)
    if not width:
        return None
    # Every body seen so far is 144 rows high (the records only mark the parts, their y2 can be smaller).
    height = 144
    if width * height > len(data) - 0x610:
        return None
    words = struct.unpack_from('>256H', data, 0x410)
    palette = [((w & 31) * 255 // 31, ((w >> 5) & 31) * 255 // 31, ((w >> 10) & 31) * 255 // 31) for w in words]
    image = Image.new('RGBA', (width, height))
    pixels = image.load()
    for i in range(width * height):
        index = data[0x610 + i]
        pixels[i % width, i // width] = (0, 0, 0, 0) if index == 0 else palette[index] + (255,)
    return image


class Iso:
    """Minimal ISO 9660 reader for a 2048-byte-sector data track."""

    def __init__(self, path):
        self.file = open(path, 'rb')
        pvd = self.read(16, 1)
        if pvd[1:6] != b'CD001':
            raise ValueError('not an ISO 9660 data track with 2048-byte sectors')
        self.root = (struct.unpack('<I', pvd[158:162])[0], struct.unpack('<I', pvd[166:170])[0])

    def read(self, sector, count):
        self.file.seek(sector * 2048)
        return self.file.read(count * 2048)

    def listdir(self, extent):
        data = self.read(extent[0], (extent[1] + 2047) // 2048)
        entries, at = [], 0
        while at < len(data):
            length = data[at]
            if length == 0:
                at = (at // 2048 + 1) * 2048
                continue
            record = data[at:at + length]
            name = record[33:33 + record[32]].decode('latin1').split(';')[0]
            entries.append((name, (struct.unpack('<I', record[2:6])[0], struct.unpack('<I', record[10:14])[0]), bool(record[25] & 2)))
            at += length
        return entries

    def find(self, path):
        current = self.root
        for part in path.strip('/').split('/'):
            for name, extent, _ in self.listdir(current):
                if name == part:
                    current = extent
                    break
            else:
                return None
        return current

    def files(self, folder):
        extent = self.find(folder)
        return [] if extent is None else [(name, e) for name, e, directory in self.listdir(extent) if not directory]

    def content(self, extent):
        return self.read(extent[0], (extent[1] + 2047) // 2048)[:extent[1]]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('iso', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--folder', default='SAKURA1')
    parser.add_argument('--prefix', default='BG')
    args = parser.parse_args()
    iso = Iso(args.iso)
    args.output.mkdir(parents=True, exist_ok=True)
    done = skipped = 0
    for name, extent in iso.files(args.folder):
        if not name.startswith(args.prefix) or not name.endswith('.BIN'):
            continue
        image = decode(iso.content(extent))
        if image is None:
            skipped += 1
            continue
        image.save(args.output / (name[:-4] + '.png'))
        done += 1
    print(f'decoded {done}, skipped {skipped} (other sizes)')


if __name__ == '__main__':
    main()
