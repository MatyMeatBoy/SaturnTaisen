"""Render the public HD checklist from its reviewed, asset-free counters."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parents[1]
CATEGORY_IDS = ('portraits', 'movies', 'hud-menus', 'backgrounds', 'large-characters', 'scenes')
STAGES = {
    'inventory': 'Inventariado',
    'matched': 'Emparejado',
    'prepared': 'Preparado',
    'integrated': 'Integrado',
    'verified': 'Verificado en juego',
}
BEGIN = '<!-- BEGIN HD PROGRESS -->'
END = '<!-- END HD PROGRESS -->'


def integer(value):
    return type(value) is int and value >= 0


def single_line(value):
    return isinstance(value, str) and bool(value.strip()) and all(c not in value for c in '\r\n|')


def validate(data):
    if not isinstance(data, dict) or type(data.get('schema')) is not int or data['schema'] != 1:
        raise ValueError('Esquema de progreso HD desconocido')
    categories = data.get('categories')
    if not isinstance(categories, list) or len(categories) != len(CATEGORY_IDS):
        raise ValueError('Se requiere una fila por categoría HD')
    if not all(isinstance(row, dict) for row in categories) or tuple(row.get('id') for row in categories) != CATEGORY_IDS:
        raise ValueError('Categorías HD duplicadas, incompletas o desordenadas')
    for row in categories:
        name = row['id']
        if not all(single_line(row.get(field)) for field in ('label', 'scope', 'unit', 'next')):
            raise ValueError(f'{name}: descripción o alcance incompleto')
        previous = None
        for key in ('total', *STAGES):
            if key not in row:
                raise ValueError(f'{name}: falta {key}; usa null si se desconoce')
            value = row[key]
            if value is None:
                continue
            if not integer(value) or (key == 'total' and value == 0):
                raise ValueError(f'{name}: contador no válido para {key}')
            if previous is not None and value > previous:
                raise ValueError(f'{name}: {key} excede la etapa anterior')
            previous = value
        sources = row.get('sources')
        if not isinstance(sources, list) or not sources:
            raise ValueError(f'{name}: falta evidencia')
        for evidence in sources:
            if not isinstance(evidence, dict) or not single_line(evidence.get('path')):
                raise ValueError(f'{name}: referencia sin ruta pública')
            path = PurePosixPath(evidence['path'])
            if (path.is_absolute() or '..' in path.parts or '\\' in str(path)
                    or not path.parts or path.parts[0] not in ('docs', 'assets')
                    or not (ROOT / path).is_file()):
                raise ValueError(f'{name}: la referencia debe existir en docs o assets')
            if 'receipt_sha256' in evidence and not re.fullmatch('[0-9a-f]{64}', str(evidence['receipt_sha256'])):
                raise ValueError(f'{name}: SHA-256 no válido')
        pending = row.get('pending_ids')
        if pending is not None:
            if not isinstance(pending, list) or row['total'] is None or row['matched'] is None:
                raise ValueError(f'{name}: los rangos requieren total y emparejados')
            identifiers = set()
            for item in pending:
                if not isinstance(item, str) or not re.fullmatch('[0-9a-f]{4}(-[0-9a-f]{4})?', item):
                    raise ValueError(f'{name}: rango de ID no válido')
                first, _, last = item.partition('-')
                start, end = int(first, 16), int(last or first, 16)
                if end < start or any(i in identifiers for i in range(start, end + 1)):
                    raise ValueError(f'{name}: rangos invertidos o solapados')
                identifiers.update(range(start, end + 1))
            if len(identifiers) != row['total'] - row['matched']:
                raise ValueError(f'{name}: los ID pendientes no cuadran con el inventario')
        details = row.get('details', [])
        if not isinstance(details, list) or not all(single_line(detail) for detail in details):
            raise ValueError(f'{name}: detalles no válidos')


def format_count(count, total):
    if count is None:
        return 'Sin dato'
    if total is None:
        return str(count)
    # Truncation prevents an incomplete stage from rounding up to 100%.
    tenths = 1000 * count // total
    percent = str(tenths // 10)
    if tenths % 10:
        percent += f',{tenths % 10}'
    return f'{count}/{total} ({percent}%)'


def global_status(data):
    rows = data['categories']
    if any(row['total'] is None for row in rows):
        return 'Indeterminado'
    if all(all(row[stage] == row['total'] for stage in STAGES) for row in rows):
        return '100% verificado'
    return 'Verificación pendiente'


def table(data, detailed=False):
    columns = ('Área', 'Unidad', 'Inventariado', 'Emparejado', 'Preparado', 'Integrado', 'Verificado en juego') if detailed \
        else ('Área', 'Preparado', 'Verificado en juego')
    stages = tuple(STAGES) if detailed else ('prepared', 'verified')
    lines = ['| ' + ' | '.join(columns) + ' |', '| ' + ' | '.join('---' for _ in columns) + ' |']
    for row in data['categories']:
        prefix = [row['label'], row['unit']] if detailed else [row['label']]
        values = [format_count(row[stage], row['total']) for stage in stages]
        lines.append('| ' + ' | '.join(prefix + values) + ' |')
    return '\n'.join(lines)


def render_report(data):
    lines = [
        '# Progreso HD', '',
        f'**Objetivo global: 100% verificado. Estado: {global_status(data)}.**', '',
        'Los porcentajes corresponden al inventario definido para cada fila. '
        'Una celda «Sin dato» indica una medición pendiente y un cero indica una ausencia confirmada. '
        'Los recuentos de candidatos se detallan por separado.', '',
        table(data, detailed=True), '',
        '## Qué cuenta en cada etapa', '',
        '- **Inventariado**. Elementos nativos identificados dentro del alcance declarado.',
        '- **Emparejado**. Correspondencia aprobada del recurso y sus variantes necesarias.',
        '- **Preparado**. Sustitución empacada y validada con el formato del runtime.',
        '- **Integrado**. Sustitución conectada a la ruta de ejecución correspondiente.',
        '- **Verificado en juego**. Elementos distintos validados en capturas o reproducciones trazables.', '',
        'El objetivo global se alcanza cuando cada categoría tiene un total confirmado y todas '
        'sus etapas cubren ese total. Las unidades se evalúan por categoría, sin promediarlas.', '',
        '## Alcance y pendientes', '',
    ]
    for row in data['categories']:
        lines.extend((f"### {row['label']}", '', row['scope'], ''))
        lines.extend(f'- {detail}' for detail in row.get('details', []))
        lines.extend((f"- **Siguiente paso**. {row['next']}", ''))
        if 'pending_ids' in row:
            lines.extend(('Rangos de ID Saturn pendientes en hexadecimal', '',
                          ' '.join(f'`{item}`' for item in row['pending_ids']), ''))
        for source in row['sources']:
            path = PurePosixPath(source['path'])
            relative = path.relative_to('docs') if path.parts[0] == 'docs' else PurePosixPath('..') / path
            receipt = f" SHA-256 del recibo local `{source['receipt_sha256']}`." if 'receipt_sha256' in source else ''
            lines.append(f'- [{path.name}]({relative}).{receipt}')
        lines.append('')
    lines.extend((
        '## Actualizar el registro', '',
        'Añade el resultado revisado a `config/hd-progress.json`. Registra la unidad y el alcance del total, '
        'la etapa comprobada y la evidencia pública correspondiente. Usa `null` si falta el inventario o '
        'el recuento, y cuenta cada identidad una vez aunque aparezca en varios discos o escenas. Una '
        'coincidencia por nombre, la extracción y la decodificación por sí solas cuentan como candidatos. '
        'Al aprobar un retrato, actualiza el número de emparejamientos y sus rangos pendientes. '
        'Conserva imágenes, vídeos, partidas, guiones y rutas locales de propietario fuera del registro.', '',
        '```powershell',
        'python tools/build_hd_progress.py',
        'python tools/build_hd_progress.py --check',
        'python -m unittest discover -s tests -p test_hd_progress.py',
        '```', '',
    ))
    return '\n'.join(lines)


def replace_readme(readme, data):
    if readme.count(BEGIN) != 1 or readme.count(END) != 1 or readme.index(BEGIN) >= readme.index(END):
        raise ValueError('README debe contener exactamente un bloque HD PROGRESS')
    summary = '\n'.join((
        BEGIN, '', '## Progreso HD', '',
        f'**Objetivo global: 100% verificado. Estado: {global_status(data)}.**', '',
        table(data), '',
        '[Inventario, alcance de los porcentajes y pendientes](docs/HD_PROGRESS.md).', '', END,
    ))
    return readme[:readme.index(BEGIN)] + summary + readme[readme.index(END) + len(END):]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='check generated files without writing')
    args = parser.parse_args()
    try:
        source = ROOT / 'config/hd-progress.json'
        data = json.loads(source.read_text(encoding='utf-8'))
        validate(data)
        readme = ROOT / 'README.md'
        outputs = {
            ROOT / 'docs/HD_PROGRESS.md': render_report(data),
            readme: replace_readme(readme.read_text(encoding='utf-8'), data),
        }
        stale = []
        for path, expected in outputs.items():
            if not path.is_file() or path.read_text(encoding='utf-8') != expected:
                if args.check:
                    stale.append(str(path.relative_to(ROOT)))
                else:
                    path.write_text(expected, encoding='utf-8', newline='\n')
        if stale:
            parser.exit(1, f"Regenera el progreso HD: {', '.join(stale)}\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
