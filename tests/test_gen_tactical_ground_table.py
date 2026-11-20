"""Tests for tools/gen_tactical_ground_table.py (synthetic fixtures; the data tests read only committed JSON and patches)."""
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import gen_tactical_ground_table as gt  # noqa: E402


def fake_bin(first_cells=0x3E40, names=None):
    """A MAP BIN with the slot table the formula reads: slot 1 cells, slot 5 the 128 x 128 ground name table."""
    names = names if names is not None else [(i * 2) & 0xFFFF for i in range(128 * 128)]
    slots = [(0x80, 0)] * 16
    slots[1] = (0x80, first_cells)
    slots[5] = (0x80 + first_cells, 0x8000)
    head = b''.join(struct.pack('>II', o, s) for o, s in slots)
    return head + bytes(first_cells) + struct.pack('>16384H', *names)


def expected(names, first_cells):
    out = b''
    for row in range(32):
        for col in range(64):
            out += struct.pack('>I', 0x600000 + names[row * 128 + col] + first_cells // 32)
    value = 14695981039346656037
    for byte in out:
        value = ((value ^ byte) * 1099511628211) & (2 ** 64 - 1)
    return '%016X' % value


def pair(stem, layout='single', size=(2048, 2048), count=1, sha=None, disc=1):
    return {'saturn': '%d:/SAKURA2/%s.BIN' % (disc, stem), 'sha256': sha or stem * 4, 'status': 'paired',
            'pc_ground': 'SAKURA2/MAP/%s/%s_A.SPR' % (stem, stem), 'ground_size': 1000, 'ground_fnv': 'AB' * 8,
            'ground_sha256': 'cd' * 32, 'ground_layout': layout, 'ground_image0_size': list(size),
            'ground_image_count': count, 'ground_image_sizes': ['%dx%d' % size]}


class SignatureTests(unittest.TestCase):
    def test_matches_independent_page_construction(self):
        names = [((i * 7) % 900) * 2 for i in range(128 * 128)]
        self.assertEqual(gt.ground_signature(fake_bin(0x3E40, names)), expected(names, 0x3E40))

    def test_only_top_left_page_matters(self):
        a = [2] * (128 * 128)
        b = list(a)
        b[40 * 128 + 3] = 99      # row 40 is outside the 32 rows of the page
        b[5 * 128 + 100] = 99     # column 100 is outside the 64 columns of the page
        self.assertEqual(gt.ground_signature(fake_bin(0x3E40, a)), gt.ground_signature(fake_bin(0x3E40, b)))
        b[5 * 128 + 10] = 99
        self.assertNotEqual(gt.ground_signature(fake_bin(0x3E40, a)), gt.ground_signature(fake_bin(0x3E40, b)))

    def test_character_base_follows_the_first_layer_cells(self):
        self.assertNotEqual(gt.ground_signature(fake_bin(0x3E40)), gt.ground_signature(fake_bin(0x4E40)))

    def test_rejects_other_files(self):
        with self.assertRaises(ValueError):
            gt.ground_signature(b'\0' * 64)
        with self.assertRaises(ValueError):
            gt.ground_signature(fake_bin(0x3E41))
        broken = bytearray(fake_bin())
        broken[5 * 8 + 4:5 * 8 + 8] = struct.pack('>I', 0x4000)
        with self.assertRaises(ValueError):
            gt.ground_signature(bytes(broken))
        with self.assertRaises(ValueError):
            gt.ground_signature(fake_bin()[:-10])


class ClassifyTests(unittest.TestCase):
    def test_single_image_is_wired_unverified_never_hd(self):
        row = gt.classify(pair('MAP07'), 'AA' * 8)
        self.assertEqual((row['status'], row['world'], row['tile_px'], row['centre_layout']),
                         ('wired-unverified', [1024, 1024], 0, 'stage07-hd-ground'))

    def test_odd_size_needs_assembler(self):
        self.assertEqual(gt.classify(pair('MAP07', size=(2047, 1024)), 'AA' * 8)['status'], 'needs-assembler')

    def test_tiles_need_the_square_plane(self):
        tiles = pair('MAP03', 'tiles', (64, 64), 626)
        self.assertEqual(gt.classify(tiles, 'AA' * 8, [2048, 2048])['tile_px'], 64)
        self.assertEqual(gt.classify(tiles, 'AA' * 8, [2048, 2112])['status'], 'needs-assembler')
        self.assertEqual(gt.classify(tiles, 'AA' * 8)['status'], 'needs-assembler')

    def test_four_large_images_are_not_tiles(self):
        row = gt.classify(pair('MAP23', 'tiles', (1392, 1232), 4), 'AA' * 8, [2784, 2464])
        self.assertEqual(row['status'], 'needs-assembler')
        self.assertIn('alternative images', row['reason'])

    def test_live_reviewed_maps_stay_native(self):
        for stem in ('MAP10', 'MAP19'):
            row = gt.classify(pair(stem), 'AA' * 8)
            self.assertEqual(row['status'], 'native')
            self.assertIn('Keep the native ground', row['reason'])

    def test_hand_entries_keep_their_recorded_signature(self):
        row = gt.classify(pair('MAP21'), '00' * 8)
        self.assertEqual((row['status'], row['table'], row['signature']), ('hd', 'hand', '446FB372F79EDD04'))


class BuildTests(unittest.TestCase):
    def test_same_bin_on_two_discs_is_one_row(self):
        pairs = {'maps': [pair('MAP07', sha='x'), pair('MAP07', sha='x', disc=2)]}
        table = gt.build(pairs, {'MAP07': 'AA' * 8}, {})
        self.assertEqual([r['saturn'] for r in table['maps']], [['1:/SAKURA2/MAP07.BIN', '2:/SAKURA2/MAP07.BIN']])

    def test_duplicate_signature_is_refused(self):
        pairs = {'maps': [pair('MAP07'), pair('MAP08')]}
        with self.assertRaises(ValueError):
            gt.build(pairs, {'MAP07': 'AA' * 8, 'MAP08': 'AA' * 8}, {})

    def test_inc_lists_only_generated_wired_entries(self):
        pairs = {'maps': [pair('MAP07'), pair('MAP10'), pair('MAP21')]}
        table = gt.build(pairs, {'MAP07': 'AA' * 8, 'MAP10': 'BB' * 8, 'MAP21': 'CC' * 8}, {})
        lines = [l for l in gt.inc_text(table).splitlines() if l.startswith('{')]
        self.assertEqual(len(lines), 1)
        self.assertIn('0xAAAAAAAAAAAAAAAAull', lines[0])
        self.assertIn('"stage07-hd-ground", 0}', lines[0])

    def test_patch_inc_extracts_added_lines(self):
        patch = ('diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-a\n+b\n'
                 'diff --git a/%s b/%s\nnew file mode 100644\n--- /dev/null\n+++ b/%s\n@@ -0,0 +2 @@\n+one\n+two\n' %
                 ((gt.INC_NAME,) * 3))
        self.assertEqual(gt.patch_inc(patch), 'one\ntwo\n')
        self.assertIsNone(gt.patch_inc('diff --git a/x b/x\n'))


class CommittedTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = json.loads(gt.TABLE.read_text(encoding='utf-8'))
        cls.rows = {r['map']: r for r in cls.table['maps']}

    def test_check_passes(self):
        self.assertEqual(gt.check(None), 0)

    def test_covers_every_paired_map_once(self):
        pairs = json.loads(gt.PAIRS.read_text(encoding='utf-8'))['maps']
        paired = sorted(p['saturn'] for p in pairs if p['status'] == 'paired')
        self.assertEqual(sorted(s for r in self.table['maps'] for s in r['saturn']), paired)
        self.assertEqual(len(paired), 27)
        self.assertEqual(len(self.rows), 26)

    def test_status_counts(self):
        counts = {}
        for row in self.table['maps']:
            counts[row['status']] = counts.get(row['status'], 0) + 1
        self.assertEqual(counts, {'hd': 6, 'wired-unverified': 17, 'native': 2, 'needs-assembler': 1})
        self.assertEqual(self.table['summary'], counts)

    def test_generated_entries_are_never_hd(self):
        for row in self.table['maps']:
            if row['table'] == 'generated':
                self.assertNotEqual(row['status'], 'hd')
            else:
                self.assertEqual(row['status'], 'hd')

    def test_signatures_equal_the_live_records(self):
        # Recorded from live runs: patches 0102/0138/0139/0140/0153/stage21 and docs/research/tactical-pairing.md (MAP10, MAP19).
        live = {'MAP01': '1CAF3218B4B0F9F0', 'MAP02': '25FF56EB6965E424', 'MAP04': '451ACDDB5522070E',
                'MAP05': 'A18A5122F7C18729', 'MAP06': 'B533F608A5E864D1', 'MAP21': '446FB372F79EDD04',
                'MAP10': 'E364F3D731C3D6DE', 'MAP19': 'FA30687F240C0BEB'}
        for stem, signature in live.items():
            self.assertEqual(self.rows[stem]['signature'], signature, stem)
        for stem in ('MAP01', 'MAP02', 'MAP04', 'MAP05', 'MAP06'):
            self.assertEqual(self.rows[stem]['derived_signature'], live[stem], stem)

    def test_geometry_of_wired_entries(self):
        for row in self.table['maps']:
            if row['status'] != 'wired-unverified':
                continue
            self.assertLessEqual(max(row['world']), 1024)
            if row['tile_px']:
                self.assertEqual(row['world'], [1024, 1024])
                self.assertEqual(row['layout'], 'tiles')
                self.assertEqual(row['plane'], [2048, 2048])
            else:
                width, height = (int(v) for v in row['images'][0].split('x'))
                self.assertEqual(row['world'], [width // 2, height // 2])

    def test_unwired_maps_state_a_reason(self):
        for stem in ('MAP10', 'MAP19', 'MAP23'):
            self.assertTrue(self.rows[stem]['reason'])

    def test_patch_is_listed_in_the_stack(self):
        stack = json.loads((ROOT / 'config/dependencies.json').read_text(encoding='utf-8'))['satrecomp']['patches']
        self.assertIn('patches/0188-sakura-tactical-ground-table.patch', stack)


if __name__ == '__main__':
    unittest.main()
