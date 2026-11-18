"""Build a Spanish disc (1 or 2) with every reviewed chapter and the Spanish menus.

  python -X utf8 tools/es/construir_todo.py --disc 1
  python -X utf8 tools/es/construir_todo.py --disc 2

1. volcar_todo.py --disc N: every dialogue table (and every battle table that has batches)
2. disc 1: menus_es.py builds the Spanish menu graphics (title, interlude, options, load/save, battle bars);
   disc 2: menus_disco2.py moves those patches onto disc 2's own SAKURA/LOGO.SH2 and redraws its WKL12-26 bars
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disc', type=int, choices=(1, 2), required=True)
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
    run('iso.py', '--source-dir', str(source), '--output-dir', str(target), '--files', str(merged))
    print(f'disco {args.disc} español listo:', target / 'game.cue')


if __name__ == '__main__':
    main()
