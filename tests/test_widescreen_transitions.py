"""Replay transitions using local owner fixtures and compare guest frame hashes."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXE = Path(os.environ.get('SAKURA_TRANSITION_TEST_EXE', ROOT / 'local/build/sakura/sakura.exe'))
DISC = ROOT / 'local/prepared/disc1/game.cue'
WORK = ROOT / 'local/work'
SEED = WORK / 'sakura/prebattle-immutable-seed.bin'


@unittest.skipUnless(all(path.is_file() for path in (EXE, DISC, SEED)),
                     'requires the local runtime, translated disc 1, and owner backup fixture')
class WidescreenTransitionTests(unittest.TestCase):
    def capture(self, folder, state, movie, frames, mode):
        folder.mkdir()
        settings = folder / 'settings.ini'
        settings.write_text(
            f'[features]\npreset=custom\npresentation_mode={mode}\nscene_view=1\n'
            'text_style=0\nrun_ahead=0\n',
            encoding='ascii',
        )
        backup = folder / 'backup.bin'
        backup.write_bytes(SEED.read_bytes())
        guest_hash = folder / 'frames.hash'
        env = {key: value for key, value in os.environ.items() if not key.startswith('SATRECOMP_')}
        env.update(
            PATH='C:/msys64/clang64/bin;' + env.get('PATH', ''),
            SATRECOMP_WINDOW_HIDDEN='1',
            SATRECOMP_SKIP_CHOOSER='1',
            SATRECOMP_BACKGROUND_WORKERS='0',
            SATRECOMP_STRICT_NATIVE='1',
            SATRECOMP_PRESENTATION_TRACE='1',
            SATRECOMP_WINDOW_KEYS=f'2:SIZE=1280x720,{frames}:QUIT',
        )
        command = [
            str(EXE), '--disc', str(DISC), '--settings', str(settings), '--backup', str(backup),
            '--state-load', f'0:{state}', '--movie', str(ROOT / 'tests' / movie),
            '--hash-log', str(guest_hash), '--stats', '--mute', '--unthrottled',
        ]
        run = subprocess.run(command, env=env, capture_output=True, timeout=120)
        trace = run.stderr.decode(errors='replace')
        self.assertEqual(run.returncode, 0, trace)
        self.assertIn('interpreted 0 (0.00%)', trace)
        hashes = guest_hash.read_bytes()
        self.assertEqual(len(hashes.splitlines()), frames)
        layouts = re.findall(r'^presentation layout: (\S+)', trace, re.MULTILINE)
        return hashes, layouts

    def replay(self, state_name, movie, frames, start_layout, end_layout):
        state = WORK / state_name
        if not state.is_file():
            self.skipTest(f'requires owner fixture {state_name}')
        with tempfile.TemporaryDirectory(dir=WORK) as temporary:
            folder = Path(temporary)
            original, _ = self.capture(folder / 'original', state, movie, frames, 0)
            enhanced, layouts = self.capture(folder / 'enhanced', state, movie, frames, 1)
        self.assertEqual(original, enhanced)
        self.assertTrue(layouts)
        # The OS can paint one initial frame before the saved guest frame is drawn.
        if layouts[0] == 'native':
            layouts.pop(0)
        self.assertTrue(layouts)
        self.assertEqual((layouts[0], layouts[-1]), (start_layout, end_layout), layouts)
        return layouts

    def test_opening_skip_reaches_title(self):
        self.replay('intro-enhanced/intro1799.state', 'chapter1-opening-skip.movie',
                    900, 'opening', 'title')

    def test_new_game_reaches_story_movie(self):
        self.replay('intro-enhanced/title-final.state', 'chapter1-title-new-game.movie',
                    1500, 'title', 'movie')

    def test_entering_dining_hall_reaches_narrative(self):
        self.replay('sakura/map-room.state', 'chapter1-map-dining-hall.movie',
                    900, 'row-gradient', 'narrative')

    def test_lips_prompt_and_reply_keep_narrative_layout(self):
        layouts = self.replay('sakura/resume-chapter-6000.state', 'chapter1-lips-confirm.movie',
                              450, 'narrative', 'narrative')
        self.assertEqual(layouts, ['narrative'])


if __name__ == '__main__':
    unittest.main()
