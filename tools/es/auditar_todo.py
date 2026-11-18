"""Auditoría global de los lotes traducidos: python -X utf8 auditar_todo.py
Comprueba: ids faltantes/duplicados, marcadores copiados, restos en inglés,
vosotros/voseo, caracteres fuera de CP1252, líneas vacías, signos ¿¡ sin abrir,
cifras/nombres que cambian entre inglés y español.
"""
import json
import re
import sys
from pathlib import Path

from _rutas import WORK
ROOT = WORK
ENG = re.compile(r"\b(the|and|you|your|with|that|this|have|what|are|was|not|but|for)\b", re.I)
VOSOTROS = re.compile(r"\b(vosotros|vosotras|os\b|vuestr[oa]s?|vais|estáis|sois|habéis|queréis|tenéis|podéis|sabéis|venid|callaos)\b", re.I)
VOSEO = re.compile(r"\b(vos|tenés|querés|podés|sabés|sos|decime|mirá|vení|andá|hacé|pensás|venís|decís)\b", re.I)
BAD = set('“”‘’—–')


def load(path):
    rows = []
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main():
    total = bad = 0
    for cap in sorted(ROOT.glob('capitulo*'), key=lambda p: int(p.name[8:])):
        for fin in sorted((cap / 'lotes').glob('lote??.in.jsonl')):
            name = fin.name.split('.')[0]
            fout = fin.with_name(name + '.out.jsonl')
            src = load(fin)
            if not fout.exists():
                print(f'{cap.name}/{name}: SIN .out ({len(src)} líneas)')
                bad += len(src)
                continue
            out = {}
            for r in load(fout):
                if r['id'] in out:
                    print(f'{cap.name}/{name} {r["id"]}: duplicado')
                    bad += 1
                out[r['id']] = r['es']
            for it in src:
                total += 1
                es = out.get(it['id'])
                en = it['en']
                if es is None:
                    print(f'{cap.name}/{name} {it["id"]}: FALTA')
                    bad += 1
                    continue
                issues = []
                if re.fullmatch(r'\d{4}TBL:\d+', en.strip()):
                    if es.strip() != en.strip():
                        issues.append('marcador alterado')
                else:
                    if not es.strip():
                        issues.append('vacío')
                    if len(ENG.findall(es)) >= 3:
                        issues.append('posible inglés')
                    if VOSOTROS.search(es):
                        issues.append('vosotros')
                    if VOSEO.search(es):
                        issues.append('voseo')
                    if any(c in BAD for c in es):
                        issues.append('char no CP1252')
                    try:
                        es.encode('cp1252')
                    except UnicodeEncodeError:
                        issues.append('no codifica CP1252')
                    for sym, op in (('?', '¿'), ('!', '¡')):
                        if sym in es and op not in es:
                            issues.append(f'falta {op}')
                    if en.count('?') != es.count('?') and en.count('?') and not es.count('?'):
                        issues.append('pregunta perdida')
                    nums_en = sorted(re.findall(r'\d+', en))
                    nums_es = sorted(re.findall(r'\d+', es))
                    if nums_en != nums_es:
                        issues.append(f'cifras {nums_en}->{nums_es}')
                    if len(es) < 0.35 * len(en):
                        issues.append('muy corto vs inglés')
                if issues:
                    bad += 1
                    print(f'{cap.name}/{name} {it["id"]}: {", ".join(issues)} | {es!r}')
            extra = set(out) - {i['id'] for i in src}
            for e in extra:
                print(f'{cap.name}/{name} {e}: id sobrante')
    print(f'\nTotal líneas {total}; con avisos {bad}')


if __name__ == '__main__':
    sys.exit(main())
