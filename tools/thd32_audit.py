"""THD32 audit of the 542 tactical SPR. Usage: python -I tools/thd32_audit.py <repo> <PC tree> <output folder>"""
"""THD32 offline audit: explicit state for each of the 542 PC tactical SPR files.

Read-only. Inputs: repo configs (register, tactical inventories, ground table) and
the extracted PC tree (file names + ASCII TAB files + sha256 only; no pixels).
Usage: python -I thd32_audit.py <repo> <pc_root> <out_dir>
"""
import csv, hashlib, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

repo, pc_root, out = (Path(a) for a in sys.argv[1:4])
load = lambda p: json.loads((repo / p).read_text(encoding='utf-8'))

reg = load('config/hd-chapter-coverage.json')
units = load('config/hd-tactical-unit-inventory.json')
items = load('config/hd-tactical-item-inventory.json')
ground_tab = load('config/hd-tactical-ground-table.json')
unit_pairs = load('config/hd-tactical-unit-pairs.json')


def reg_rows(kind):
    for k, r in reg['unassigned'].get(kind, {}).items():
        yield 'unassigned', k, r
    for c in reg['chapters']:
        for k, r in c['resources'].get(kind, {}).items():
            yield c['chapter'], k, r


# Register state per PC file (tactical-maps and menus-hud for ITEM).
def per_pc(kind, prefix):
    acc = defaultdict(list)
    for ch, key, r in reg_rows(kind):
        pc = r.get('pc') or ''
        if pc.startswith(prefix):
            acc[pc].append((key, r))
    return acc

ground_rows = per_pc('tactical-maps', 'SAKURA2/MAP/')
item_rows = per_pc('menus-hud', 'SAKURA1/ITEM/')
gt_status = {m['pc_ground']: m['status'] for m in ground_tab['maps']}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --- enumerate the 542 files from the PC tree ---
files = []
for folder in ('SAKURA2/MAP', 'SAKURA1/MAP', 'SAKURA2/UNIT', 'SAKURA1/ITEM'):
    base = pc_root / folder
    for p in sorted(base.rglob('*')):
        if p.is_file() and p.suffix.upper() == '.SPR':
            files.append(p.relative_to(pc_root).as_posix())
assert len(files) == 542, len(files)

# --- TAB roles (active lines only; '#' lines are commented out) ---
roles = defaultdict(set)          # upper path -> {role}
commented = defaultdict(set)
for tab in sorted((pc_root / 'SAKURA2/MAP').glob('*/*.TAB')):
    mapdir = tab.parent
    for raw in tab.read_bytes().decode('ascii', 'replace').splitlines():
        line = raw.strip()
        if not line:
            continue
        active = not line.startswith('#')
        body = line.lstrip('#').strip()
        m = re.match(r'([A-Za-z]+)\s*:\s*File\s*:\s*(.*)', body)
        if not m:
            continue
        role = m.group(1)
        for name in m.group(2).split():
            if not name.lower().endswith('.spr'):
                continue
            target = (mapdir / name.replace('\\', '/')).resolve()
            try:
                rel = target.relative_to(pc_root.resolve()).as_posix().upper()
            except ValueError:
                continue
            (roles if active else commented)[rel].add(role)

unit_by_pc = {u['pc']: u for u in units['pc_units']}
item_by_pc = {i['pc']: i for i in items['pc_items']}
leads = {l['pc'] for l in unit_pairs.get('ambiguous_leads', [])}

