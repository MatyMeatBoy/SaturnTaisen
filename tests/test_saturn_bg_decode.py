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

    def variant_b_sample(self):
        table_at = 0x610
        tile_at = table_at + 4 * 4
        data = bytearray(tile_at + 2 * 64)
        struct.pack_into('>4H', data, 0, 1, 2, 4, 1)
        struct.pack_into('>H', data, 8, 2)
        struct.pack_into('>H', data, 0x10 + 7 * 2, 31)  # palette 7 = R31
        struct.pack_into('>4I', data, table_at, 2, 0x40000002, 0x80000002, 0xC0000002)
        data[tile_at + 64 + 8 + 2] = 7  # second tile, pixel (2,1)
        return data, tile_at

    def test_variant_b_maps_reused_tiles_and_flips_independently(self):
        data, tile_at = self.variant_b_sample()
        image = bg.decode(data)
        self.assertEqual(image.size, (32, 8))
        for x, y in [(2, 1), (13, 1), (18, 6), (29, 6)]:
            self.assertEqual(image.getpixel((x, y)), (255, 0, 0))
        self.assertIn((4, (255, 0, 0)), image.getcolors())
        self.assertEqual(bg.picture_bytes(data), data[tile_at:])

    def test_variant_b_counts_physical_tiles_when_declared_count_is_high(self):
        data, _ = self.variant_b_sample()
        struct.pack_into('>H', data, 8, 5)  # BG4302-like count, higher than the payload
        self.assertIsNotNone(bg.decode(data))
        self.assertIsNone(bg.decode(data[:-1]))
        self.assertIsNone(bg.picture_bytes(data[:-1]))

    def test_variant_b_rejects_pattern_names_outside_the_tile_payload(self):
        data, _ = self.variant_b_sample()
        struct.pack_into('>I', data, 0x610, 4)
        self.assertIsNone(bg.decode(data))
        self.assertIsNone(bg.picture_bytes(data))

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

    def test_nc_body_is_a_flat_bitmap_after_its_palette(self):
        width, height = 64, 144
        data = bytearray(0x610 + width * height + 6000)
        data[:2] = bytes([0, 2])
        struct.pack_into('>H', data, 0x410 + 4 * 2, 31)  # palette 4 = R31
        # a smooth ramp that changes slowly from row to row, so the stride detector finds rows of 40 pixels
        for i in range(width * height + 6000):
            data[0x610 + i] = (i % width) // 3 + 1 + (i // width) // 8  # rows differ a little, so only the true stride is closest
        data[0x610 + 3 * width + 7] = 4
        image = bg.decode_nc(bytes(data))
        self.assertEqual(image.size[1], 144)
        self.assertEqual(image.size[0], width)
        self.assertEqual(image.getpixel((7, 3)), (255, 0, 0, 255))

    def test_body_map_has_firm_pairs(self):
        import json
        data = json.loads((ROOT / 'config/hd-body-map.json').read_text(encoding='utf-8'))
        firm = [p for p in data['pairs'] if p['tier'] == 'content']
        self.assertGreaterEqual(len(firm), 100)
        for pair in firm:
            self.assertEqual(pair['same_name_pc'], pair['best_pc'])
            self.assertGreaterEqual(pair['same_name_correlation'], 0.75)

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
            if pair['saturn_file'].startswith('SAKURA2/EVE'):
                # An event picture is paired by eye with a PC battle background of another name (tools/add_eve_pairs.py).
                self.assertTrue(pair['pc_file'].startswith('SAKURA2/BG/BBG'))
                self.assertGreaterEqual(pair['correlation'], 0.8)
                continue
            self.assertEqual(pair['pc_file'].split('/')[-1][:-4], pair['saturn_file'].split('/')[-1][:-4])
            self.assertIn(pair['tier'], ('content', 'number'))


if __name__ == '__main__':
    unittest.main()
