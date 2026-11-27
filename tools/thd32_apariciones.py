"""THD32 appearance census. Usage: python -I tools/thd32_apariciones.py <folder with thd32-tactical-542.csv (from thd32_audit.py), output also goes there> <PC tree>"""
import csv, re, sys, os, collections
S = sys.argv[1]; P = sys.argv[2]
rows = list(csv.DictReader(open(os.path.join(S, 'thd32-tactical-542.csv'), encoding='utf-8')))
assert len(rows) == 542
O = 'observado'; I = 'inferido (numeracion)'; U = 'desconocido'
NOLOAD = 'ningun estado lo carga (tactical-ground-probe.md)'
M = {
 '01': ('1 y 2', '1 (disco 1); copia disco 2 sin uso atribuido', O, 'hd-chapter-coverage.json cap1; stage01-pc-ground.md'),
 '02': ('1', '2', O, 'hd-chapter-coverage.json cap2; hd-chapter-2.md'),
 '03': ('1', '3 (combate 1, Tsukiji)', O, 'tactical-ground-table.md#map03-at-1440p (Episode 3 disc 1); el JSON lo deja en unassigned'),
 '04': ('1', '3 (combate 2)', O, 'hd-chapter-coverage.json cap3; tactical-ground-probe.md'),
 '05': ('1', '3 (combate 3)', O, 'hd-chapter-coverage.json cap3; map05-pc-ground.md'),
 '06': ('1', '4', O, 'hd-chapter-coverage.json cap4; map06-pc-ground.md'),
 '07': ('1', '5 candidato', I, 'tactical-ground-table.md#map07-at-1440p (disco 1, EVT07; capitulo no escrito); hueco entre cap4 y cap6'),
 '08': ('1', '6', O, 'tactical-ground-table.md#map08-at-1440p (episode 6 battle save)'),
 '09': ('1', '7', O, 'tactical-ground-table.md#map09-at-1440p (Episode 7)'),
 '10': ('1', '7', O, 'hd-chapter-coverage.json cap7; tactical-pairing.md#live-map10-and-map19-ground-review'),
 '11': ('1', '7 candidato (sigue a MAP10)', I, 'solo disco y numeracion; ' + NOLOAD),
 '12': ('2', '8', O, 'hd-chapter-coverage.json cap8; tactical-pairing.md#live-map12-pc-ground'),
 '13': ('2', '8', O, 'hd-chapter-coverage.json cap8; tactical-pairing.md#live-map13-pc-ground'),
 '14': ('2', '8 (combate 2)', O, 'hd-chapter-coverage.json cap8; tactical-pairing.md#live-map14-pc-ground'),
 '15': ('2', '9', O, 'hd-chapter-coverage.json cap9; tactical-pairing.md#live-map15-ground-review'),
 '16': ('2', '9', O, 'hd-chapter-coverage.json cap9; tactical-pairing.md#live-map16-pc-ground'),
 '17': ('2', '9 o 10 candidato', I, 'solo numeracion (entre MAP16 cap9 y MAP19 cap10); ' + NOLOAD),
 '18': ('2', '9 o 10 candidato', I, 'solo numeracion (entre MAP16 cap9 y MAP19 cap10); ' + NOLOAD),
 '19': ('2', '10 (combate 2 y final)', O, 'hd-chapter-coverage.json cap10; tactical-ground-probe.md'),
 '20': ('2', '10 candidato', I, 'solo numeracion (sigue a MAP19); ' + NOLOAD),
 '21': ('1', '4', O, 'hd-chapter-coverage.json cap4; stage21-pc-ground.md'),
 '22': ('1', 'desconocido (disco 1, cap 1-7)', U, 'numero fuera de secuencia, como MAP21; ' + NOLOAD),
 '23': ('2', '10 candidato (ruta Episode 10 tras MAP19)', I, 'tactical-ground-table.md#disc-2-route-to-map23; camara jugable no alcanzada'),
 '24': ('2', 'desconocido (disco 2, cap 8-10)', U, 'solo disco; ' + NOLOAD),
 '25': ('2', 'desconocido (disco 2, cap 8-10)', U, 'solo disco; ' + NOLOAD),
 '26': ('2', 'desconocido (disco 2, cap 8-10)', U, 'solo disco; ' + NOLOAD),
 '27': ('ninguno (solo PC)', 'no aplica en Saturn', 'no aplica', 'tactical-pairing.md: MAP27 reutiliza MAP06 y no tiene BIN Saturn'),
}
ua = collections.defaultdict(set)
for ln in open(os.path.join(P, 'SAKURA2', 'UNITANM.TAB'), 'rb'):
    t = ln.decode('ascii', 'replace')
    m = re.match(r'^([A-Z][A-Z0-9_]*)\s+([A-Z_0-9]+)\s+(UNIT\\\S+?\.spr)', t, re.I)
    if m:
        ua['SAKURA2/' + m.group(3).replace('\\', '/').upper()].add((m.group(1), m.group(2)))
