"""Synthetic tests of tools/tactical_ground_probe.py (no runtime, no owner data)."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import tactical_ground_probe as probe  # noqa: E402


class GeometryTests(unittest.TestCase):
    def test_centre_rect_1440p(self):
        self.assertEqual(probe.centre_rect(2560, 1440), (320, 48, 2240, 1392))

    def test_centre_rect_rejects_tiny(self):
        with self.assertRaises(ValueError):
            probe.centre_rect(300, 200)

    def test_parse_size(self):
        self.assertEqual(probe.parse_size('2560x1440'), (2560, 1440))
        with self.assertRaises(ValueError):
            probe.parse_size('big')

    def test_ground_file(self):
        self.assertEqual(str(probe.ground_file('MAP14')), 'SAKURA2/MAP/MAP14/MAP14_A.SPR')
        with self.assertRaises(ValueError):
            probe.ground_file('BG1')

    def test_shot_frames(self):
        self.assertEqual(probe.shot_frames(240), [177, 237])
        self.assertEqual(probe.shot_frames(30), [27])


class VerdictTests(unittest.TestCase):
    def test_drawn(self):
        self.assertEqual(probe.classify([(1000, 0, 10000)])[0], 'drawn')

    def test_not_drawn(self):
        self.assertEqual(probe.classify([(0, 0, 10000), (0, 0, 10000)])[0], 'not-drawn')

    def test_ambiguous(self):
        self.assertEqual(probe.classify([(5, 0, 10000)])[0], 'ambiguous')

    def test_invalid(self):
        self.assertEqual(probe.classify([None])[0], 'invalid')

    def test_guest_evidence(self):
        self.assertTrue(probe.guest_evidence_valid(b'a\nb\n', 'x interpreted 0 (0.00%)', 2))
        self.assertFalse(probe.guest_evidence_valid(b'a\n', 'interpreted 0 (', 2))
        self.assertFalse(probe.guest_evidence_valid(b'a\nb\n', 'interpreted 3 (', 2))


class ControlRootTests(unittest.TestCase):
    def test_only_the_ground_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            donor = pathlib.Path(tmp, 'donor')
            for name in ('MAP14_A.SPR', 'MAP14_B.SPR'):
                (donor / 'SAKURA2/MAP/MAP14').mkdir(parents=True, exist_ok=True)
                (donor / 'SAKURA2/MAP/MAP14' / name).write_bytes(b'x')
            control = probe.build_control_root(donor, pathlib.Path(tmp, 'control'), 'MAP14')
            self.assertFalse((control / 'SAKURA2/MAP/MAP14/MAP14_A.SPR').exists())
            self.assertTrue((control / 'SAKURA2/MAP/MAP14/MAP14_B.SPR').exists())
            self.assertTrue((control / 'SAKURA1').is_dir())


class RegionTests(unittest.TestCase):
    def test_changes_split_by_rect(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Pillow missing')
        with tempfile.TemporaryDirectory() as tmp:
            a, b = pathlib.Path(tmp, 'a.png'), pathlib.Path(tmp, 'b.png')
            Image.new('RGB', (20, 20), (0, 0, 0)).save(a)
            image = Image.new('RGB', (20, 20), (0, 0, 0))
            for x in range(4, 8):
                image.putpixel((x, 5), (9, 0, 0))
            image.putpixel((0, 0), (0, 1, 0))
            image.save(b)
            self.assertEqual(probe.region_changes(a, b, (2, 2, 12, 12)), (4, 1, 100))


if __name__ == '__main__':
    unittest.main()
