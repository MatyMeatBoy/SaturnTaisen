"""Spanish LOADING scroll (LOAD.BIN of disc 1), drafted by program (T87).

  python -X utf8 tools/es/carga_es.py [--output DIR]

LOAD.BIN is a 320x224 picture (palette, table of cells, 8x8 8 bpp cells; docs/research/saturn-bg-format.md): the
dark logo pattern with a vertical brush-lettered scroll ("LOADING") inside a double red frame at x 131-187,
y 8-215. The interior of the frame is cleared to black and "CARGANDO" is drawn, one letter per row, in a brush
face (Ink Free), white with a soft edge; only the cells under the frame interior are rewritten, to the nearest
palette colour, so the file keeps its size, palette and cell table. Output: DIR/SAKURA1/LOAD.BIN and a preview.
Wire it in with `construir_todo.py --disc 1 --portadas`. A draft of the lettering, not the hand-made one.
"""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import decode_saturn_bg as s  # noqa: E402
from _rutas import OWNER, WORK  # noqa: E402

TEXT = 'CARGANDO'
INTERIOR = (136, 13, 183, 210)   # inside the double red frame, inclusive


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path, default=WORK / 'builds/es-portadas')
    args = parser.parse_args()
    iso = s.Iso(OWNER / 'local/prepared/disc1/Track 01.iso')
    data = bytearray(iso.content(dict(iso.files('SAKURA1'))['LOAD.BIN']))
    palette = [((w & 31) * 255 // 31, ((w >> 5) & 31) * 255 // 31, ((w >> 10) & 31) * 255 // 31)
               for w in struct.unpack_from('>256H', data, 0)]
    entries = struct.unpack_from('>1120I', data, 512)
    left, top, right, bottom = INTERIOR
    width, height = right - left + 1, bottom - top + 1
    scale = 4  # draw big, then reduce for a soft edge
    canvas = Image.new('L', (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(canvas)
    cell = height * scale / len(TEXT)
    font = ImageFont.truetype('C:/Windows/Fonts/Inkfree.ttf', int(cell * 0.92))
    for i, letter in enumerate(TEXT):
        box = draw.textbbox((0, 0), letter, font=font)
        x = (width * scale - (box[2] - box[0])) / 2 - box[0]
        y = i * cell + (cell - (box[3] - box[1])) / 2 - box[1]
        draw.text((x, y), letter, font=font, fill=255, stroke_width=5, stroke_fill=255)
    small = canvas.resize((width, height), Image.LANCZOS)
    nearest = {}
    def pick(level):
        if level not in nearest:
            target = (level, level, level)
            nearest[level] = min(range(256), key=lambda k: sum((palette[k][c] - target[c]) ** 2 for c in range(3)))
        return nearest[level]
    for cell_number, entry in enumerate(entries):
        base = 512 + 4480 + (entry >> 1) * 64
        for yy in range(8):
            for xx in range(8):
                x, y = (cell_number % 40) * 8 + xx, (cell_number // 40) * 8 + yy
                if left <= x <= right and top <= y <= bottom:
                    data[base + yy * 8 + xx] = pick(small.getpixel((x - left, y - top)))
    out = args.output / 'SAKURA1'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'LOAD.BIN').write_bytes(bytes(data))
    preview = s.decode(bytes(data)).convert('RGB')
    preview.resize((640, 448), Image.NEAREST).save(args.output / 'carga.png')
    print('LOAD.BIN written', len(data), 'bytes; preview', args.output / 'carga.png')


if __name__ == '__main__':
    main()
