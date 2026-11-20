import json, pathlib, subprocess, sys, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class MenuOpenClassification(unittest.TestCase):
    def test_file_is_current(self):
        r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'menu_open_classification.py'), '--check'])
        self.assertEqual(r.returncode, 0)

    def test_totals_match_register(self):
        d = json.loads((ROOT / 'config' / 'hd-menu-open-classification.json').read_text(encoding='utf-8'))
        self.assertEqual(sum(f['open'] for f in d['families'].values()), d['open_system_images'])
        self.assertEqual(d['open_total'], d['open_system_images'] + d['open_item_pictures'])


if __name__ == '__main__':
    unittest.main()
