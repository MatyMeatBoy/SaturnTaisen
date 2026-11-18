"""Lee registros japoneses de cualquier tabla: python -X utf8 leer_japones.py TABLA DESDE HASTA [disco]
Glifos aun no transcritos salen como <md5corto>. Ejemplo: leer_japones.py 0801 560 576 2"""
import hashlib
import json
import mmap
import struct
import sys
from pathlib import Path

from _rutas import OWNER, ROOT as REPO, WORK
HERE = WORK
ROOT = OWNER
sys.path.insert(0, str(REPO / 'tools'))
from audit_sdk import files  # noqa: E402

table, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
disc = sys.argv[4] if len(sys.argv) > 4 else '2'
glyphs = HERE / 'japones-glifos'
order = json.loads((glyphs / 'order.json').read_text())
chars = []
for index in range(len(list(glyphs.glob('map*.txt')))):
    chars += (glyphs / f'map{index:02d}.txt').read_text(encoding='utf-8').split('\n')
glyph_char = dict(zip(order, chars))
image = ROOT / f'local/prepared/japanese-disc{disc}/Track 01.iso'
with image.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
    extents = {p: (lba, size) for p, lba, size in files(iso)}

    def read(name):
        lba, size = extents[name]
        return bytes(iso[lba * 2048:lba * 2048 + size])

    data, sheet = read(f'/SAKURA1/{table}TBL.BIN'), read(f'/SAKURA1/{table}KNJ.BIN')
    sheet_chars = []
    for g in range(len(sheet) // 128):
        h = hashlib.md5(sheet[g * 128:(g + 1) * 128]).hexdigest()
        sheet_chars.append(glyph_char.get(h, '<' + h[:4] + '>'))
    start, footer = (2 * v for v in struct.unpack_from('>HH', data))
    entries = list(struct.iter_unpack('>HH', data[4:start]))
    for index in range(lo, min(hi, len(entries))):
        record_id, offset = entries[index]
        begin = start + offset * 2
        end = start + entries[index + 1][1] * 2 if index + 1 < len(entries) else footer
        text = []
        for code in struct.unpack_from(f'>{(end - begin) // 2}H', data, begin)[2:]:
            if code == 0:
                break
            text.append('\n' if code == 0x0A0D else (sheet_chars[code - 1] if 0 < code <= len(sheet_chars) else f'<{code:x}>'))
        print(f'{table}-{index:04d}', ''.join(text).replace('\n', ' / '))
