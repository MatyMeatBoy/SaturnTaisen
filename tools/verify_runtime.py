"""Compare actual guest state frame-by-frame; no reference game bytes leave local/."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frames', type=int, default=4200)
    p.add_argument('--disc', type=Path, default=ROOT / 'local/prepared/disc1/game.cue')
    p.add_argument('--movie', type=Path, default=ROOT / 'tests/opening.movie')
    p.add_argument('--toolchain', type=Path, default=Path('C:/msys64/clang64'))
    p.add_argument('--experimental-functions', action='store_true', help='diagnose currently unvalidated function linking')
    args = p.parse_args()
    out = Path(tempfile.mkdtemp(prefix='parity-', dir=ROOT / 'local/work/sakura'))
    base = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
    base['PATH'] = str(args.toolchain / 'bin') + os.pathsep + base.get('PATH', '')
    modes = [('interpreter', {'SATRECOMP_NO_BLOCKS': '1', 'SATRECOMP_NO_CALLS': '1'}),
             ('aot-blocks', {'SATRECOMP_NO_FUNCTIONS': '1', 'SATRECOMP_NO_CALLS': '1', 'SATRECOMP_STRICT_NATIVE': '1'}),
             ('aot-repeat', {'SATRECOMP_NO_FUNCTIONS': '1', 'SATRECOMP_NO_CALLS': '1', 'SATRECOMP_STRICT_NATIVE': '1'})]
    if args.experimental_functions:
        modes.append(('aot-functions', {'SATRECOMP_STRICT_NATIVE': '1'}))
    rows = []
    reference = None
    for name, flags in modes:
        cmd = [str(ROOT / 'local/build/sakura/sakura.exe'), '--disc', str(args.disc.resolve()),
               '--headless', '--frames', str(args.frames), '--movie', str(args.movie.resolve()),
               '--backup', str(out / (name + '-backup.bin')), '--hash-log', str(out / (name + '.hash')), '--stats']
        start = time.perf_counter()
        with (out / (name + '.log')).open('w') as log:
            result = subprocess.run(cmd, env=base | flags, stdout=log, stderr=subprocess.STDOUT, timeout=120)
        duration = time.perf_counter() - start
        hashes = (out / (name + '.hash')).read_text().splitlines()
        if reference is None:
            reference = hashes
        row = {'mode': name, 'exit': result.returncode, 'frames': len(hashes), 'seconds': duration,
               'headless_fps': len(hashes) / duration, 'equal_reference': hashes == reference,
               'first_difference': next((i + 1 for i, (a, b) in enumerate(zip(reference, hashes)) if a != b), None)}
        rows.append(row)
        print(json.dumps(row), flush=True)
        (out / 'report.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(f'Evidence: {out}')
    if any(r['exit'] or r['frames'] != args.frames or not r['equal_reference'] for r in rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
