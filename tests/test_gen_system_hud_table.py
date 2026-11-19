import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import gen_system_hud_table as g  # noqa: E402

LOCAL = ROOT.parent / 'workspace' / 'local'


def synthetic():
    ev = lambda i, t: {'pc_index': i, 'size': [8, 16], 'texture_sha256': t * 64, 'cram_sha256': 'c' * 64,
                       'cmd_mode': '0080', 'cmd_color': 'A2D0'}
    return {'system': [
        {'id': 'FONT_CSL', 'pc_path': 'S/FONT_CSL.SPR', 'pc_sha256': 'f' * 64, 'status': 'conditional_candidate',
         'saved_command_evidence': [ev(1, 'b'), ev(0, 'a')]},
        {'id': 'BURO_W', 'status': 'no_native_witness', 'saved_command_evidence': []},
        {'id': 'TUIKA_W', 'status': 'needs_layout', 'saved_command_evidence': []},
        {'id': 'OP_WIN', 'status': 'keep_native', 'saved_command_evidence': []},
        {'id': 'KAO', 'status': 'existing_portrait_source', 'saved_command_evidence': []}],
        'wall': {'status': 'existing_backdrop_provenance', 'pc_file': 'W/K.SPR', 'pc_index': 0, 'pc_sha256': 'e' * 64,
                 'saturn_size': [320, 224], 'palette_fnv': '48291f6f1c8a4707'}}


class SystemHudTable(unittest.TestCase):
    def test_build_synthetic(self):
        rows, pending = g.build(synthetic())
        self.assertEqual([(r['kind'], r['index'], r['enabled']) for r in rows],
                         [('command', 0, 0), ('command', 1, 0), ('palette', 0, 0)])
        self.assertEqual(pending, [('BURO_W', 'no_native_witness', 'needs_runtime_witness'),
                                   ('KAO', 'existing_portrait_source', 'existing_route'),
                                   ('OP_WIN', 'keep_native', 'keep_native'),
                                   ('TUIKA_W', 'needs_layout', 'needs_runtime_layout')])

    def test_render_is_deterministic_and_disabled(self):
        text = g.render(*g.build(synthetic()))
        self.assertEqual(text, g.render(*g.build(synthetic())))
        self.assertIn('0x48291F6F1C8A4707ull', text)
        self.assertNotIn(',1},', text)  # nothing enabled before T110a

    def test_real_review_cli(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'h.h'
            r = subprocess.run([sys.executable, str(ROOT / 'tools/gen_system_hud_table.py'),
                                str(ROOT / 'config/hd-system-hud-review.json'), str(out)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('3 entries, 8 pending', r.stdout)
            self.assertEqual(out.read_text(encoding='utf-8').count('"SAKURA1/'), 3)

    def test_real_local_data_read_only(self):
        iso = LOCAL / 'prepared/disc1/Track 01.iso'
        if not iso.is_file():
            self.skipTest('private disc not present')
        review = json.loads((ROOT / 'config/hd-system-hud-review.json').read_text(encoding='utf-8'))
        results = g.verify(review, iso, LOCAL / 'work/pc-cab/out')
        self.assertTrue(results['wall1_sha256'])
        self.assertTrue(results['wall1_palette_fnv'])
        self.assertFalse(any(v is False for v in results.values()), results)


if __name__ == '__main__':
    unittest.main()
