"""Autopilot coverage campaign: which HD items does the runtime really draw when the game is explored?

Runs the development runtime hidden and unthrottled from a start point (a saved state, optionally plus an input movie) with the random
input of `--auto SEED:FROM`, several seeds in parallel, and keeps the distinct trace lines that say what was drawn: HD scene pictures
(`scene picture:`), shared-palette pictures recognised by the cell hash, large bodies (`body:`, `body frame`, `body skipped`) and PC clips
(`clip:`). The union over all runs goes to `hits.json` and a readable `summary.txt`; compare it with `config/hd-chapter-coverage.json` to
raise `verified_in_game`. Development tool only (it needs a runtime without `release.marker`, the owner's discs and the PC edition).

    python tools/coverage_campaign.py --exe local/build/sakura/sakura-<you>.exe --state local/work/intro-enhanced/title-final.state \
        --movie tests/chapter1-title-new-game.movie --seeds 1-4 --frames 20000 --from 6000 --jobs 2 --out local/work/campaign/run1

Each run uses its own profile folder under `--out`; the shared executable is only read. Never run it from the shared build path while
someone links it (copy the executable first, see docs/SHARDS.md).
"""
import argparse, json, os, pathlib, re, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
KEEP = ('scene picture:', 'body:', 'body frame', 'body skipped', 'clip: open', 'scene picture with a shared palette')


def parse_seeds(text):
    seeds = []
    for part in text.split(','):
        if '-' in part:
            low, high = part.split('-')
            seeds += list(range(int(low), int(high) + 1))
        else:
            seeds.append(int(part))
    return seeds


def keep_line(line):
    return line.startswith(KEEP) and 'no match' not in line


def one_run(args, seed):
    run = args.out / ('seed-%d' % seed)
    shutil.rmtree(run, ignore_errors=True)
    run.mkdir(parents=True)
    (run / 's.ini').write_text('[features]\npreset=custom\npresentation_mode=1\nscene_view=1\ntext_style=0\nrun_ahead=0\n')
    shutil.copyfile(args.seed_backup, run / 'backup.bin')
    env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
    # the runtime's DLLs: beside the executable, or in the clang64 folder of a development machine
    extra = [str(args.exe.parent)] + [p for p in ('C:/msys64/clang64/bin',) if pathlib.Path(p).is_dir()]
    env['PATH'] = os.pathsep.join(extra + [env.get('PATH', '')])
    env.update(SATRECOMP_WINDOW_HIDDEN='1', SATRECOMP_SKIP_CHOOSER='1', SATRECOMP_BACKGROUND_WORKERS='0', SATRECOMP_BACKGROUND_STATS='1',
               SATRECOMP_CLIP_TRACE='1', SATRECOMP_WINDOW_KEYS='2:SIZE=1280x720,%d:QUIT' % args.frames)
    cmd = [str(args.exe), '--disc', str(args.disc), '--settings', str(run / 's.ini'), '--backup', str(run / 'backup.bin'),
           '--state-load', '0:' + str(args.state), '--auto', '%d:%d' % (seed, args.start), '--mute', '--unthrottled']
    if args.movie:
        cmd += ['--movie', str(args.movie)]
    if args.pc_assets:
        cmd += ['--pc-assets', str(args.pc_assets)]
    seen = {}
    process = subprocess.Popen(cmd, env=env, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, errors='replace')
    for line in process.stderr:
        line = line.strip()
        if keep_line(line):
            seen[line] = seen.get(line, 0) + 1
    process.wait()
    (run / 'lines.json').write_text(json.dumps(seen, indent=1))
    return seed, process.returncode, seen


def summarise(all_lines):
    bodies, pictures, clips = set(), set(), set()
    for line in all_lines:
        match = re.match(r'body: (\S+) usable=1', line)
        if match:
            bodies.add(match.group(1))
        match = re.match(r'scene picture: (\S+) usable=1', line)
        if match:
            pictures.add(match.group(1))
        match = re.search(r'-> (SAKURA\S+\.SPR)$', line)
        if match:
            pictures.add(match.group(1))
        match = re.match(r'clip: open (\S+) -> 1', line)
        if match:
            clips.add(match.group(1))
    return sorted(bodies), sorted(pictures), sorted(clips)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exe', type=pathlib.Path, required=True)
    ap.add_argument('--state', type=pathlib.Path, required=True)
    ap.add_argument('--movie', type=pathlib.Path)
    ap.add_argument('--disc', type=pathlib.Path, default=ROOT / 'local/prepared/disc1/game.cue')
    ap.add_argument('--pc-assets', type=pathlib.Path, default=ROOT / 'local/work/v02-pc-game/_t_@_C__')
    ap.add_argument('--seed-backup', type=pathlib.Path, default=ROOT / 'local/work/sakura/prebattle-immutable-seed.bin')
    ap.add_argument('--seeds', default='1')
    ap.add_argument('--frames', type=int, default=20000)
    ap.add_argument('--from', dest='start', type=int, default=0)
    ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--out', type=pathlib.Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    union = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for seed, code, seen in pool.map(lambda s: one_run(args, s), parse_seeds(args.seeds)):
            print('seed %d: exit %s, %d distinct lines' % (seed, code, len(seen)), flush=True)
            for line, count in seen.items():
                union[line] = union.get(line, 0) + count
    (args.out / 'hits.json').write_text(json.dumps(union, indent=1))
    bodies, pictures, clips = summarise(union)
    text = 'bodies drawn (%d): %s\nscene pictures drawn (%d): %s\nclips opened (%d): %s\n' % (
        len(bodies), ' '.join(bodies), len(pictures), ' '.join(pictures), len(clips), ' '.join(clips))
    (args.out / 'summary.txt').write_text(text)
    print(text)


if __name__ == '__main__':
    sys.exit(main())
