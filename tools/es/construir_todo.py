"""Build a Spanish disc (1 or 2) with every reviewed chapter and the Spanish menus.

  python -X utf8 tools/es/construir_todo.py --disc 1
  python -X utf8 tools/es/construir_todo.py --disc 2

1. volcar_todo.py --disc N: every dialogue table (and every battle table that has batches)
2. disc 1: menus_es.py builds the Spanish menu graphics (title, interlude, options, load/save, battle bars);
   disc 2: menus_disco2.py moves those patches onto disc 2's own SAKURA/LOGO.SH2 and redraws its WKL12-26 bars
(optional) --portadas: the Spanish episode cards and loading scroll replace TITLE1..10.BIN and LOAD.BIN on either disc
3. iso.py copies local/prepared/discN to local/prepared/discN-es with the tables in fixed slots

Inputs and outputs stay under SAKURA_OWNER_ROOT/local; nothing here is meant for Git data-wise.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _rutas import OWNER, WORK  # noqa: E402


def run(script, *args):
    print('==>', script, *args, flush=True)
    subprocess.run([sys.executable, '-X', 'utf8', str(HERE / script), *args], check=True)


def media_es(disc, source, merged):
    from decodificar import Disc

    run('portadas_es.py')
    run('carga_es.py')
    disc1 = Disc(OWNER / 'local/prepared/disc1/Track 01.iso')
    target_disc = disc1 if disc == 1 else Disc(source / 'Track 01.iso')
    cards = WORK / 'builds/es-portadas/SAKURA1'
    replacements = {}
    for name in ('LOAD.BIN', *(f'TITLE{episode}.BIN' for episode in range(1, 11))):
        path = f'/SAKURA1/{name}'
        original = disc1.read(path)
        localized = (cards / name).read_bytes()
        if (target_disc.read(path) != original or len(localized) != len(original)
                or localized[:0x1380] != original[:0x1380]):
            raise SystemExit(f'{path}: el disco {disc} o la portada no coinciden con el formato original')
        replacements[name] = localized

    destination = merged / 'SAKURA1'
    destination.mkdir(parents=True, exist_ok=True)
    for name, localized in replacements.items():
        (destination / name).write_bytes(localized)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disc', type=int, choices=(1, 2), required=True)
    parser.add_argument('--portadas', action='store_true',
                        help='also use the Spanish episode cards and loading scroll (portadas_es.py, carga_es.py)')
    args = parser.parse_args()
    source = OWNER / f'local/prepared/disc{args.disc}'
    target = OWNER / f'local/prepared/disc{args.disc}-es'
    if not (source / 'Track 01.iso').is_file():
        raise SystemExit(f'falta el disco {args.disc} inglés preparado en {source}')
    run('volcar_todo.py', '--disc', str(args.disc))
    tables = WORK / f'builds/es-all/disc{args.disc}/files'
    merged = WORK / f'builds/es-all/disc{args.disc}/merged'
    if merged.exists():
        shutil.rmtree(merged)
    shutil.copytree(tables, merged)
    if args.disc == 1:
        run('menus_es.py')
        menus = WORK / 'builds/es-cap1/files'
        for file in menus.rglob('*'):
            name = file.name.upper()
            if file.is_file() and not name.endswith(('TBL.BIN', 'MES.BIN')):
                out = merged / file.relative_to(menus)
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, out)
    elif args.disc == 2:
        run('menus_disco2.py')   # needs the disc-1 menus (builds/es-cap1) already built
        menus = WORK / 'builds/es-all/disc2/menus'
        for file in menus.rglob('*'):
            name = file.name.upper()
            if file.is_file() and not name.endswith(('TBL.BIN', 'MES.BIN')):
                out = merged / file.relative_to(menus)
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, out)
    if args.portadas:
        media_es(args.disc, source, merged)
    run('iso.py', '--source-dir', str(source), '--output-dir', str(target), '--files', str(merged))
    print(f'disco {args.disc} español listo:', target / 'game.cue')


if __name__ == '__main__':
    main()
