import json, pathlib, re, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def pair(name, palette, pc, cells, tier='content'):
    return {'saturn_file': 'SAKURA1/%s.BIN' % name, 'decoded': True, 'size': [288, 144], 'palette_fnv': palette,
            'pc_file': 'SAKURA1/BG/%s.SPR' % pc, 'pc_image_index': 0, 'tier': tier, 'cells_fnv': cells}


def generate(pairs, confirmed=(), choice=None):
    with tempfile.TemporaryDirectory() as folder:
        folder = pathlib.Path(folder)
        (folder / 'm.json').write_text(json.dumps({'pairs': pairs}), encoding='utf-8')
        (folder / 'hd-scene-bg-review.json').write_text(json.dumps(
            {'eye_confirmed_number_tier': list(confirmed), 'rejected': [], 'shared_cell_choice': choice or {}}), encoding='utf-8')
        out = folder / 'o.h'
        subprocess.run([sys.executable, str(ROOT / 'tools/gen_scene_bg_table.py'), str(folder / 'm.json'), str(out)],
                       check=True, capture_output=True)
        text = out.read_text(encoding='utf-8')
    first = re.findall(r'\{0x([0-9A-F]+)ull,"([^"]+)",(\d+)\}', text.split('kSceneBgAmbiguous')[0])
    second = re.findall(r'\{0x([0-9A-F]+)ull,0x([0-9A-F]+)ull,"([^"]+)",(\d+)\}', text)
    return first, second


class AmbiguousPaletteTable(unittest.TestCase):
    def test_shared_palette_goes_to_the_second_table(self):
        # BG1 and BG2 share a palette and map to different PC files (a content pair and a number pair confirmed by eye).
        first, second = generate([pair('BG1011', 'AA', 'BG1011', '01'), pair('BG1012', 'AA', 'BG1012', '02')])
        self.assertEqual(first, [])
        self.assertEqual({(p, c, f) for p, c, f, _ in second},
                         {('AA', '01', 'SAKURA1/BG/BG1011.SPR'), ('AA', '02', 'SAKURA1/BG/BG1012.SPR')})

    def test_unique_palette_stays_in_the_first_table(self):
        first, second = generate([pair('BG1011', 'AA', 'BG1011', '01'), pair('BG1012', 'BB', 'BG1012', '02')])
        self.assertEqual(len(first), 2)
        self.assertEqual(second, [])

    def test_identical_cells_for_two_pc_files_stay_out(self):
        first, second = generate([pair('BG1011', 'AA', 'BG1011', '01'), pair('BG1012', 'AA', 'BG1012', '01')])
        self.assertEqual((first, second), ([], []))

    def test_shared_cells_accept_identical_pc_container_and_image_index(self):
        left = pair('BG1011', 'AA', 'BG1011', '01')
        right = pair('BG1012', 'AA', 'BG1012', '01')
        left['pc_sha256'] = right['pc_sha256'] = 'a' * 64
        for rows in ([left, right], [right, left]):
            self.assertEqual(generate(rows), ([], [('AA', '01', 'SAKURA1/BG/BG1011.SPR', '0')]))
        changed_image = dict(right, pc_image_index=1)
        changed_bytes = dict(right, pc_sha256='b' * 64)
        self.assertEqual(generate([left, changed_image]), ([], []))
        self.assertEqual(generate([left, changed_bytes]), ([], []))

    def test_content_pair_does_not_hide_a_neighbour_with_other_cells(self):
        # BG1016 (number, confirmed) shares its palette with BG1017 (content) but has its own cells and PC file.
        first, second = generate([pair('BG1016', 'AA', 'BG1016', '01', 'number'), pair('BG1017', 'AA', 'BG1017', '02')], ['BG1016'])
        self.assertEqual(first, [])
        self.assertEqual({(c, f) for _, c, f, _ in second}, {('01', 'SAKURA1/BG/BG1016.SPR'), ('02', 'SAKURA1/BG/BG1017.SPR')})

    def test_recorded_choice_resolves_shared_cells_with_different_pc_pictures(self):
        rows = [pair('BG2015', 'AA', 'BG2015', '01', 'number'), pair('BG2016', 'AA', 'BG2016', '01')]
        self.assertEqual(generate(rows, ['BG2015']), ([], []))
        self.assertEqual(generate(rows, ['BG2015'], {'BG2015': 'BG2015', 'BG2016': 'BG2015'}),
                         ([], [('AA', '01', 'SAKURA1/BG/BG2015.SPR', '0')]))
        self.assertEqual(generate(rows, ['BG2015'], {'BG2015': 'BG2015', 'BG2016': 'BG2016'}), ([], []))

    def test_rejected_and_cut_out_pictures_never_enter(self):
        first, second = generate([pair('BG3011', 'AA', 'BG3011', '01'), pair('BG1012', 'AA', 'BG1012', '02')])
        self.assertEqual([(p, f) for p, f, _ in first], [('AA', 'SAKURA1/BG/BG1012.SPR')])
        self.assertEqual(second, [])


if __name__ == '__main__':
    unittest.main()
