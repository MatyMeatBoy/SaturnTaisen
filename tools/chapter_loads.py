"""Chapter attribution trace: every file the game loads while a route plays, with a frame bracket and the SHA-256 of a saved state.

Development tool (owner's discs, a development runtime without `release.marker`; see docs/SHARDS.md). It replays a route headless, strict
native and unthrottled (a cold backup plus an input movie, or a saved state plus its movie), and maps each `Play Disc` command of the CD
block (`SATRECOMP_CD_TRACE`) to the ISO 9660 file that holds the start sector (FAD = LBA + 150). Unlike tools/witness_sweep.py (scenes
only) it records every file (SAKURA1/SAKURA2 scenes, NC bodies, FCE/TBL portraits, EVT/MAP/UNIT/FACE/WKL/FIX tactical files, FILM
streams, menus). A state is saved every `--interval` frames; each first load is attributed to the first state at or after its estimated
frame (the hash log is buffered, so the estimate can be early by a few dozen frames: `--margin`). The report records names, frames and hashes. Save states stay in a new directory under local/work.

    python tools/chapter_loads.py --exe local/build/sakura-th2/sakura-th2.exe --disc 1 --backup B --movie M --frames 28491 \
        --interval 500 --out local/work/th2/continuous [--state S]
"""
import argparse, hashlib, json, os, pathlib, re, shutil, struct, subprocess, sys, bisect

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAY = re.compile(r'^cd cmd ([0-9A-F]{4}) ([0-9A-F]{4}) ([0-9A-F]{4}) ([0-9A-F]{4}) ')


