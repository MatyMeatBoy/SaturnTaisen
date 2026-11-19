from collections import Counter
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


class SystemHudReviewTest(unittest.TestCase):
    def test_all_previous_unknowns_are_classified(self):
        inventory = read_json('docs/research/pc-menu-hud-inventory.json')
        review = read_json('config/hd-system-hud-review.json')
        menus = {row['id']: row for row in inventory['menus']}
        reviewed = {row['id']: row for row in review['system']}
        self.assertEqual(len(review['system']), len(reviewed))
        self.assertEqual(set(reviewed), set(inventory['named_without_candidate']))
        self.assertEqual(sum(shape['count'] for row in reviewed.values() for shape in row['pc_shapes']), 430)
        self.assertEqual([row['id'] for row in review['system'] if row['status'] == 'conditional_candidate'],
                         ['FONT_CSL'])
        for name, row in reviewed.items():
            with self.subTest(name=name):
                source = menus[name]
                self.assertEqual(row['pc_path'], source['pc_path'])
                self.assertEqual(row['pc_sha256'], source['sha256'])
                sizes = Counter((img['width'], img['height']) for img in source['images'])
                self.assertEqual({tuple(shape['size']): shape['count'] for shape in row['pc_shapes']}, sizes)
                indices = {img['index'] for img in source['images']}
                for command in row['saved_command_evidence']:
                    self.assertIn(command['pc_index'], indices)
                    self.assertRegex(command['texture_sha256'], r'^[0-9a-f]{64}$')
                    self.assertRegex(command['cram_sha256'], r'^[0-9a-f]{64}$')
        arrows = reviewed['FONT_CSL']['saved_command_evidence']
        self.assertEqual([arrow['pc_index'] for arrow in arrows], [0, 1])
        self.assertEqual([arrow['size'] for arrow in arrows], [[8, 16], [8, 16]])
        self.assertNotEqual(arrows[0]['texture_sha256'], arrows[1]['texture_sha256'])
        self.assertEqual(arrows[0]['cram_sha256'], arrows[1]['cram_sha256'])

    def test_wall_matches_the_existing_provenance(self):
        wall = read_json('config/hd-system-hud-review.json')['wall']
        sources = read_json('assets/generated/backgrounds/provenance.json')['backgrounds']
        pc_sources = read_json('assets/generated/pc-backgrounds/provenance.json')['backgrounds']
        source = next(row for row in sources if row['id'] == 'KABE00')
        pc_source = next(row for row in pc_sources if row['id'] == 'KABE0100')
        self.assertEqual(wall['saturn_sha256'], source['source_kabe_sha256'])
        self.assertEqual(int(wall['palette_fnv'], 16), int(source['source_palette_fingerprint'], 16))
        self.assertEqual(wall['pc_sha256'], pc_source['source_spred_sha256'])
        self.assertEqual(wall['pc_index'], pc_source['source_image'])
        self.assertEqual(wall['pc_size'], pc_source['source_size'])


if __name__ == '__main__':
    unittest.main()
