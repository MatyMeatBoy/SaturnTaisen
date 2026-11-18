"""Render sheets of any new (unseen) glyphs for a chapter's KNJ sheets, continuing
japones-glifos/order.json and sheetNN.png where the previous chapter left off:

  python glifos_nuevos.py --tables 0201 0202 0203 0204 0205 0206

After running, transcribe each new sheet by eye into mapNN.txt (one character per
line, matching the printed index order; 〓 = not read with confidence), then run
japones.py to rebuild that chapter's script.
"""
import argparse
import hashlib
import json
import mmap
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _rutas import OWNER, ROOT, WORK as HERE  # noqa: E402
sys.path.insert(0, str(ROOT / 'tools'))
from audit_sdk import files  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

GLYPHS_DIR = HERE / 'japones-glifos'


def glyph_bitmap(blob: bytes):
    rows = []
    for y in range(16):
        row = []
        for x in range(16):
            b = blob[y * 8 + x // 2]
            row.append((b >> 4) if x % 2 == 0 else (b & 15))
        rows.append(row)
    return rows


def main(tables, per_sheet=30, scale=4):
    order = json.loads((GLYPHS_DIR / 'order.json').read_text())
    known = set(order)
    image = OWNER / 'local/prepared/japanese-disc1/Track 01.iso'
    new_glyphs = []
    seen_this_run = set()
    with image.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        extents = {p: (lba, size) for p, lba, size in files(iso)}

        def read(name):
            lba, size = extents[name]
            return bytes(iso[lba * 2048:lba * 2048 + size])

        for table in tables:
            sheet = read(f'/SAKURA1/{table}KNJ.BIN')
            for g in range(len(sheet) // 128):
                blob = sheet[g * 128:(g + 1) * 128]
                md5 = hashlib.md5(blob).hexdigest()
                if md5 in known or md5 in seen_this_run:
                    continue
                seen_this_run.add(md5)
                new_glyphs.append((md5, glyph_bitmap(blob)))

    print(f'{len(new_glyphs)} glifos nuevos')
    start_sheet = len(sorted(GLYPHS_DIR.glob('sheet*.png')))
    cell, label_h = 16 * scale, 14
    for s in range(0, len(new_glyphs), per_sheet):
        chunk = new_glyphs[s:s + per_sheet]
        cols = 10
        rows_n = (len(chunk) + cols - 1) // cols
        img = Image.new('RGB', (cols * cell, rows_n * (cell + label_h)), 'white')
        draw = ImageDraw.Draw(img)
        for i, (_md5, bitmap) in enumerate(chunk):
            x0, y0 = (i % cols) * cell, (i // cols) * (cell + label_h)
            draw.text((x0 + 1, y0 + 1), str(s + i), fill=(255, 0, 0))
            for y in range(16):
                for x in range(16):
                    if bitmap[y][x]:  # grayscale shading, not binary: matches the font's own AA
                        g = 255 - bitmap[y][x] * 17
                        draw.rectangle([x0 + x * scale, y0 + label_h + y * scale,
                                        x0 + x * scale + scale - 1, y0 + label_h + y * scale + scale - 1],
                                       fill=(g, g, g))
        out = GLYPHS_DIR / f'sheet{start_sheet + s // per_sheet:02d}.png'
        img.save(out)
        print('wrote', out, len(chunk), 'glyphs')

    order.extend(md5 for md5, _ in new_glyphs)
    (GLYPHS_DIR / 'order.json').write_text(json.dumps(order), encoding='utf-8')
    print('order.json actualizado:', len(order), 'glifos totales — falta transcribir las hojas nuevas a mapNN.txt')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tables', nargs='+', required=True)
    parser.add_argument('--per-sheet', type=int, default=30)
    args = parser.parse_args()
    main(args.tables, args.per_sheet)
