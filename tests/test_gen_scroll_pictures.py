"""Synthetic checks of the calibrated-crop options of tools/gen_scroll_pictures.py (no game data needed)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import gen_scroll_pictures as gen  # noqa: E402


class AffineCropOptions(unittest.TestCase):
    FIT = (2000, -20, 570, 0, 320)

    def test_plain_crop_is_unchanged(self):
        self.assertEqual(gen.affine_crop('x', 100, (1992, 0, 569, 8, 312)), (199, 8, 768, 320))
        self.assertEqual(gen.affine_crop('y', 10, (2008, 5, 290, 26, 536)), (26, 25, 562, 315))

    def test_negative_origin(self):
        self.assertEqual(gen.affine_crop('x', 20, self.FIT)[0], 20)
        self.assertEqual(gen.affine_crop('x', 5, self.FIT)[0], -10)  # outside the PC art: the row needs a minimum offset

    def test_end_clamp_keeps_the_crop_inside_the_picture(self):
        fit = (2200, -20, 570, 0, 320)
        self.assertEqual(gen.affine_crop('x', 144, fit, 864, False), (297, 0, 867, 320))
        self.assertEqual(gen.affine_crop('x', 144, fit, 864, True), (294, 0, 864, 320))
        self.assertEqual(gen.affine_crop('y', 144, fit, 864, True), (0, 294, 320, 864))
        # a crop that already fits is not moved
        self.assertEqual(gen.affine_crop('x', 50, fit, 864, True), gen.affine_crop('x', 50, fit))

    def test_registered_options_are_consistent(self):
        for name, options in gen.FIT_OPTIONS.items():
            self.assertIn(name, gen.FITTED_CROPS)
            self.assertLessEqual(set(options), {'min_offset', 'clamp_end'})
            fit = gen.FITTED_CROPS[name]
            first = gen.affine_crop('x', options.get('min_offset', 0), fit)
            self.assertGreaterEqual(first[0], 0, name)


if __name__ == '__main__':
    unittest.main()
