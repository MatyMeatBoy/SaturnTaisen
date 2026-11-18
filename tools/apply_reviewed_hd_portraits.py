"""Apply reviewed portrait bindings to a new private matcher workspace."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

import hd_matching as matching

ROOT = Path(__file__).resolve().parents[1]
PARTS = ['base', 'eyes', 'mouth']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def apply_reviews(project, workspace, reviewed):
    if project['schema'] != 1 or project['kind'] != 'sakura-narrative-portraits' or reviewed['schema'] != 1:
        raise ValueError('Esquema de proyecto o revisión no admitido')
    expected = reviewed['source']
    source = project['source']
    if any(source[key] != expected[key] for key in ('bytes', 'sha256', 'fnv64')):
        raise ValueError('KAO.SPR no coincide con el origen revisado')
    archive = Path(source['path'])
    if archive.stat().st_size != expected['bytes'] or matching.fingerprint(archive) != expected['sha256']:
        raise ValueError('KAO.SPR no coincide con el origen revisado')

    result = deepcopy(project)
    candidates = {candidate['index']: candidate for candidate in result['candidates']}
    rows = {row['id']: row for row in result['rows']}
    if len(rows) != len(result['rows']) or len(candidates) != len(result['candidates']):
        raise ValueError('Identidades duplicadas en el proyecto')
    matches = reviewed['matches']
    if not matches or len({match['id'] for match in matches}) != len(matches):
        raise ValueError('Revisión vacía o con identidades duplicadas')
    for match in matches:
        identity, pc_index = match['id'], match['pc_index']
        if not re.fullmatch('[0-9a-f]{4}', identity) or type(pc_index) is not int:
            raise ValueError('Identidad revisada no admitida')
        if identity not in rows or pc_index not in candidates or match['parts'] != PARTS:
            raise ValueError(f'{identity}: falta identidad, candidato o región aprobada')
        row, candidate = rows[identity], candidates[pc_index]
        if row['status'] == 'rejected' or (
            row['status'] in ('accepted', 'auto')
            and any(row[field] != approved for field, approved in
                    (('selected', pc_index), ('dx', match['dx']), ('dy', match['dy'])))
        ):
            raise ValueError(f'{identity}: conflicto con una revisión del proyecto')
        native_file = matching.workspace_file(workspace, row['raw'])
        if native_file.stat().st_size != 3200:
            raise ValueError(f'{identity}: tamaño de atlas Saturn no admitido')
        native = native_file.read_bytes()
        if row['raw_sha256'] != match['native_raw_sha256'] or sha(native) != match['native_raw_sha256']:
            raise ValueError(f'{identity}: atlas Saturn distinto de la identidad revisada')
        pc_file = matching.workspace_file(workspace, candidate['path'])
        if matching.fingerprint(pc_file) != candidate['sha256']:
            raise ValueError(f'{identity}: PNG del candidato PC modificado')
        image = matching.load_image(pc_file)
        if image.size != (80, 160) or sha(image.tobytes()) != match['pc_rgba_sha256']:
            raise ValueError(f'{identity}: píxeles del candidato PC distintos de la revisión')
        for density in (1, 2):
            pixels = matching.prepare_variant(image, native, density, match['dx'], match['dy'])
            if sha(pixels.tobytes()) != match['variants_rgba_sha256'][str(density)]:
                raise ValueError(f'{identity}: la variante {density}× difiere de la revisión')
        row.update(status='accepted', selected=pc_index, dx=match['dx'], dy=match['dy'])
    return result


def write_reviewed_project(project_file, output_project, metadata, *, export=False):
    project_file = project_file.resolve()
    output_project = output_project.absolute()
    destination = output_project.parent
    if output_project.name != 'project.json' or destination.exists() or destination.is_symlink():
        raise ValueError('La salida debe ser project.json en un directorio nuevo')
    if project_file.stat().st_size > 4 * 1024 * 1024:
        raise ValueError('Proyecto demasiado grande')
    workspace = project_file.parent
    project = json.loads(project_file.read_text(encoding='utf-8'))
    approved = apply_reviews(project, workspace, metadata)
    inputs = {row[key] for row in approved['rows'] for key in ('path', 'raw')}
    inputs.update(candidate['path'] for candidate in approved['candidates'])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.reviewed-', dir=destination.parent) as directory:
        staging = Path(directory) / 'project'
        staging.mkdir()
        for relative in sorted(inputs):
            source = matching.workspace_file(workspace, relative)
            target = matching.workspace_file(staging, relative)
            if target == staging / 'project.json' or target.is_relative_to(staging / 'portrait-pack'):
                raise ValueError('Ruta de recurso incompatible con el proyecto de salida')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        # Validate the bytes that will be used from the copy.
        approved = apply_reviews(approved, staging, metadata)
        if export:
            approved['output'] = str(staging / 'portrait-pack')
            matching.export_pack(approved, staging)
        approved['output'] = str(destination / 'portrait-pack')
        matching.atomic_json(staging / 'project.json', approved)
        if destination.exists() or destination.is_symlink():
            raise ValueError('El directorio de salida ya existe')
        staging.rename(destination)
    return dict(portraits=sum(row['status'] in ('accepted', 'auto') for row in approved['rows']),
                approved_ids=[row['id'] for row in metadata['matches']], project=str(output_project))


def main():
    owner = Path(os.environ.get('SAKURA_OWNER_ROOT', ROOT)).resolve()
    private = owner / 'local' / 'work'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=private / 'hd-matcher-project/project.json')
    parser.add_argument('--output-project', type=Path, required=True)
    parser.add_argument('--reviewed', type=Path, default=ROOT / 'config/hd-portrait-reviewed.json')
    parser.add_argument('--export', action='store_true', help='compile a new portrait pack in the copied workspace')
    args = parser.parse_args()
    try:
        if not args.output_project.resolve().is_relative_to(private.resolve()):
            raise ValueError('El proyecto de salida debe quedar en local/work del propietario')
        if args.reviewed.stat().st_size > 64 * 1024:
            raise ValueError('Registro de revisión demasiado grande')
        metadata = json.loads(args.reviewed.read_text(encoding='utf-8'))
        report = write_reviewed_project(args.project, args.output_project, metadata, export=args.export)
    except (KeyError, TypeError, OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
