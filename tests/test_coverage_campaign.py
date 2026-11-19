import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import coverage_campaign as cc


class CoverageCampaign(unittest.TestCase):
    def test_seeds(self):
        self.assertEqual(cc.parse_seeds('1-3,7'), [1, 2, 3, 7])

    def test_lines_kept_and_dropped(self):
        self.assertTrue(cc.keep_line('body: NC20.BIN usable=1 parts=9 runs=2'))
        self.assertTrue(cc.keep_line('scene picture: SAKURA1/BG/BG1011.SPR usable=1'))
        self.assertFalse(cc.keep_line('scene picture with a shared palette AA: cells BB -> no match'))
        self.assertFalse(cc.keep_line('video: frame 3 differs'))

    def test_summary(self):
        lines = ['body: NC20.BIN usable=1 parts=9', 'body: NC99.BIN usable=0 parts=0',
                 'scene picture: SAKURA1/BG/BG1002.SPR usable=1',
                 'scene picture with a shared palette AA: cells BB -> SAKURA1/BG/BG1012.SPR',
                 'clip: open MOVIE/MOVIE001.MPG -> 1']
        bodies, pictures, clips = cc.summarise(lines)
        self.assertEqual(bodies, ['NC20.BIN'])
        self.assertEqual(pictures, ['SAKURA1/BG/BG1002.SPR', 'SAKURA1/BG/BG1012.SPR'])
        self.assertEqual(clips, ['MOVIE/MOVIE001.MPG'])


if __name__ == '__main__':
    unittest.main()
