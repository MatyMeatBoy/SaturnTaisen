import pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReleaseMarker(unittest.TestCase):
    def test_every_package_gets_the_release_marker(self):
        source = (ROOT / 'tools/package_release.py').read_text(encoding='utf-8')
        self.assertRegex(source, r"\(app/'release\.marker'\)\.write_text")

    def test_the_marker_sits_beside_the_executable_and_portable_marker(self):
        source = (ROOT / 'tools/package_release.py').read_text(encoding='utf-8')
        self.assertIn("(app/'portable.txt')", source)
        self.assertIn("(app/'release.marker')", source)

    def test_the_patch_gates_every_state_entry_point(self):
        patch = next((ROOT / 'patches').glob('*dev-states-off-in-packages.patch')).read_text(encoding='utf-8')
        for needle in ('DevStatesAllowed', 'release.marker', 'Port::SaveState', 'Port::LoadState', 'SetResetPoint', 'GoToResetPoint',
                       'SDL_SCANCODE_F5', 'SDL_SCANCODE_F2', 'SDL_SCANCODE_F6', 'menu.Open(DevStatesAllowed())'):
            self.assertIn(needle, patch)


if __name__ == '__main__':
    unittest.main()
