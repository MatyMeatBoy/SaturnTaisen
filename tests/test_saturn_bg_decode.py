"""Synthetic check of the Saturn BG*.BIN layout (T67); needs no game data."""
import struct, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import decode_saturn_bg as bg


def sample():
    data = bytearray(bg.SIZE)
    data[:4] = b'\x00\x01\x00\x01'
    # cell 37 (second row, second cell) pixel (3,5) uses palette index 9
    data[bg.HEADER + 37 * 64 + 5 * 8 + 3] = 9
    struct.pack_into('>H', data, bg.PALETTE_AT + 9 * 2, (31 << 10) | (16 << 5) | 8)  # B=31 G=16 R=8
    return bytes(data)


class SaturnBgTests(unittest.TestCase):
    def test_cells_palette_and_size(self):
        image = bg.decode(sample())
        self.assertEqual(image.size, (288, 144))
        self.assertEqual(image.getpixel((8 + 3, 8 + 5)), (8 * 255 // 31, 16 * 255 // 31, 255))
        self.assertEqual(image.getpixel((0, 0)), (0, 0, 0))

    def test_other_sizes_and_headers_are_rejected(self):
        self.assertIsNone(bg.decode(sample()[:-1]))
        self.assertIsNone(bg.decode(b'\x00\x02' + sample()[2:]))

    def test_map_pairs_share_file_number_and_have_a_key(self):
        import json
        path = Path(__file__).resolve().parents[1] / 'config/hd-scene-bg-map.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertGreater(len(data['pairs']), 600)
        for pair in data['pairs']:
            self.assertEqual(len(pair['cells_sha256']), 64)
            self.assertEqual(pair['pc_file'].split('/')[-1][:-4], pair['saturn_file'].split('/')[-1][:-4])
            self.assertIn(pair['tier'], ('content', 'number'))


if __name__ == '__main__':
    unittest.main()
