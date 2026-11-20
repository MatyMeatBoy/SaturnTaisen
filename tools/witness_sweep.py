"""Witness sweep: which scenes does a route reach, and at which frame is there a saved state inside each one?

Development tool (needs the owner's discs and a development runtime without `release.marker`, see docs/SHARDS.md). It starts the
runtime headless and unthrottled from a saved state (or a cold backup plus an input movie), lets the random input `--auto SEED:FROM`
play, and watches the disc: every `Play Disc` command of the CD block (`SATRECOMP_CD_TRACE`) is mapped to the ISO 9660 file that
holds the sector (FAD = LBA + 150). A scene is a load of a scene file (BG####, IC####, ENDING, EVE####, EVT##, BBG##, MAP##, ...).
The run also saves a state every `--interval` frames; each load is attributed to the first saved state at or after the (estimated)
frame, so a worker can load that state and look at the scene. The frame of a load is estimated from the size of the hash log the
runtime writes, which is buffered, so it can be early by up to a few dozen frames: `--margin` moves the pick later.

    python tools/witness_sweep.py --exe local/build/sakura-witness/sakura-witness.exe --disc 1 \
        --state local/work/witness/jump-bank3-1/state-9000.bin --backup local/work/witness/jump-bank3-1/backup.bin \
        --seeds 1-4 --frames 20000 --from 0 --interval 500 --out local/work/witness/sweep-bank3-1

Output per seed under `--out/seed-N/`: `scenes.json` (the loads, with frame estimate, file, kind, state path and SHA-256 of the state),
`run.log`, `frames.hash`; states that no scene needs are deleted unless `--keep-all`. `--out/summary.json` and `summary.md` join the
seeds. Only names, seeds, frames and hashes are written: never pixels. States stay in local/work and are never committed.
"""
import argparse, bisect, hashlib, json, os, pathlib, re, shutil, struct, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCENE_KINDS = (
    ('BG', re.compile(r'^BG\d+\.')), ('IC', re.compile(r'^IC\d+\.')), ('ENDING', re.compile(r'^ENDING')),
    ('EVE', re.compile(r'^EVE\d+\.')), ('EVT', re.compile(r'^EVT\d+\.')), ('BBG', re.compile(r'^BBG\d+')),
    ('MAP', re.compile(r'^MAP\d+')), ('CG', re.compile(r'^(CG|OMAKE)')), ('MINI', re.compile(r'^MINI')),
)
TARGETS = ('BG2077', 'BG1283', 'BG2093', 'BG2290')   # the owner's first scenario backgrounds
PLAY = re.compile(r'^cd cmd ([0-9A-F]{4}) ([0-9A-F]{4}) ([0-9A-F]{4}) ([0-9A-F]{4}) ')


