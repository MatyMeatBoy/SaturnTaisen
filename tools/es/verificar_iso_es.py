"""Comprobación estructural de un disco español ya construido: python -X utf8 verificar_iso_es.py N
Relee cada tabla de diálogo y de combate de local/prepared/discN-es, la compara con la inglesa
(mismo nº de registros, mismos ids, marcadores intactos) y cuenta cuántos textos cambian."""
import mmap
import re
import sys
from pathlib import Path

from _rutas import OWNER, ROOT as REPO, WORK
ROOT = OWNER
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_sdk import files  # noqa: E402
from export_dialogue_catalog import parse_table  # noqa: E402
import combate  # noqa: E402

disc = sys.argv[1]
MARK = re.compile(r'^\d{4}TBL:\d+\s*$')


def load(path):
    out = {}
    with path.open('rb') as s, mmap.mmap(s.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        for name, lba, size in files(iso):
            out[name.upper()] = bytes(iso[lba * 2048:lba * 2048 + size])
    return out


en = load(ROOT / f'local/prepared/disc{disc}/Track 01.iso')
es = load(ROOT / f'local/prepared/disc{disc}-es/Track 01.iso')
tot = chg = bad = 0
same = {}
for name in sorted(en):
    base = name.rsplit('/', 1)[-1]
    if re.fullmatch(r'\d{4}TBL\.BIN', base):
        a = [(r.record_id, r.display_text) for r in parse_table(en[name])]
        b = [(r.record_id, r.display_text) for r in parse_table(es[name])]
    elif re.fullmatch(r'M\d{2}MES\.BIN', base):
        a = [(r['record_id'], combate.decode(r['words'])) for r in combate.parse(en[name])[2]]
        b = [(r['record_id'], combate.decode(r['words'])) for r in combate.parse(es[name])[2]]
    else:
        continue
    if [x[0] for x in a] != [x[0] for x in b]:
        print('IDS DISTINTOS', name)
        bad += 1
        continue
    n = c = 0
    for (_, ta), (_, tb) in zip(a, b):
        if MARK.match(ta):
            if ta != tb:
                print('MARCADOR ALTERADO', name)
                bad += 1
            continue
        if not ta.strip():
            continue
        n += 1
        c += ta != tb
        if ta == tb:
            same.setdefault(name, []).append(ta.replace(chr(10), ' / ')[:60])
    tot += n
    chg += c
    if c < n:
        print(f'{name}: {c}/{n} cambiados')
print(f'disco {disc}: {chg}/{tot} textos distintos del inglés; problemas {bad}')

if len(sys.argv) > 2:
    from collections import Counter
    allsame = Counter(t for lst in same.values() for t in lst)
    print('textos iguales más frecuentes:', allsame.most_common(40))
