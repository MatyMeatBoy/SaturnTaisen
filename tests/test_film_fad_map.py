import json
import unittest
from collections import Counter
from pathlib import Path

MAP = Path(__file__).resolve().parents[1] / 'config' / 'film-fad-map.json'


class FilmFadMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MAP.read_text(encoding='utf-8'))
        cls.streams = cls.data['streams']

    def test_counts(self):
        paired = [s for s in self.streams if s.get('movie')]
        self.assertEqual(len(self.streams), 54)
        self.assertEqual(len(paired), 52)
        self.assertEqual(len(self.streams) - len(paired), 2)
        self.assertEqual(self.data['unpaired_pc'], ['MOVIE118', 'REDLOGO'])
        self.assertEqual(self.data['unpaired_saturn'], [])

    def test_alternate_cuts(self):
        alt = {s['movie'] for s in self.streams if s.get('alternate_cut')}
        self.assertEqual(alt, {f'MOVIE{n:03d}' for n in (4, 9, 11, 20, 102, 105)})

    def test_no_duplicate_fads_and_known_shared_clips(self):
        keys = [(s['disc'], s['fad']) for s in self.streams]
        self.assertEqual(len(keys), len(set(keys)))
        shared = {m for m, n in Counter(s.get('movie') for s in self.streams).items() if n > 1 and m}
        self.assertEqual(shared, {'MOVIE015', 'MOVIE105'})

    def test_entry_shape(self):
        for s in self.streams:
            self.assertEqual(s['fad_hex'], hex(s['fad']).replace('0x', '0x').upper().replace('0X', '0x'))
            self.assertGreater(s['duration'], 0)
            if s.get('movie'):
                self.assertRegex(s['movie'], r'^MOVIE\d{3}$')
                self.assertGreater(s['pc_duration'], 0)


if __name__ == '__main__':
    unittest.main()
