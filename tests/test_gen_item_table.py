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
    return {'saturn_file': 'SAKURA1/ITEM01.BIN', 'palette_fnv': pal, 'pc_file': pc, 'pc_image_index': idx, 'tier': tier}


class ItemTable(unittest.TestCase):
    def test_filters(self):
        rows = g.build_rows({'pairs': [
            pair('AA', 'A.SPR'), pair('bb', 'B.SPR', 'candidate'),
            pair('CC', 'C.SPR'), pair('CC', 'D.SPR'),  # ambiguous palette
            pair('CC', 'C.SPR'), pair('EE', 'E.SPR', idx=2)]})
        self.assertEqual(rows, [('AA', ('A.SPR', 0)), ('EE', ('E.SPR', 2))])

    def test_render_cli_and_real_map(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'item.h'
            r = subprocess.run([sys.executable, str(ROOT / 'tools/gen_item_table.py'),
                                str(ROOT / 'config/hd-item-map.json'), str(out)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            text = out.read_text(encoding='utf-8')
            real = json.loads((ROOT / 'config/hd-item-map.json').read_text(encoding='utf-8'))
            self.assertEqual(text.count('ull,"'), real['summary']['content'])
            self.assertIn('kItemCount', text)


if __name__ == '__main__':
    unittest.main()
