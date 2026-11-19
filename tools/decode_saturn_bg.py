"""Read-only decoder for the Saturn scene backgrounds `BG*.BIN` (T67).

Format (verified on SAKURA1/BG1001.BIN, the theatre lobby):

  0x0000  header, 0x50 bytes (starts 00 01 00 01, rest zero in every file checked)
  0x0050  288x144 picture, 8 bits per pixel, stored as 36x18 cells of 8x8 pixels
          (64 bytes per cell, cells in row-major order, rows inside a cell in order)
  0xA250  palette, 256 big-endian RGB555 words (Saturn layout: bits 0-4 R, 5-9 G, 10-14 B)
  0xA450  trailing data (not needed to draw the picture; 45,120-byte files are zero padded)

Variant B (header `00 01 00 02`, 31 files such as BG1207 and BG2207: wide or tall scenes) stores its size in
the header and puts the palette first:

  0x0000  00 01 00 02, cells wide (u16 BE), cells high (u16 BE), 8 more bytes
  0x0010  palette, 256 big-endian RGB555 words
  0x0210  picture, 8 bpp, (cells wide) x (cells high) cells of 8x8, row-major (e.g. 64x18 = 512x144)
  after   trailing data (not needed to draw)

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


def decode(data):
    """Return an RGB Pillow image (288x144 for the common variant), or None when `data` is not a known layout."""
    if data[:4] == b'\x00\x01\x00\x02' and len(data) >= 0x210:
        cells_w, cells_h = struct.unpack_from('>HH', data, 4)
        if not cells_w or not cells_h or 0x210 + cells_w * cells_h * 64 > len(data):
            return None
        return _cells(data, 0x10, 0x210, cells_w, cells_h)
    if len(data) != SIZE or data[:4] != b'\x00\x01\x00\x01':
        return None
    return _cells(data, PALETTE_AT, HEADER, CELLS_W, CELLS_H)


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
