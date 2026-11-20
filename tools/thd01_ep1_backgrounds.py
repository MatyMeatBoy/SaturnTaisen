"""THD01: table of episode 1 backgrounds (names only, no pixels).

Usage: python tools/thd01_ep1_backgrounds.py OUT.md
Connected = the picture's palette (or palette+cells) resolves to one PC picture in the table gen_scene_bg_table.py writes.
Attributed = config/hd-chapter-coverage.json chapter 1 lists it with verified_in_game.
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path
R = Path(__file__).resolve().parents[1]
cov = json.loads((R / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
mp = json.loads((R / 'config/hd-scene-bg-map.json').read_text(encoding='utf-8'))
rev = json.loads((R / 'config/hd-scene-bg-review.json').read_text(encoding='utf-8'))
ch = cov['chapters'][0]['resources']['scene-pictures']
cold = set(re.findall(r'BG\d+', (R / 'docs/research/hd-chapter-1.md').read_text(encoding='utf-8').split('### Bodies')[0]))
with tempfile.TemporaryDirectory() as scratch:
    table = Path(scratch) / 'scene-bg.h'
    subprocess.run([sys.executable, str(R / 'tools/gen_scene_bg_table.py'),
                    str(R / 'config/hd-scene-bg-map.json'), str(table)],
                   check=True, capture_output=True)
    txt = table.read_text(encoding='utf-8')
first = {palette: (file, int(index)) for palette, file, index in
         re.findall(r'\{0x([0-9A-F]+)ull,"([^"]+)",(\d+)\}', txt)}
amb = {(palette, cells): (file, int(index)) for palette, cells, file, index in
       re.findall(r'\{0x([0-9A-F]+)ull,0x([0-9A-F]+)ull,"([^"]+)",(\d+)\}', txt)}
pairs = {p['saturn_file'].split('/')[-1][:-4]: p for p in mp['pairs'] if p['saturn_file'].startswith('SAKURA1/BG')}
names = {k.split('/')[-1][:-4] for k in ch if '/BG' in k and k.split('/')[-1].startswith('BG')} | cold | {'BG1120'}
rows = []
for n in sorted(names):
    p = pairs.get(n); c = ch.get(f'1:/SAKURA1/{n}.BIN')
    if not p: rows.append((n, '-', 'sin pareja', 'sin entrada en hd-scene-bg-map.json', 'no conectado')); continue
    pc = p['pc_file'].split('/')[-1]
    selected = first.get(p['palette_fnv']) or amb.get((p['palette_fnv'], p.get('cells_fnv')))
    con = selected == (p['pc_file'], p['pc_image_index'])
    if n[2] in '34': why = 'recorte con clave de color (fuera de la tabla 288x144; dibujo propio documentado)'; con = False
    elif n in rev['rejected']: why = 'rechazado en revision'; con = False
    elif p.get('size') != [288, 144]: why = f"tamano {p.get('size')} fuera de la tabla 288x144 (dibujo de scroll propio)"; con = False
    elif con: why = ''
    elif selected: why = f"la clave selecciona {Path(selected[0]).name}, imagen {selected[1]}"
    else: why = 'paleta compartida sin segunda clave / sin pareja segura'
    attr = bool(c and c.get('verified_in_game'))
    st = ('conectado y atribuido' if con and attr else 'conectado sin atribuir' if con else
          'conectado por ruta propia (scroll/recorte), atribuido' if attr and (n[2] in '34' or p.get('size') != [288, 144]) else 'no conectado')
    var = ' (variante de iluminacion de BG1119)' if n == 'BG1120' else ''
    rows.append((n, pc, st, (why + var).strip(), c['runtime_evidence'] if c else '-'))
out = ['# THD01: fondos del episodio 1 (una fila por SPR fisico de la ruta fria y variantes)', '',
       'Generado con `python tools/thd01_ep1_backgrounds.py docs/research/thd01-episode1-backgrounds.md`. Solo nombres y estados; sin pixeles.',
       'Alcance: BG de `config/hd-chapter-coverage.json` capitulo 1, los de la ruta fria de `hd-chapter-1.md`, y BG1120 (iluminacion nocturna). IC/EVE/BBG/TITLE se tratan aparte.', '',
       '| Saturn BG | PC SPR | Estado | Motivo | Evidencia |', '|---|---|---|---|---|']
out += [f'| {a} | {b} | {c} | {d} | {e} |' for a, b, c, d, e in rows]
spr = {}
for r in rows: spr.setdefault(r[1], []).append(r[0])
dup = {k: v for k, v in spr.items() if len(v) > 1 and k != '-'}
out += ['', f'SPR fisicos compartidos por varios BG Saturn: {dup or "ninguno"}.', '']
from collections import Counter
out.append('Resumen: ' + ', '.join(f'{k}: {v}' for k, v in Counter(r[2] for r in rows).items()))
Path(sys.argv[1]).write_text('\n'.join(out) + '\n', encoding='utf-8')
print(out[-1])
