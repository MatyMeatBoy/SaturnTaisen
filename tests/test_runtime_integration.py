"""Optional real-disc integration checks; all inputs and outputs remain local."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / 'local/build/sakura/sakura.exe'
DISC = ROOT / 'local/prepared/disc1/game.cue'


@unittest.skipUnless(EXE.is_file() and DISC.is_file(), 'requires local runtime and own prepared disc')
class RuntimeTests(unittest.TestCase):
    def test_strict_aot_new_game_route_runs_without_guest_interpreter(self):
        env = os.environ.copy()
        env['PATH'] = 'C:/msys64/clang64/bin' + os.pathsep + env.get('PATH', '')
        env['SATRECOMP_STRICT_NATIVE'] = '1'
        env['SATRECOMP_NO_FUNCTIONS'] = '1'
        env['SATRECOMP_NO_CALLS'] = '1'
        env.pop('SATRECOMP_NO_BLOCKS', None)
        with tempfile.TemporaryDirectory(dir=ROOT / 'local') as directory:
            base = Path(directory)
            movie = base / 'route.movie'
            movie.write_text('650 0800 0\n655 0 0\n2200 0800 0\n2210 0 0\n2320 0400 0\n2330 0 0\n2600 0400 0\n2610 0 0\n3200 0400 0\n3210 0 0\n')
            result = subprocess.run([str(EXE), '--disc', str(DISC), '--headless', '--frames', '4200', '--stats',
                                     '--movie', str(movie), '--backup', str(base / 'backup.bin')],
                                    env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('interpreted 0 (0.00%)', result.stderr)

    def test_boot_cd_track_seek_does_not_take_game_bios_exit_path(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
        env['PATH'] = 'C:/msys64/clang64/bin' + os.pathsep + env.get('PATH', '')
        env.update(SATRECOMP_NO_BLOCKS='1', SATRECOMP_NO_CALLS='1')
        with tempfile.TemporaryDirectory(dir=ROOT / 'local') as directory:
            result = subprocess.run([str(EXE), '--disc', str(DISC), '--headless', '--frames', '600',
                                     '--backup', str(Path(directory) / 'backup.bin')],
                                    env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('BIOS service at 0x0600026C', result.stderr,
                         'CD initialization failed and the game tried to exit to the BIOS')

    def test_strict_aot_boot_runs_without_guest_interpreter(self):
        env = os.environ.copy()
        env['PATH'] = 'C:/msys64/clang64/bin' + os.pathsep + env.get('PATH', '')
        env['SATRECOMP_STRICT_NATIVE'] = '1'
        env['SATRECOMP_NO_FUNCTIONS'] = '1'
        env['SATRECOMP_NO_CALLS'] = '1'
        env.pop('SATRECOMP_NO_BLOCKS', None)
        result = subprocess.run([str(EXE), '--disc', str(DISC), '--headless', '--frames', '600', '--stats',
                                 '--backup', str(ROOT / 'local/work/sakura/strict-positive-backup.bin')],
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('interpreted 0 (0.00%)', result.stderr)

    def test_strict_aot_stops_before_interpreting_untranslated_game_code(self):
        env = os.environ.copy()
        env['PATH'] = 'C:/msys64/clang64/bin' + os.pathsep + env.get('PATH', '')
        env['SATRECOMP_STRICT_NATIVE'] = '1'
        env['SATRECOMP_NO_BLOCKS'] = '1'
        result = subprocess.run([str(EXE), '--disc', str(DISC), '--headless', '--frames', '120',
                                 '--backup', str(ROOT / 'local/work/sakura/strict-test-backup.bin')],
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0, 'strict AOT silently ran an interpreter')
        self.assertIn('strict AOT: untranslated', result.stderr)


if __name__ == '__main__':
    unittest.main()
