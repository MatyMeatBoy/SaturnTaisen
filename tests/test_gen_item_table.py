import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import gen_item_table as g  # noqa: E402


def pair(pal, pc, tier='content', idx=0):
    return {'saturn_file': 'SAKURA1/ITEM01.BIN', 'palette_fnv': pal, 'pc_file': pc, 'pc_image_index': idx, 'tier': tier, 'pc_sha256': 'original'}


class ItemTable(unittest.TestCase):
    def test_filters(self):
        rows = g.build_rows({'pairs': [
            pair('AA', 'A.SPR'), pair('bb', 'B.SPR', 'candidate'),
            pair('CC', 'C.SPR'), pair('CC', 'D.SPR'),  # ambiguous palette
            pair('CC', 'C.SPR'), pair('EE', 'E.SPR', idx=2)]})
        self.assertEqual(rows, [('AA', ('A.SPR', 0)), ('EE', ('E.SPR', 2))])

    def test_only_exact_approved_candidate_is_used(self):
        reviewed = pair('BB', 'B.SPR', 'candidate')
        icon = pair('CC', 'C.SPR', 'candidate')
        review = [dict(reviewed, verdict='confirmed'), dict(icon, verdict='icon_only')]
        data = {'pairs': [reviewed, icon]}
        self.assertEqual(g.build_rows(data, review), [('BB', ('B.SPR', 0))])
        for changed_field, value in [('pc_sha256', 'changed'), ('pc_image_index', 1), ('pc_file', 'D.SPR')]:
            with self.subTest(changed_field=changed_field):
                changed = dict(reviewed, **{changed_field: value})
                self.assertEqual(g.build_rows({'pairs': [changed]}, review), [])

    def test_render_cli_and_real_map(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'item.h'
            r = subprocess.run([sys.executable, str(ROOT / 'tools/gen_item_table.py'),
                                str(ROOT / 'config/hd-item-map.json'), str(out)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            text = out.read_text(encoding='utf-8')
            real = json.loads((ROOT / 'config/hd-item-map.json').read_text(encoding='utf-8'))
            review = json.loads((ROOT / 'config/hd-item-review.json').read_text(encoding='utf-8'))['pairs']
            candidates = {g.review_key(row) for row in real['pairs'] if row['tier'] == 'candidate'}
            self.assertEqual({g.review_key(row) for row in review}, candidates)
            self.assertEqual(len(review), len(candidates))
            self.assertEqual(text.count('ull,"'), real['summary']['content'] + 26)
            self.assertIn('kItemCount', text)


if __name__ == '__main__':
    unittest.main()
