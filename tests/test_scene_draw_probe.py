"""Synthetic tests of tools/scene_draw_probe.py (no runtime, no owner data)."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import scene_draw_probe as probe  # noqa: E402

DRAWN = """background renderer: direct3d11
presentation layer 4 count=41472 bbox=16,8-303,151
scene zoom: image=864x432 scale=3 dialogue=918x201 scale=3 y=488 shadow=12
presentation layout: narrative
scene picture: SAKURA1/BG/BG1209.SPR usable=1
scene picture: SAKURA1/BG/BG9999.SPR usable=0
scene picture with a shared palette 4CABAADB62E5EFAB: cells 0123456789ABCDEF -> SAKURA1/BG/BG1021.SPR
video: 201 frames, the VDP1 drew 201 times
"""
NATIVE = """background renderer: direct3d11
presentation palette: 48291F6F1C8A4707
presentation layout: native
video: 201 frames, the VDP1 drew 201 times
"""


class ParseTests(unittest.TestCase):
    def test_drawn_run(self):
        trace = probe.parse_trace(DRAWN)
        self.assertEqual(trace['pictures'], {'SAKURA1/BG/BG1209.SPR': 1, 'SAKURA1/BG/BG9999.SPR': 0})
        self.assertEqual(trace['shared'], ['SAKURA1/BG/BG1021.SPR'])
        self.assertTrue(trace['zoom'])
        self.assertEqual(trace['layouts'], ['narrative'])
        self.assertEqual(probe.drawn_files(trace), ['SAKURA1/BG/BG1209.SPR', 'SAKURA1/BG/BG1021.SPR'])

    def test_native_run(self):
        trace = probe.parse_trace(NATIVE)
        self.assertFalse(trace['zoom'])
        self.assertEqual(probe.drawn_files(trace), [])
        drew, message = probe.verdict(trace, 0, True)
        self.assertFalse(drew)
        self.assertIn('Zoom scene path never ran', message)
        self.assertIn('native', message)

    def test_verdicts(self):
        trace = probe.parse_trace(DRAWN)
        self.assertTrue(probe.verdict(trace, 1000, False)[0])
        self.assertIn('trace only', probe.verdict(trace, 0, True)[1])
        self.assertIn('no scene picture trace line', probe.verdict(probe.parse_trace(NATIVE), 5, False)[1])
        unusable = probe.parse_trace('scene picture: SAKURA1/BG/BG1.SPR usable=0\nscene zoom: x\n')
        self.assertIn('did not load', probe.verdict(unusable, 0, True)[1])

    def test_count_changed(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Pillow missing')
        with tempfile.TemporaryDirectory() as temp:
            a, b = pathlib.Path(temp) / 'a.png', pathlib.Path(temp) / 'b.png'
            Image.new('RGB', (4, 4), (0, 0, 0)).save(a)
            image = Image.new('RGB', (4, 4), (0, 0, 0))
            image.putpixel((1, 1), (0, 0, 1))
            image.putpixel((2, 3), (9, 0, 0))
            image.save(b)
            self.assertEqual(probe.count_changed(a, a), 0)
            self.assertEqual(probe.count_changed(a, b), 2)
            self.assertIsNone(probe.count_changed(a, pathlib.Path(temp) / 'missing.png'))

    def test_preflight_requires_art_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = pathlib.Path(temp)
            exe = folder / 'sakura-x.exe'
            exe.write_bytes(b'')
            state = folder / 's.state'
            state.write_bytes(b'')
            args = probe.argparse.Namespace(exe=exe, state=state, disc=state, pc_assets=None)
            self.assertTrue(any('art/' in p for p in probe.preflight(args)))
            (folder / 'art').mkdir()
            self.assertEqual(probe.preflight(args), [])


if __name__ == '__main__':
    unittest.main()
