"""Synthetic checks for the public HD progress report."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_hd_progress as report


def specimen():
    return {
        'schema': 1,
        'categories': [
            {
                'id': name, 'label': name, 'scope': 'Synthetic', 'unit': 'items',
                'total': 2, 'inventory': 2, 'matched': 2, 'prepared': 2,
                'integrated': 2, 'verified': 2,
                'sources': [{'path': 'docs/research/portrait-animation-coverage.md'}],
                'next': 'Comprobar.',
            }
            for name in report.CATEGORY_IDS
        ],
    }


class HdProgressTests(unittest.TestCase):
    def test_distinguishes_unknown_from_zero(self):
        self.assertEqual(report.format_count(0, 12), '0/12 (0%)')
        self.assertEqual(report.format_count(0, None), '0')
        self.assertEqual(report.format_count(None, 12), 'Sin dato')
        self.assertEqual(report.format_count(1999, 2000), '1999/2000 (99,9%)')

    def test_badges_distinguish_prepared_catalog_from_global_verification(self):
        data=specimen()
        data['categories'][0].update(prepared=1,integrated=1,verified=1)
        text=report.badges(data)
        self.assertIn('Retratos_HD_preparados',text)
        self.assertIn('1%2F2%20%2850%25%29',text)
        self.assertIn('Verificaci%C3%B3n%20pendiente',text)

    def test_requires_evidence_and_consistent_counts(self):
        data = specimen()
        report.validate(data)
        for updates in ({'total': 1}, {'prepared': True}, {'matched': 1},
                        {'sources': []}, {'sources': [{'path': '../local/secret'}]},
                        {'sources': [{'path': 'docs/research/missing.md'}]},
                        {'pending_ids': ['0001', '0001']}, {'verified': -1}):
            invalid = deepcopy(data)
            invalid['categories'][0].update(updates)
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                report.validate(invalid)

    def test_only_full_verified_coverage_can_report_global_completion(self):
        data = specimen()
        self.assertEqual(report.global_status(data), '100% verificado')
        data['categories'][0]['verified'] = None
        self.assertEqual(report.global_status(data), 'Verificación pendiente')
        data['categories'][0]['total'] = None
        self.assertEqual(report.global_status(data), 'Indeterminado')

    def test_body_counts_follow_native_resources_and_shared_donors(self):
        data = specimen()
        body = data['categories'][-1]
        body.update(total=4, inventory=4, matched=2, prepared=None, integrated=2, verified=1)
        resources = {
            '1:/SAKURA1/NC10.BIN': {'status': 'hd', 'pc': 'BODIES/COMMON.SPR'},
            '2:/SAKURA1/NC10.BIN': {'status': 'hd', 'pc': 'BODIES/COMMON.SPR'},
            '1:/SAKURA1/NC11.BIN': {'status': 'hd', 'pc': 'BODIES/COMMON.SPR'},
            '1:/SAKURA1/NC12.BIN': {'status': 'hd', 'pc': 'BODIES/COMMON.SPR'},
            '1:/SAKURA1/NC13.BIN': {'status': 'paired-not-wired', 'pc': 'BODIES/OTHER.SPR'},
        }
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'coverage.json'
            path.write_text(json.dumps({'unassigned': {'bodies': resources}}), encoding='utf-8')
            report.apply_register(data, path)
        self.assertEqual((body['matched'], body['integrated'], body['verified']), (4, 3, 1))

    def test_scene_verification_deduplicates_both_discs_and_requires_an_hd_witness(self):
        data = specimen()
        scene = next(row for row in data['categories'] if row['id'] == 'scene-images')
        scene.update(total=3, inventory=3, matched=3, prepared=None, integrated=2, verified=None)
        witness = {'status': 'hd', 'pc': 'BG/A.SPR', 'verified_in_game': True}
        data_by_disc = {
            '1:/BG/A.BIN': witness,
            '2:/BG/A.BIN': witness,
            '1:/BG/B.BIN': {'status': 'hd', 'pc': 'BG/B.SPR'},
            '2:/BG/C.BIN': {'status': 'paired-not-wired', 'pc': 'BG/C.SPR', 'verified_in_game': True},
        }
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'coverage.json'
            path.write_text(json.dumps({'unassigned': {'scene-pictures': data_by_disc}}), encoding='utf-8')
            report.apply_register(data, path)
        self.assertEqual((scene['integrated'], scene['verified']), (2, 1))

    def test_committed_report_and_readme_are_current(self):
        config = json.loads((ROOT / 'config/hd-progress.json').read_text(encoding='utf-8'))
        report.apply_register(config, ROOT / 'config/hd-chapter-coverage.json')
        report.validate(config)
        self.assertEqual((ROOT / 'docs/HD_PROGRESS.md').read_text(encoding='utf-8'), report.render_report(config))
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertEqual(report.replace_readme(readme, config), readme)
