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

    def test_runtime_table_matches_the_patch(self):
        data = json.loads((ROOT / 'config/hd-item-map.json').read_text(encoding='utf-8'))
        review = json.loads((ROOT / 'config/hd-item-review.json').read_text(encoding='utf-8'))['pairs']
        textures = json.loads((ROOT / 'config/hd-item-texture-fingerprints.json').read_text(encoding='utf-8'))
        rows = g.build_rows(data, review)
        self.assertEqual(len(rows), 41)
        for name, palette in (('ITEM03', '303817C07D8AD3EA'), ('ITEM12', '235B09AEB829FB4C'),
                              ('ITEM27', '61BE6F092AD8446C')):
            with self.subTest(item=name):
                self.assertIn((palette, (f'SAKURA1/ITEM/{name}.SPR', 0)), rows)
        runtime_header = g.render_runtime(rows, textures)
        spec = json.loads((ROOT / 'config/dependencies.json').read_text(encoding='utf-8'))['satrecomp']
        with tempfile.TemporaryDirectory() as directory:
            header = Path(directory) / 'port/item_card_table.h'
            for path in spec['patches']:
                patch = ROOT / path
                if 'diff --git a/port/item_card_table.h ' in patch.read_text(encoding='utf-8'):
                    subprocess.run(['git', 'apply', '--include=port/item_card_table.h', str(patch)],
                                   cwd=directory, check=True)
            self.assertEqual(header.read_text(encoding='utf-8'), runtime_header)

    def test_runtime_table_rejects_mismatched_and_duplicate_fingerprints(self):
        rows = [('AA', ('A.SPR', 0)), ('BB', ('B.SPR', 0))]
        with self.assertRaises(ValueError):
            g.render_runtime(rows, {'AA': '0000000000000001'})
        with self.assertRaises(ValueError):
            g.render_runtime(rows, {'AA': '0000000000000001', 'BB': '0000000000000001'})

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
            self.assertEqual(text.count('ull,"'), real['summary']['content'] + 29)
            self.assertIn('kItemCount', text)


if __name__ == '__main__':
    unittest.main()
