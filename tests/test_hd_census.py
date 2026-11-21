"""Synthetic tests for tools/hd_census.py (no discs, no assets)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import hd_census as census  # noqa: E402

CENSUS_MD = """| Folder | SPR files | HD category |
| --- | --- | --- |
| SAKURA1/BG | 4 | Scene images |
| SAKURA2/BG | 2 | Scene images |
| SAKURA2/EVENT | 3 | Scene images |
| SAKURA3/CG | 1 | Scene images |
| SAKURA1/ENDING | 1 | Scene images |
| SAKURA1/TITLE | 1 | Scene images |
| SAKURA1/ICATCH | 1 | Scene images |
| SAKURA1/SYSTEM, SAKURA2/SYSTEM | 40 + 19 | HUD |
"""


def register(rows, groups=()):
    return {'unassigned': {'scene-pictures': rows}, 'chapters': [],
            'scene_file_duplicate_groups': [list(g) for g in groups]}


def scene(status, pc=None, **extra):
    row = {'status': status, 'association': 'unknown'}
    if pc:
        row['pc'] = pc
    row.update(extra)
    return row


class FolderCensus(unittest.TestCase):
    def test_parses_table_and_split_rows(self):
        table = census.folder_census(CENSUS_MD)
        self.assertEqual(table['SAKURA1/BG'], 4)
        self.assertEqual(table['SAKURA1/SYSTEM'], 40)
        self.assertEqual(table['SAKURA2/SYSTEM'], 19)

    def test_real_census_has_scene_folders(self):
        table = census.folder_census((census.ROOT / 'docs/research/pc-asset-census.md').read_text(encoding='utf-8'))
        self.assertEqual(sum(table[f] for _, _, f in census.SCENE_FOLDERS), 1267)


class SceneRows(unittest.TestCase):
    def rows(self, reg):
        out, goal, unpaired = census.scene_rows(reg, census.folder_census(CENSUS_MD))
        return {r['id']: r for r in out}, goal, unpaired

    def test_donor_counts_once_across_discs_and_keys(self):
        reg = register({
            '1:/SAKURA1/BG1.BIN': scene('hd', 'SAKURA1/BG/BG1.SPR', verified_in_game=True),
            '2:/SAKURA1/BG1.BIN': scene('hd', 'SAKURA1/BG/BG1.SPR'),
            '1:/SAKURA1/BG2.BIN': scene('hd', 'SAKURA1/BG/BG1.SPR'),
        })
        rows, _, _ = self.rows(reg)
        self.assertEqual(rows['scene-bg']['hd'], 1)
        self.assertEqual(rows['scene-bg']['verified'], 1)
        self.assertEqual(rows['scene-bg']['without_register_row'], 3)

    def test_duplicate_group_counts_once_in_denominator_and_status(self):
        reg = register({
            '1:/a': scene('hd', 'SAKURA1/BG/BG1.SPR'),
            '1:/b': scene('excluded', 'SAKURA1/BG/BG2.SPR', reason='cut-out on a key colour'),
        }, groups=[('SAKURA1/BG/BG1.SPR', 'SAKURA1/BG/BG2.SPR')])
        rows, _, _ = self.rows(reg)
        bg = rows['scene-bg']
        self.assertEqual((bg['raw_files'], bg['candidates'], bg['hd'], bg['excluded']), (4, 3, 1, 0))

    def test_partial_and_blocked_reasons(self):
        reg = register({
            '1:/a': scene('hd', 'SAKURA1/ENDING/E.SPR'),
            '2:/a': scene('paired-not-wired', 'SAKURA1/ENDING/E.SPR', reason='needs an ending witness'),
            '1:/b': scene('unsupported-size', 'SAKURA2/BG/BBG1.SPR', reason='size [320, 224]'),
            '1:/c': scene('excluded', 'SAKURA1/TITLE/T.SPR', reason='Japanese lettering is baked into the PC image'),
            '1:/d': scene('unpaired'),
        })
        rows, goal, unpaired = self.rows(reg)
        self.assertEqual((rows['scene-ending']['hd'], rows['scene-ending']['partial']), (1, 1))
        self.assertEqual(rows['scene-bbg']['blocked_reasons'], {'tamaño no soportado (T105c)': 1})
        self.assertEqual(rows['scene-title']['goal'], 0)
        self.assertEqual(len(unpaired), 1)
        self.assertEqual(goal, sum(r['goal'] for r in rows.values()))

    def test_unmatched_is_the_remainder(self):
        rows, _, _ = self.rows(register({'1:/a': scene('hd', 'SAKURA2/EVENT/E1.SPR')}))
        ev = rows['scene-event']
        self.assertEqual((ev['candidates'], ev['hd'], ev['unmatched']), (3, 1, 2))

    def test_mixed_donors(self):
        reg = register({'1:/a': scene('hd', 'SAKURA1/BG/BG1.SPR'),
                        '2:/a': scene('excluded', 'SAKURA1/BG/BG1.SPR', reason='x')})
        self.assertEqual(census.mixed_scene_donors(reg), {'SAKURA1/BG/BG1.SPR': {'hd', 'excluded'}})


class Helpers(unittest.TestCase):
    def test_percent_truncates(self):
        self.assertEqual(census.pct(999, 1000), '99,9%')
        self.assertEqual(census.pct(1, 0), '-')

    def test_block_replacement_is_idempotent(self):
        text = f'a\n{census.BEGIN}\nold\n{census.END}\nb\n'
        block = f'{census.BEGIN}\nnew\n{census.END}'
        once = census.replace_block(text, block)
        self.assertEqual(once, f'a\n{block}\nb\n')
        self.assertEqual(census.replace_block(once, block), once)
        with self.assertRaises(ValueError):
            census.replace_block('none', block)


class RepositoryNumbers(unittest.TestCase):
    """The census must agree with the published HD progress for the scene panel."""

    def test_scene_matches_hd_progress(self):
        report = census.build()
        scene = [r for r in report['rows'] if r['id'].startswith('scene-')]
        self.assertEqual(sum(r['goal'] for r in scene), report['scene_goal'])
        progress = (census.ROOT / 'docs/HD_PROGRESS.md').read_text(encoding='utf-8')
        extras = [r for r in scene if r['id'] in ('scene-event', 'scene-cg')]
        core = [r for r in scene if r not in extras]
        goal = sum(r['goal'] for r in core)
        hd = sum(r['hd'] for r in core)
        verified = sum(r['verified'] for r in core)
        scene_line = next(line for line in progress.splitlines() if line.startswith('| Imágenes de escena |'))
        self.assertIn(f'{hd}/{goal}', scene_line)
        self.assertIn(f'{verified}/{goal}', scene_line)
        extra_line = next(line for line in progress.splitlines() if line.startswith('**Extras EVENT y CG**'))
        self.assertIn(f"{sum(r['hd'] for r in extras)}/{sum(r['goal'] for r in extras)}", extra_line)


if __name__ == '__main__':
    unittest.main()
