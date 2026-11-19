"""T105: the wide/tall background plan follows the committed pair map."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import plan_wide_bg as pw  # noqa: E402


class WideBgPlanTests(unittest.TestCase):
    def test_classes(self):
        self.assertEqual(pw.classify([512, 144]), 'wide_scroll')
        self.assertEqual(pw.classify([288, 296]), 'tall_scroll')
        self.assertEqual(pw.classify([320, 224]), 'full_screen')
        self.assertEqual(pw.classify([320, 144]), 'wide_scroll')

    def test_scale_match(self):
        m = {'pairs': [
            {'saturn_file': 'A', 'decoded': True, 'size': [512, 144], 'tier': 'number', 'pc_file': 'p',
             'pc_size': [1024, 288], 'cells_sha256': 'x'},
            {'saturn_file': 'B', 'decoded': True, 'size': [512, 144], 'tier': 'number', 'pc_file': 'p',
             'pc_size': [1241, 320], 'cells_sha256': 'y'},
            {'saturn_file': 'C', 'decoded': True, 'size': [288, 144], 'tier': 'content', 'pc_file': 'p',
             'pc_size': [576, 288], 'cells_sha256': 'z'}]}
        got = {e['saturn_file']: e for e in pw.plan(m)['entries']}
        self.assertEqual(set(got), {'A', 'B'})
        self.assertTrue(got['A']['scale_match'])
        self.assertFalse(got['B']['scale_match'])

    def test_committed_plan_is_current(self):
        pm = json.loads((ROOT / 'config' / 'hd-scene-bg-map.json').read_text('utf-8'))
        want = json.dumps(pw.plan(pm), indent=1) + '\n'
        self.assertEqual((ROOT / 'config' / 'hd-wide-bg-plan.json').read_text('utf-8'), want)


if __name__ == '__main__':
    unittest.main()
