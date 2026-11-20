import json
from pathlib import Path
import unittest
from tools import hd_chapter_coverage as coverage
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


    def test_chapter5_intermission_has_verified_hd_draw_on_disc1(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter5 = catalog['chapters'][4]['resources']['scene-pictures']
        row = chapter5['1:/SAKURA1/IC0501.BIN']
        self.assertEqual((row['association'], row['status']), ('observed', 'hd'))
        self.assertEqual(row['pc'], 'SAKURA1/ICATCH/IC0501.SPR')
        self.assertTrue(row['verified_in_game'])
        self.assertEqual(row['runtime_evidence'], 'docs/research/ic0501-intermission-witness.md#enhanced-presentation')
        disc2 = catalog['unassigned']['scene-pictures']['2:/SAKURA1/IC0501.BIN']
        self.assertEqual(disc2['status'], 'paired-not-wired')
        self.assertFalse(disc2.get('verified_in_game'))

    def test_ic_table_controlled_draws_leave_natural_occurrence_unverified(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        table = json.loads((root / 'config/hd-ic-table.json').read_text(encoding='utf-8'))
        rows = dict(catalog['unassigned']['scene-pictures'])
        for chapter in catalog['chapters']:
            rows.update(chapter['resources']['scene-pictures'])
        witnessed = {'1:/SAKURA1/IC0501.BIN', '1:/SAKURA1/IC03.BIN'}
        controlled = {'IC02', 'IC04', 'IC0502', 'IC06', 'IC07', 'IC08', 'IC09',
                      'IC1001', 'IC1002', 'IC1003', 'IC1004', 'IC1005', 'IC1006'}
        self.assertEqual(coverage.IC_CONTROLLED_IDS, controlled)
        for entry in table['entries']:
            key = f"1:/SAKURA1/{entry['id']}.BIN"
            if key in witnessed:
                self.assertEqual(rows[key]['status'], 'hd')
                continue
            row = rows[key]
            self.assertFalse(row['verified_in_game'], key)
            self.assertEqual(row['association'], 'unknown', key)
            self.assertNotIn('runtime_evidence', row, key)
            self.assertEqual(row['pc'], entry['pc_file'])
            if entry['id'] in controlled:
                self.assertEqual(row['status'], 'hd', key)
                self.assertEqual(row['fixture_evidence'],
                                 'docs/research/ic-intermission-table.md#controlled-disc-1-runtime-verification')
            else:
                self.assertEqual(row['status'], 'wired-unverified', key)
                self.assertNotIn('fixture_evidence', row, key)
            disc2 = f"2:/SAKURA1/{entry['id']}.BIN"
            if entry['id'] == 'IC08':
                self.assertEqual((rows[disc2]['status'], rows[disc2]['association']), ('hd', 'observed'))
                self.assertTrue(rows[disc2]['verified_in_game'])
            if entry['id'] not in ('IC06', 'IC08'):
                self.assertEqual(rows[disc2]['status'], 'paired-not-wired', disc2)

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
        self.assertEqual((ground2['association'], ground2['status']), ('observed', 'hd'))
        self.assertEqual(ground2['pc'], 'SAKURA2/MAP/MAP02/MAP02_A.SPR')
        self.assertIs(ground2.get('verified_in_game'), True)
        self.assertEqual(ground2['scope'], 'source-4 ground only')
        self.assertEqual(chapter2['tactical-units']['1:/SAKURA2/UNIT02.BIN']['association'], 'observed')
        episode2 = by_chapter[2]['resources']['scene-pictures']
        airship = episode2.get('1:/SAKURA2/EVE002.BIN', {})
        self.assertEqual(airship.get('association'), 'observed')
        self.assertEqual(airship.get('status'), 'hd')
        self.assertIs(airship.get('verified_in_game'), True)
        self.assertNotIn('1:/SAKURA2/EVE002.BIN', catalog['unassigned']['scene-pictures'])
        controlled_eve = {'EVE102', 'EVE105', 'EVE205', 'EVE207'}
        self.assertEqual(coverage.EVE_CONTROLLED_INSETS, controlled_eve)
        for name in controlled_eve:
            plate = catalog['unassigned']['scene-pictures'][f'1:/SAKURA2/{name}.BIN']
            self.assertEqual((plate['status'], plate['association']), ('hd', 'unknown'))
            self.assertFalse(plate['verified_in_game'])
            self.assertEqual(plate['fixture_evidence'],
                             'docs/research/disc1-battle-insets.md#controlled-eve-plate-replays')
            self.assertNotIn('runtime_evidence', plate)
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
        ground13 = by_chapter[8]['resources']['tactical-maps']['2:/SAKURA2/MAP13.BIN']
        self.assertEqual((ground13['association'], ground13['status']), ('observed', 'hd'))
        self.assertIs(ground13['verified_in_game'], True)
        self.assertEqual(ground13['runtime_evidence'], coverage.STAGE13_REPORT)
        ground12 = by_chapter[8]['resources']['tactical-maps']['2:/SAKURA2/MAP12.BIN']
        self.assertEqual((ground12['association'], ground12['status']), ('observed', 'hd'))
        self.assertIs(ground12['verified_in_game'], True)
        self.assertEqual(ground12['scope'], 'source-4 ground only')
        self.assertEqual(ground12['runtime_evidence'], coverage.STAGE12_REPORT)
        self.assertEqual(catalog['unassigned']['tactical-maps']['2:/SAKURA2/MAP15.BIN']['status'],
                         'paired-not-wired')
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
        self.assertTrue(scene['verified_in_game'])
        self.assertFalse(catalog['unassigned']['scene-pictures']['2:/SAKURA1/BG1116.BIN'].get('verified_in_game'))
        for name in ('BG1143', 'BG2004'):
            scene = chapter1['scene-pictures'][f'1:/SAKURA1/{name}.BIN']
            self.assertEqual(scene['association'], 'observed')
            self.assertTrue(scene['verified_in_game'])
        for name in ('BG1144', 'BG2005'):
            sibling = catalog['unassigned']['scene-pictures'][f'1:/SAKURA1/{name}.BIN']
            self.assertEqual(sibling['association'], 'unknown')
            self.assertFalse(sibling.get('verified_in_game'))
        self.assertIn('2:/SAKURA1/BG1116.BIN', catalog['unassigned']['scene-pictures'])
        body = chapter1['bodies']['1:/SAKURA1/NC51.BIN']
        self.assertEqual(body['association'], 'observed')
        self.assertTrue(body['verified_in_game'])
        self.assertTrue(body['native_face_fallback'])
        self.assertEqual(body['runtime_evidence'], 'docs/research/nc51-registered-faces.md')
        sakura = chapter1['bodies']['1:/SAKURA1/NC12.BIN']
        self.assertTrue(sakura['verified_in_game'])
        self.assertTrue(sakura['native_face_fallback'])
        self.assertEqual(sakura['runtime_evidence'], 'docs/research/nc12-registered-faces.md')
        unwitnessed = chapter1['bodies']['1:/SAKURA1/NC3004.BIN']
        self.assertEqual(unwitnessed['association'], 'observed')
        self.assertFalse(unwitnessed.get('verified_in_game'))
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
        self.assertEqual((iris['association'], iris['status'], iris['pc_index']), ('observed', 'hd', 160))
        self.assertTrue(iris['verified_in_game'])
        self.assertTrue(iris['runtime_evidence'].endswith('#iris-00a1-command-room-portrait'))
        self.assertNotIn('00a1', catalog['chapters'][6]['resources']['portraits'])
        self.assertEqual((emblem['association'], emblem['status'], emblem['pc_index']), ('observed', 'hd', 360))
        self.assertTrue(emblem['verified_in_game'])
        atlas = chapter1['portraits']['1:/SAKURA1/0102FCE.BIN']
        self.assertEqual(atlas['status'], 'hd')
        self.assertIn('00a1', atlas['identities'])
        self.assertEqual(atlas['association'], 'resident')
        self.assertFalse(atlas.get('verified_in_game'))
        self.assertIn('0169', atlas['identities'])
        self.assertNotIn('native_by_design', atlas)
        self.assertNotIn('uncovered', atlas)
        films = dict(catalog['unassigned']['film'])
        for chapter in catalog['chapters']:
            films.update(chapter['resources']['film'])
        alternate_cuts = [row for row in films.values() if row.get('alternate_cut')]
        self.assertEqual(len({row['pc'] for row in alternate_cuts}), 6)
        self.assertTrue(all(row['status'] == 'bounded' and row['audio'] == 'saturn'
                            and row['pc_video_spans'] for row in alternate_cuts))
        self.assertEqual({row['pc'] for row in alternate_cuts if row.get('verified_in_game')},
                         {'MOVIE004', 'MOVIE011'})
        for disc in (1, 2):
            transition = catalog['unassigned']['film'][f'{disc}:/SAKURA1/OPSAKURA.CPK+0']
            self.assertEqual(transition['status'], 'excluded')
            self.assertNotIn('pc', transition)

    def test_chapter7_separates_native_display_from_tactical_residency(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 7)
        for name, verified in (('BG1267', False), ('BG1268', True), ('BG2080', True)):
            with self.subTest(scene=name):
                scene = chapter['scene-pictures'][f'1:/SAKURA1/{name}.BIN']
                self.assertEqual(scene['association'], 'observed')
                self.assertEqual(bool(scene.get('verified_in_game')), verified)
                self.assertIn(f'2:/SAKURA1/{name}.BIN', catalog['unassigned']['scene-pictures'])
        film = chapter['film']['1:/SAKURA4+164800512']
        self.assertEqual((film['association'], film['fad'], film['pc']), ('observed', 80874, 'MOVIE019'))
        self.assertEqual(chapter['tactical-units']['1:/SAKURA2/UNIT10.BIN']['association'], 'resident')
        self.assertEqual(chapter['menus-hud']['1:/SAKURA2/WKL10.BIN']['association'], 'resident')
        ground = chapter['tactical-maps']['1:/SAKURA2/MAP10.BIN']
        self.assertEqual((ground['association'], ground['status']), ('observed', 'paired-not-wired'))
        self.assertIn('different offsets', ground['reason'])
        self.assertFalse(ground.get('verified_in_game'))
        self.assertNotIn('runtime_evidence', ground)

    def test_chapter8_native_scenes_preserve_donor_decisions(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 8)
        for name, status in (('BG1050', 'hd'), ('BG1212', 'unpaired'), ('BG4187', 'hd'), ('TITLE8', 'excluded')):
            with self.subTest(scene=name):
                row = chapter['scene-pictures'][f'2:/SAKURA1/{name}.BIN']
                self.assertEqual((row['association'], row['status']), ('observed', status))
                self.assertEqual(bool(row.get('verified_in_game')), name in ('BG1050', 'BG4187'))
                self.assertNotIn(f'1:/SAKURA1/{name}.BIN', chapter['scene-pictures'])
        self.assertNotIn('2:/SAKURA1/BG1341.BIN', chapter['scene-pictures'])

    def test_chapter10_keeps_native_occurrence_and_hd_witness_separate(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 10)
        for name in ('BG1213', 'BG4055'):
            with self.subTest(scene=name):
                scene = chapter['scene-pictures'][f'2:/SAKURA1/{name}.BIN']
                self.assertEqual(scene['association'], 'observed')
                self.assertFalse(scene.get('verified_in_game'))
        background = chapter['scene-pictures']['2:/SAKURA1/BG1160.BIN']
        self.assertEqual((background['association'], background['status']), ('observed', 'hd'))
        self.assertTrue(background['verified_in_game'])
        self.assertEqual(chapter['portraits']['2:/SAKURA1/1001FCE.BIN']['association'], 'resident')
        self.assertTrue(chapter['scene-pictures']['2:/SAKURA1/BG1285.BIN']['verified_in_game'])
        ground = chapter['tactical-maps']['2:/SAKURA2/MAP19.BIN']
        self.assertEqual((ground['association'], ground['status']), ('observed', 'paired-not-wired'))
        self.assertIn('lamps and rails differently', ground['reason'])
        self.assertFalse(ground.get('verified_in_game'))
        self.assertNotIn('runtime_evidence', ground)

    def test_body_witness_batch_remains_disc_scoped(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        nc90 = catalog['chapters'][4]['resources']['bodies']['1:/SAKURA1/NC90.BIN']
        nc81 = catalog['chapters'][8]['resources']['bodies']['2:/SAKURA1/NC81.BIN']
        self.assertTrue(nc90['verified_in_game'])
        self.assertTrue(nc81['verified_in_game'])
        self.assertTrue(nc81['native_face_fallback'])
        self.assertEqual(nc81['runtime_evidence'], 'docs/research/nc81-nc90-1440p.md')
        self.assertFalse(catalog['chapters'][0]['resources']['bodies']['1:/SAKURA1/NC81.BIN']['verified_in_game'])
        nc3018 = catalog['chapters'][8]['resources']['bodies']['2:/SAKURA1/NC3018.BIN']
        self.assertTrue(nc3018['verified_in_game'])
        self.assertEqual(nc3018['runtime_evidence'], 'docs/research/nc3018-registered-faces.md')
        self.assertFalse(catalog['unassigned']['bodies']['1:/SAKURA1/NC3018.BIN']['verified_in_game'])

    def test_eve202_only_attributes_the_witnessed_disc(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 2)
        eve = chapter['scene-pictures']['1:/SAKURA2/EVE202.BIN']
        self.assertEqual((eve['association'], eve['status']), ('observed', 'hd'))
        self.assertIs(eve['verified_in_game'], True)
        self.assertEqual(eve['runtime_evidence'], 'docs/research/eve202-tactical-inset.md')
        self.assertFalse(catalog['unassigned']['scene-pictures'].get('2:/SAKURA2/EVE202.BIN', {}).get('verified_in_game'))

    def test_map04_keeps_native_layers_outside_the_ground_scope(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter3 = catalog['chapters'][2]['resources']
        row = chapter3['tactical-maps']['1:/SAKURA2/MAP04.BIN']
        self.assertEqual((row['association'], row['status']), ('observed', 'hd'))
        self.assertEqual(row['pc'], 'SAKURA2/MAP/MAP04/MAP04_A.SPR')
        self.assertEqual(row['scope'], 'source-4 ground only')
        self.assertIs(row['verified_in_game'], True)
        self.assertEqual(row['runtime_evidence'], 'docs/research/map04-pc-ground.md')

    def test_bg2093_dream_uses_native_compositing(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 9)
        dream = chapter['scene-pictures']['2:/SAKURA1/BG2093.BIN']
        self.assertEqual((dream['association'], dream['status']), ('observed', 'hd'))
        self.assertEqual(dream['evidence'], 'docs/research/bg2093-dream-transition.md')
        self.assertTrue(dream['verified_in_game'])
        self.assertEqual(dream['runtime_evidence'], dream['evidence'])
        self.assertFalse(catalog['unassigned']['scene-pictures']['1:/SAKURA1/BG2093.BIN'].get('verified_in_game'))
        self.assertTrue(chapter['scene-pictures']['2:/SAKURA1/BG2238.BIN']['verified_in_game'])

    def test_narrative_cutout_followup_has_exact_disc_scope(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        rows = dict(catalog['unassigned']['scene-pictures'])
        for chapter in catalog['chapters']:
            rows.update(chapter['resources']['scene-pictures'])
        for disc, name in ((1, 'BG3289'), (1, 'BG4059'), (1, 'BG4119'), (2, 'BG4187')):
            with self.subTest(name=name):
                row = rows[f'{disc}:/SAKURA1/{name}.BIN']
                self.assertEqual(row['status'], 'hd')
                self.assertTrue(row['verified_in_game'])
                self.assertEqual(row['runtime_evidence'], 'docs/research/narrative-foreground-followup.md')
                other = rows[f'{3 - disc}:/SAKURA1/{name}.BIN']
                self.assertEqual(other['status'], 'excluded')
                self.assertFalse(other.get('verified_in_game'))

    def test_registered_narrative_cutouts_are_disc_one_only(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 5)
        for name in ('BG3132', 'BG3133'):
            with self.subTest(name=name):
                row = chapter['scene-pictures'][f'1:/SAKURA1/{name}.BIN']
                self.assertEqual(row['status'], 'hd')
                self.assertTrue(row['verified_in_game'])
                self.assertEqual(row['runtime_evidence'], 'docs/research/narrative-foreground-cutouts.md')
                row = catalog['unassigned']['scene-pictures'][f'2:/SAKURA1/{name}.BIN']
                self.assertEqual(row['status'], 'excluded')
                self.assertFalse(row.get('verified_in_game'))

    def test_three_disc_two_scroll_witnesses(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        for name, number in (('BG1282', 9), ('BG2077', 8), ('BG2176', 8)):
            with self.subTest(name=name):
                chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == number)
                row = chapter['scene-pictures'][f'2:/SAKURA1/{name}.BIN']
                self.assertEqual((row['association'], row['status']), ('observed', 'hd'))
                self.assertTrue(row['verified_in_game'])
                self.assertTrue(row['runtime_evidence'].endswith('#bg1282-bg2077-and-bg2176-on-english-disc-2'))
                other_disc = f'1:/SAKURA1/{name}.BIN'
                for category in [catalog['unassigned'], *(a['resources'] for a in catalog['chapters'])]:
                    self.assertFalse(category['scene-pictures'].get(other_disc, {}).get('verified_in_game'))

    def test_bg2247_native_pan_preserves_framing(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter = next(row['resources'] for row in catalog['chapters'] if row['chapter'] == 8)
        pan = chapter['scene-pictures']['2:/SAKURA1/BG2247.BIN']
        self.assertEqual((pan['association'], pan['status']), ('observed', 'unsupported-size'))
        self.assertEqual(pan['evidence'], 'docs/research/bg2247-native-pan.md')
        self.assertFalse(pan.get('verified_in_game'))
        self.assertIn('1:/SAKURA1/BG2247.BIN', catalog['unassigned']['scene-pictures'])
        self.assertTrue(chapter['scene-pictures']['2:/SAKURA1/BG2159.BIN']['verified_in_game'])

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
        self.assertEqual(len(drawn), 59)
        self.assertEqual(sum(1 for pc, _ in drawn if '/SYSTEM/' in pc), 18)
        self.assertIn(('SAKURA1/SYSTEM/SIS_ICON.SPR', 3), drawn)
        self.assertEqual({index for pc, index in drawn if pc == 'SAKURA1/SYSTEM/SISTEM.SPR'}, {1, 2, 4, 5, 8, 9, 11, 12, 14})
        items = catalog['unassigned']['menus-hud']
        for index in (0, 1):
            row = items[f'pc:SAKURA1/SYSTEM/WINDOW.SPR#{index}']
            self.assertEqual((row['status'], row['pc_image_index']), ('hd', index))
            self.assertTrue(row['verified_in_game'])
        for index in (11, 14):
            row = items[f'pc:SAKURA1/SYSTEM/SISTEM.SPR#{index}']
            self.assertEqual((row['status'], row['pc_image_index']), ('hd', index))
            self.assertTrue(row['verified_in_game'])
        for index in (1, 4):
            row = items[f'pc:SAKURA1/SYSTEM/SISTEM.SPR#{index}']
            self.assertEqual((row['status'], row['pc_image_index']), ('hd', index))
            self.assertTrue(row['verified_in_game'])
        frame = items['pc:SAKURA1/SYSTEM/OPTION.SPR#1']
        self.assertEqual((frame['status'], frame['pc_image_index']), ('hd', 1))
        self.assertTrue(frame['verified_in_game'])
        frame = items['pc:SAKURA1/SYSTEM/WINDOW.SPR#2']
        self.assertEqual((frame['status'], frame['pc_image_index']), ('hd', 2))
        self.assertTrue(frame['verified_in_game'])
        frame = items['pc:SAKURA1/SYSTEM/TUIKA_W.SPR#0']
        self.assertEqual((frame['status'], frame['pc_image_index']), ('hd', 0))
        self.assertTrue(frame['verified_in_game'])
        for disc in (1, 2):
            for name in ('ITEM03', 'ITEM12', 'ITEM27'):
                with self.subTest(disc=disc, card=name):
                    row = items[f'{disc}:/SAKURA1/{name}.BIN']
                    self.assertEqual(row['status'], 'hd')
                    self.assertEqual((row['pc'], row['pc_image_index']), (f'SAKURA1/ITEM/{name}.SPR', 0))
                    self.assertEqual(row.get('verified_in_game', False), disc == 1 and name == 'ITEM12')
        self.assertEqual(sum(row.get('images', 0) for row in rows if row['status'] == 'excluded'), 394)
        self.assertEqual(catalog['hud_census'], {'system_images': 572, 'item_images': 51})

    def test_pc_title_donors_remain_excluded_in_both_disc_inventories(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        groups = [catalog['unassigned']] + [chapter['resources'] for chapter in catalog['chapters']]
        scenes = {key: row for group in groups for key, row in group['scene-pictures'].items()}
        for disc in (1, 2):
            for episode in range(1, 11):
                row = scenes[f'{disc}:/SAKURA1/TITLE{episode}.BIN']
                self.assertEqual(row['status'], 'excluded')
                self.assertEqual(row['pc'], f'SAKURA1/TITLE/TITLE{episode}.SPR')
                self.assertFalse(row.get('verified_in_game'))

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

    def test_ending_bank_status_tracks_unique_and_shared_photographs(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter10 = catalog['chapters'][9]['resources']['scene-pictures']
        catalog = catalog['unassigned']['scene-pictures']
        sumire = chapter10['2:/SAKURA1/SU_CG.BIN']
        self.assertEqual((sumire['association'], sumire['status']), ('observed', 'hd'))
        self.assertTrue(sumire['verified_in_game'])
        self.assertEqual(sumire['pc'], 'SAKURA1/ENDING/END_SU.SPR')
        self.assertEqual(sumire['pc_image_indices'], [8, 10])
        self.assertEqual(sumire['shared_runtime_donor'], 'SAKURA1/ENDING/END_SA.SPR')
        self.assertEqual(sumire['shared_pc_image_indices'], [6, 7])
        self.assertEqual(sumire['native_records'], [])
        self.assertNotIn('2:/SAKURA1/SU_CG.BIN', catalog)
        kanna = catalog['2:/SAKURA1/KA_CG.BIN']
        self.assertEqual((kanna['association'], kanna['status']), ('unknown', 'hd'))
        self.assertFalse(kanna['verified_in_game'])
        self.assertEqual(kanna['pc'], 'SAKURA1/ENDING/END_KA.SPR')
        self.assertEqual(kanna['pc_image_indices'], [8, 10])
        self.assertEqual(kanna['shared_runtime_donor'], 'SAKURA1/ENDING/END_SA.SPR')
        self.assertEqual(kanna['shared_pc_image_indices'], [6, 7])
        self.assertEqual(kanna['native_records'], [])
        self.assertEqual(kanna['fixture_evidence'], 'docs/research/ending-bank-pairs.md#controlled-kanna-ending-photographs')
        for mark in ('AI', 'KO'):
            inset = catalog[f'2:/SAKURA1/{mark}_CG.BIN']
            self.assertEqual((inset['status'], inset['pc_image_indices']), ('hd', [5]))
            self.assertEqual(inset['fixture_evidence'], 'docs/research/ending-bank-pairs.md#controlled-iris-and-kohran-theatre-insets')
            self.assertFalse(inset['verified_in_game'])
            self.assertEqual(inset['native_records'], [8, 11])
            self.assertEqual(inset['shared_runtime_donor'], 'SAKURA1/ENDING/END_SA.SPR')
        for disc in (1, 2):
            for name in ('AI', 'GE', 'KA', 'KO', 'MA', 'SA', 'SU'):
                if disc == 2 and name in ('AI', 'KA', 'KO', 'SU'):
                    continue
                with self.subTest(disc=disc, ending=name):
                    row = catalog[f'{disc}:/SAKURA1/{name}_CG.BIN']
                    self.assertEqual(row['association'], 'unknown')
                    self.assertEqual(row['pc'], f'SAKURA1/ENDING/END_{name}.SPR')
                    if name == 'GE' or disc == 1:
                        self.assertEqual(row['status'], 'paired-not-wired')
                        self.assertFalse(row.get('verified_in_game'))
                    else:
                        self.assertEqual(row['pc_image_indices'], [6, 7])
                        self.assertEqual(row['native_records'], [8, 11])
                        self.assertEqual(row['status'], 'hd' if name == 'SA' else 'wired-unverified')
                        self.assertEqual(bool(row.get('verified_in_game')), name == 'SA')
                    if name == 'GE':
                        self.assertEqual(row['pc_image_indices'], [0, 1, 2, 3])

    def test_ending_photo_keys_are_shared_by_the_six_heroine_banks(self):
        root = Path(__file__).resolve().parents[1]
        banks = {p['saturn_file']: p for p in json.loads(
            (root / 'config/hd-ending-bank-map.json').read_text(encoding='utf-8'))['pairs']}
        keys = coverage.runtime_ending_photo_keys(root)
        self.assertEqual(keys, {'A19A0B84409A3AB8', 'BD98B23C7D99D3DD'})
        for name, bank in banks.items():
            photos = {r['saturn_record']: r['palette_fnv'] for r in bank['records'] if r['saturn_record'] in (6, 7)}
            self.assertEqual(set(photos.values()) <= keys and len(photos) == 2, 'GE' not in name, name)

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
            for name in ('NC3517',):
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
        self.assertEqual((ground['association'], ground['status']), ('observed', 'hd'))
        self.assertEqual(ground['pc'], 'SAKURA2/MAP/MAP06/MAP06_A.SPR')
        self.assertEqual(ground['scope'], 'source-4 ground only')
        self.assertTrue(ground.get('verified_in_game'))
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
        self.assertFalse(chapter3['scene-pictures'][background].get('verified_in_game'))
        self.assertTrue(chapter5['scene-pictures'][background]['verified_in_game'])
        body = chapter5['bodies']['1:/SAKURA1/NC3058.BIN']
        self.assertEqual((body['association'], body['status']), ('observed', 'hd'))
        self.assertTrue(body['verified_in_game'])
        self.assertTrue(body['native_face_fallback'])
        self.assertEqual(body['runtime_evidence'], 'docs/research/nc3058-cutout-1440p.md')
        self.assertFalse(catalog['unassigned']['bodies']['2:/SAKURA1/NC3058.BIN']['verified_in_game'])
        emblem = chapter5['portraits']['0169']
        self.assertEqual((emblem['association'], emblem['status'], emblem['pc_index']), ('observed', 'hd', 360))
        self.assertTrue(catalog['chapters'][0]['resources']['portraits']['0169']['verified_in_game'])
        for identity, donor in (('010f', 270), ('016a', 361)):
            row = chapter5['portraits'][identity]
            self.assertEqual((row['association'], row['status'], row['pc_index']), ('observed', 'hd', donor))
            self.assertTrue(row['verified_in_game'])
            self.assertEqual(row['atlases'], ['1:/SAKURA1/0501FCE.BIN'])
            self.assertTrue(row['runtime_evidence'].endswith('#verified-0501fce-portrait-bases'))
        for identity in ('00ff', '0169', '1:/SAKURA1/0501FCE.BIN'):
            self.assertFalse(chapter5['portraits'][identity].get('verified_in_game'))
        self.assertNotIn('016a', catalog['unassigned']['portraits'])

    def test_chapter9_native_observations_and_residency_are_distinct(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        chapter9 = catalog['chapters'][8]['resources']
        for name in ('BG1072', 'BG1076', 'BG1176', 'BG2098', 'BG2100'):
            row = chapter9['scene-pictures'][f'2:/SAKURA1/{name}.BIN']
            self.assertEqual(row['association'], 'observed')
            self.assertEqual(bool(row.get('verified_in_game')), name != 'BG1072')
        self.assertTrue(chapter9['scene-pictures']['2:/SAKURA1/BG2238.BIN']['verified_in_game'])
        self.assertEqual(chapter9['portraits']['2:/SAKURA1/0901FCE.BIN']['association'], 'resident')
        yoneda = chapter9['portraits']['00e9']
        self.assertEqual(yoneda['pc_index'], 232)
        self.assertTrue(yoneda['verified_in_game'])
        self.assertTrue(yoneda['runtime_evidence'].endswith('#yoneda-00e9-storage-portrait'))
        self.assertFalse(catalog['chapters'][0]['resources']['portraits']['00e9'].get('verified_in_game'))
        for identity in ('0001', '00e9'):
            self.assertEqual(chapter9['portraits'][identity]['association'], 'observed')
            self.assertEqual(catalog['chapters'][0]['resources']['portraits'][identity]['association'], 'observed')

    def test_registered_short_bodies_record_witness_scope(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        rows = dict(catalog['unassigned']['bodies'])
        for chapter in catalog['chapters']:
            rows.update(chapter['resources']['bodies'])
        for disc in (1, 2):
            for name, anchor in (
                ('NC4138', '#nc4138-registered-silhouette'),
                ('NC3125', '#nc3125-and-nc3126-registered-subsets'),
                ('NC3126', '#nc3125-and-nc3126-registered-subsets'),
            ):
                body = rows[f'{disc}:/SAKURA1/{name}.BIN']
                self.assertEqual((body['status'], body['pc']), ('hd', f'SAKURA1/NC/{name}.SPR'))
                self.assertTrue(body['native_face_fallback'])
                self.assertFalse(body.get('verified_in_game'))
                self.assertTrue(body['fixture_evidence'].endswith(anchor))
            self.assertEqual(rows[f'{disc}:/SAKURA1/NC3517.BIN']['status'], 'paired-not-wired')
            body = rows[f'{disc}:/SAKURA1/NC3290.BIN']
            self.assertEqual((body['status'], body['pc']), ('hd', 'SAKURA1/NC/NC3290.SPR'))
            self.assertTrue(body['native_face_fallback'])
            self.assertEqual(bool(body.get('verified_in_game')), disc == 1)
            if disc == 1:
                self.assertEqual(body['association'], 'observed')
                self.assertEqual(body['runtime_evidence'], 'docs/research/nc3290-stage-wing.md')

    def test_scene_corridor_aliases_use_existing_runtime_keys(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        scenes = dict(catalog['unassigned']['scene-pictures'])
        for chapter in catalog['chapters']:
            scenes.update(chapter['resources']['scene-pictures'])
        for disc in (1, 2):
            for alias, canonical in (('BG1130', 'BG1134'), ('BG1131', 'BG1135')):
                row = scenes[f'{disc}:/SAKURA1/{alias}.BIN']
                self.assertEqual(row['status'], 'hd')
                self.assertEqual(row['native_alias_of'], canonical)
                self.assertEqual(row['pc'], f'SAKURA1/BG/{canonical}.SPR')
                self.assertFalse(row.get('verified_in_game'))
        self.assertEqual(scenes['1:/SAKURA1/BG4049.BIN']['status'], 'unpaired')

    def test_chapter3_0301_portrait_draws_are_occurrence_specific(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        portraits = catalog['chapters'][2]['resources']['portraits']
        atlas = '1:/SAKURA1/0301FCE.BIN'
        for identity, donor in (('0068', 103), ('00fe', 253), ('0116', 277), ('013d', 316)):
            row = portraits[identity]
            self.assertEqual((row['association'], row['status'], row['pc_index']), ('observed', 'hd', donor))
            self.assertEqual(row['atlases'], [atlas])
            self.assertTrue(row['verified_in_game'])
            self.assertTrue(row['runtime_evidence'].endswith('#witnessed-0301fce-portrait-bases'))
        self.assertFalse(portraits[atlas].get('verified_in_game'))
        self.assertFalse(portraits.get('0001', {}).get('verified_in_game'))
        self.assertFalse(catalog['chapters'][0]['resources']['portraits']['0068'].get('verified_in_game'))
        self.assertNotIn('0116', catalog['unassigned']['portraits'])

    def test_chapter2_tactical_portraits_do_not_attribute_narrative_fce(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / 'config/hd-chapter-coverage.json').read_text(encoding='utf-8'))
        portraits = catalog['chapters'][1]['resources']['portraits']
        bank = '1:/SAKURA2/FACE02.BIN'
        self.assertEqual((portraits[bank]['association'], portraits[bank]['status']), ('resident', 'unknown'))
        for slot, donor in ((0, 10), (30, 208), (31, 209)):
            row = portraits[f'{bank}#{slot}']
            self.assertEqual((row['association'], row['status'], row['pc_index']), ('observed', 'hd', donor))
            self.assertTrue(row['verified_in_game'])
            self.assertEqual(row['scope'], 'tactical portrait base only')
            self.assertTrue(row['runtime_evidence'].endswith('#face02-pc-runtime'))
        for atlas in range(1, 7):
            self.assertEqual(portraits[f'1:/SAKURA1/020{atlas}FCE.BIN']['association'], 'inferred')
