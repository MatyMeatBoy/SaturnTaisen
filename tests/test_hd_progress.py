"""Synthetic checks for the public HD progress report."""
from copy import deepcopy
import json
from pathlib import Path
import sys
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

    def test_committed_report_and_readme_are_current(self):
        config = json.loads((ROOT / 'config/hd-progress.json').read_text(encoding='utf-8'))
        report.validate(config)
        self.assertEqual((ROOT / 'docs/HD_PROGRESS.md').read_text(encoding='utf-8'), report.render_report(config))
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertEqual(report.replace_readme(readme, config), readme)
