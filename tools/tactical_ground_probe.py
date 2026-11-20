"""Does the runtime draw the PC tactical ground of a map? Runs a tactical state with and without the donor and says.

The tactical ground is not a `scene picture:` (see tools/scene_draw_probe.py): the runtime loads `SAKURA2/MAP/MAPnn/MAPnn_A.SPR`
with `tactical_ground::Load` when the VDP2 source-4 page signature of the map matches a table row, and the compositor replaces
eligible ground pixels inside the integer-scaled 320 x 224 centre. No trace line says so, so the evidence is a capture
comparison by rectangle: the donor run and the control run (the same donor root with only that map's `_A.SPR` hard-linked out)
start from the same state, must have identical strict guest hashes frame by frame, the same final SRAM and `interpreted 0`, and
the ground is DRAWN when RGB pixels differ inside the centre rectangle (and only there: a difference outside is reported).

    python tools/tactical_ground_probe.py --exe local/build/sakura-tgprobe/sakura-full.exe \
        --state local/work/sweep/run2-bank-8-battle-2/state-6999.bin --backup local/work/sweep/run2-bank-8-battle-2/backup.bin \
        --disc local/prepared/disc2/game.cue --pc-assets local/work/pc-cab/out-tac --map MAP14 --size 2560x1440

The executable needs the `art/` folder beside it (floral backdrop; without it no enhanced presentation runs). Never commit the
captures or states it writes (they stay under --out, normally in local/work/). Exit code: 0 drawn, 1 not drawn or ambiguous,
2 the evidence is not valid.
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLCHAIN = ROOT.parent / 'toolkit' / 'msys64' / 'clang64' / 'bin'
MAP_NAME = re.compile(r'^MAP(\d{2})$')
INTERPRETED = re.compile(r'interpreted 0 \(')
# The compositor changes only eligible ground pixels of the centre; a handful of changed pixels is a flicker, not a ground.
DRAWN_FRACTION = 0.02


def local_path(relative):
    """`local/...` of this checkout, or of the main workspace when this is a git worktree without its own local/."""
    for base in (ROOT, ROOT.parent / 'workspace'):
        if (base / relative).exists():
            return base / relative
    return ROOT / relative


def ground_file(map_name):
    """Path of the PC ground inside an extraction root, for `MAPnn`."""
    match = MAP_NAME.match(map_name)
    if not match:
        raise ValueError('map must look like MAP14, got %r' % map_name)
    return pathlib.PurePosixPath('SAKURA2/MAP/%s/%s_A.SPR' % (map_name, map_name))


def centre_rect(width, height):
    """(x0, y0, x1, y1) of the integer-scaled 320 x 224 native centre in a window of this size (x1, y1 exclusive)."""
    scale = min(width // 320, height // 224)
    if scale < 1:
        raise ValueError('window %dx%d is smaller than the native 320x224 frame' % (width, height))
    x0, y0 = (width - 320 * scale) // 2, (height - 224 * scale) // 2
    return x0, y0, x0 + 320 * scale, y0 + 224 * scale


def parse_size(text):
    match = re.fullmatch(r'(\d+)x(\d+)', text)
    if not match:
        raise ValueError('size must look like 2560x1440, got %r' % text)
    return int(match.group(1)), int(match.group(2))


def region_changes(path_a, path_b, rect):
    """(changed inside rect, changed outside rect, pixels inside rect) between two PNG captures, or None when not comparable."""
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return None
    if not (path_a.is_file() and path_b.is_file()):
        return None
    with Image.open(path_a) as a, Image.open(path_b) as b:
        a, b = a.convert('RGB'), b.convert('RGB')
        if a.size != b.size:
            return None
        channels = ImageChops.difference(a, b).split()
        diff = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2]).point(lambda v: 255 if v else 0)
        inside = diff.crop(rect)
        area = (rect[2] - rect[0]) * (rect[3] - rect[1])
        inside_changed = inside.histogram()[255]
        total_changed = diff.histogram()[255]
        return inside_changed, total_changed - inside_changed, area


def classify(changes, fraction=DRAWN_FRACTION):
    """Verdict word for the per-capture (inside, outside, area) tuples: drawn, not-drawn or ambiguous, plus a reason."""
    usable = [c for c in changes if c is not None]
    if not usable:
        return 'invalid', 'no capture pair could be compared (Pillow missing, files absent or sizes differ)'
    best = max(usable, key=lambda c: c[0])
    inside, outside, area = best
    if inside == 0 and all(c[0] == 0 for c in usable):
        return 'not-drawn', 'no changed RGB pixel in the centre in %d capture(s): the native ground stays' % len(usable)
    if inside >= area * fraction:
        extra = '; %d changed pixels outside the centre' % outside if outside else ''
        return 'drawn', '%d of %d centre pixels differ from the control (%.1f%%)%s' % (inside, area, 100.0 * inside / area, extra)
    return 'ambiguous', 'only %d of %d centre pixels differ (below %.0f%%)' % (inside, area, fraction * 100)


def guest_evidence_valid(guest_hash_bytes, stderr_text, frames):
    """True when a run logged one strict guest hash per frame and no block was interpreted."""
    return len(guest_hash_bytes.splitlines()) == frames and bool(INTERPRETED.search(stderr_text))


def build_control_root(donor, control, map_name):
    """A copy of the extraction root made of hard links (or copies) without the `MAPnn_A.SPR` under test."""
    skip = pathlib.Path(donor, *ground_file(map_name).parts).resolve()
    if control.resolve().is_relative_to(donor.resolve()):
        raise ValueError('control root must be outside the donor tree')
    control.mkdir(parents=True)
    for base, _, names in os.walk(donor):
        for name in names:
            source = pathlib.Path(base, name)
            if source.resolve() == skip:
                continue
            target = control / source.relative_to(donor)
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(source, target)
            except OSError:
                shutil.copyfile(source, target)
    (control / 'SAKURA1').mkdir(parents=True, exist_ok=True)
    return control


def shot_frames(frames):
    """Frames at which captures are taken: the end, and 60 frames earlier when the run is long enough (a second camera)."""
    last = frames - 3
    return [last - 60, last] if last - 60 >= 5 else [last]


def run_once(args, run, assets):
    run.mkdir(parents=True, exist_ok=True)
    (run / 'settings.ini').write_text('[features]\npreset=custom\npresentation_mode=1\nscene_view=1\ntext_style=0\nrun_ahead=0\n')
    backup = run / 'backup.bin'
    if args.backup:
        shutil.copyfile(args.backup, backup)
    else:
        backup.unlink(missing_ok=True)
    shots = [run / ('shot-%d.png' % n) for n in range(len(shot_frames(args.frames)))]
    for shot in shots:
        shot.unlink(missing_ok=True)
    guest_hash = run / 'guest.hash'
    guest_hash.unlink(missing_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
    extra = [str(args.exe.parent)] + [str(p) for p in (TOOLCHAIN, pathlib.Path('C:/msys64/clang64/bin')) if p.is_dir()]
    env['PATH'] = os.pathsep.join(extra + [env.get('PATH', '')])
    keys = ['2:SIZE=%s' % args.size] + ['%d:WINDOWSHOT=%s' % (f, s.as_posix()) for f, s in zip(shot_frames(args.frames), shots)]
    keys.append('%d:QUIT' % args.frames)
    env.update(SATRECOMP_WINDOW_HIDDEN='1', SATRECOMP_SKIP_CHOOSER='1', SATRECOMP_BACKGROUND_WORKERS='0',
               SATRECOMP_BACKGROUND_STATS='1', SATRECOMP_PRESENTATION_TRACE='1', SATRECOMP_HD_STATS='1',
               SATRECOMP_STRICT_NATIVE='1', SATRECOMP_WINDOW_KEYS=','.join(keys))
    command = [str(args.exe), '--disc', str(args.disc), '--settings', str(run / 'settings.ini'), '--backup', str(backup),
               '--state-load', '0:' + str(args.state), '--mute', '--unthrottled', '--hash-log', str(guest_hash), '--stats',
               '--pc-assets', str(assets)]
    if args.movie:
        command += ['--movie', str(args.movie)]
    return command, env, run, shots


def finish(process, run, args):
    _, err = process.communicate(timeout=args.timeout)
    text = err.decode(errors='replace')
    (run / 'stderr.log').write_text(text, encoding='utf-8')
    return process.returncode, text


def preflight(args):
    problems = []
    if not args.exe.is_file():
        problems.append('executable not found: %s' % args.exe)
    elif not (args.exe.parent / 'art').is_dir():
        problems.append('no art/ folder beside %s (copy it from the build the executable came from)' % args.exe)
    for name in ('state', 'disc'):
        if not getattr(args, name).is_file():
            problems.append('%s not found: %s' % (name, getattr(args, name)))
    if args.backup and not args.backup.is_file():
        problems.append('backup not found: %s' % args.backup)
    if not args.pc_assets.is_dir():
        problems.append('--pc-assets is not a folder: %s' % args.pc_assets)
    else:
        try:
            if not (args.pc_assets / pathlib.Path(*ground_file(args.map).parts)).is_file():
                problems.append('%s is not in --pc-assets' % ground_file(args.map))
        except ValueError as error:
            problems.append(str(error))
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--exe', type=pathlib.Path, required=True)
    ap.add_argument('--state', type=pathlib.Path, required=True)
    ap.add_argument('--pc-assets', type=pathlib.Path, required=True, help='extraction root holding SAKURA2/MAP/MAPnn/MAPnn_A.SPR')
    ap.add_argument('--map', required=True, help='tactical map under test, e.g. MAP14')
    ap.add_argument('--disc', type=pathlib.Path, default=local_path('local/prepared/disc1/game.cue'))
    ap.add_argument('--backup', type=pathlib.Path)
    ap.add_argument('--movie', type=pathlib.Path)
    ap.add_argument('--expect', choices=('drawn', 'not-drawn'), help='exit 1 when the verdict differs (MAP19 is native by review)')
    ap.add_argument('--frames', type=int, default=240)
    ap.add_argument('--size', default='2560x1440')
    ap.add_argument('--out', type=pathlib.Path, default=local_path('local/work') / 'tactical-ground-probe')
    ap.add_argument('--timeout', type=int, default=1800)
    args = ap.parse_args(argv)
    for name in ('exe', 'state', 'pc_assets', 'disc', 'backup', 'movie', 'out'):
        value = getattr(args, name)
        if value is not None:
            setattr(args, name, value.resolve())
    if args.frames < 8:
        ap.error('--frames must be at least 8')
    try:
        width, height = parse_size(args.size)
        rect = centre_rect(width, height)
    except ValueError as error:
        ap.error(str(error))
    problems = preflight(args)
    if problems:
        print('\n'.join('preflight: ' + p for p in problems), file=sys.stderr)
        return 2
    if args.out.is_relative_to(args.pc_assets):
        ap.error('--out must be outside the donor tree')
    args.out.mkdir(parents=True, exist_ok=True)
    trial = pathlib.Path(tempfile.mkdtemp(prefix='trial-', dir=args.out))
    print('Evidence directory: %s' % trial)
    control_root = build_control_root(args.pc_assets, trial / 'control-root', args.map)
    runs = {}
    for label, assets in (('donor', args.pc_assets), ('control', control_root)):
        runs[label] = run_once(args, trial / label, assets)
    # Two executables at once at most (donor and control), well below the three-process limit.
    processes = {label: subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                 for label, (cmd, env, _, _) in runs.items()}
    evidence = {}
    for label, process in processes.items():
        code, text = finish(process, runs[label][2], args)
        run, shots = runs[label][2], runs[label][3]
        guest = (run / 'guest.hash').read_bytes() if (run / 'guest.hash').is_file() else b''
        if code != 0 or not guest_evidence_valid(guest, text, args.frames):
            print('%s run: exit %d or incomplete strict guest evidence, see %s' % (label, code, run / 'stderr.log'), file=sys.stderr)
            return 2
        backup = run / 'backup.bin'
        evidence[label] = (guest, backup.read_bytes() if backup.is_file() else None, shots)
    if evidence['donor'][0] != evidence['control'][0] or evidence['donor'][1] != evidence['control'][1]:
        print('Donor and control guest evidence differs', file=sys.stderr)
        return 2
    changes = [region_changes(a, b, rect) for a, b in zip(evidence['donor'][2], evidence['control'][2])]
    verdict, reason = classify(changes)
    for number, change in enumerate(changes):
        print('capture %d: %s' % (number, 'not comparable' if change is None else
                                  'centre changed %d / %d, outside changed %d' % (change[0], change[2], change[1])))
    print('%s %s: %s' % (args.map, verdict.upper(), reason))
    print('guest hashes identical for %d frames, final SRAM identical, interpreted 0; centre rect %s at %s' % (args.frames, rect, args.size))
    if verdict == 'invalid':
        return 2
    if args.expect:
        return 0 if verdict == args.expect else 1
    return 0 if verdict == 'drawn' else 1


if __name__ == '__main__':
    sys.exit(main())
