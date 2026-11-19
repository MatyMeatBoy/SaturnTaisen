"""Synthetic check of the Saturn BG*.BIN layouts (T67); needs no game data except the pair map."""
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import decode_saturn_bg as bg  # noqa: E402


def sample():
    data = bytearray(bg.SIZE)
    data[:4] = bytes([0, 1, 0, 1])
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

    def test_variant_b_has_size_in_header_and_palette_first(self):
        data = bytearray(0x210 + 4 * 2 * 64)
        data[:8] = bytes([0, 1, 0, 2, 0, 4, 0, 2])
        struct.pack_into('>H', data, 0x10 + 7 * 2, 31)  # palette 7 = R31
        data[0x210 + 5 * 64 + 8 + 2] = 7  # cell 5 = (1,1), pixel (2,1)
        image = bg.decode(bytes(data))
        self.assertEqual(image.size, (32, 16))
        self.assertEqual(image.getpixel((8 + 2, 8 + 1)), (255, 0, 0))

    def test_variant_d_full_screen_picture_with_u32_table(self):
        data = bytearray(512 + 4480 + 1120 * 64)
        for cell in range(1120):
            struct.pack_into('>I', data, 512 + cell * 4, cell * 2)
        struct.pack_into('>H', data, 5 * 2, 31)  # palette 5 = R31
        data[512 + 4480 + 41 * 64 + 3 * 8 + 4] = 5  # cell 41 = (1,1), pixel (4,3)
        image = bg.decode(bytes(data))
        self.assertEqual(image.size, (320, 224))
        self.assertEqual(image.getpixel((8 + 4, 8 + 3)), (255, 0, 0))
        self.assertIsNone(bg.decode(bytes(data[:70000])))

    def test_title_cards_start_their_table_at_two(self):
        data = bytearray(512 + 4480 + 1121 * 64)
        for cell in range(1120):
            struct.pack_into('>I', data, 512 + cell * 4, cell * 2 + 2)
        struct.pack_into('>H', data, 3 * 2, 31)  # palette 3 = R31
        data[512 + 4480 + 1 * 64 + 2 * 8 + 5] = 3  # tile 1 is the first cell: pixel (5,2)
        image = bg.decode(bytes(data))
        self.assertEqual(image.size, (320, 224))
        self.assertEqual(image.getpixel((5, 2)), (255, 0, 0))

    def test_screen_map_has_firm_eyecatches(self):
        import json
        data = json.loads((ROOT / 'config/hd-screen-map.json').read_text(encoding='utf-8'))
        firm = [p for p in data['pairs'] if p['tier'] == 'content']
        self.assertEqual(len(firm), 16)
        for pair in firm:
            self.assertGreaterEqual(pair['correlation'], 0.95)
            self.assertTrue(pair['pc_file'].startswith('SAKURA1/ICATCH/'))

    def test_other_sizes_and_headers_are_rejected(self):
        self.assertIsNone(bg.decode(sample()[:-1]))
        self.assertIsNone(bg.decode(bytes([0, 2]) + sample()[2:]))
        self.assertIsNone(bg.decode(bytes([0, 1, 0, 2, 0xFF, 0xFF, 0xFF, 0xFF]) + bytes(0x300)))

    def test_map_pairs_share_file_number_and_have_a_key(self):
        data = json.loads((ROOT / 'config/hd-scene-bg-map.json').read_text(encoding='utf-8'))
        self.assertGreater(len(data['pairs']), 600)
        for pair in data['pairs']:
            if pair['tier'] == 'missing':
                continue
            self.assertEqual(len(pair['cells_sha256']), 64)
            self.assertEqual(pair['pc_file'].split('/')[-1][:-4], pair['saturn_file'].split('/')[-1][:-4])
            self.assertIn(pair['tier'], ('content', 'number'))


if __name__ == '__main__':
    unittest.main()