def read_iso(path):
    """(lba, size, path) of every file of an ISO 9660 image of 2048-byte sectors, sorted by LBA."""
    out = []
    with open(path, 'rb') as f:
        def sector(lba, n=1):
            f.seek(lba * 2048)
            return f.read(2048 * n)

        def walk(lba, size, prefix):
            data = sector(lba, (size + 2047) // 2048)
            i = 0
            while i < len(data):
                length = data[i]
                if length == 0:
                    i = (i // 2048 + 1) * 2048
                    continue
                extent, = struct.unpack_from('<I', data, i + 2)
                length_bytes, = struct.unpack_from('<I', data, i + 10)
                name = data[i + 33:i + 33 + data[i + 32]].decode('latin1')
                if name not in ('\x00', '\x01'):
                    if data[i + 25] & 2:
                        walk(extent, length_bytes, prefix + '/' + name)
                    else:
                        out.append((extent, length_bytes, prefix + '/' + name.split(';')[0]))
                i += length
        pvd = sector(16)
        root, = struct.unpack_from('<I', pvd, 156 + 2)
        root_size, = struct.unpack_from('<I', pvd, 156 + 10)
        walk(root, root_size, '')
    out.sort()
    return out


def file_at(table, fad):
    """The file that holds sector FAD (LBA = FAD - 150), or None."""
    lba = fad - 150
    i = bisect.bisect_right([row[0] for row in table], lba) - 1
    if i >= 0 and lba < table[i][0] + max(1, (table[i][1] + 2047) // 2048):
        return table[i][2]
    return None


def classify(path):
    """(kind, stem) of a disc path, or None when it is not a scene file."""
    base = path.rsplit('/', 1)[-1]
    for kind, rx in SCENE_KINDS:
        if rx.match(base):
            return kind, base.split('.')[0]
    return None


def cd_plays(lines):
    """Yield (line_number, start_fad, sectors) of each Play Disc command that starts at a frame address."""
    for number, line in enumerate(lines):
        m = PLAY.match(line)
        if not m:
            continue
        c1, c2, c3, c4 = (int(g, 16) for g in m.groups())
        if c1 >> 8 != 0x10:
            continue
        start = ((c1 & 0xFF) << 16) | c2
        end = ((c3 & 0xFF) << 16) | c4
        if start == 0xFFFFFF or not start & 0x800000:
            continue
        yield number, start & 0x7FFFFF, (end & 0x7FFFFF) if end & 0x800000 else 0


def frames_in_hash_bytes(size):
    """Lines ('N hhhhhhhhhhhhhhhh\\n', N from 1) that fit in `size` bytes: the frame count the flushed part of the log shows."""
    frames, used = 0, 0
    digits = 1
    while True:
        block = min(10 ** digits - 1, 10 ** 9) - frames
        need = block * (digits + 1 + 16 + 1)
        if used + need > size:
            return frames + (size - used) // (digits + 18)
        used += need
        frames += block
        digits += 1


def attribute(events, interval, margin, frames):
    """Pick for each (estimated_frame, ...) the first checkpoint frame (k*interval - 1) at or after estimate + margin, or None."""
    picked = []
    for event in events:
        want = event['frame_estimate'] + margin
        k = max(1, -(-(want + 1) // interval))
        frame = k * interval - 1
        picked.append(frame if frame < frames else None)
    return picked


def dedupe(loads):
    """Keep the first load of each file inside a run of identical consecutive files, and every load of a different file."""
    out = []
    for item in loads:
        if out and out[-1]['file'] == item['file']:
            continue
        out.append(item)
    return out


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def parse_seeds(text):
    seeds = []
    for part in text.split(','):
        if '-' in part:
            low, high = part.split('-')
            seeds += list(range(int(low), int(high) + 1))
        else:
            seeds.append(int(part))
    return seeds


def run_one(args, table, seed):
    run = args.out / ('seed-%d' % seed)
    run.mkdir(parents=True)
    backup = run / 'backup.bin'
    if args.backup:
        shutil.copyfile(args.backup, backup)
    else:
        backup.write_bytes(b'\0' * 32768)
    (run / 'settings.ini').write_text('[features]\npreset=custom\npresentation_mode=0\nrun_ahead=0\n', encoding='ascii')
    hash_log = run / 'frames.hash'
    checkpoints = list(range(args.interval - 1, args.frames, args.interval))
    cmd = [str(args.exe), '--disc', str(ROOT / ('local/prepared/disc%d/game.cue' % args.disc)), '--headless', '--unthrottled', '--mute',
           '--frames', str(args.frames), '--backup', str(backup), '--settings', str(run / 'settings.ini'),
           '--hash-log', str(hash_log), '--auto', '%d:%d' % (seed, args.start_auto),
           '--state-save', ','.join('%d:%s' % (n, (run / ('state-%d.bin' % n)).as_posix()) for n in checkpoints)]
    if args.state:
        cmd += ['--state-load', '0:' + str(args.state)]
    if args.movie:
        cmd += ['--movie', str(args.movie)]
    env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
    env['PATH'] = os.pathsep.join([str(args.exe.parent)] + [p for p in ('C:/msys64/clang64/bin',) if pathlib.Path(p).is_dir()] + [env.get('PATH', '')])
    env.update(SATRECOMP_CD_TRACE='1', SATRECOMP_NO_CALLS='1', SATRECOMP_NO_FUNCTIONS='1', SATRECOMP_STRICT_NATIVE='1')
    loads, nonscene, log_lines = [], 0, []
    process = subprocess.Popen(cmd, cwd=run, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors='replace')
    count = 0
    for line in process.stderr:
        line = line.rstrip('\n')
        if not line.startswith('cd '):
            log_lines.append(line)
            continue
        plays = list(cd_plays([line]))
        if not plays:
            continue
        _, fad, sectors = plays[0]
        name = file_at(table, fad)
        size = hash_log.stat().st_size if hash_log.exists() else 0
        info = classify(name) if name else None
        if info:
            loads.append({'file': name, 'kind': info[0], 'scene': info[1], 'fad': fad, 'frame_estimate': frames_in_hash_bytes(size)})
        else:
            nonscene += 1
        count += 1
    process.wait()
    (run / 'run.log').write_text('\n'.join(log_lines[-200:]) + '\nexit %d\n' % process.returncode, encoding='utf-8')
    loads = dedupe(loads)
    for item, frame in zip(loads, attribute(loads, args.interval, args.margin, args.frames)):
        state = run / ('state-%d.bin' % frame) if frame is not None else None
        item['state_frame'] = frame
        if state and state.exists():
            item['state'] = state.relative_to(args.out).as_posix()
            item['state_sha256'] = sha256(state)
    used = {item['state'] for item in loads if 'state' in item}
    if not args.keep_all:
        for f in run.glob('state-*.bin'):
            if f.relative_to(args.out).as_posix() not in used:
                f.unlink()
    result = {'seed': seed, 'exit': process.returncode, 'cd_plays': count, 'non_scene_plays': nonscene, 'loads': loads,
              'argv': [c if not str(c).startswith('--state-save') else c for c in cmd[:-2]] + ['--state-save', '<every %d frames>' % args.interval]}
    (run / 'scenes.json').write_text(json.dumps(result, indent=1), encoding='utf-8')
    return result


def summarise(results):
    """seed rows, the union of scenes with the first (seed, frame, state) that shows each, and the target hits."""
    first = {}
    for result in results:
        for item in result['loads']:
            key = item['scene']
            if key not in first:
                first[key] = {'kind': item['kind'], 'seed': result['seed'], 'frame_estimate': item['frame_estimate'],
                              'state_frame': item.get('state_frame'), 'state': item.get('state'), 'state_sha256': item.get('state_sha256')}
    return {'scenes': dict(sorted(first.items())), 'targets': {t: first.get(t) for t in TARGETS},
            'by_kind': {k: sorted(s for s, v in first.items() if v['kind'] == k) for k in sorted({v['kind'] for v in first.values()})}}


def markdown(summary, args):
    lines = ['# Witness sweep', '', 'Start: `%s`, disc %d, %d frames, checkpoint every %d, auto from frame %d.' %
             (args.state.name if args.state else 'cold', args.disc, args.frames, args.interval, args.start_auto), '',
             '| scene | kind | seed | frame (est.) | state frame | state SHA-256 |', '|---|---|---|---|---|---|']
    for scene, v in summary['scenes'].items():
        lines.append('| %s | %s | %d | %d | %s | %s |' % (scene, v['kind'], v['seed'], v['frame_estimate'], v['state_frame'],
                                                         (v['state_sha256'] or '')[:16]))
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--exe', type=pathlib.Path, required=True)
    ap.add_argument('--disc', type=int, choices=(1, 2), required=True)
    ap.add_argument('--state', type=pathlib.Path)
    ap.add_argument('--backup', type=pathlib.Path)
    ap.add_argument('--movie', type=pathlib.Path)
    ap.add_argument('--seeds', default='1')
    ap.add_argument('--frames', type=int, default=20000)
    ap.add_argument('--from', dest='start_auto', type=int, default=0)
    ap.add_argument('--interval', type=int, default=500)
    ap.add_argument('--margin', type=int, default=60)
    ap.add_argument('--jobs', type=int, default=1)
    ap.add_argument('--keep-all', action='store_true')
    ap.add_argument('--out', type=pathlib.Path, required=True)
    args = ap.parse_args()
    args.exe, args.out = args.exe.resolve(), args.out.resolve()
    for name in ('state', 'backup', 'movie'):
        if getattr(args, name):
            setattr(args, name, getattr(args, name).resolve())
    table = read_iso(ROOT / ('local/prepared/disc%d/Track 01.iso' % args.disc))
    args.out.mkdir(parents=True)
    with ThreadPoolExecutor(args.jobs) as pool:
        results = list(pool.map(lambda s: run_one(args, table, s), parse_seeds(args.seeds)))
    summary = summarise(results)
    (args.out / 'summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    (args.out / 'summary.md').write_text(markdown(summary, args), encoding='utf-8')
    print(markdown(summary, args))
    print('targets:', {k: bool(v) for k, v in summary['targets'].items()})


if __name__ == '__main__':
    sys.exit(main())
