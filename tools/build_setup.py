"""Freeze the Windows setup helper with one Python environment and verify it."""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    args = parser.parse_args()

    tools = Path(__file__).resolve().parent
    subprocess.run([sys.executable, '-I', '-c', 'import PIL.Image, PIL.ImageChops, PIL.ImageStat'],
                   check=True)
    subprocess.run([
        sys.executable, '-I', '-m', 'PyInstaller', '--clean', '--noconfirm',
        '--onefile', '--console', '--name', 'preparar-juego',
        '--paths', str(tools), '--hidden-import', 'hd_matching',
        '--distpath', str(args.output_dir.resolve()),
        '--workpath', str(args.work_dir.resolve()), '--specpath', str(args.work_dir.resolve()),
        str(tools/'taisen_setup.py'),
    ], check=True)
    executable = args.output_dir.resolve()/'preparar-juego.exe'
    output = subprocess.check_output([str(executable), 'self-test'], cwd=executable.parent,
                                     timeout=60, text=True, encoding='utf-8')
    if output.strip() != 'OK preparar-juego PNG':
        raise ValueError(f'Unexpected preparar-juego self-test output: {output!r}')
    print(output.strip())


if __name__ == '__main__':
    main()
