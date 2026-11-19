"""T100/S3: synthetic tests of the FAD -> clip lookup (no game data: only config/film-fad-map.json)."""
import sys, unittest, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import film_clip_hook as h

class ClipHookTests(unittest.TestCase):
    def setUp(self): self.t = h.load_table()
    def test_opening_film_trace(self):
        # T53 trace: the opening film plays `1080 2EC7 ...` = stream 1 of disc 1 = MOVIE001.
        self.assertEqual(h.lookup_play_command(self.t, 1, [0x1080, 0x2EC7, 0x0080, 0x0026])['movie'], 'MOVIE001')
    def test_parse_play(self):
        self.assertEqual(h.parse_play([0x1082, 0x7465, 0x0080, 0x0026]), 0x027465)
        self.assertIsNone(h.parse_play([0x1000, 0x2EC7]))      # bit 7 clear: not an FAD start
        self.assertIsNone(h.parse_play([0x0600, 0x2EC7]))      # not a play
        self.assertIsNone(h.parse_play([0x1080]))
    def test_exact_start_only(self):
        self.assertIsNone(h.lookup_fad(self.t, 1, 0x2EC8))        # resume inside the stream is not mapped
        self.assertIsNone(h.lookup_fad(self.t, 1, 0x289DA))       # 0.15 s logo stub has no PC pair
    def test_same_fad_two_discs(self):
        a = [k for k in self.t if sum(1 for j in self.t if j[1] == k[1]) > 1]
        self.assertTrue(a)                                      # a FAD present on both discs maps per disc
        for d, f in a: self.assertIsNotNone(h.lookup_fad(self.t, d, f))
    def test_table_counts(self):
        self.assertEqual(len({e['movie'] for e in self.t.values()}), 50)
        self.assertEqual(len({e['movie'] for e in self.t.values() if e['alternate_cut']}), 6)
        self.assertEqual(len(self.t), 52)                      # includes the stored-again copies

if __name__ == '__main__': unittest.main()
