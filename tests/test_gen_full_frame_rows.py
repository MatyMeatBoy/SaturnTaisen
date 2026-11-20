import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import gen_full_frame_rows as g  # noqa: E402


def candidate(minimum=0.95, box=(74, 33, 615, 425), pc=(640, 480), native=(320, 224)):
    return {'native': list(native), 'pc': list(pc), 'passes_floor': minimum >= 0.90, 'min': minimum, 'best_boxes': [list(box)]}


def resolver(palette_for=lambda name: name.encode().hex().upper().ljust(16, '0')[:16], pc=(640, 480)):
    def resolve(name):
        return {'disc': 2, 'native_bytes': 100, 'native_fnv': '0' * 16, 'palette': palette_for(name), 'rgb': '1' * 16,
                'pc_file': f'SAKURA2/BG/{name}.SPR', 'pc_bytes': 10, 'pc_fnv': '2' * 16, 'pc_size': list(pc)}
    return resolve


class FullFrameRows(unittest.TestCase):
    def test_floor_and_box_filter(self):
        rows, skipped = g.build_rows({
            'BBG238': candidate(), 'BBG239': candidate(0.848),
            'BG2093': candidate(native=(320, 144)),          # not a battle frame
            'BBG243': candidate(box=(0, 0, 640, 100)),       # too thin: a different composition
            'BBG300': candidate(box=(8, 0, 640, 473)),
        }, resolver())
        self.assertEqual([r['name'] for r in rows], ['BBG238', 'BBG300'])
        self.assertEqual(rows[0]['crop'], {'x': 74, 'y': 33, 'w': 541, 'h': 392})
        self.assertIn('floor', skipped['BBG239'])
        self.assertIn('too little', skipped['BBG243'])
        self.assertNotIn('BG2093', skipped)

    def test_box_must_stay_inside_the_pc_picture(self):
        for box in [(0, 0, 641, 480), (-1, 0, 600, 400), (300, 0, 300, 400)]:
            with self.assertRaises(ValueError):
                g.crop_from_box(box, (640, 480))
        self.assertEqual(g.crop_from_box((0, 0, 640, 480), (640, 480)), {'x': 0, 'y': 0, 'w': 640, 'h': 480})

    def test_stretched_aspect_is_rejected(self):
        with self.assertRaises(ValueError):
            g.crop_from_box((0, 0, 640, 300), (640, 480))

    def test_pc_size_mismatch_and_missing_files_are_skipped(self):
        rows, skipped = g.build_rows({'BBG238': candidate()}, resolver(pc=(800, 600)))
        self.assertEqual(rows, [])
        self.assertIn('size differs', skipped['BBG238'])
        rows, skipped = g.build_rows({'BBG238': candidate()}, lambda name: None)
        self.assertIn('not on the prepared discs', skipped['BBG238'])

    def test_shared_palette_drops_both_rows(self):
        rows, skipped = g.build_rows({'BBG238': candidate(), 'BBG240': candidate()}, resolver(lambda name: 'A' * 16))
        self.assertEqual(rows, [])
        self.assertEqual(sorted(skipped), ['BBG238', 'BBG240'])

    def test_rgb_hash_is_fnv_of_widened_channels(self):
        from PIL import Image
        image = Image.new('RGB', (2, 1))
        image.putpixel((0, 0), (255, 0, 8))
        image.putpixel((1, 0), (0, 255, 0))
        self.assertEqual(g.saturn_frame_bytes(image), bytes([248, 0, 8, 0, 248, 0]))
        self.assertEqual(g.fnv(b''), 0xcbf29ce484222325)
        self.assertEqual(g.fnv(b'a'), 0xaf63dc4c8601ec8c)

    def test_header_row_format(self):
        rows, _ = g.build_rows({'BBG238': candidate()}, resolver())
        text = g.render_header(rows)
        self.assertIn('{"BBG238", 0x', text)
        self.assertTrue(text.rstrip().endswith('640, 480, {74, 33, 541, 392}},'))

    def test_committed_table_matches_the_data_file(self):
        data = json.loads((ROOT / 'config/hd-full-frames.json').read_text(encoding='utf-8'))
        names = [r['name'] for r in data['rows']]
        self.assertEqual(names, ['BBG238', 'BBG240', 'BBG241', 'BBG242', 'BBG243', 'BBG300'])
        self.assertEqual(list(data['skipped']), ['BBG239'])
        candidates = json.loads((ROOT / 'config/hd-size-candidates.json').read_text(encoding='utf-8'))
        for r in data['rows']:
            c = candidates[r['name']]
            self.assertEqual(g.crop_from_box(c['best_boxes'][0], (r['pc_width'], r['pc_height'])), r['crop'])
        self.assertEqual(len({r['palette'] for r in data['rows']}), len(data['rows']))


if __name__ == '__main__':
    unittest.main()
