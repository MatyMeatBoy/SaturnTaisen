"""Synthetic tests for tools/measure_size_candidates.py (TP2a-size). No game pixels."""
import sys, unittest
from importlib.util import find_spec
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
HAS_NUMPY = find_spec("numpy") is not None
if HAS_NUMPY:
    import numpy as np
    import measure_size_candidates as m


def texture(w, h, seed=1):
    rng = np.random.default_rng(seed)
    base = rng.integers(0, 255, (h // 8 + 1, w // 8 + 1, 3), dtype=np.uint8)
    return Image.fromarray(base).resize((w, h), Image.BICUBIC)


@unittest.skipUnless(HAS_NUMPY, "offline crop audit requires NumPy")
class SizeCandidates(unittest.TestCase):
    def test_free_box_recovers_a_scaled_crop(self):
        pc = texture(800, 320)
        native = pc.crop((200, 20, 200 + 576, 20 + 288)).resize((288, 144), Image.BOX)
        score, box = m.best_box(native, pc, [1.9, 2.0, 2.1], [1.9, 2.0, 2.1], work=0.5)
        self.assertGreater(score, 0.97)
        self.assertLess(abs(box[0] - 200), 8)
        self.assertLess(abs(box[1] - 20), 8)

    def test_unrelated_picture_stays_below_the_floor(self):
        score, _ = m.best_box(texture(288, 144, 7), texture(800, 320, 9), [2.0], [2.0], work=0.5)
        self.assertLess(score, m.FLOOR)


if __name__ == '__main__':
    unittest.main()
