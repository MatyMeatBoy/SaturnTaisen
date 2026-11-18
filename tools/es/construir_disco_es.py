"""Build the Spanish disc 1 in one step from the private translation data.

  python -X utf8 tools/es/construir_disco_es.py

1. volcar.py: reviewed chapter-one batches -> Spanish *TBL.BIN and M01MES.BIN
2. menus_es.py: Spanish menu graphics and tile lists (title, intermission, options, load/save)
3. iso.py: copy of local/prepared/disc1 with those files -> local/prepared/disc1-es (fixed slots)

Inputs and outputs stay under SAKURA_OWNER_ROOT/local; nothing here is meant for Git.
"""
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
    source = OWNER / 'local/prepared/disc1'
    target = OWNER / 'local/prepared/disc1-es'
    if not (source / 'Track 01.iso').is_file():
        raise SystemExit(f'falta el disco 1 inglés preparado en {source}')
    run('volcar.py')
    run('menus_es.py')
    run('iso.py', '--source-dir', str(source), '--output-dir', str(target), '--files', str(WORK / 'builds/es-cap1/files'))
    print('disco español listo:', target / 'game.cue')


if __name__ == '__main__':
    main()