def read_iso(path):
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
    lba = fad - 150
    i = bisect.bisect_right([row[0] for row in table], lba) - 1
    if i >= 0 and lba < table[i][0] + max(1, (table[i][1] + 2047) // 2048):
        return table[i][2], (lba - table[i][0]) * 2048
    return None, 0


def cd_plays(line):
    m = PLAY.match(line)
    if not m:
        return None
    c1, c2, c3, c4 = (int(g, 16) for g in m.groups())
    if c1 >> 8 != 0x10:
        return None
    start = ((c1 & 0xFF) << 16) | c2
    if start == 0xFFFFFF or not start & 0x800000:
        return None
    return start & 0x7FFFFF


def frames_in_hash_bytes(size):
    frames, used, digits = 0, 0, 1
    while True:
        block = min(10 ** digits - 1, 10 ** 9) - frames
        need = block * (digits + 1 + 16 + 1)
        if used + need > size:
            return frames + (size - used) // (digits + 18)
        used += need
        frames += block
        digits += 1


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--exe', type=pathlib.Path, required=True)
    ap.add_argument('--disc', type=int, choices=(1, 2), default=1)
    ap.add_argument('--backup', type=pathlib.Path, required=True)
    ap.add_argument('--movie', type=pathlib.Path)
    ap.add_argument('--auto', help='SEED:FROM random input as in tools/witness_sweep.py instead of (or after) a movie')
    ap.add_argument('--state', type=pathlib.Path)
    ap.add_argument('--frames', type=int, required=True)
    ap.add_argument('--interval', type=int, default=500)
    ap.add_argument('--margin', type=int, default=60)
    ap.add_argument('--keep-all', action='store_true')
    ap.add_argument('--out', type=pathlib.Path, required=True)
    a = ap.parse_args()
    out, exe = a.out.resolve(), a.exe.resolve()
    work = (ROOT / 'local/work').resolve()
    if out == work or not out.is_relative_to(work):
        ap.error('--out must name a new directory under local/work')
    if a.frames < 1 or a.interval < 1 or a.margin < 0:
        ap.error('--frames and --interval must be positive, and --margin cannot be negative')
    if out.exists():
        ap.error('--out already exists')
    out.mkdir(parents=True)
    shutil.copyfile(a.backup, out / 'backup.bin')
    if a.movie:
        shutil.copyfile(a.movie, out / 'input.movie')
    (out / 'settings.ini').write_text('[features]\npreset=custom\npresentation_mode=0\nrun_ahead=0\n', encoding='ascii')
    table = read_iso(ROOT / ('local/prepared/disc%d/Track 01.iso' % a.disc))
    hash_log = out / 'frames.hash'
    checkpoints = list(range(a.interval - 1, a.frames, a.interval))
    cmd = [str(exe), '--disc', str(ROOT / ('local/prepared/disc%d/game.cue' % a.disc)), '--headless', '--unthrottled', '--mute',
           '--frames', str(a.frames), '--backup', str(out / 'backup.bin'), '--settings', str(out / 'settings.ini'),
           '--hash-log', str(hash_log), '--stats']
    if checkpoints:
        cmd += ['--state-save', ','.join(f"{n}:{(out / f'state-{n}.bin').as_posix()}" for n in checkpoints)]
    if a.movie:
        cmd += ['--movie', str(out / 'input.movie')]
    if a.auto:
        cmd += ['--auto', a.auto]
    if a.state:
        cmd += ['--state-load', '0:' + str(a.state.resolve())]
    env = {k: v for k, v in os.environ.items()
           if not k.upper().startswith(('SATRECOMP_', 'SATURN_TAISEN'))}
    env['PATH'] = os.pathsep.join([str(exe.parent), env.get('PATH', '')])
    env.update(SATRECOMP_CD_TRACE='1', SATRECOMP_NO_CALLS='1', SATRECOMP_NO_FUNCTIONS='1',
               SATRECOMP_STRICT_NATIVE='1', SATURN_TAISEN_FIRST_HOME=str(out), SDL_AUDIODRIVER='dummy')
    loads, log_lines = [], []
    p = subprocess.Popen(cmd, cwd=out, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors='replace')
    for line in p.stderr:
        line = line.rstrip('\n')
        if not line.startswith('cd '):
            log_lines.append(line)
            continue
        fad = cd_plays(line)
        if fad is None:
            continue
        name, offset = file_at(table, fad)
        size = hash_log.stat().st_size if hash_log.exists() else 0
        if name is None:
            name = '?'
        if loads and loads[-1]['file'] == name and loads[-1]['offset'] == offset:
            continue
        loads.append({'file': name, 'fad': fad, 'offset': offset, 'frame_estimate': frames_in_hash_bytes(size)})
    p.wait()
    (out / 'run.log').write_text('\n'.join(log_lines[-200:]) + '\nexit %d\n' % p.returncode, encoding='utf-8')
    first = {}
    for item in loads:
        first.setdefault(item['file'], item)
    for item in first.values():
        want = item['frame_estimate'] + a.margin
        k = max(1, -(-(want + 1) // a.interval))
        frame = k * a.interval - 1
        item['state_frame'] = frame if frame < a.frames else None
        state = out / ('state-%d.bin' % frame)
        if item['state_frame'] is not None and state.exists():
            item['state_sha256'] = sha256(state)
    used = {'state-%d.bin' % i['state_frame'] for i in first.values() if i.get('state_sha256')}
    if not a.keep_all:
        for f in out.glob('state-*.bin'):
            if f.name not in used:
                f.unlink()
    hashes = hash_log.read_text().splitlines() if hash_log.exists() else []
    interpreted_zero = any('interpreted 0 (0.00%)' in l for l in log_lines)
    result = {'exit': p.returncode, 'frames': a.frames, 'frame_hashes': len(hashes),
              'frames_hash_sha256': hashlib.sha256('\n'.join(hashes).encode()).hexdigest() if hashes else None,
              'interpreted_zero': interpreted_zero, 'backup_sha256': sha256(a.backup), 'movie_sha256': sha256(a.movie) if a.movie else None, 'auto': a.auto,
              'state_sha256': sha256(a.state) if a.state else None, 'exe_sha256': sha256(exe),
              'first_loads': list(first.values()), 'load_sequence': [(i['file'], i['frame_estimate']) for i in loads]}
    (out / 'loads.json').write_text(json.dumps(result, indent=1), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('first_loads', 'load_sequence')}))
    return p.returncode


if __name__ == '__main__':
    sys.exit(main())