rows = []
for f in files:
    up = f.upper()
    folder = '/'.join(f.split('/')[:2])
    row = dict(pc=f, folder=folder, role='', state='', reason='', evidence='', sha256='')
    if folder == 'SAKURA1/ITEM':
        inv = item_by_pc[f]
        row['sha256'] = inv['sha256']
        regs = item_rows.get(f, [])
        hd = any(r.get('status') == 'hd' for _, r in regs)
        ver = any(r.get('status') == 'hd' and r.get('verified_in_game') is True for _, r in regs)
        sec = 'hd+verified' if ver else ('hd' if hd else 'sin fila')
        row.update(role='tarjeta/icono de objeto', state='excluido',
                   reason=f'seccion propia ITEM/HUD (estado alli: {sec}; inventario: {inv["status"]})',
                   evidence='config/hd-tactical-item-inventory.json; hd-chapter-coverage.json menus-hud')
    elif folder == 'SAKURA2/UNIT':
        u = unit_by_pc[f]
        row['sha256'] = u['sha256']
        row['role'] = 'unidad ' + u['group']
        lead = ' (pista ambigua en hd-tactical-unit-pairs.json)' if f in leads else ''
        row.update(state='pendiente', reason='sin pareja: banco UNITnn.BIN Saturn sin decodificador' + lead,
                   evidence='config/hd-tactical-unit-inventory.json')
    elif folder == 'SAKURA1/MAP':
        row['sha256'] = sha(pc_root / f)
        row.update(role='pantalla de mapa estrategico (TMAP/FUKA, fuera del combate)', state='pendiente',
                   reason='sin pareja; filas Saturn TMAP.BIN en menus-hud con estado unknown; sin seccion propia',
                   evidence='docs/research/pc-saturn-name-links.json')
    else:  # SAKURA2/MAP
        row['sha256'] = sha(pc_root / f)
        r_active, r_comm = sorted(roles.get(up, ())), sorted(commented.get(up, ()))
        regs = ground_rows.get(f, [])
        if regs:
            st = {r.get('status') for _, r in regs}
            ver = any(r.get('status') == 'hd' and r.get('verified_in_game') is True for _, r in regs)
            ev = sorted({r.get('runtime_evidence') or r.get('pairing_evidence') or r.get('evidence') or '' for _, r in regs} - {''})
            row['role'] = 'suelo registrado (' + '/'.join(r_active) + ')'
            row['evidence'] = '; '.join(ev)
            if 'hd' in st:
                row['state'] = 'verificado' if ver else 'integrado'
                row['reason'] = 'hd fuente 4' + ('' if ver else ', verified_in_game false/ausente')
            else:
                row['state'] = 'pendiente'
                g = gt_status.get(f, '?')
                why = next((r.get('reason') for _, r in regs if r.get('reason')), '')
                row['reason'] = f'bloqueado ({"/".join(sorted(st))}; tabla de suelos: {g}) ' + why[:120]
        elif r_active:
            row['role'] = '+'.join(r_active)
            row['state'] = 'pendiente'
            if 'Priority' in r_active:
                row['reason'] = 'capa de prioridad PC (mascara .PRI); sin pareja Saturn ni funcion en el runtime'
            elif 'AllMapImage' in r_active:
                row['reason'] = 'vista de mapa completo; sin pareja Saturn establecida'
            else:
                row['reason'] = 'capa animada/cielo/subsuelo secundaria; sin pareja Saturn'
            row['evidence'] = 'TAB PC activo'
        else:
            row['role'] = ('comentado: ' + '+'.join(r_comm)) if r_comm else 'sin referencia'
            row['state'] = 'excluido'
            row['reason'] = ('linea del TAB PC comentada: el PC no la carga' if r_comm
                             else 'ningun TAB PC lo referencia: el PC no lo carga')
            row['evidence'] = 'TAB PC'
    rows.append(row)

# duplicates by content
dup = Counter(r['sha256'] for r in rows)
for r in rows:
    r['dup_family'] = dup[r['sha256']] if dup[r['sha256']] > 1 else ''

out.mkdir(parents=True, exist_ok=True)
cols = ['pc', 'folder', 'role', 'state', 'reason', 'evidence', 'dup_family', 'sha256']
with open(out / 'thd32-tactical-542.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

summ = {'total': len(rows), 'by_state': Counter(r['state'] for r in rows),
        'by_folder_state': Counter(f"{r['folder']}|{r['state']}" for r in rows),
        'map_roles': Counter(f"{r['role']}|{r['state']}" for r in rows if r['folder'] == 'SAKURA2/MAP'),
        'unit_groups_top': Counter(r['role'].split('/')[0] for r in rows if r['folder'] == 'SAKURA2/UNIT'),
        'dup_files': sum(1 for r in rows if r['dup_family']),
        'dup_families': sum(1 for h, n in dup.items() if n > 1)}
print(json.dumps(summ, indent=1, ensure_ascii=False, default=dict))
