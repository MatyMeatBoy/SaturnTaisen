"""Build an immutable, private GA36 RC2 overlay for an existing RC1 install."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import stat
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
RC1_SHA = '0b060875bddd1a8746666c072ba57b021d2cc61c6047ded3de9fc6b894d3f63d'
RUNTIME_SHA = '5cce1a6fcd0a695488de5e39e628516a91b442b8c718bf9872d64564e5a214a1'

def digest(path: Path) -> str:
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rc1', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if digest(args.rc1) != RC1_SHA:
        raise SystemExit('El ZIP RC1 no coincide con la referencia.')
    if digest(args.runtime) != RUNTIME_SHA:
        raise SystemExit('El runtime no coincide con el candidato probado.')
    target = args.output.resolve()
    temp = target.with_name(target.name + '.preparing')
    checksum = target.with_name(target.name + '.sha256')
    if target.exists() or temp.exists() or checksum.exists():
        raise SystemExit('El destino ya existe; no se sobrescribirá.')
    target.parent.mkdir(parents=True, exist_ok=True)
    prefix = ROOT / 'patches/platform'
    mapping = {'ports/saturntaisen/rc2/sakura': args.runtime}
    for name in ('ga36-rc2-launch.sh', 'ga36-rc2-case.sh', 'ga36-rc2-battery.sh'):
        mapping['ports/saturntaisen/' + name] = prefix / name
    for name in ('saturntaisen-ga36-rc2.puppy', 'saturntaisen-ga36-rc2-diagnostico.puppy'):
        mapping['.local/share/applications/' + name] = prefix / name
    mapping['ports/saturntaisen/rc2/ga36-aot-fast-dispatch.patch'] = prefix / 'ga36-aot-fast-dispatch.patch'
    readme = ("SATURNTAISEN GA36 RC2 — LABORATORIO\n\n"
              "Requiere RC1 para GA36 instalada con el disco 1 español. Extrae este overlay en HOME.\n"
              "Ports ofrece RC2 laboratorio y RC2 comparacion. Esta última ejecuta RC1/RC2/RC2/RC1\n"
              "sin pulsar botones; espera a que termine. Los resultados se guardan en\n"
              "ports/saturntaisen/user/rc2-bateria.* y pueden incluir copia privada de la partida.\n"
              "El juego RC2 usa perfil separado. No se ha demostrado mejora de FPS ni probado en placa.\n"
              "El port conserva ritmo Saturn; 80 FPS como margen de cálculo no están demostrados.\n").encode('utf-8')
    files = {name: digest(path) for name, path in mapping.items()}
    files['LEEME-RC2.txt'] = hashlib.sha256(readme).hexdigest()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    manifest = json.dumps({'schema': 1, 'revision': revision, 'rc1_zip_sha256': RC1_SHA,
                           'runtime_sha256': RUNTIME_SHA, 'files': files}, indent=2).encode() + b'\n'
    with ZipFile(temp, 'x', compression=ZIP_DEFLATED, compresslevel=4, allowZip64=True) as archive:
        for name in [*mapping, 'LEEME-RC2.txt', 'manifest.json']:
            info = ZipInfo(name)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | (0o755 if name.endswith(('/sakura', '.sh')) else 0o644)) << 16
            info.compress_type = ZIP_DEFLATED
            with archive.open(info, 'w', force_zip64=True) as entry:
                if name == 'manifest.json':
                    entry.write(manifest)
                elif name == 'LEEME-RC2.txt':
                    entry.write(readme)
                else:
                    with mapping[name].open('rb') as source:
                        shutil.copyfileobj(source, entry, 4 << 20)
    with ZipFile(temp) as archive:
        if set(archive.namelist()) != set(files) | {'manifest.json'}:
            raise RuntimeError('Inventario del ZIP inesperado.')
        for name, expected in files.items():
            with archive.open(name) as entry:
                if hashlib.file_digest(entry, 'sha256').hexdigest() != expected:
                    raise RuntimeError('CRC o SHA-256 incorrecto: ' + name)
        if archive.read('manifest.json') != manifest:
            raise RuntimeError('Manifiesto alterado.')
    temp.rename(target)
    checksum.write_text(f'{digest(target)}  {target.name}\n', encoding='ascii')
    print(f'{target} ({target.stat().st_size} bytes)')

if __name__ == '__main__':
    main()
