"""Textos ingleses idénticos (dentro de un capítulo) cuyo japonés difiere de registro/hablante.
python -X utf8 dedup_riesgo.py -> riesgo_dedup.json  [{cap, en, es, variantes:[{ids, ja, registro}]}]
Registro: cortés (です/ます/ございます/ください/ませ), kansai (や/やで/はん/ウチ), femenino-superior (なさい/わ/のよ),
llano (resto)."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from _rutas import OWNER, ROOT as REPO, WORK
HERE = WORK
CATALOG = WORK.parents[1] / 'work' / 'dialogue-catalog-worker' / 'dialogue.jsonl'
MARKER = re.compile(r'^\d{4}TBL:\d+\s*$')


def registro(ja: str) -> str:
    if re.search(r'です|ます|ございま|ください|ませ|でしょう|ました', ja):
        return 'cortes'
    if re.search(r'はん|ウチ|やで|やな|や[。！？…]|やろ', ja):
        return 'kansai'
    if re.search(r'なさい|のよ|わよ|かしら|だわ', ja):
        return 'fem-sup'
    return 'llano'


groups = defaultdict(lambda: defaultdict(list))
ja_by_cap = {}
with CATALOG.open(encoding='utf-8') as f:
    for line in f:
        row = json.loads(line)
        table = row['iso_path'].split('/')[-1][:4]
        text = row['display_text']
        if MARKER.match(text) or not text.strip():
            continue
        cap = int(table[:2])
        if cap not in ja_by_cap:
            path = HERE / f'capitulo{cap}' / 'japones_tol.json'
            ja_by_cap[cap] = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        rid = f"{table}-{row['index']:04d}"
        ja = ja_by_cap[cap].get(rid, {}).get('ja')
        if ja is None:
            continue
        groups[(cap, text)][ja].append(rid)

es_by = {}
for cap in range(1, 11):
    for path in (HERE / f'capitulo{cap}' / 'lotes').glob('lote??.out.jsonl'):
        src = path.with_name(path.name.replace('.out.', '.in.'))
        ens = {json.loads(l)['id']: json.loads(l)['en'] for l in src.read_text(encoding='utf-8').splitlines() if l.strip()}
        for l in path.read_text(encoding='utf-8').splitlines():
            if l.strip():
                r = json.loads(l)
                es_by[(cap, ens[r['id']])] = r['es']

risk, total_multi = [], 0
for (cap, en), variants in groups.items():
    if len(variants) < 2:
        continue
    total_multi += 1
    regs = {registro(j) for j in variants}
    if len(regs) > 1:
        risk.append(dict(cap=cap, en=en, es=es_by.get((cap, en)), variantes=[
            dict(ids=ids, n=len(ids), ja=ja.replace('\n', ' / '), registro=registro(ja)) for ja, ids in variants.items()]))
out = HERE / 'riesgo_dedup.json'
out.write_text(json.dumps(risk, ensure_ascii=False, indent=1), encoding='utf-8')
print('grupos con >1 japones distinto:', total_multi, '| con registro distinto:', len(risk))
by_cap = defaultdict(int)
for r in risk:
    by_cap[r['cap']] += 1
print(dict(sorted(by_cap.items())))
