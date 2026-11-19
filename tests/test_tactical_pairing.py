"""Synthetic tests for tools/tactical_pairing.py (no game data, no pixels)."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import tactical_pairing as tp  # noqa: E402


def fake_spr(sizes):
    """A SPRED file whose image table lists `sizes` (pixel data is a stub: the tool never decodes)."""
    table = struct.pack('>H', len(sizes)) + b'\0' * 14
    for w, h in sizes:
        table += struct.pack('>HHHHII', w, h, 2, 0, 0, 4)
    bitmaps_at = 16 + 16 * 2
    head = b'SEGA SPRED' + b'\0' * 6
    head += struct.pack('>III', bitmaps_at, len(table), 2) + b'\0' * 4
    head += b'\0' * 16
    return head + table + b'\0' * 8


TAB = 'Ground:\t\tFile:\t\tmap01_a.spr\r\nPriority:\tFile:\t\tmap01_b.spr\r\n#UnderGround:\tFile:\t\tmap01_c.spr\r\n'


class TabTests(unittest.TestCase):
    def test_parse_ignores_comments(self):
        rows = tp.parse_tab(TAB)
        self.assertIn(('Ground', 'File', 'map01_a.spr'), rows)
        self.assertFalse([r for r in rows if r[0] == 'UnderGround'])

    def test_underground_ground_and_parent_path(self):
        rows = tp.parse_tab(r'UnderGround:	File:		..\Map06\map06_a.spr' + '\r\n')
        self.assertEqual(tp.tab_ground(rows), ('../map06/map06_a.spr', 'UnderGround'))

    def test_no_ground(self):
        self.assertEqual(tp.tab_ground(tp.parse_tab('Priority:\tFile:\tx.spr\n')), (None, None))


class SprTests(unittest.TestCase):
    def test_images(self):
        self.assertEqual([i[:2] for i in tp.spr_images(fake_spr([(64, 32), (8, 8)]))], [(64, 32), (8, 8)])

    def test_rejects_other_files(self):
        with self.assertRaises(ValueError):
            tp.spr_images(b'x' * 64)

    def test_hashes(self):
        self.assertEqual(tp.fnv1a64(b''), 'CBF29CE484222325')
        self.assertEqual(len(tp.sha256(b'a')), 64)


class PairTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bin = b'BIN' * 100

    def tearDown(self):
        self.tmp.cleanup()

    def folder(self, stem, bin_bytes, tab, spr=None):
        d = self.root / 'SAKURA2' / 'MAP' / stem
        d.mkdir(parents=True)
        (d / f'{stem}.BIN').write_bytes(bin_bytes)
        (d / f'{stem}.TAB').write_text(tab, encoding='latin1')
        for name, data in (spr or {}).items():
            (d / name).write_bytes(data)
        return d

    def test_paired(self):
        self.folder('MAP01', self.bin, TAB, {'MAP01_A.SPR': fake_spr([(1408, 960)])})
        row = tp.pair_map('1:/SAKURA2/MAP01.BIN', self.bin, self.root)
        self.assertEqual(row['status'], 'paired')
        self.assertEqual(row['pc_ground'], 'SAKURA2/MAP/MAP01/MAP01_A.SPR')
        self.assertEqual(row['ground_image0_size'], [1408, 960])
        self.assertEqual(row['ground_layout'], 'single')
        self.assertTrue(row['identical'])

    def test_tiles(self):
        self.folder('MAP03', self.bin, TAB.replace('map01', 'map03'), {'MAP03_A.SPR': fake_spr([(64, 64)] * 3)})
        row = tp.pair_map('1:/SAKURA2/MAP03.BIN', self.bin, self.root)
        self.assertEqual((row['ground_layout'], row['ground_image_count']), ('tiles', 3))

    def test_different_bytes(self):
        self.folder('MAP01', self.bin + b'x', TAB, {'MAP01_A.SPR': fake_spr([(8, 8)])})
        row = tp.pair_map('1:/SAKURA2/MAP01.BIN', self.bin, self.root)
        self.assertEqual(row['status'], 'no-counterpart')
        self.assertFalse(row['identical'])

    def test_missing_folder_and_ground(self):
        self.assertEqual(tp.pair_map('1:/SAKURA2/MAP09.BIN', self.bin, self.root)['status'], 'no-counterpart')
        self.folder('MAP02', self.bin, TAB.replace('map01', 'map02'))
        self.assertEqual(tp.pair_map('1:/SAKURA2/MAP02.BIN', self.bin, self.root)['status'], 'paired-no-ground')

    def test_shared_ground_folder_case_insensitive(self):
        self.folder('MAP06', b'six', 'UnderGround:\tFile:\tmap06_a.spr\n', {'MAP06_A.SPR': fake_spr([(16, 16)])})
        self.folder('MAP27', self.bin, r'UnderGround:	File:	..\Map06\map06_a.spr' + '\n')
        row = tp.pair_map('1:/SAKURA2/MAP27.BIN', self.bin, self.root)
        self.assertEqual(row['status'], 'paired')
        self.assertEqual(row['ground_shared_with'], 'MAP06')

    def test_build_summary_and_register(self):
        self.folder('MAP01', self.bin, TAB, {'MAP01_A.SPR': fake_spr([(8, 8)])})
        self.folder('MAP27', b'z', TAB)
        coverage = {'chapters': [{'resources': {'tactical-maps': {'1:/SAKURA2/MAP01.BIN': {'status': 'hd'}}}}],
                    'unassigned': {}}
        result = tp.build_maps({'1:/SAKURA2/MAP01.BIN': self.bin}, self.root, coverage)
        self.assertEqual(result['summary'], {'paired': 1})
        self.assertEqual(result['maps'][0]['register'], 'hd')
        self.assertEqual(result['pc_maps_without_saturn_file'], ['MAP27'])
        json.dumps(result)


class UnitTests(unittest.TestCase):
    def test_inventory_groups_identical_banks_and_lists_pc_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            for rel, sizes in (('SAKURA/A.SPR', [(32, 48)]), ('BOSS/KAGE/B.SPR', [(8, 8), (8, 8)]), ('X.SPR', [(4, 4)])):
                path = Path(tmp) / 'SAKURA2' / 'UNIT' / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(fake_spr(sizes))
            (Path(tmp) / 'SAKURA2' / 'UNIT' / 'SAKURA' / 'note.DAT').write_bytes(b'ignored')
            banks = {'1:/SAKURA2/UNIT02.BIN': bytes((0, 0, 0, 208)) + b'a' * 20, '1:/SAKURA2/UNIT03.BIN': bytes((0, 0, 0, 208)) + b'a' * 20,
                     '2:/SAKURA2/UNIT14.BIN': bytes((0, 0, 0, 208)) + b'b' * 20}
            result = tp.build_units(banks, tmp)
        self.assertEqual(result['summary']['saturn_files'], 3)
        self.assertEqual(result['summary']['saturn_distinct'], 2)
        self.assertEqual(result['summary']['pc_files'], 3)
        self.assertEqual(result['summary']['pc_groups'], {'(root)': 1, 'BOSS/KAGE': 1, 'SAKURA': 1})
        self.assertEqual(result['saturn_units'][1]['same_as'], '1:/SAKURA2/UNIT02.BIN')
        self.assertEqual(result['summary']['paired'], 0)
        self.assertEqual({r['status'] for r in result['pc_units']}, {'no-counterpart'})


class CommittedDataTests(unittest.TestCase):
    def test_committed_map_pairs_are_data_only(self):
        path = Path(__file__).resolve().parent.parent / 'config/hd-tactical-map-pairs.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(len(data['maps']), 27)
        for row in data['maps']:
            self.assertRegex(row['sha256'], r'^[0-9a-f]{64}$')
            if row['status'] == 'paired':
                self.assertTrue(row['identical'])
                self.assertEqual(row['sha256'], row['pc_bin_sha256'])

    def test_committed_unit_inventory_is_data_only(self):
        path = Path(__file__).resolve().parent.parent / 'config/hd-tactical-unit-inventory.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(data['summary']['pc_files'], 291)
        self.assertEqual(data['summary']['saturn_files'], 27)
        for row in data['saturn_units'] + data['pc_units']:
            self.assertRegex(row['sha256'], r'^[0-9a-f]{64}$')
            self.assertEqual(row['status'], 'no-counterpart')


if __name__ == '__main__':
    unittest.main()