KOBU = {'OOGAMI', 'SAKURA', 'SUMIRE', 'MARIA', 'IRIS', 'KORAN', 'KANNA'}
out = []
for r in rows:
    pc = r['pc']; f = r['folder']
    d = dict(pc=pc, folder=f, role=r['role'], state=r['state'], map='', disco_saturn='', capitulos='', asociacion='', unit_ids='', evidencia='')
    if f == 'SAKURA2/MAP':
        n = re.search(r'/MAP(\d\d)/', pc).group(1); disc, cap, asoc, ev = M[n]
        d.update(map='MAP' + n, disco_saturn=disc, capitulos=cap, asociacion=asoc, evidencia=ev + '; carpeta PC MAP' + n)
        if r['state'] == 'excluido':
            d['asociacion'] += ' (pieza no cargada por el PC)'
    elif f == 'SAKURA1/MAP':
        d.update(map='mapa estrategico', disco_saturn='?', capitulos='desconocido', asociacion=U, evidencia='fuera del combate; sin TAB ni traza que lo ate a un capitulo')
    elif f == 'SAKURA1/ITEM':
        d.update(map='HUD/ITEM comun', disco_saturn='1 y 2', capitulos='todos los combates (HUD comun); no se censa por mapa', asociacion='no aplica (excluido, seccion ITEM)', evidencia='agent-thd32.md')
    else:
        ids = sorted(ua.get(pc.upper(), ())); uid = sorted({a for a, b in ids})
        d['unit_ids'] = ' '.join(f'{a}:{b}' for a, b in ids)
        d['map'] = 'grupo ' + pc.split('/')[2].upper()
        if not ids:
            d.update(capitulos='desconocido', asociacion='desconocido (no referenciado en UNITANM.TAB)', evidencia='UNITANM.TAB')
        elif all(u in KOBU for u in uid):
            d.update(capitulos='combates con ese piloto en Koubu; capitulos sin censar', asociacion='desconocido (unidad jugable)', evidencia='UNITANM.TAB')
        elif all(u[0] == 'G' and u[1:] in KOBU for u in uid):
            d.update(capitulos='combates con Shinbu; capitulos sin censar', asociacion='desconocido (unidad jugable Shinbu)', evidencia='UNITANM.TAB')
        else:
            d.update(capitulos='desconocido', asociacion=U, evidencia='UNITANM.TAB; el PC no trae lista ASCII de unidades por mapa (MAPnn.DAT y HENKANnn.DAT son binarios)')
    out.append(d)
w = csv.DictWriter(open(os.path.join(S, 'thd32-apariciones.csv'), 'w', newline='', encoding='utf-8'), fieldnames=list(out[0]))
w.writeheader(); w.writerows(out)
c = collections.Counter((d['folder'], d['asociacion']) for d in out)
for k, v in sorted(c.items()): print(k, v)
pm = collections.defaultdict(collections.Counter)
for d in out:
    if d['folder'] == 'SAKURA2/MAP': pm[d['map']][d['state']] += 1
for k in sorted(pm): print(k, M[k[3:]][1], '|', M[k[3:]][2], dict(pm[k]))
print(collections.Counter(d['map'] for d in out if d['folder'] == 'SAKURA2/UNIT'))
print('ids', collections.Counter(a.split(':')[0] for d in out if d['folder']=='SAKURA2/UNIT' for a in d['unit_ids'].split()))
