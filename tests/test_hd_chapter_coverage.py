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
        eve = chapter1['scene-pictures']['1:/SAKURA2/EVE0101.BIN']
        self.assertEqual((eve['status'], eve['pc']), ('hd', 'SAKURA2/BG/BBG001.SPR'))
        self.assertIs(eve['verified_in_game'], True)
        eve_disc2 = catalog['unassigned']['scene-pictures']['2:/SAKURA2/EVE0101.BIN']
        self.assertEqual(eve_disc2['status'], 'hd')
        self.assertNotIn('verified_in_game', eve_disc2)
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
        chapter2 = by_chapter[2]['resources']
        ground2 = chapter2['tactical-maps']['1:/SAKURA2/MAP02.BIN']
        self.assertEqual((ground2['association'], ground2['status']), ('observed', 'paired-not-wired'))
        self.assertEqual(ground2['pc'], 'SAKURA2/MAP/MAP02/MAP02_A.SPR')
        self.assertIsNone(ground2.get('verified_in_game'))
        self.assertEqual(chapter2['tactical-units']['1:/SAKURA2/UNIT02.BIN']['association'], 'observed')
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
        for name in ('BBG002', 'BBG003', 'BBG004', 'BBG005', 'BBG006', 'BBG007', 'BBG008', 'BBG103', 'BBG104', 'BBG106', 'BBG205', 'BBG235'):
            wired = catalog['unassigned']['scene-pictures'][f'1:/SAKURA2/{name}.BIN']
            self.assertEqual((wired['status'], wired['pc']), ('hd', f'SAKURA2/BG/{name}.SPR'))
            self.assertFalse(wired.get('verified_in_game'))
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
        maria = chapter1['portraits']['0176']
        self.assertEqual((maria['association'], maria['status'], maria['pc_index']), ('observed', 'hd', 373))
        self.assertTrue(maria['verified_in_game'])
        self.assertTrue(maria['runtime_evidence'].endswith('#maria-0176-natural-strip-verification'))
        for offset, movie in ((45410304, 'MOVIE002'), (56039424, 'MOVIE003')):
            clip = chapter1['film'][f'1:/SAKURA4+{offset}']
            self.assertEqual((clip['association'], clip['pc']), ('observed', movie))
        self.assertIn('1:/SAKURA4+0', catalog['unassigned']['film'])
        iris = chapter1['portraits']['00a1']
        emblem = chapter1['portraits']['0169']
        self.assertEqual((iris['status'], iris['pc_index']), ('hd', 160))
        self.assertEqual((emblem['status'], emblem['candidate_pc_indices']), ('excluded', [348, 360]))
        atlas = chapter1['portraits']['1:/SAKURA1/0102FCE.BIN']
        self.assertEqual(atlas['status'], 'hd')
        self.assertIn('00a1', atlas['identities'])
        self.assertEqual(atlas['native_by_design'], ['0169'])
        self.assertNotIn('uncovered', atlas)
        alternate_cuts = [row for row in catalog['unassigned']['film'].values() if row.get('alternate_cut')]
        self.assertEqual(len({row['pc'] for row in alternate_cuts}), 6)
        self.assertTrue(all(row['status'] == 'excluded' for row in alternate_cuts))
        for disc in (1, 2):
            transition = catalog['unassigned']['film'][f'{disc}:/SAKURA1/OPSAKURA.CPK+0']
            self.assertEqual(transition['status'], 'excluded')
            self.assertNotIn('pc', transition)

    def test_chapter7_separates_native_display_from_tactical_residency(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 7)
        for name in ('BG1267', 'BG1268', 'BG2080'):
            with self.subTest(scene=name):
                scene = chapter['scene-pictures'][f'1:/SAKURA1/{name}.BIN']
                self.assertEqual(scene['association'], 'observed')
                self.assertFalse(scene.get('verified_in_game'))
                self.assertIn(f'2:/SAKURA1/{name}.BIN', catalog['unassigned']['scene-pictures'])
        film = chapter['film']['1:/SAKURA4+164800512']
        self.assertEqual((film['association'], film['fad'], film['pc']), ('observed', 80874, 'MOVIE019'))
        self.assertEqual(chapter['tactical-units']['1:/SAKURA2/UNIT10.BIN']['association'], 'resident')
        self.assertEqual(chapter['menus-hud']['1:/SAKURA2/WKL10.BIN']['association'], 'resident')
        self.assertNotIn('1:/SAKURA2/MAP10.BIN', chapter['tactical-maps'])

    def test_chapter8_native_scenes_preserve_donor_decisions(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 8)
        for name, status in (('BG1050', 'hd'), ('BG1212', 'unpaired'), ('BG4187', 'excluded'), ('TITLE8', 'excluded')):
            with self.subTest(scene=name):
                row = chapter['scene-pictures'][f'2:/SAKURA1/{name}.BIN']
                self.assertEqual((row['association'], row['status']), ('observed', status))
                self.assertFalse(row.get('verified_in_game'))
                self.assertNotIn(f'1:/SAKURA1/{name}.BIN', chapter['scene-pictures'])
        self.assertNotIn('2:/SAKURA1/BG1341.BIN', chapter['scene-pictures'])

    def test_chapter10_keeps_native_occurrence_and_hd_witness_separate(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 10)
        for name in ('BG1213', 'BG1160', 'BG4055'):
            with self.subTest(scene=name):
                scene = chapter['scene-pictures'][f'2:/SAKURA1/{name}.BIN']
                self.assertEqual(scene['association'], 'observed')
                self.assertFalse(scene.get('verified_in_game'))
        self.assertEqual(chapter['portraits']['2:/SAKURA1/1001FCE.BIN']['association'], 'resident')
        self.assertTrue(chapter['scene-pictures']['2:/SAKURA1/BG1285.BIN']['verified_in_game'])
        self.assertNotIn('2:/SAKURA2/MAP19.BIN', chapter['tactical-maps'])

    def test_eve202_only_attributes_the_witnessed_disc(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 2)
        eve = chapter['scene-pictures']['1:/SAKURA2/EVE202.BIN']
        self.assertEqual((eve['association'], eve['status']), ('observed', 'hd'))
        self.assertIs(eve['verified_in_game'], True)
        self.assertEqual(eve['runtime_evidence'], 'docs/research/eve202-tactical-inset.md')
        self.assertFalse(catalog['unassigned']['scene-pictures'].get('2:/SAKURA2/EVE202.BIN', {}).get('verified_in_game'))

    def test_bg2338_counterpart_remains_outside_the_runtime_table(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        for disc in (1, 2):
            row = catalog['unassigned']['scene-pictures'][f'{disc}:/SAKURA1/BG2338.BIN']
            self.assertEqual(row['pc'], 'SAKURA1/BG/BG2238.SPR')
            self.assertEqual(row['status'], 'unsupported-size')
            self.assertFalse(row.get('verified_in_game'))

    def test_menu_hud_measure_counts_distinct_pc_images_once(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        groups = [catalog['unassigned']] + [chapter['resources'] for chapter in catalog['chapters']]
        rows = [row for group in groups for row in group['menus-hud'].values()]
        drawn = {(row['pc'], row['pc_image_index']) for row in rows if row['status'] == 'hd'}
        self.assertEqual(len(drawn), 41)
        self.assertEqual(sum(1 for pc, _ in drawn if '/SYSTEM/' in pc), 3)
        self.assertEqual(sum(row.get('images', 0) for row in rows if row['status'] == 'excluded'), 394)
        self.assertEqual(catalog['hud_census'], {'system_images': 572, 'item_images': 50})

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

    def test_ending_bank_donors_are_subimage_pairs_with_no_runtime_claim(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        catalog = catalog['unassigned']['scene-pictures']
        for disc in (1, 2):
            for name in ('AI', 'GE', 'KA', 'KO', 'MA', 'SA', 'SU'):
                with self.subTest(disc=disc, ending=name):
                    row = catalog[f'{disc}:/SAKURA1/{name}_CG.BIN']
                    self.assertEqual((row['association'], row['status']), ('unknown', 'paired-not-wired'))
                    self.assertEqual(row['pc'], f'SAKURA1/ENDING/END_{name}.SPR')
                    self.assertEqual(row['pc_image_indices'], [0, 1, 2, 3] if name == 'GE' else [6, 7])
                    self.assertFalse(row.get('verified_in_game'))

    def test_guarded_viewport_connections_have_no_in_game_witness(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        for disc in (1, 2):
            for name in ('BG1306', 'BG2260'):
                with self.subTest(disc=disc, background=name):
                    row = catalog['unassigned']['scene-pictures'][f'{disc}:/SAKURA1/{name}.BIN']
                    self.assertEqual(row['pc'], f'SAKURA1/BG/{name}.SPR')
                    self.assertEqual(row['status'], 'hd')
                    self.assertFalse(row.get('verified_in_game'))

    def test_short_body_pairs_keep_native_compositing(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        for disc in (1, 2):
            for name in ('NC3125', 'NC3126', 'NC3290', 'NC3517', 'NC4138'):
                with self.subTest(disc=disc, body=name):
                    row = catalog['unassigned']['bodies'][f'{disc}:/SAKURA1/{name}.BIN']
                    self.assertEqual(row['pc'], f'SAKURA1/NC/{name}.SPR')
                    self.assertEqual(row['status'], 'paired-not-wired')
                    self.assertFalse(row.get('verified_in_game'))

    def test_cutout_body_review_is_reflected_in_runtime_coverage(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        review = json.loads((root / 'config/hd-body-review.json').read_text(encoding='utf-8'))
        groups = [catalog['unassigned'], *(chapter['resources'] for chapter in catalog['chapters'])]
        bodies = {key: row for group in groups for key, row in group.get('bodies', {}).items()}
        for disc in (1, 2):
            for name in review['cutout']:
                with self.subTest(disc=disc, body=name):
                    row = bodies[f'{disc}:/SAKURA1/{name}.BIN']
                    self.assertEqual((row['status'], row['pc']), ('hd', f'SAKURA1/NC/{name}.SPR'))

    def test_chapter4_map_pair_and_resident_work_ram_have_distinct_scope(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter4 = catalog['chapters'][3]['resources']
        ground = chapter4['tactical-maps']['1:/SAKURA2/MAP06.BIN']
        self.assertEqual((ground['association'], ground['status']), ('observed', 'paired-not-wired'))
        self.assertEqual(ground['pc'], 'SAKURA2/MAP/MAP06/MAP06_A.SPR')
        self.assertFalse(ground.get('verified_in_game'))
        self.assertTrue(chapter4['tactical-maps']['1:/SAKURA2/MAP21.BIN']['verified_in_game'])
        for name in ('WKL06', 'WKL21'):
            row = chapter4['menus-hud'][f'1:/SAKURA2/{name}.BIN']
            self.assertEqual((row['association'], row['status']), ('resident', 'unknown'))

    def test_chapter5_native_observations_preserve_other_occurrences(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter3 = catalog['chapters'][2]['resources']
        chapter5 = catalog['chapters'][4]['resources']
        background = '1:/SAKURA1/BG1198.BIN'
        self.assertEqual(chapter3['scene-pictures'][background]['association'], 'observed')
        self.assertEqual(chapter5['scene-pictures'][background]['association'], 'observed')
        self.assertFalse(chapter5['scene-pictures'][background].get('verified_in_game'))
        body = chapter5['bodies']['1:/SAKURA1/NC3058.BIN']
        self.assertEqual((body['association'], body['status']), ('observed', 'hd'))
        self.assertFalse(body['verified_in_game'])
        emblem = chapter5['portraits']['0169']
        self.assertEqual((emblem['association'], emblem['status']), ('observed', 'excluded'))
        self.assertEqual(catalog['chapters'][0]['resources']['portraits']['0169']['association'], 'inferred')
        self.assertNotIn('016a', catalog['unassigned']['portraits'])

    def test_chapter9_native_observations_and_residency_are_distinct(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter9 = catalog['chapters'][8]['resources']
        for name in ('BG1072', 'BG1076', 'BG1176', 'BG2098', 'BG2100'):
            row = chapter9['scene-pictures'][f'2:/SAKURA1/{name}.BIN']
            self.assertEqual(row['association'], 'observed')
            self.assertFalse(row.get('verified_in_game'))
        self.assertTrue(chapter9['scene-pictures']['2:/SAKURA1/BG2238.BIN']['verified_in_game'])
        self.assertEqual(chapter9['portraits']['2:/SAKURA1/0901FCE.BIN']['association'], 'resident')
        for identity in ('0001', '00e9'):
            self.assertEqual(chapter9['portraits'][identity]['association'], 'observed')
            self.assertEqual(catalog['chapters'][0]['resources']['portraits'][identity]['association'], 'observed')
