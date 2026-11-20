"""Offline HD census (THD32): one denominator table per resource type.

Reads only files tracked in the repository (config/hd-chapter-coverage.json, the
tactical inventories, config/hd-progress.json, docs/research/pc-asset-census.md,
docs/research/kabe-backgrounds.json). No disc, no PC dump, no runtime.

Counting rule: every PC donor file counts once, however many Saturn keys, discs
or chapters use it; exact-duplicate PC files (scene_file_duplicate_groups) count
once as a group. A donor takes the best status among its rows
(hd > wired-unverified > paired-not-wired > unsupported-size > excluded), so a
donor that is `hd` for one key and still pending for another is reported as
`hd` and listed again as `partial`.

    python tools/hd_census.py            # print the markdown table
    python tools/hd_census.py --json     # machine readable
    python tools/hd_census.py --write    # refresh the block in docs/research/hd-census.md
    python tools/hd_census.py --check    # fail if that block is stale
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = 'docs/research/hd-census.md'
BEGIN = '<!-- BEGIN HD CENSUS -->'
END = '<!-- END HD CENSUS -->'
PRECEDENCE = ('hd', 'wired-unverified', 'paired-not-wired', 'unsupported-size', 'excluded')
SCENE_FOLDERS = (
    ('scene-bg', 'Fondos de escena (BG)', 'SAKURA1/BG'),
    ('scene-bbg', 'Fondos EVE/BBG (batalla y evento)', 'SAKURA2/BG'),
    ('scene-event', 'EVENT (SAKURA2/EVENT)', 'SAKURA2/EVENT'),
    ('scene-cg', 'CG (SAKURA3/CG)', 'SAKURA3/CG'),
    ('scene-ending', 'Finales (SAKURA1/ENDING)', 'SAKURA1/ENDING'),
    ('scene-ic', 'IC / eyecatch (ICATCH)', 'SAKURA1/ICATCH'),
    ('scene-title', 'TITLE (tarjetas de episodio PC)', 'SAKURA1/TITLE'),
)


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def folder_census(text):
    """{'SAKURA1/BG': 716, ...} from the SPR table of pc-asset-census.md (`A + B` rows are split in file order)."""
    out = {}
    for line in text.splitlines():
        cells = [c.strip().strip('`') for c in line.strip().strip('|').split('|')]
        if len(cells) >= 2 and re.fullmatch(r'SAKURA\d/[A-Z]+', cells[0].split(',')[0].strip()) and re.fullmatch(r'\d+(,\d{3})*', cells[1].split('+')[0].strip()):
            names = [n.strip() for n in cells[0].split(',')]
            counts = [int(n.strip().replace(',', '')) for n in cells[1].split('+')]
            if len(names) > 1 and len(counts) == len(names):
                names = [names[0]] + [n if '/' in n else names[0].split('/')[0] + '/' + n for n in names[1:]]
                out.update(zip(names, counts))
            elif len(names) == 1:
                out[names[0]] = counts[0]
    return out


def groups_of(register):
    return [(c['chapter'], c['resources']) for c in register['chapters']], register['unassigned']


def all_rows(register, kind):
    chapters, unassigned = groups_of(register)
    for key, row in unassigned.get(kind, {}).items():
        yield 'unassigned', key, row
    for chapter, resources in chapters:
        for key, row in resources.get(kind, {}).items():
            yield chapter, key, row


def folder_of(path):
    return '/'.join(path.split('/')[:2])


def excluded_bucket(reason):
    low = (reason or '').lower()
    if 'cut-out' in low or 'blank' in low:
        return 'recorte sobre color clave o imagen en blanco (diseño)'
    if 'japanese lettering' in low:
        return 'rótulo japonés incrustado (tarjetas: capas locales)'
    if 'does not follow' in low:
        return 'composición PC no sigue la cámara nativa'
    if 'portrait atlas' in low:
        return 'contado en retratos'
    if 'empty atlas' in low:
        return 'atlas vacío'
    if 'native transition' in low:
        return 'transición nativa corta sin clip PC'
    return 'otro'


def blocked_bucket(status, reason):
    low = (reason or '').lower()
    if status == 'unsupported-size':
        return 'tamaño no soportado (T105c)'
    if 'witness' in low or 'no saved state' in low or 'disc 2' in low:
        return 'falta de testigo'
    if any(w in low for w in ('fingerprint', 'sampler', 'assembler')):
        return 'falta conexión en el runtime'
    if any(w in low for w in ('offset', 'omits', 'places')):
        return 'composición PC distinta (conservar nativo salvo testigo)'
    return 'otro'


def best_status(statuses):
    for status in PRECEDENCE:
        if status in statuses:
            return status
    return 'unknown'


def collapse_map(register):
    """member path -> canonical path of its exact-duplicate group."""
    mapping = {}
    for group in register.get('scene_file_duplicate_groups', []):
        rep = sorted(group)[0]
        for member in group:
            mapping[member] = rep
    return mapping


def new_row(rid, label, unit, source, manual=False):
    return {'id': rid, 'label': label, 'unit': unit, 'source': source, 'manual': manual,
            'candidates': 0, 'excluded': 0, 'excluded_reasons': {}, 'goal': 0, 'hd': 0,
            'wired_unverified': 0, 'blocked': 0, 'blocked_reasons': {}, 'unmatched': 0,
            'verified': 0, 'partial': 0, 'note': ''}


def finish(row):
    row['goal'] = row['candidates'] - row['excluded']
    row['unmatched'] = row['goal'] - row['hd'] - row['wired_unverified'] - row['blocked']
    return row


def scene_rows(register, census):
    canon = collapse_map(register)
    donors = defaultdict(lambda: {'status': set(), 'verified': False, 'reasons': {}})
    unpaired_keys = set()
    for _, key, row in all_rows(register, 'scene-pictures'):
        pc = row.get('pc')
        if not pc:
            if row['status'] == 'unpaired':
                unpaired_keys.add(key.partition(':')[2])
            continue
        identity = canon.get(pc, pc)
        if row.get('pc_identity', identity) != identity:
            raise ValueError(f'Invalid exact duplicate identity for {pc}')
        donor = donors[identity]
        donor['status'].add(row['status'])
        donor['reasons'][row['status']] = row.get('reason', '')
        if row['status'] == 'hd' and row.get('verified_in_game') is True:
            donor['verified'] = True
    reduction = Counter()
    for group in register.get('scene_file_duplicate_groups', []):
        for member in sorted(group)[1:]:
            reduction[folder_of(member)] += 1
    rows = []
    for rid, label, folder in SCENE_FOLDERS:
        row = new_row(rid, label, 'archivos SPR PC distintos (duplicados exactos = 1)',
                      'config/hd-chapter-coverage.json + docs/research/pc-asset-census.md')
        row['candidates'] = census[folder] - reduction[folder]
        row['raw_files'] = census[folder]
        row['duplicate_members'] = reduction[folder]
        seen = 0
        for path, donor in donors.items():
            if folder_of(path) != folder:
                continue
            seen += 1
            status = best_status(donor['status'])
            if status == 'hd':
                row['hd'] += 1
                row['verified'] += donor['verified']
                if donor['status'] & {'wired-unverified', 'paired-not-wired', 'unsupported-size'}:
                    row['partial'] += 1
            elif status == 'wired-unverified':
                row['wired_unverified'] += 1
            elif status in ('paired-not-wired', 'unsupported-size'):
                row['blocked'] += 1
                bucket = blocked_bucket(status, donor['reasons'].get(status))
                row['blocked_reasons'][bucket] = row['blocked_reasons'].get(bucket, 0) + 1
            elif status == 'excluded':
                row['excluded'] += 1
                bucket = excluded_bucket(donor['reasons'].get('excluded'))
                row['excluded_reasons'][bucket] = row['excluded_reasons'].get(bucket, 0) + 1
        row['donors_in_register'] = seen
        row['without_register_row'] = row['candidates'] - seen
        rows.append(finish(row))
    scene_goal = sum(r['goal'] for r in rows)
    rows[0]['note'] = (f'{len(unpaired_keys)} claves Saturn distintas `unpaired` (sin donante PC) no entran en el '
                       f'denominador de archivos PC; total escena sin excluidos: {scene_goal}.')
    return rows, scene_goal, unpaired_keys


def mixed_scene_donors(register):
    canon = collapse_map(register)
    status = defaultdict(set)
    for _, _, row in all_rows(register, 'scene-pictures'):
        if row.get('pc'):
            status[canon.get(row['pc'], row['pc'])].add(row['status'])
    return {pc: s for pc, s in status.items() if len(s) > 1}


def hud_rows(register):
    census = register['hud_census']
    system = new_row('hud-system', 'HUD y menús (SYSTEM sin KAO)', 'imágenes PC distintas (archivo, subimagen)',
                     'config/hd-chapter-coverage.json (menus-hud, hud_census)')
    item = new_row('hud-item', 'ITEM (tarjetas de objeto)', 'imágenes PC distintas (archivo, subimagen)',
                   'config/hd-chapter-coverage.json (menus-hud, hud_census)')
    kao = 0
    hd = {'SYSTEM': set(), 'ITEM': set()}
    ver = {'SYSTEM': set(), 'ITEM': set()}
    files = {'ITEM': set()}
    saturn_unknown = set()
    saturn_unpaired = set()
    for _, key, row in all_rows(register, 'menus-hud'):
        if row['status'] == 'excluded':
            kao += row.get('images', 0)
        elif row['status'] == 'hd' and row.get('pc') and 'pc_image_index' in row:
            fam = 'ITEM' if '/ITEM/' in row['pc'] else 'SYSTEM'
            hd[fam].add((row['pc'], row['pc_image_index']))
            if row.get('verified_in_game') is True:
                ver[fam].add((row['pc'], row['pc_image_index']))
            if fam == 'ITEM':
                files['ITEM'].add(row['pc'])
        elif row['status'] == 'unknown':
            saturn_unknown.add(key.partition(':')[2])
        elif row['status'] == 'unpaired':
            saturn_unpaired.add(key.partition(':')[2])
    system['candidates'] = census['system_images']
    system['excluded'] = kao
    system['excluded_reasons'] = {'KAO: atlas de retratos, contado en retratos': kao}
    item['candidates'] = census['item_images']
    for row, fam in ((system, 'SYSTEM'), (item, 'ITEM')):
        row['hd'] = len(hd[fam])
        row['verified'] = len(ver[fam])
        finish(row)
    system['note'] = f'{len(saturn_unknown)} claves Saturn de menu sin pareja establecida (`unknown`).'
    item['note'] = (f'{len(files["ITEM"])} archivos ITEM con imagen dibujada; {len(saturn_unpaired)} claves Saturn de objeto '
                    '`unpaired`. Los 57 SPR de ITEM también están en el 542 táctico: aquí se cuentan una vez.')
    return [system, item]


def tactical_rows(register, census):
    maps = new_row('tactical-ground', 'Mapas tácticos: suelos', 'archivos SPR PC de suelo emparejados',
                   'config/hd-chapter-coverage.json (tactical-maps) + hd-tactical-map-pairs.json')
    pcs, hd, ver, reasons = {}, set(), set(), Counter()
    for _, key, row in all_rows(register, 'tactical-maps'):
        pcs.setdefault(row['pc'], set()).add(row['status'])
        if row['status'] == 'hd':
            hd.add(row['pc'])
            if row.get('verified_in_game') is True:
                ver.add(row['pc'])
        else:
            reasons[blocked_bucket(row['status'], row.get('reason'))] += 1
    pending = {pc for pc, s in pcs.items() if pc not in hd}
    maps['candidates'] = len(pcs)
    maps['hd'] = len(hd)
    maps['verified'] = len(ver)
    maps['blocked'] = len(pending)
    maps['blocked_reasons'] = dict(Counter(
        blocked_bucket('paired-not-wired', next((r.get('reason') for _, _, r in all_rows(register, 'tactical-maps') if r['pc'] == pc), ''))
        for pc in pending))
    map_pairs = load('config/hd-tactical-map-pairs.json')
    spr_maps = census.get('SAKURA2/MAP', 0) + census.get('SAKURA1/MAP', 0)
    maps['note'] = (f'{spr_maps} SPR de MAP en el volcado PC; {len(pcs)} son suelos emparejados con las {len(map_pairs["maps"])} '
                    f'MAP BIN Saturn. Los otros {spr_maps - len(pcs)} (teselas, objetos, fotogramas) no tienen función asignada: '
                    'no son denominador hasta emparejarse.')
    finish(maps)
    inv = load('config/hd-tactical-unit-inventory.json')
    units = new_row('tactical-units', 'Unidades tácticas (UNIT)', 'archivos SPR PC UNIT',
                    'config/hd-tactical-unit-inventory.json')
    units['candidates'] = inv['summary']['pc_files']
    units['note'] = (f'{inv["summary"]["saturn_files"]} bancos UNIT Saturn ({inv["summary"]["saturn_distinct"]} conjuntos distintos): '
                     f'emparejados {inv["summary"]["paired"]}, ambiguos {inv["summary"]["ambiguous"]}. Ningún archivo con estado explicito.')
    finish(units)
    return [maps, units]


def body_rows(register, census):
    row = new_row('nc-bodies', 'Cuerpos NC (personajes grandes)', 'archivos NC Saturn distintos (ambos discos = 1)',
                  'config/hd-chapter-coverage.json (bodies)')
    native, verified = {}, set()
    pc_files = set()
    for _, key, r in all_rows(register, 'bodies'):
        path = key.partition(':')[2]
        native[path] = best_status({native.get(path, 'unknown'), r['status']}) if path in native else r['status']
        if r['status'] == 'hd' and r.get('verified_in_game') is True:
            verified.add(path)
        if r.get('pc'):
            pc_files.add(r['pc'])
    row['candidates'] = len(native)
    row['hd'] = sum(1 for s in native.values() if s == 'hd')
    row['verified'] = len(verified)
    alternates = register.get('pc_body_alternates', {})
    if len(alternates) != census.get('SAKURA3/NC', 0):
        raise ValueError('El inventario de alternos NC no coincide con el censo PC')
    if (len(set(alternates.values())) != len(alternates)
            or any(path not in native or f'SAKURA1/NC/{Path(path).stem}.SPR' not in pc_files for path in alternates)):
        raise ValueError('Un alterno NC carece de identidad Saturn o donante base registrado')
    row['note'] = (f'{len(pc_files)} donantes PC SAKURA1/NC y {len(alternates)} alternos SAKURA3 del mismo conjunto Saturn. '
                   f'Filas del registro por disco/capitulo: {sum(1 for _ in all_rows(register, "bodies"))}.')
    return [finish(row)]


def portrait_rows(register, progress):
    row = new_row('portraits', 'Retratos (identidades Saturn)', 'identidades Saturn distintas', 'config/hd-chapter-coverage.json (portraits)')
    ids = {}
    verified = set()
    for _, key, r in all_rows(register, 'portraits'):
        if re.fullmatch('[0-9a-f]{4}', key):
            ids[key] = r['status']
            if r.get('verified_in_game') is True:
                verified.add(key)
    row['candidates'] = next(c['total'] for c in progress['categories'] if c['id'] == 'portraits')
    row['hd'] = sum(1 for s in ids.values() if s == 'hd')
    row['verified'] = len(verified)
    row['note'] = (f'{len(ids)} identidades con fila en el registro; el denominador es el de hd-progress.json. '
                   '394 caras PC en KAO se cuentan aquí y no en HUD.')
    return [finish(row)]


def film_rows(register):
    row = new_row('film', 'Vídeos (FILM)', 'clips PC distintos (completo o por tramos)', 'config/hd-chapter-coverage.json (film)')
    clips, native_only, verified = {}, set(), set()
    for _, key, r in all_rows(register, 'film'):
        if r.get('pc') and r['status'] in ('hd', 'bounded'):
            clips[r['pc']] = r['status']
            if r.get('verified_in_game') is True:
                verified.add(r['pc'])
        elif r['status'] == 'excluded':
            native_only.add(key)
    row['candidates'] = len(clips) + len(native_only)
    row['excluded'] = len(native_only)
    row['excluded_reasons'] = {excluded_bucket('short native transition'): len(native_only)}
    row['hd'] = len(clips)
    row['verified'] = len(verified)
    row['note'] = (f'{sum(1 for _ in all_rows(register, "film"))} apariciones FILM (disco, FAD) -> {len(clips)} clips PC '
                   f'({sum(1 for s in clips.values() if s == "bounded")} por tramos). Verificado solo donde la fila lo declara.')
    return [finish(row)]


def kabe_row(progress):
    cat = next(c for c in progress['categories'] if c['id'] == 'backgrounds')
    row = new_row('kabe', 'Fondos decorativos KABE', 'temas', 'config/hd-progress.json (backgrounds)')
    row['candidates'] = cat['total']
    row['hd'] = cat['integrated']
    row['note'] = 'Sin fila por tema en el registro; el recuento viene de hd-progress.json. 25 WALL PC, 19 temas usados. Verificación: THD25.'
    return [finish(row)]


def episode_card_row():
    """Manual: docs/research/thd23-episode-cards.md witness table (no register rows exist)."""
    row = new_row('episode-cards', 'Tarjetas de episodio', 'episodios', 'docs/research/thd23-episode-cards.md (manual)', manual=True)
    row['candidates'] = 10
    row['hd'] = 1
    row['wired_unverified'] = 9
    row['verified'] = 1
    row['note'] = 'Marco y rótulo español de los 10 episodios en el paquete; solo el episodio 1 tiene testigo de dibujo. Los 10 TITLE PC se excluyen (letras japonesas).'
    return [finish(row)]


def evidence_gaps(register):
    keys = ('evidence', 'runtime_evidence', 'pairing_evidence', 'fixture_evidence', 'decision_evidence',
            'runtime_table', 'cold_run_frame', 'native_reason', 'native_records', 'runtime_patch', 'draw')
    out = {}
    for kind in ('scene-pictures', 'bodies', 'portraits', 'film', 'menus-hud', 'tactical-maps'):
        hd = [r for _, _, r in all_rows(register, kind) if r['status'] == 'hd']
        out[kind] = {'hd_rows': len(hd), 'without_evidence': sum(1 for r in hd if not any(k in r for k in keys)),
                     'verified_rows': sum(1 for r in hd if r.get('verified_in_game') is True)}
    return out


def build():
    register = load('config/hd-chapter-coverage.json')
    progress = load('config/hd-progress.json')
    census = folder_census((ROOT / 'docs/research/pc-asset-census.md').read_text(encoding='utf-8'))
    scenes, scene_goal, unpaired = scene_rows(register, census)
    rows = scenes + tactical_rows(register, census) + hud_rows(register) + body_rows(register, census) \
        + portrait_rows(register, progress) + film_rows(register) + kabe_row(progress) + episode_card_row()
    mixed = mixed_scene_donors(register)
    dup_members = {r['pc'] for _, _, r in all_rows(register, 'scene-pictures') if r.get('pc')}
    double = sum(max(0, len(set(g) & dup_members) - 1) for g in register.get('scene_file_duplicate_groups', []))
    return {
        'rows': rows,
        'scene_goal': scene_goal,
        'scene_candidates': sum(r['candidates'] for r in rows if r['id'].startswith('scene-')),
        'unpaired_scene_keys': len(unpaired),
        'mixed_donors': {'total': len(mixed),
                         'hd_and_excluded': sum(1 for s in mixed.values() if s == {'hd', 'excluded'}),
                         'hd_and_pending': sum(1 for s in mixed.values() if 'hd' in s and s & {'paired-not-wired', 'unsupported-size', 'wired-unverified'})},
        'duplicate_donors_listed_twice': double,
        'evidence_gaps': evidence_gaps(register),
    }


def pct(num, den):
    if not den:
        return '-'
    tenths = 1000 * num // den
    return f'{tenths // 10},{tenths % 10}%'


def reasons(text):
    return '; '.join(f'{k} ({v})' for k, v in sorted(text.items())) or '-'


def render_table(report):
    head = ('| Tipo | Denominador (candidatos) | Excluidos por diseño | Meta | hd | wired-unverified | Bloqueados | Sin pareja / sin conectar '
            '| % integrado | Verificado | % verificado |')
    lines = [head, '| ' + ' | '.join('---' for _ in head.strip('|').split('|')) + ' |']
    for r in report['rows']:
        lines.append(f"| {r['label']}{' (manual)' if r['manual'] else ''} | {r['candidates']} | {r['excluded']} | {r['goal']} | {r['hd']} | "
                     f"{r['wired_unverified']} | {r['blocked']} | {r['unmatched']} | {pct(r['hd'], r['goal'])} | {r['verified']} | {pct(r['verified'], r['goal'])} |")
    lines += ['', '| Tipo | Motivos de exclusion por diseño | Motivos de bloqueo | Nota |', '| --- | --- | --- | --- |']
    for r in report['rows']:
        lines.append(f"| {r['label']} | {reasons(r['excluded_reasons'])} | {reasons(r['blocked_reasons'])} | {(r['note'] + ' ') if r['note'] else ''}{('Parcial (hd con otra clave pendiente): ' + str(r['partial']) + '.') if r['partial'] else ''}{'-' if not r['note'] and not r['partial'] else ''} |")
    return '\n'.join(lines)


def render_block(report):
    scene = [r for r in report['rows'] if r['id'].startswith('scene-')]
    totals = {k: sum(r[k] for r in scene) for k in ('candidates', 'excluded', 'goal', 'hd', 'verified', 'blocked', 'wired_unverified', 'unmatched', 'partial')}
    extra = [
        '', f"Escena (7 carpetas SPR): candidatos {totals['candidates']}, excluidos {totals['excluded']}, meta {totals['goal']}, "
            f"hd {totals['hd']} ({pct(totals['hd'], totals['goal'])}), verificados {totals['verified']} ({pct(totals['verified'], totals['goal'])}), "
            f"bloqueados {totals['blocked']}, sin pareja o sin fila {totals['unmatched']}; de los hd, {totals['partial']} aún tienen otra clave pendiente (parcial).",
        '', 'Donantes de escena que cuentan en dos estados: ' +
            f"{report['mixed_donors']['hd_and_excluded']} hd y excluido a la vez, {report['mixed_donors']['hd_and_pending']} hd con otra clave pendiente. "
            f"Rutas físicas extra de familias exactas presentes en el registro: {report['duplicate_donors_listed_twice']}. "
            "Comparten una identidad de conteo y conservan sus rutas del runtime.",
        '', 'Filas `hd` sin ninguna referencia de evidencia por fila (son `hd` por la tabla del runtime, no por testigo): ' +
            ', '.join(f"{k} {v['without_evidence']}/{v['hd_rows']}" for k, v in report['evidence_gaps'].items()) + '.',
    ]
    return '\n'.join([BEGIN, '', render_table(report)] + extra + ['', END])


def replace_block(text, block):
    if BEGIN not in text or END not in text:
        raise ValueError(f'{DOC} no tiene los marcadores {BEGIN} y {END}')
    head, _, rest = text.partition(BEGIN)
    _, _, tail = rest.partition(END)
    return head + block + tail


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    report = build()
    if args.json:
        print(json.dumps(report, indent=1, sort_keys=True))
        return 0
    block = render_block(report)
    if args.write or args.check:
        path = ROOT / DOC
        expected = replace_block(path.read_text(encoding='utf-8'), block)
        if args.check:
            if path.read_text(encoding='utf-8') != expected:
                print(f'{DOC} desactualizado: ejecuta python tools/hd_census.py --write', file=sys.stderr)
                return 1
            return 0
        path.write_text(expected, encoding='utf-8', newline='\n')
        return 0
    print(block)
    return 0


if __name__ == '__main__':
    sys.exit(main())
