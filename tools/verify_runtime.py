"""Compare actual guest state frame-by-frame; no reference game bytes leave local/."""
from pathlib import Path
import argparse
import hashlib
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
    p.add_argument('--backup-seed', type=Path,
                   help='native 32 KiB backup image copied into each run; source is never written')
    p.add_argument('--toolchain', type=Path, default=Path('C:/msys64/clang64'))
    p.add_argument('--experimental-functions', action='store_true', help='diagnose currently unvalidated function linking')
    p.add_argument('--timeout', type=int, default=120, help='maximum seconds per mode (long story routes need more)')
    args = p.parse_args()
    if args.frames <= 0 or args.timeout <= 0:
        p.error('--frames and --timeout must be positive')
    seed = None
    if args.backup_seed:
        try:
            if args.backup_seed.stat().st_size != 32768:
                p.error('--backup-seed requires a formatted native 32 KiB backup image')
            seed = args.backup_seed.read_bytes()
        except OSError as error:
            p.error(f'cannot read backup seed: {error}')
        if len(seed) != 32768 or not seed.startswith(b'BackUpRam Format'):
            p.error('--backup-seed requires a formatted native 32 KiB backup image')
    out = Path(tempfile.mkdtemp(prefix='parity-', dir=ROOT / 'local/work/sakura'))
    if seed is not None:
        (out / 'inputs.json').write_text(json.dumps({
            'backup_seed': str(args.backup_seed.resolve()),
            'backup_seed_sha256': hashlib.sha256(seed).hexdigest(),
            'backup_seed_bytes': len(seed),
        }, indent=2) + '\n')
    base = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
    base['PATH'] = str(args.toolchain / 'bin') + os.pathsep + base.get('PATH', '')
    modes = [('interpreter', {'SATRECOMP_NO_BLOCKS': '1', 'SATRECOMP_NO_CALLS': '1'}),
             ('aot-blocks', {'SATRECOMP_NO_FUNCTIONS': '1', 'SATRECOMP_NO_CALLS': '1', 'SATRECOMP_STRICT_NATIVE': '1'}),
             ('aot-repeat', {'SATRECOMP_NO_FUNCTIONS': '1', 'SATRECOMP_NO_CALLS': '1', 'SATRECOMP_STRICT_NATIVE': '1'})]
    if args.experimental_functions:
        modes.append(('aot-functions', {'SATRECOMP_STRICT_NATIVE': '1', 'SATRECOMP_EXPERIMENTAL_FUNCTIONS': '1'}))
    rows = []
    reference = None
    for name, flags in modes:
        backup = out / (name + '-backup.bin')
        if seed is not None:
            backup.write_bytes(seed)
        cmd = [str(ROOT / 'local/build/sakura/sakura.exe'), '--disc', str(args.disc.resolve()),
               '--headless', '--frames', str(args.frames), '--movie', str(args.movie.resolve()),
               '--backup', str(backup), '--hash-log', str(out / (name + '.hash')), '--stats']
        start = time.perf_counter()
        with (out / (name + '.log')).open('w') as log:
            result = subprocess.run(cmd, env=base | flags, stdout=log, stderr=subprocess.STDOUT, timeout=args.timeout)
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
