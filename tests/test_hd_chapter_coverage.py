import json
from pathlib import Path
import unittest
from tools.hd_chapter_coverage import asset_category, indexed_chapter, film_key



class ChapterCoverageTest(unittest.TestCase):
    def test_asset_kinds_are_explicit(self):
        self.assertEqual(asset_category('/SAKURA2/EVE0101.BIN'), 'scene-pictures')
        self.assertEqual(asset_category('/SAKURA2/EVT01.BIN'), None)
        self.assertEqual(asset_category('/SAKURA2/UNIT01.BIN'), 'tactical-units')
        self.assertEqual(asset_category('/SAKURA2/WKL01.BIN'), 'menus-hud')

    def test_chapter_families_do_not_apply_to_other_assets(self):
        self.assertEqual(indexed_chapter('/SAKURA1/0601FCE.BIN'), 6)
        self.assertEqual(indexed_chapter('/SAKURA1/TITLE10.BIN'), 10)
        self.assertEqual(indexed_chapter('/SAKURA1/BG1001.BIN'), None)
        self.assertEqual(indexed_chapter('/SAKURA2/MAP01.BIN'), None)

    def test_fad_uses_each_inventory_rows_lba_and_offset(self):
        self.assertEqual(film_key({'disc': 2, 'lba': 300}, 4096), (2, 452))


    def test_published_catalog_keeps_replacement_and_occurrence_separate(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf8'))
        by_chapter = {row['chapter']: row for row in catalog['chapters']}
        self.assertEqual([by_chapter[n]['disc'] for n in range(1, 11)], [1]*7 + [2]*3)
        chapter1 = by_chapter[1]['resources']
        self.assertEqual(chapter1['scene-pictures']['1:/SAKURA1/BG1119.BIN']['association'], 'observed')
        self.assertEqual(chapter1['portraits']['0001']['association'], 'inferred')
        self.assertEqual(chapter1['portraits']['00a1']['status'], 'unpaired')
        alternate_cuts = [row for row in catalog['unassigned']['film'].values() if row.get('alternate_cut')]
        self.assertEqual(len({row['pc'] for row in alternate_cuts}), 6)
        self.assertTrue(all(row['status'] == 'paired-not-wired' for row in alternate_cuts))
