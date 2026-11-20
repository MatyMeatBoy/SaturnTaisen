import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from episode_lettering import paint_episode_center, prepared_japanese_track


class EpisodeCenterTests(unittest.TestCase):
    def test_recovers_aligned_donor_and_preserves_approved_lettering(self):
        background = Image.new("RGB", (320, 224), (41, 49, 82))
        ImageDraw.Draw(background).rectangle((20, 87, 145, 95), fill=(88, 140, 108))
        english, japanese = background.copy(), background.copy()
        ImageDraw.Draw(english).rectangle((30, 80, 83, 105), fill=(255, 255, 255))
        ImageDraw.Draw(japanese).rectangle((100, 80, 150, 105), fill=(255, 255, 255))
        lettering = Image.new("RGBA", background.size)
        lettering.putpixel((50, 84), (230, 70, 120, 255))
        result = paint_episode_center(english, lettering, 2, japanese=japanese)
        self.assertEqual(result.getpixel((50, 90)), (88, 140, 108, 255))
        self.assertEqual(result.getpixel((50, 84)), (230, 70, 120, 255))
        self.assertEqual(result.getpixel((115, 91)), (88, 140, 108, 255))
        self.assertEqual(result.getpixel((1, 1)), (41, 49, 82, 255))

    def test_overlap_is_initialized_from_intact_background(self):
        english = Image.new("RGB", (320, 224), (41, 49, 82))
        japanese = english.copy()
        ImageDraw.Draw(english).rectangle((30, 80, 80, 105), fill=(255, 255, 255))
        ImageDraw.Draw(japanese).rectangle((60, 80, 100, 105), fill=(246, 246, 246))
        result = paint_episode_center(english, Image.new("RGBA", english.size), 2, japanese=japanese)
        self.assertEqual(result.getpixel((65, 92)), (41, 49, 82, 255))

    def test_unaligned_donor_keeps_english_fallback(self):
        native = Image.new("RGB", (320, 224), (0, 0, 0))
        ImageDraw.Draw(native).rectangle((30, 80, 80, 105), fill=(255, 255, 255))
        wrong = Image.new("RGB", native.size, (8, 0, 0))
        lettering = Image.new("RGBA", native.size)
        self.assertEqual(paint_episode_center(native, lettering, 2, japanese=wrong).tobytes(),
                         paint_episode_center(native, lettering, 2).tobytes())

    def test_episode_seven_recovers_an_exact_black_plate(self):
        native = Image.new("RGB", (320, 224))
        ImageDraw.Draw(native).rectangle((30, 80, 80, 105), fill=(0, 60, 140))
        result = paint_episode_center(native, Image.new("RGBA", native.size), 7)
        self.assertEqual(result.convert("RGB").getbbox(), None)

    def test_finds_installers_original_disc_but_allows_missing_disc(self):
        with TemporaryDirectory() as folder:
            game = Path(folder)
            english = game / "disc1" / "Track 01.iso"
            self.assertIsNone(prepared_japanese_track(english))
            japanese = game / "disc1-ja" / "Track 01.iso"
            japanese.parent.mkdir()
            japanese.touch()
            self.assertEqual(prepared_japanese_track(english), japanese)
