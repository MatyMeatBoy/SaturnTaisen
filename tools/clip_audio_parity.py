"""S4/T101: guest-hash parity with the PC clip (video and audio) on and off, and the clip-audio trace.

All inputs are private owner data under SAKURA_OWNER_ROOT (default: repository root); nothing here is committed.

  python tools/clip_audio_parity.py run EXE TAG SCENARIO on|off [--sound] [--realtime]
  python tools/clip_audio_parity.py compare TAG_A TAG_B SCENARIO

'on' passes --pc-assets (local/work/pc-cab/out-movie, MOVIE/MOVIEnnn.MPG); 'off' passes none (pure Saturn). The sound is muted
unless --sound; --realtime drops --unthrottled (the audio queue is then paced by the device, as in play). Scenarios: opening
(title-final.state + chapter1-title-new-game.movie, 5,500 frames: MOVIE001), coldskip (cold boot, B at 900: MOVIE000 then
B skip, 1,800 frames), and the T103/T104 bench scenarios office, resume, attack (1,200 frames: no clip). Output in local/work/clip-audio/TAG-SCENARIO/.
The toolchain bin directory must be on PATH for the DLLs.
"""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys

ROOT = Path(os.environ.get('SAKURA_OWNER_ROOT', Path(__file__).resolve().parents[1]))
OUT = ROOT / 'local/work/clip-audio'
SAKURA = ROOT / 'local/work/sakura'
SCENARIOS = {  # name: (state or None, movie, frames)
    'opening': (ROOT / 'local/work/intro-enhanced/title-final.state', ROOT / 'tests/chapter1-title-new-game.movie', 5500),
    'coldskip': (None, ROOT / 'local/work/clip-audio/coldskip.movie', 1800),
    'office': (SAKURA / 'office-return-3000.state', SAKURA / 'advance.movie', 1200),
    'resume': (SAKURA / 'resume-chapter-6000.state', SAKURA / 'resume-chapter.movie', 1200),
    'attack': (SAKURA / 'chapter1-first-attack.state', SAKURA / 'advance.movie', 1200)}


def run(exe, tag, scenario, mode, sound=False, realtime=False):
    state, movie, frames = SCENARIOS[scenario]
    folder = OUT / f'{tag}-{scenario}'
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    (folder / 'settings.ini').write_text('[features]\npreset=custom\npresentation_mode=1\nscene_view=1\npc_hd_portraits=0\n'
                                         'pc_hd_backgrounds=0\nhd_preload=0\nrun_ahead=0\n', encoding='ascii')
    shutil.copytree(Path(__file__).resolve().parents[1] / 'assets/generated', folder / 'art')
    backup = ROOT / ('local/work/intro-enhanced/title-backup.bin' if scenario == 'opening' else
                     'local/work/sakura/prebattle-immutable-seed.bin')
    if state is not None:
        shutil.copy2(backup, folder / 'backup.bin')
    env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_') or k.startswith(('SATRECOMP_CLIP', 'SATRECOMP_PRESENTATION'))}
    env.update(SATRECOMP_STRICT_NATIVE='1', SATRECOMP_WINDOW_HIDDEN='1', SATRECOMP_SKIP_CHOOSER='1', SATRECOMP_BACKGROUND_WORKERS='0',
               SATRECOMP_CLIP_TRACE='1', SATRECOMP_WINDOW_KEYS=f'2:SIZE=1280x720,{frames - 2}:WINDOWSHOT={(folder / "shot.png").as_posix()},{frames}:QUIT')
    args = [str(exe), '--disc', str(ROOT / 'local/prepared/disc1/game.cue'), '--movie', str(movie),
            '--backup', str(folder / 'backup.bin'), '--settings', str(folder / 'settings.ini'),
            '--hash-log', str(folder / 'frames.hash'), '--stats']
    if state is not None:
        args += ['--state-load', '0:' + str(state)]
    if mode == 'on':
        args += ['--pc-assets', str(ROOT / 'local/work/pc-cab/out-movie')]
    if not sound:
        args.append('--mute')
    if not realtime:
        args.append('--unthrottled')
    done = subprocess.run(args, env=env, capture_output=True, timeout=1500)
    log = (done.stdout + done.stderr).decode(errors='replace')
    (folder / 'run.log').write_text(log, encoding='utf-8')
    if done.returncode:
        raise RuntimeError(f'{exe} exited {done.returncode} on {scenario}')
    interpreted = re.search(r'interpreted (\d+) \(', log)
    return int(interpreted.group(1)) if interpreted else -1, [l for l in log.splitlines() if l.startswith('clip')]


def compare(a, b, scenario):
    x, y = OUT / f'{a}-{scenario}', OUT / f'{b}-{scenario}'
    ha, hb = (x / 'frames.hash').read_text().splitlines(), (y / 'frames.hash').read_text().splitlines()
    different = [i for i, (p, q) in enumerate(zip(ha, hb)) if p != q]
    print(scenario, 'frames', len(ha), len(hb), 'hash-identical', ha == hb, 'first difference', different[:1])


def main():
    if sys.argv[1] == 'run':
        interpreted, trace = run(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], '--sound' in sys.argv, '--realtime' in sys.argv)
        print(sys.argv[4], sys.argv[3], sys.argv[5], 'interpreted', interpreted)
        print('\n'.join(trace[:12]))
    else:
        compare(*sys.argv[2:5])


if __name__ == '__main__':
    main()
