"""VDP speed work: guest/picture parity and A/B timing between two runtime executables (T103).

Runs a saved state for 1,200 frames in a hidden unthrottled window with the strict-native runtime, writes the
per-frame state hash (it includes the picture) and a 1280x720 window shot of frame 1,198, and optionally the
frame profile (SATRECOMP_FRAME_PROFILE). All inputs are private owner data under SAKURA_OWNER_ROOT (default: the
repository root); nothing here is committed.

  python tools/vdp_parity_bench.py run EXE TAG SCENARIO [--prof]      # writes local/work/vdp-bench/TAG-SCENARIO/
  python tools/vdp_parity_bench.py compare TAG_A TAG_B                # hashes and RGB of the three scenarios
  python tools/vdp_parity_bench.py ab EXE_A EXE_B REPS [SCENARIO...]  # interleaved runs, median video ms

Scenarios: office (office-return-3000 + advance.movie), resume (resume-chapter-6000 + resume-chapter.movie),
attack (chapter1-first-attack + advance.movie). The toolchain's bin directory must be on PATH for the DLLs.
"""
from pathlib import Path
import os
import re
import shutil
import statistics
import subprocess
import sys
import time

ROOT = Path(os.environ.get('SAKURA_OWNER_ROOT', Path(__file__).resolve().parents[1]))
OUT = ROOT / 'local/work/vdp-bench'
FRAMES = 1200
SCENARIOS = {'office': ('office-return-3000.state', 'advance.movie'),
             'resume': ('resume-chapter-6000.state', 'resume-chapter.movie'),
             'attack': ('chapter1-first-attack.state', 'advance.movie')}


def run(exe, tag, scenario, profile=False):
    state, movie = SCENARIOS[scenario]
    folder = OUT / f'{tag}-{scenario}'
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    (folder / 'settings.ini').write_text('[features]\npresentation_mode=1\nscene_view=1\npc_hd_portraits=0\n'
                                         'pc_hd_backgrounds=0\nhd_preload=0\nrun_ahead=0\n', encoding='ascii')
    shutil.copy2(ROOT / 'local/work/sakura/prebattle-immutable-seed.bin', folder / 'backup.bin')
    env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
    env.update(SATRECOMP_STRICT_NATIVE='1', SATRECOMP_WINDOW_HIDDEN='1', SATRECOMP_SKIP_CHOOSER='1',
               SATRECOMP_BACKGROUND_WORKERS='0',
               SATRECOMP_WINDOW_KEYS=f'2:SIZE=1280x720,{FRAMES - 2}:WINDOWSHOT={(folder / "shot.png").as_posix()},{FRAMES}:QUIT')
    if profile:
        env['SATRECOMP_FRAME_PROFILE'] = '1'
    args = [str(exe), '--disc', str(ROOT / 'local/prepared/disc1/game.cue'), '--pc-assets', str(ROOT / 'local/work/v012-prepared-hd'),
            '--state-load', '0:' + str(ROOT / 'local/work/sakura' / state), '--movie', str(ROOT / 'local/work/sakura' / movie),
            '--backup', str(folder / 'backup.bin'), '--settings', str(folder / 'settings.ini'),
            '--hash-log', str(folder / 'frames.hash'), '--stats', '--mute', '--unthrottled']
    began = time.time()
    done = subprocess.run(args, env=env, capture_output=True, timeout=300)
    log = (done.stdout + done.stderr).decode(errors='replace')
    (folder / 'run.log').write_text(log, encoding='utf-8')
    if done.returncode:
        raise RuntimeError(f'{exe} exited {done.returncode} on {scenario}')
    interpreted = re.search(r'interpreted (\d+) \(', log)
    return log, time.time() - began, int(interpreted.group(1)) if interpreted else -1


def compare(a, b):
    from PIL import Image
    for scenario in SCENARIOS:
        x, y = OUT / f'{a}-{scenario}', OUT / f'{b}-{scenario}'
        same_hash = (x / 'frames.hash').read_bytes() == (y / 'frames.hash').read_bytes()
        frames = len((x / 'frames.hash').read_text().splitlines())
        with Image.open(x / 'shot.png') as one, Image.open(y / 'shot.png') as two:
            same_rgb = one.convert('RGB').tobytes() == two.convert('RGB').tobytes()
        print(scenario, 'frames', frames, 'hash-identical', same_hash, 'rgb-identical', same_rgb)


def video_ms(log):
    video = re.search(r'video \(vdp phases\)\s+n=\d+ avg=([\d.]+)', log)
    emulation = re.search(r'emulation\s+n=\d+ avg=([\d.]+)', log)
    return float(video.group(1)), float(emulation.group(1))


def main():
    action = sys.argv[1]
    if action == 'run':
        log, seconds, interpreted = run(sys.argv[2], sys.argv[3], sys.argv[4], '--prof' in sys.argv)
        print(f'{sys.argv[4]} {sys.argv[3]}: {seconds:.1f} s, interpreted {interpreted}')
        print('\n'.join(line for line in log.splitlines() if 'frame profile' in line))
    elif action == 'compare':
        compare(sys.argv[2], sys.argv[3])
    elif action == 'ab':
        exe_a, exe_b, reps = sys.argv[2], sys.argv[3], int(sys.argv[4])
        for scenario in sys.argv[5:] or list(SCENARIOS):
            runs = {'A': [], 'B': []}
            for _ in range(reps):
                for name, exe in (('A', exe_a), ('B', exe_b)):
                    runs[name].append(video_ms(run(exe, 'ab' + name, scenario, True)[0]))
            median = lambda name, i: statistics.median(r[i] for r in runs[name])
            print(f'{scenario}: video ms A {median("A", 0):.3f} B {median("B", 0):.3f}; emulation ms A {median("A", 1):.3f} '
                  f'B {median("B", 1):.3f}; runs A {[r[0] for r in runs["A"]]} B {[r[0] for r in runs["B"]]}', flush=True)


if __name__ == '__main__':
    main()
