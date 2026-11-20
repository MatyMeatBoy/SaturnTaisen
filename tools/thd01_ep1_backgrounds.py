"""THD01: table of episode 1 backgrounds (names only, no pixels).

Usage: python tools/thd01_ep1_backgrounds.py OUT.md
The generated chapter register supplies the selected PC donor and the disc-specific
verification status, including shared donors and dedicated drawing paths.
"""
from collections import Counter
import json
import re
import sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
cov = json.loads((R / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
ch = cov['chapters'][0]['resources']['scene-pictures']
cold = set(re.findall(r'BG\d+', (R / 'docs/research/hd-chapter-1.md').read_text(encoding='utf-8').split('### Bodies')[0]))
disc1 = {
    key: row
    for group in [cov['unassigned'], *(chapter['resources'] for chapter in cov['chapters'])]
    for key, row in group['scene-pictures'].items()
    if key.startswith('1:/SAKURA1/BG')
}
names = {k.split('/')[-1][:-4] for k in ch if '/BG' in k and k.split('/')[-1].startswith('BG')} | cold | {'BG1120'}
rows = []
for name in sorted(names):
    key = f'1:/SAKURA1/{name}.BIN'
    row = disc1.get(key, {})
    donor = Path(row['pc']).name if row.get('pc') else '-'
    reason = row.get('reason', '')
    if row.get('status') == 'hd':
        verified = row.get('verified_in_game', False)
        state = 'conectado y verificado' if verified else 'conectado sin verificar'
        if donor != f'{name}.SPR':
            reason = f'reutiliza {donor}'
    else:
        state = row.get('status', 'sin registro')
    if name == 'BG1120':
        reason = ' · '.join(filter(None, (reason, 'variante de iluminación de BG1119')))
    rows.append((name, donor, state, reason, row.get('runtime_evidence', '-')))
out = ['# THD01: fondos del episodio 1 (donantes PC de la ruta fría y variantes)', '',
       'Generado con `python tools/thd01_ep1_backgrounds.py docs/research/thd01-episode1-backgrounds.md`. Solo nombres y estados; sin pixeles.',
       'Alcance: BG de `config/hd-chapter-coverage.json` capitulo 1, los de la ruta fria de `hd-chapter-1.md`, y BG1120 (iluminacion nocturna). IC/EVE/BBG/TITLE se tratan aparte.', '',
       '| Saturn BG | PC SPR | Estado | Motivo | Evidencia |', '|---|---|---|---|---|']
out += [f'| {a} | {b} | {c} | {d} | {e} |' for a, b, c, d, e in rows]
spr = {}
for r in rows: spr.setdefault(r[1], []).append(r[0])
dup = {k: v for k, v in spr.items() if len(v) > 1 and k != '-'}
out += ['', f'Donantes PC distintos: {len(set(spr) - {"-"})}.']
for donor, appearances in sorted(dup.items()):
    out.append(f'- `{donor}` se reutiliza en {", ".join(appearances)}.')
out.append('')
out.append('Apariciones Saturn: ' + ', '.join(f'{k}: {v}' for k, v in Counter(r[2] for r in rows).items()))
destination = Path(sys.argv[1])
witness_heading = '\n\n## Verificacion en juego a 2560x1440'
existing = destination.read_text(encoding='utf-8') if destination.is_file() else ''
_, heading, evidence = existing.partition(witness_heading)
destination.write_text('\n'.join(out) + (heading + evidence if heading else '\n'), encoding='utf-8', newline='\n')
print(out[-1])
