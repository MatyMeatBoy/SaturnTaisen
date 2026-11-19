"""T101/S4: checks config/clip-audio-map.json against config/film-fad-map.json (no game data)."""
import json, pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import gen_clip_audio_map as g

class ClipAudioTests(unittest.TestCase):
    def setUp(self):
        self.d = json.load(open(g.OUT, encoding='utf8'))['clips']
    def test_up_to_date(self):
        self.assertEqual(g.OUT.read_text(encoding='utf8'), json.dumps(g.build(), indent=1) + '\n')
    def test_44_pc_audio_pairs(self):
        pc = [c for c in self.d if c['audio'] == 'pc']
        self.assertEqual(len(pc), 44)
        for c in pc: self.assertLessEqual(abs(c['duration_delta']), 0.5)
    def test_alternate_cuts_keep_saturn_audio(self):
        self.assertEqual({c['movie'] for c in self.d if c['audio'] == 'saturn'},
                         {'MOVIE004', 'MOVIE009', 'MOVIE011', 'MOVIE020', 'MOVIE102', 'MOVIE105'})
        for c in self.d:
            if c['audio'] == 'saturn': self.assertGreater(abs(c['duration_delta']), 0.5)
    def test_every_start_unique(self):
        starts = [(s['disc'], s['fad']) for c in self.d for s in c['starts']]
        self.assertEqual(len(starts), len(set(starts)))

if __name__ == '__main__': unittest.main()
