import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import chapter_jump as cj

BASE = ['# comment', '650 0800 0', '655 0 0']


class ChapterJump(unittest.TestCase):
    def test_slot_one_adds_nothing(self):
        self.assertEqual(cj.build_events(BASE, 1, False, 12000), [(650, '650 0800 0'), (655, '655 0 0')])

    def test_slot_three_steps_down_twice(self):
        frames = [f for f, _ in cj.build_events(BASE, 3, False, 12000)]
        self.assertEqual(frames, [650, 655, 3600, 3608, 3900, 3908])

    def test_advance_presses_a_periodically(self):
        events = cj.build_events(BASE, 1, True, 9700, advance_from=9250, advance_period=200)
        self.assertEqual([l for _, l in events][2:], ['9250 0400 0', '9254 0 0', '9450 0400 0', '9454 0 0', '9650 0400 0', '9654 0 0'])


if __name__ == '__main__':
    unittest.main()
