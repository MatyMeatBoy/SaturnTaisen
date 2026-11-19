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
        ground = chapter1['tactical-maps']['1:/SAKURA2/MAP01.BIN']
        self.assertEqual((ground['association'], ground['scope']), ('observed', 'source-4 ground only'))
        self.assertEqual(ground['status'], 'hd')
        self.assertNotIn('1:/SAKURA2/MAP01.BIN', catalog['unassigned']['tactical-maps'])
        self.assertEqual(chapter1['scene-pictures']['1:/SAKURA1/BG1119.BIN']['association'], 'observed')
        for name in ('BG1011', 'BG1012', 'BG1017'):
            with self.subTest(scene=name):
                witnessed = chapter1['scene-pictures'].get(f'1:/SAKURA1/{name}.BIN', {})
                self.assertEqual(witnessed.get('association'), 'observed')
                self.assertEqual(witnessed.get('status'), 'hd')
                self.assertIs(witnessed.get('verified_in_game'), True)
                disc2 = catalog['unassigned']['scene-pictures'][f'2:/SAKURA1/{name}.BIN']
                self.assertFalse(disc2.get('verified_in_game'))
        episode2 = by_chapter[2]['resources']['scene-pictures']
        airship = episode2.get('1:/SAKURA2/EVE002.BIN', {})
        self.assertEqual(airship.get('association'), 'observed')
        self.assertEqual(airship.get('status'), 'hd')
        self.assertIs(airship.get('verified_in_game'), True)
        self.assertNotIn('1:/SAKURA2/EVE002.BIN', catalog['unassigned']['scene-pictures'])
        self.assertFalse(catalog['unassigned']['scene-pictures']['1:/SAKURA2/EVE102.BIN'].get('verified_in_game'))
        for name in ('BG1001', 'BG1006', 'BG1209', 'BG2159', 'BG2250', 'BG2251'):
            with self.subTest(campaign_scene=name):
                scene = chapter1['scene-pictures'][f'1:/SAKURA1/{name}.BIN']
                report = 'docs/research/coverage-campaign-v026.md'
                self.assertEqual((scene['evidence'], scene['runtime_evidence']), (report, report))
                self.assertIs(scene['verified_in_game'], True)
        chapter4 = by_chapter[4]['resources']['scene-pictures']
        inset = chapter4['1:/SAKURA2/BBG204.BIN']
        self.assertEqual((inset['association'], inset['status']), ('observed', 'hd'))
        self.assertEqual(inset['pc'], 'SAKURA2/BG/BBG204.SPR')
        self.assertIs(inset['verified_in_game'], True)
        self.assertNotIn('1:/SAKURA2/BBG204.BIN', catalog['unassigned']['scene-pictures'])
        chapter8 = by_chapter[8]['resources']['scene-pictures']
        city = chapter8.get('2:/SAKURA1/BG2159.BIN', {})
        self.assertEqual(city.get('association'), 'observed')
        self.assertEqual(city.get('status'), 'hd')
        self.assertIs(city.get('verified_in_game'), True)
        self.assertEqual(city.get('runtime_evidence'), 'docs/research/bg2159-disc2-visual.md')
        self.assertNotIn('2:/SAKURA1/BG2159.BIN', catalog['unassigned']['scene-pictures'])
        corridor = chapter1['scene-pictures']['1:/SAKURA1/BG1119.BIN']
        self.assertIs(corridor.get('verified_in_game'), True)
        hanami = chapter1['scene-pictures']['1:/SAKURA1/BG1216.BIN']
        self.assertIs(hanami.get('verified_in_game'), True)
        scene = chapter1['scene-pictures']['1:/SAKURA1/BG1116.BIN']
        self.assertEqual(scene['association'], 'observed')
        self.assertFalse(scene.get('verified_in_game'))
        self.assertIn('1:/SAKURA1/BG2004.BIN', catalog['unassigned']['scene-pictures'])
        self.assertIn('2:/SAKURA1/BG1116.BIN', catalog['unassigned']['scene-pictures'])
        body = chapter1['bodies']['1:/SAKURA1/NC51.BIN']
        self.assertEqual(body['association'], 'observed')
        self.assertFalse(body.get('verified_in_game'))
        self.assertEqual(chapter1['portraits']['0001']['association'], 'observed')
        for offset, movie in ((45410304, 'MOVIE002'), (56039424, 'MOVIE003')):
            clip = chapter1['film'][f'1:/SAKURA4+{offset}']
            self.assertEqual((clip['association'], clip['pc']), ('observed', movie))
        self.assertIn('1:/SAKURA4+0', catalog['unassigned']['film'])
        self.assertEqual(chapter1['portraits']['00a1']['status'], 'unpaired')
        alternate_cuts = [row for row in catalog['unassigned']['film'].values() if row.get('alternate_cut')]
        self.assertEqual(len({row['pc'] for row in alternate_cuts}), 6)
        self.assertTrue(all(row['status'] == 'paired-not-wired' for row in alternate_cuts))

    def test_bg2338_counterpart_remains_outside_the_runtime_table(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        for disc in (1, 2):
            row = catalog['unassigned']['scene-pictures'][f'{disc}:/SAKURA1/BG2338.BIN']
            self.assertEqual(row['pc'], 'SAKURA1/BG/BG2238.SPR')
            self.assertEqual(row['status'], 'unsupported-size')
            self.assertFalse(row.get('verified_in_game'))

    def test_pc_title_donors_remain_excluded_in_both_disc_inventories(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        groups = [catalog['unassigned']] + [chapter['resources'] for chapter in catalog['chapters']]
        scenes = {key: row for group in groups for key, row in group['scene-pictures'].items()}
        for disc in (1, 2):
            for episode in range(1, 10):
                row = scenes[f'{disc}:/SAKURA1/TITLE{episode}.BIN']
                self.assertEqual(row['status'], 'excluded')
                self.assertEqual(row['pc'], f'SAKURA1/TITLE/TITLE{episode}.SPR')
                self.assertFalse(row.get('verified_in_game'))
            self.assertEqual(scenes[f'{disc}:/SAKURA1/TITLE10.BIN']['status'], 'unknown')

    def test_bg2238_only_records_the_witnessed_disc_and_chapter(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter9 = next(chapter for chapter in catalog['chapters'] if chapter['chapter'] == 9)
        scene = chapter9['resources']['scene-pictures']['2:/SAKURA1/BG2238.BIN']
        self.assertEqual((scene['status'], scene['association']), ('hd', 'observed'))
        self.assertTrue(scene['verified_in_game'])
        self.assertEqual(scene['runtime_evidence'], 'docs/research/bg2238-still.md')
        disc1 = catalog['unassigned']['scene-pictures']['1:/SAKURA1/BG2238.BIN']
        self.assertFalse(disc1.get('verified_in_game'))
