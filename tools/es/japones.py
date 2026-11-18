"""Rebuild the Japanese chapter-one script from the prepared Japanese disc.

Japanese TBL records hold 16-bit codes: 0 ends the record, 0x0A0D is a line break,
any other code c is glyph c-1 of the table's own ????KNJ.BIN sheet (16x16, 4 bpp).
Glyph bitmaps are identified by MD5 and mapped to characters transcribed by eye in
japones-glifos/mapNN.txt (〓 = not read with confidence).
"""
import hashlib
import json
import mmap
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _rutas import OWNER, ROOT, WORK as HERE  # noqa: E402
sys.path.insert(0, str(ROOT / 'tools'))
from audit_sdk import files  # noqa: E402

TABLES = ('0100', '0101', '0102', '0103', '0108', '0109')


def main():
    glyphs = HERE / 'japones-glifos'
    order = json.loads((glyphs / 'order.json').read_text())
    chars = []
    for index in range(len(list(glyphs.glob('map*.txt')))):
        chars += (glyphs / f'map{index:02d}.txt').read_text(encoding='utf-8').split('\n')
    glyph_char = dict(zip(order, chars, strict=True))
    image = OWNER / 'local/prepared/japanese-disc1/Track 01.iso'
    out, total, unknown = {}, 0, 0
    with image.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        extents = {path: (lba, size) for path, lba, size in files(iso)}

        def read(name):
            lba, size = extents[name]
            return bytes(iso[lba * 2048:lba * 2048 + size])

        for table in TABLES:
            data, sheet = read(f'/SAKURA1/{table}TBL.BIN'), read(f'/SAKURA1/{table}KNJ.BIN')
            sheet_chars = [glyph_char[hashlib.md5(sheet[g * 128:(g + 1) * 128]).hexdigest()] for g in range(len(sheet) // 128)]
            start, footer = (2 * v for v in struct.unpack_from('>HH', data))
            entries = list(struct.iter_unpack('>HH', data[4:start]))
            for index, (record_id, offset) in enumerate(entries):
                begin = start + offset * 2
                end = start + entries[index + 1][1] * 2 if index + 1 < len(entries) else footer
                text = []
                for code in struct.unpack_from(f'>{(end - begin) // 2}H', data, begin)[2:]:
                    if code == 0:
                        break
                    if code == 0x0A0D:
                        text.append('\n')
                        continue
                    char = sheet_chars[code - 1] if 0 < code <= len(sheet_chars) else f'<{code:x}>'
                    text.append(char)
                    total += 1
                    unknown += char == '〓'
                out[f'{table}-{index:04d}'] = dict(record_id=record_id, ja=''.join(text))
    target = HERE / 'capitulo1/japones.json'
    target.write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding='utf-8')
    print(f'{len(out)} records, {total} glyphs, {unknown} unread ({unknown / total:.1%}) -> {target}')


if __name__ == '__main__':
    main()
