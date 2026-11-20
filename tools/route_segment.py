"""Run one scripted route segment: a saved state, a typed input list, strict native, a final state and the CD loads it caused.

Development tool (needs the owner's discs and a development runtime without `release.marker`). One segment loads STATE (with a copy of
BACKUP), replays the inputs for FRAMES frames and saves a state at FRAMES-1, so the next segment starts from it (the runtime saves a
state before running that frame; see tools/stitch_battle_replay.py). Inputs are written as `FRAME BUTTONS[+BUTTONS]...` where a press
is held for 8 frames and the input is released again, e.g. `8 A, 38 RIGHT, 70 A+B` (BUTTONS: UP DOWN LEFT RIGHT A B C X Y Z L R START).
Every `Play Disc` command of the CD block is mapped to its ISO file (FAD = LBA + 150) and printed, so a run says which scene file the
game asked for without a screenshot. Only names, frames and hashes are written next to the pictures; nothing is committed.

    python tools/route_segment.py --exe E --disc 1 --state S --backup B --inputs "8 A,38 RIGHT" --frames 600 --out OUT [--shots 120]
"""
import argparse, bisect, hashlib, json, os, pathlib, re, shutil, struct, subprocess, sys

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




ROOT = pathlib.Path(__file__).resolve().parents[1]
BIT = dict(RIGHT=0x8000, LEFT=0x4000, DOWN=0x2000, UP=0x1000, START=0x0800, A=0x0400, C=0x0200, B=0x0100,
           R=0x0080, X=0x0040, Y=0x0020, Z=0x0010, L=0x0008)


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def movie_text(spec, hold):
    events = {}
    for item in [s.strip() for s in spec.split(',') if s.strip()]:
        frame, _, buttons = item.partition(' ')
        value = 0
        for name in buttons.replace('+', ' ').split():
            value |= BIT[name.upper()]
        frame = int(frame)
        events[frame] = value
        events.setdefault(frame + hold, 0)
    lines, last = [], None
    for frame in sorted(events):
        lines.append('%d %04X 0' % (frame, events[frame]))
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--exe', type=pathlib.Path, required=True)
    ap.add_argument('--disc', type=int, choices=(1, 2), default=1)
    ap.add_argument('--root', type=pathlib.Path, default=ROOT, help='folder that holds local/prepared')
    ap.add_argument('--state', type=pathlib.Path, required=True)
    ap.add_argument('--backup', type=pathlib.Path, required=True)
    ap.add_argument('--inputs', default='')
    ap.add_argument('--movie', type=pathlib.Path, help='an input movie file instead of --inputs')
    ap.add_argument('--hold', type=int, default=8)
    ap.add_argument('--frames', type=int, required=True)
    ap.add_argument('--shots', type=int, default=0)
    ap.add_argument('--interpret', action='store_true', help='reference run: SATRECOMP_NO_BLOCKS instead of strict native')
    ap.add_argument('--dump', action='store_true', help='write work RAM (ram-high.bin, ram-low.bin) at exit')
    ap.add_argument('--out', type=pathlib.Path, required=True)
    a = ap.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True)
    shutil.copyfile(a.backup, out / 'backup.bin')
    movie = out / 'input.movie'
    if a.movie:
        shutil.copyfile(a.movie, movie)
    else:
        movie.write_text(movie_text(a.inputs, a.hold), encoding='ascii')
    (out / 'settings.ini').write_text('[features]\npreset=custom\npresentation_mode=0\n', encoding='ascii')
    table = read_iso(a.root / ('local/prepared/disc%d/Track 01.iso' % a.disc))
    cmd = [str(a.exe.resolve()), '--disc', str(a.root / ('local/prepared/disc%d/game.cue' % a.disc)), '--backup', str(out / 'backup.bin'),
           '--settings', str(out / 'settings.ini'), '--headless', '--unthrottled', '--mute', '--frames', str(a.frames),
           '--hash-log', str(out / 'frames.hash'), '--state-load', '0:' + str(a.state.resolve()),
           '--state-save', '%d:%s' % (a.frames - 1, (out / 'finish.state').as_posix()), '--movie', str(movie), '--stats']
    if a.dump:
        cmd += ['--dump-ram', (out / 'ram-').as_posix()]
    if a.shots:
        cmd += ['--shot-every', '%d:%s/frame-' % (a.shots, out.as_posix())]
    env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
    env['PATH'] = os.pathsep.join([str(a.exe.resolve().parent), 'D:/01Claude/TaisenFirst/toolkit/msys64/clang64/bin', env.get('PATH', '')])
    env.update(SATRECOMP_CD_TRACE='1', SATRECOMP_NO_CALLS='1', SATRECOMP_NO_FUNCTIONS='1')
    env['SATRECOMP_NO_BLOCKS' if a.interpret else 'SATRECOMP_STRICT_NATIVE'] = '1'
    p = subprocess.run(cmd, cwd=out, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, errors='replace')
    lines = p.stdout.splitlines()
    loads = []
    for line in lines:
        for _, fad, _ in cd_plays([line]):
            name = file_at(table, fad)
            if name and (not loads or loads[-1] != name):
                loads.append(name)
    (out / 'run.log').write_text('\n'.join(l for l in lines if not l.startswith('cd cmd')) + '\nexit %d\n' % p.returncode, encoding='utf-8')
    hashes = (out / 'frames.hash').read_text().splitlines() if (out / 'frames.hash').exists() else []
    report = dict(exit=p.returncode, frames=a.frames, state_sha256=sha256(a.state), movie_sha256=sha256(movie),
                  finish_state_sha256=sha256(out / 'finish.state') if (out / 'finish.state').exists() else None,
                  last_hash=hashes[-1] if hashes else None, interpreted_zero=any('interpreted 0 (0.00%)' in l for l in lines),
                  disc_files=loads)
    (out / 'run.json').write_text(json.dumps(report, indent=1), encoding='utf-8')
    print(json.dumps(report))
    return p.returncode


if __name__ == '__main__':
    sys.exit(main())
