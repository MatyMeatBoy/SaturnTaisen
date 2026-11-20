"""T101/S4: the runtime clip table (which carries the PC audio) names exactly the 44 clips whose audio is `pc` (no game data)."""
import json, pathlib, re, sys, tempfile, unittest, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]

class ClipTableAudioGate(unittest.TestCase):
    def test_table_movies_are_the_pc_audio_clips(self):
        with tempfile.TemporaryDirectory() as folder:
            target = pathlib.Path(folder) / 'film_clip_table.h'
            subprocess.run([sys.executable, str(ROOT / 'tools/gen_film_clip_table.py'), str(target)], check=True, capture_output=True)
            movies = {int(m) for m in re.findall(r'\{\d,0x[0-9A-F]+,\d+,(-?\d+)\}', target.read_text())} - {-1}
        audio = json.load(open(ROOT / 'config/clip-audio-map.json', encoding='utf8'))['clips']
        pc = {int(c['movie'][5:]) for c in audio if c['audio'] == 'pc'}
        saturn = {int(c['movie'][5:]) for c in audio if c['audio'] == 'saturn'}
        self.assertEqual(movies, pc)
        self.assertEqual(len(pc), 44)
        self.assertFalse(movies & saturn)

    def test_bounded_video_edits_keep_saturn_audio(self):
        edits = json.loads((ROOT / 'config/film-video-spans.json').read_text(encoding='utf8'))['edits']
        audio = json.loads((ROOT / 'config/clip-audio-map.json').read_text(encoding='utf8'))['clips']
        saturn = {int(clip['movie'][5:]) for clip in audio if clip['audio'] == 'saturn'}
        expected = {(edit['disc'], int(edit['movie'][5:])) for edit in edits}
        with tempfile.TemporaryDirectory() as folder:
            target = pathlib.Path(folder) / 'film_clip_table.h'
            subprocess.run([sys.executable, str(ROOT / 'tools/gen_film_clip_table.py'), str(target)],
                           check=True, capture_output=True)
            actual = {(int(disc), int(movie)) for disc, movie in re.findall(
                r'\{(\d), (\d+), 0x[0-9A-F]+, \d+, \d+, kVideo\w+\}', target.read_text())}
        self.assertEqual(expected, actual)
        self.assertTrue(actual)
        self.assertTrue({movie for _, movie in actual} <= saturn)

if __name__ == '__main__': unittest.main()
