"""Does the runtime draw the PC scene picture in a headless run? Runs a state with and without the PC donor and says.

A development runtime (no release.marker) is started hidden and unthrottled twice from the same state: once with
`--pc-assets DONOR` (the PC picture can be drawn) and once without it (control). The picture is "drawn" when the donor run prints
a `scene picture: FILE usable=1` line and the capture comparison is reported separately. An unexplained capture difference alone does not identify a scene.

    python tools/scene_draw_probe.py --exe local/build/sakura-probe/sakura-probe.exe \
        --state local/work/probe-cold/b1209.state --pc-assets local/work/pc-cab/out-bg --size 2560x1440

Read docs/research/headless-scene-draw.md first: a runtime copied WITHOUT the `art/` folder that sits beside the original
executable never draws any scene picture (no floral backdrop, so the enhanced presentation is skipped). This tool refuses to run
in that case. Never commit the captures or states it writes (they stay under --out, normally in local/).
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def local_path(relative):
    """`local/...` of this checkout, or of the main workspace when this is a git worktree without its own local/."""
    for base in (ROOT, ROOT.parent / 'workspace'):
        if (base / relative).exists():
            return base / relative
    return ROOT / relative


TOOLCHAIN = ROOT.parent / 'toolkit' / 'msys64' / 'clang64' / 'bin'

PICTURE = re.compile(r'^scene picture: (\S+) usable=(\d)\s*$')
SHARED = re.compile(r'^scene picture with a shared palette (\S+): cells (\S+) -> (\S+\.SPR)\s*$')
LAYOUT = re.compile(r'^presentation layout: (\S+)\s*$')
ZOOM = re.compile(r'^scene zoom: ')


def parse_trace(text):
    """Distinct scene-draw evidence in the stderr text of a run.

    Returns a dict: `pictures` (file -> usable 0/1), `shared` (list of PC files selected by cell hash), `layouts` (in order of first
    appearance) and `zoom` (True when the Zoom scene path ran, which is the only path that draws the picture).
    """
    result = {'pictures': {}, 'shared': [], 'layouts': [], 'zoom': False}
    for raw in text.splitlines():
        line = raw.strip()
        match = PICTURE.match(line)
        if match:
            result['pictures'][match.group(1)] = max(result['pictures'].get(match.group(1), 0), int(match.group(2)))
            continue
        match = SHARED.match(line)
        if match:
            if match.group(3) not in result['shared']:
                result['shared'].append(match.group(3))
            continue
        match = LAYOUT.match(line)
        if match and match.group(1) not in result['layouts']:
            result['layouts'].append(match.group(1))
            continue
        if ZOOM.match(line):
            result['zoom'] = True
    return result


def drawn_files(trace):
    # The shared-palette message is emitted before the file is opened.
    return sorted(name for name, usable in trace['pictures'].items() if usable)


def count_changed(path_a, path_b):
    """Number of pixels that differ between two PNG captures, or None when they cannot be compared (no Pillow, a missing file)."""
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
        diff = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
        return a.width * a.height - diff.histogram()[0]


def verdict(trace, changed):
    """One line: whether the draw happened and which evidence says so."""
    files = drawn_files(trace)
    by_trace = bool(files)
    by_capture = bool(changed)
    if by_trace and by_capture:
        return True, 'DRAWN: %s (trace and capture agree; %s)' % (
            ', '.join(files), '%d pixels differ from the control' % changed if changed is not None else 'the captures differ')
    if by_trace:
        return False, 'trace only: %s (no changed RGB pixels were verified)' % ', '.join(files)
    if by_capture:
        return False, 'capture differs from the control (%s pixels) but no scene picture trace line identifies the cause' % changed
    why = []
    if not trace['zoom']:
        why.append('the Zoom scene path never ran (layouts seen: %s)' % (', '.join(trace['layouts']) or 'none'))
    if trace['pictures'] and not files:
        why.append('the picture was found but its PC file did not load (usable=0)')
    return False, 'NOT DRAWN: ' + ('; '.join(why) or 'the palette of this scene is not in the scene table, or a fade/blend was on screen')


def preflight(args):
    problems = []
    if not args.exe.is_file():
        problems.append('executable not found: %s' % args.exe)
    elif not (args.exe.parent / 'art').is_dir():
        problems.append('no art/ folder beside %s: copy it from the build the executable came from, e.g. '
                        'cp -r local/build/rebuild-evt/art %s/art (without it the floral backdrop is missing, the enhanced '
                        'presentation never runs and no scene picture is ever drawn)' % (args.exe, args.exe.parent))
    if not args.state.is_file():
        problems.append('state not found: %s' % args.state)
    if not args.disc.is_file():
        problems.append('disc not found: %s' % args.disc)
    if args.pc_assets and not args.pc_assets.is_dir():
        problems.append('--pc-assets is not a folder: %s' % args.pc_assets)
    elif args.pc_assets and not (args.pc_assets / 'SAKURA1').is_dir():
        problems.append('--pc-assets has no SAKURA1/ inside (use the extraction root, e.g. local/work/pc-cab/out-bg): %s' % args.pc_assets)
    control = getattr(args, 'control_pc_assets', None)
    if control is not None and not (control / 'SAKURA1').is_dir():
        problems.append('--control-pc-assets must contain SAKURA1/: %s' % control)
    return problems


def run_once(args, run, donor):
    run.mkdir(parents=True, exist_ok=True)
    settings = run / 'settings.ini'
    settings.write_text('[features]\npreset=custom\npresentation_mode=1\nscene_view=1\ntext_style=0\nrun_ahead=0\n')
    backup = run / 'backup.bin'
    if args.backup:
        shutil.copyfile(args.backup, backup)
    else:
        backup.unlink(missing_ok=True)  # the runtime creates a fresh one; an empty file is rejected
    shot = run / 'shot.png'
    shot.unlink(missing_ok=True)
    guest_hash = run / 'guest.hash'
    guest_hash.unlink(missing_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
    extra = [str(args.exe.parent)] + [str(p) for p in (TOOLCHAIN, pathlib.Path('C:/msys64/clang64/bin')) if p.is_dir()]
    env['PATH'] = os.pathsep.join(extra + [env.get('PATH', '')])
    env.update(SATRECOMP_WINDOW_HIDDEN='1', SATRECOMP_SKIP_CHOOSER='1', SATRECOMP_BACKGROUND_WORKERS='0',
               SATRECOMP_BACKGROUND_STATS='1', SATRECOMP_PRESENTATION_TRACE='1', SATRECOMP_HD_STATS='1',
               SATRECOMP_STRICT_NATIVE='1',
               SATRECOMP_WINDOW_KEYS='2:SIZE=%s,%d:WINDOWSHOT=%s,%d:QUIT' % (args.size, args.frames - 3, shot.as_posix(), args.frames))
    command = [str(args.exe), '--disc', str(args.disc), '--settings', str(settings), '--backup', str(backup),
               '--state-load', '0:' + str(args.state), '--mute', '--unthrottled', '--hash-log', str(guest_hash), '--stats']
    if args.movie:
        command += ['--movie', str(args.movie)]
    assets = args.pc_assets if donor else args.control_pc_assets
    if assets is not None:
        command += ['--pc-assets', str(assets)]
    done = subprocess.run(command, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=args.timeout)
    text = done.stderr.decode(errors='replace')
    (run / 'stderr.log').write_text(text, encoding='utf-8')
    return done.returncode, text, shot


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--exe', type=pathlib.Path, required=True)
    ap.add_argument('--state', type=pathlib.Path, required=True)
    ap.add_argument('--pc-assets', type=pathlib.Path, required=True, help='extraction root holding SAKURA1/BG/*.SPR')
    ap.add_argument('--control-pc-assets', type=pathlib.Path, help='matched control pack without the scene SPR under test')
    ap.add_argument('--expect', metavar='SPR', help='skip the control when this donor is not used, for example SAKURA1/BG/BG2057.SPR')
    ap.add_argument('--disc', type=pathlib.Path, default=local_path('local/prepared/disc1/game.cue'))
    ap.add_argument('--backup', type=pathlib.Path, help='backup RAM to copy (default: a fresh one is created)')
    ap.add_argument('--movie', type=pathlib.Path)
    ap.add_argument('--frames', type=int, default=200, help='frames to run after the state (the capture is taken 3 before the end)')
    ap.add_argument('--size', default='1280x720', help='window size, e.g. 2560x1440')
    ap.add_argument('--out', type=pathlib.Path, default=local_path('local/work') / 'scene-draw-probe')
    ap.add_argument('--timeout', type=int, default=900)
    args = ap.parse_args(argv)
    for name in ('exe', 'state', 'pc_assets', 'control_pc_assets', 'disc', 'backup', 'movie', 'out'):
        value = getattr(args, name)
        if value is not None:
            setattr(args, name, value.resolve())
    if args.frames < 6:
        ap.error('--frames must be at least 6')
    problems = preflight(args)
    if problems:
        print('\n'.join('preflight: ' + p for p in problems), file=sys.stderr)
        return 2
    results = {}
    for label, donor in (('donor', True), ('control', False)):
        code, text, shot = run_once(args, args.out / label, donor)
        if code != 0:
            print('%s run exited with %d, see %s' % (label, code, args.out / label / 'stderr.log'), file=sys.stderr)
            return 2
        evidence = args.out / label
        hashes = (evidence / 'guest.hash').read_bytes() if (evidence / 'guest.hash').is_file() else b''
        if len(hashes.splitlines()) != args.frames or not re.search(r'interpreted 0 \(', text):
            print(f'{label}: incomplete strict guest evidence', file=sys.stderr)
            return 2
        backup = evidence / 'backup.bin'
        trace = parse_trace(text)
        if donor and args.expect and args.expect not in drawn_files(trace):
            print(f'SKIP: {args.expect} unused in this replay window; no control run')
            return 1
        results[label] = (trace, shot, hashes, backup.read_bytes() if backup.is_file() else None)
    trace, donor_shot, donor_hashes, donor_backup = results['donor']
    control_trace, control_shot, control_hashes, control_backup = results['control']
    if donor_hashes != control_hashes or donor_backup != control_backup:
        print('Donor and control guest evidence differs', file=sys.stderr)
        return 2
    if not donor_shot.is_file() or not control_shot.is_file():
        print('Missing donor or control capture', file=sys.stderr)
        return 2
    changed = count_changed(donor_shot, control_shot)
    if changed is None:
        print('Cannot compare RGB captures. Check Pillow and the capture dimensions.', file=sys.stderr)
        return 2
    if args.expect and set(drawn_files(trace)) ^ set(drawn_files(control_trace)) != {args.expect}:
        print(f'Cannot isolate {args.expect}; check the donor and control packs', file=sys.stderr)
        return 2
    drew, message = verdict(trace, changed)
    print(message)
    print('layouts: %s; zoom path: %s; control trace lines: %d' % (', '.join(trace['layouts']) or 'none', trace['zoom'],
                                                                   len(drawn_files(results['control'][0]))))
    return 0 if drew else 1


if __name__ == '__main__':
    sys.exit(main())
