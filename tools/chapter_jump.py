"""Jump to a chapter without playing: boot the game with a copy of a save (backup RAM) and press Continue, then save states on the way.

For testing only (the game is played naturally by players: no state or save tools reach them, see docs/SHARDS.md). Needs the owner's
discs, a development runtime (no `release.marker` beside it) and a seeds folder with 32 KB backup RAM copies (the sweep used the public
"Battle Saves" of each chapter plus three public endings; see docs/research/scene-jump.md). Nothing from the saves is committed.

    python tools/chapter_jump.py bank-5-battle --exe local/build/sakura/sakura-<you>.exe --frames 12000 --state-at 9000 --state-at 11999

A case is a key of `seeds.json` next to the seeds (`slot` = the file to continue, `disc_hint` the disc). The runtime is run headless and
strict native, with the input movie of tests/cold-load.movie plus the slot selection and, with --advance, a periodic confirm press that
walks through the dialogue. Output folder: state-N.bin files, frames.hash, shots, run.log and report.json. Feed a state to
tools/coverage_campaign.py (windowed, HD) to see what the chapter draws.
"""
import argparse, hashlib, json, os, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SEEDS = ROOT / 'local/work/later-chapter-audit/chapter-sweep'


def build_events(cold_load_lines, slot, advance, frames, advance_from=9250, advance_period=120):
    """The input events (frame, line) of the jump: the Continue sequence, the selection of file `slot` and the optional confirm presses."""
    events = [(int(line.split()[0]), line) for line in cold_load_lines if line and not line.startswith('#')]
    for frame in (3600, 3900)[:max(slot - 1, 0)]:          # file 2 and 3: one step down each
        events += [(frame, '%d 2000 0' % frame), (frame + 8, '%d 0 0' % (frame + 8))]
    if advance:
        for frame in range(advance_from, frames, advance_period):   # confirm (button A)
            events += [(frame, '%d 0400 0' % frame), (frame + 4, '%d 0 0' % (frame + 4))]
    return sorted(events)


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('case')
    ap.add_argument('--exe', type=pathlib.Path, required=True)
    ap.add_argument('--seeds', type=pathlib.Path, default=DEFAULT_SEEDS)
    ap.add_argument('--out', type=pathlib.Path)
    ap.add_argument('--disc', type=int, choices=(1, 2))
    ap.add_argument('--slot', type=int, choices=(1, 2, 3))
    ap.add_argument('--frames', type=int, default=12000)
    ap.add_argument('--state-at', type=int, action='append', default=[])
    ap.add_argument('--interval', type=int, default=1500)
    ap.add_argument('--advance', action='store_true')
    ap.add_argument('--advance-from', type=int, default=9250)
    ap.add_argument('--advance-period', type=int, default=120)
    a = ap.parse_args()
    catalog = json.loads((a.seeds / 'seeds.json').read_text(encoding='utf-8'))
    row = catalog[a.case]
    disc = a.disc or row['disc_hint']
    slot = a.slot or row['slot']
    out = (a.out or (ROOT / 'local/work/chapter-jump' / a.case)).resolve()
    a.exe = a.exe.resolve()
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    backup = out / 'backup.bin'
    shutil.copyfile(a.seeds / row['seed'], backup)
    (out / 'settings.ini').write_text('[features]\npreset=custom\npresentation_mode=0\nrun_ahead=0\n', encoding='ascii')
    lines = (ROOT / 'tests/cold-load.movie').read_text(encoding='utf-8').splitlines()
    events = build_events(lines, slot, a.advance, a.frames, a.advance_from, a.advance_period)
    (out / 'input.movie').write_text('\n'.join(line for _, line in events) + '\n', encoding='ascii')
    env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
    env['PATH'] = os.pathsep.join([str(a.exe.parent)] + [p for p in ('C:/msys64/clang64/bin',) if pathlib.Path(p).is_dir()] + [env.get('PATH', '')])
    env.update(SATRECOMP_NO_CALLS='1', SATRECOMP_NO_FUNCTIONS='1', SATRECOMP_STRICT_NATIVE='1')
    cmd = [str(a.exe), '--disc', str(ROOT / ('local/prepared/disc%d/game.cue' % disc)), '--headless', '--frames', str(a.frames),
           '--backup', str(backup), '--settings', str(out / 'settings.ini'), '--movie', str(out / 'input.movie'), '--stats',
           '--shot-every', '%d:%s/shot-' % (a.interval, out.as_posix()), '--hash-log', str(out / 'frames.hash')]
    if a.state_at:
        cmd += ['--state-save', ','.join('%d:%s' % (n, (out / ('state-%d.bin' % n)).as_posix()) for n in a.state_at)]
    with (out / 'run.log').open('wb') as log:
        process = subprocess.run(cmd, cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=1800)
    hashes = (out / 'frames.hash').read_text(encoding='ascii').splitlines() if (out / 'frames.hash').exists() else []
    missing = re.search(r'strict AOT: untranslated (\w+) SH-2 block at ([0-9A-Fa-f]+)', (out / 'run.log').read_text(errors='replace'))
    report = {'case': a.case, 'disc': disc, 'slot': slot, 'exit': process.returncode, 'frames': len(hashes),
              'last_hash': hashes[-1] if hashes else None, 'untranslated': list(missing.groups()) if missing else None,
              'seed_sha256': row.get('seed_sha256'), 'movie_sha256': sha(out / 'input.movie'), 'argv': cmd}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(a.case, 'exit', process.returncode, 'frames', len(hashes), 'untranslated', report['untranslated'])


if __name__ == '__main__':
    sys.exit(main())
