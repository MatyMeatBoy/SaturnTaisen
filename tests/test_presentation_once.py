"""The presentation (4:3 / 16:9) is asked once: nothing preselects it, the game and launcher record presentation_chosen=1."""
import pathlib, re, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEP = ROOT / 'local/deps/satrecomp'
sys.path.insert(0, str(ROOT / 'tools'))


class PresentationOnce(unittest.TestCase):
    def test_default_settings_do_not_preselect(self):
        import taisen_setup
        self.assertNotIn('presentation_mode', taisen_setup.DEFAULT_SETTINGS)
        self.assertNotIn('presentation_chosen', taisen_setup.DEFAULT_SETTINGS)
        bundle = (ROOT / 'tools/package_personal_bundle.py').read_text(encoding='utf8')
        self.assertNotIn('presentation_mode=1', re.search(r"defaults='[^']*'", bundle).group(0))

    def test_widescreen_flag_records_the_choice(self):
        text = (ROOT / 'tools/taisen_setup.py').read_text(encoding='utf8')
        self.assertIn("('features', 'presentation_chosen'): '1'", text)

    @unittest.skipUnless(DEP.is_dir(), 'needs the SDK tree')
    def test_sources(self):
        frontend = (DEP / 'port/frontend_sdl.cpp').read_text(encoding='utf8')
        self.assertIn('!satrecomp::PresentationChosen()', frontend)
        self.assertIn('SATRECOMP_SKIP_CHOOSER', frontend)
        game = (DEP / 'runtime/game.cpp').read_text(encoding='utf8')
        self.assertIn('"presentation_chosen", "1"', game)
        for name in ('sakura_hd.cpp', 'sakura_setup.cpp'):
            text = (DEP / 'launcher/src' / name).read_text(encoding='utf8')
            for line in text.splitlines():
                if 'presentation_mode' in line and 'Save(' in line and '"hd_preload","1"' in line:
                    self.assertIn('presentation_chosen', line, name)
        self.assertNotIn('"hd_preload","1"},{"presentation_mode","1"}})\n', (DEP / 'launcher/src/sakura_hd.cpp').read_text(encoding='utf8'))

    @unittest.skipUnless(DEP.is_dir(), 'needs the SDK tree')
    def test_window_policy(self):
        exe = pathlib.Path(tempfile.mkdtemp()) / 'wp.exe'
        build = subprocess.run(['clang++', '-std=c++20', f'-I{DEP / "port"}', str(ROOT / 'tests/test_window_policy.cpp'), '-o', str(exe)],
                               capture_output=True, text=True)
        if build.returncode and 'not found' in build.stderr + build.stdout:
            self.skipTest('no clang++')
        self.assertEqual(build.returncode, 0, build.stderr)
        self.assertEqual(subprocess.run([str(exe)]).returncode, 0)


if __name__ == '__main__':
    unittest.main()
