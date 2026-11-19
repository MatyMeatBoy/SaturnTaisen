"""The drafted Spanish episode cards keep each file's size, palette and cell table (needs the owner's disc)."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER = Path(os.environ.get('SAKURA_OWNER_ROOT', ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
import decode_saturn_bg as bg  # noqa: E402

ISO = OWNER / 'local/prepared/disc1/Track 01.iso'
CARDS = OWNER / 'local/work/guion-es/builds/es-portadas/SAKURA1'


@unittest.skipUnless(ISO.is_file() and (CARDS / 'TITLE1.BIN').is_file(), 'needs the owner disc and the drafted cards')
class SpanishCardTests(unittest.TestCase):
    def test_layout_is_preserved(self):
        files = dict(bg.Iso(ISO).files('SAKURA1'))
        iso = bg.Iso(ISO)
        for n in range(1, 11):
            original = iso.content(files[f'TITLE{n}.BIN'])
            card = (CARDS / f'TITLE{n}.BIN').read_bytes()
            self.assertEqual(len(card), len(original))
            self.assertEqual(card[:512 + 4480], original[:512 + 4480])  # palette and cell table untouched
            image = bg.decode(card)
            self.assertEqual(image.size, (320, 224))
            self.assertNotEqual(card, original)

    def test_loading_scroll_keeps_the_layout(self):
        if not (CARDS / 'LOAD.BIN').is_file():
            self.skipTest('LOAD.BIN draft missing')
        original = bg.Iso(ISO).content(dict(bg.Iso(ISO).files('SAKURA1'))['LOAD.BIN'])
        card = (CARDS / 'LOAD.BIN').read_bytes()
        self.assertEqual(len(card), len(original))
        self.assertEqual(card[:512 + 4480], original[:512 + 4480])
        self.assertNotEqual(card, original)
        self.assertEqual(bg.decode(card).size, (320, 224))


if __name__ == '__main__':
    unittest.main()
