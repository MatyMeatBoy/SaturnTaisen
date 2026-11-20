import json
import pathlib
import struct
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import gen_ic_table as ic  # noqa: E402


def screen_file(words, indices):
    """A variant D full-screen picture: palette, 40x28 table of 2 x tile number, 8x8 8 bpp tiles."""
    tiles = []
    table = []
    for cell in range(40 * 28):
        left, top = (cell % 40) * 8, (cell // 40) * 8
        tile = bytes(indices[top + y][left + x] for y in range(8) for x in range(8))
        if tile not in tiles:
            tiles.append(tile)
        table.append(tiles.index(tile) * 2)
    tiles += [bytes(64)] * (1120 - len(tiles))  # real files carry 1120 tiles (76,672 bytes)
    return struct.pack('>256H', *words) + struct.pack('>1120I', *table) + b''.join(tiles)


def sample(seed):
    words = [(seed * 7 + i * 131) & 0x7FFF for i in range(256)]
    indices = [[(x // 8 + y // 8 * 3 + seed * 5 + (x * y) % 7) % 256 for x in range(320)] for y in range(224)]
    return words, indices


class PlateHash(unittest.TestCase):
    def test_cells_decode_back_to_the_indices(self):
        words, indices = sample(1)
        got_words, got = ic.screen_cells(screen_file(words, indices))
        self.assertEqual(list(got_words), words)
        self.assertEqual(got, indices)

    def test_hash_matches_a_plain_reimplementation(self):
        words, indices = sample(2)
        for offset in (0, -16):
            raw = bytearray()
            for y in range(224):
                for x in range(320):
                    if 184 <= x < 296 and 16 <= y < 144:
                        continue
                    word = words[indices[y][x]]
                    for shift in (0, 5, 10):
                        raw.append(max(0, min(255, ((word >> shift) & 31) * 8 + offset)))
            self.assertEqual(ic.plate_fnv(indices, words, offset), ic.fnv1a(raw))

    def test_panel_rectangle_does_not_change_the_hash(self):
        words, indices = sample(3)
        before = ic.plate_fnv(indices, words)
        for y in range(16, 144):
            for x in range(184, 296):
                indices[y][x] = (indices[y][x] + 1) % 256
        self.assertEqual(ic.plate_fnv(indices, words), before)
        indices[0][0] = (indices[0][0] + 1) % 256
        self.assertNotEqual(ic.plate_fnv(indices, words), before)

    def test_offset_changes_the_hash_and_clamps(self):
        words, indices = sample(4)
        self.assertNotEqual(ic.plate_fnv(indices, words), ic.plate_fnv(indices, words, -16))
        self.assertEqual(ic.rgb_of(0, -16), (0, 0, 0))
        self.assertEqual(ic.rgb_of(0x7FFF, 0), (248, 248, 248))
        self.assertEqual(ic.rgb_of(0x7FFF, -16), (232, 232, 232))


class Registration(unittest.TestCase):
    def picture(self, shift=(0, 0)):
        # A 640x480 picture whose squashed 320x224 sampling reproduces a known plate.
        words, indices = sample(5)
        rgb = ic.plate_rgb(indices, words)
        pixels = [[rgb[min(223, max(0, (y * 896 // 480) // 2 - shift[1]))][min(319, max(0, x // 2 - shift[0]))]
                   for x in range(640)] for y in range(480)]
        return rgb, pixels

    def test_aligned_picture_is_registered(self):
        rgb, pixels = self.picture()
        fit = ic.registration(rgb, ic.pc_plate(pixels))
        self.assertTrue(fit['registered'], fit)
        self.assertEqual(fit['best_shift'], [0, 0])

    def test_shifted_picture_is_refused(self):
        rgb, pixels = self.picture((2, 1))
        fit = ic.registration(rgb, ic.pc_plate(pixels))
        self.assertFalse(fit['registered'], fit)

    def test_wrong_size_is_refused(self):
        with self.assertRaises(ValueError):
            ic.pc_plate([[(0, 0, 0)] * 320] * 240, 320, 240)


class Table(unittest.TestCase):
    def row(self, name, plate, dark):
        return {'id': name, 'saturn_file': 'SAKURA1/%s.BIN' % name, 'pc_file': 'SAKURA1/ICATCH/%s.SPR' % name,
                'pc_bytes': 10, 'pc_fnv': '00000000000000AB', 'plate': plate, 'plate_dark': dark}

    def test_header_lists_every_entry_in_order(self):
        table = ic.finish([self.row('IC03', '0000000000000003', '0000000000000033'),
                           self.row('IC02', '0000000000000002', '0000000000000022')], {'IC01': 'x'})
        text = ic.render_header(table)
        self.assertLess(text.index('IC02.SPR'), text.index('IC03.SPR'))
        self.assertIn('0x0000000000000033ull', text)
        self.assertIn('kIcLogoPalette = 0xE9107F892185CCC8ull', text)
        self.assertEqual(table['not_in_table'], {'IC01': 'x'})

    def test_two_pictures_with_the_same_hash_are_refused(self):
        with self.assertRaises(SystemExit):
            ic.finish([self.row('IC02', '01', '02'), self.row('IC03', '01', '03')], {})
        with self.assertRaises(SystemExit):
            ic.finish([self.row('IC02', '01', '02'), self.row('IC03', '03', '02')], {})

    def test_check_flag_detects_a_stale_header(self):
        table = ic.finish([self.row('IC02', '02', '22')], {})
        with tempfile.TemporaryDirectory() as folder:
            folder = pathlib.Path(folder)
            (folder / 't.json').write_text(json.dumps(table), encoding='utf-8')
            out = folder / 'o.h'
            self.assertEqual(ic.main(['header', str(folder / 't.json'), str(out)]), 0)
            self.assertEqual(ic.main(['header', str(folder / 't.json'), str(out), '--check']), 0)
            out.write_text('stale', encoding='utf-8')
            self.assertEqual(ic.main(['header', str(folder / 't.json'), str(out), '--check']), 1)


class CommittedTable(unittest.TestCase):
    """The committed table is data from the owner's files: check what can be checked without them."""

    def setUp(self):
        self.table = json.loads((ROOT / 'config/hd-ic-table.json').read_text(encoding='utf-8'))

    def test_covers_the_catalog_except_ic01(self):
        screens = json.loads((ROOT / 'config/hd-screen-map.json').read_text(encoding='utf-8'))
        wanted = {pathlib.Path(p['saturn_file']).stem for p in screens['pairs']
                  if p['saturn_file'].split('/')[-1].startswith('IC') and p['tier'] == 'content'} - {'ICLOGO'}
        have = {e['id'] for e in self.table['entries']}
        self.assertEqual(have | set(self.table['not_in_table']), wanted)
        self.assertEqual(set(self.table['not_in_table']), {'IC01'})

    def test_ic0501_reproduces_the_in_game_measurement(self):
        row = next(e for e in self.table['entries'] if e['id'] == 'IC0501')
        self.assertEqual(int(row['plate'], 16), ic.WITNESSED['IC0501']['plate'])
        self.assertEqual(int(row['plate_dark'], 16), ic.WITNESSED['IC0501']['plate_dark'])
        self.assertEqual(row['pc_bytes'], 218568)

    def test_every_entry_is_registered_and_unique(self):
        hashes = []
        for row in self.table['entries']:
            self.assertTrue(row['registration']['registered'], row['id'])
            self.assertEqual(row['discs'], 2, row['id'])
            hashes += [row['plate'], row['plate_dark']]
        self.assertEqual(len(hashes), len(set(hashes)))

    def test_committed_header_inputs_are_current(self):
        # Regenerating from the committed table must give the header the patch carries.
        text = ic.render_header(self.table)
        patch = (ROOT / 'patches/0185-sakura-ic-intermission-table.patch').read_text(encoding='utf-8')
        for line in text.splitlines():
            self.assertIn('+' + line, patch)


if __name__ == '__main__':
    unittest.main()
