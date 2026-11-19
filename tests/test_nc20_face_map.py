"""Check the offline NC20 face table without proprietary inputs."""
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Nc20FaceMapTest(unittest.TestCase):
    def test_body_and_face_table(self):
        data = json.loads((ROOT / 'config/hd-nc20-face-map.json').read_text(encoding='utf-8'))
        body, frames = data['body'], data['frames']
        self.assertEqual(data['schema'], 1)
        self.assertEqual(len(frames), 63)
        self.assertEqual(len({row['saturn_sha256'] for row in frames}), 63)
        for digest in (data['assets']['saturn_sha256'], data['assets']['pc_sha256'], body['saturn_sha256'],
                       *(row['saturn_sha256'] for row in frames)):
            self.assertRegex(digest, r'^[0-9a-f]{64}$')
        self.assertEqual(body['saturn_offsets'], [0x610])
        self.assertEqual(body['saturn_size'], [152, 144])
        self.assertEqual(body['pc_index'], 0)
        self.assertEqual(body['pc_size'], [296, 320])
        self.assertEqual(data['blank'], {'saturn_offset': 0x610 + 152 * 144, 'length': 17280})

        by_offset = {offset: frame for frame in frames for offset in frame['saturn_offsets']}
        self.assertEqual(len(by_offset), 72)
        offset = data['blank']['saturn_offset'] + data['blank']['length']
        for group, height in enumerate([16, 16, 16, 24, 32, 32, 24, 16]):
            pc_group = group % 7
            self.assertEqual(data['groups'][group],
                             {'saturn_offset': offset, 'eye_height': height, 'pc_group': pc_group + 1})
            eyes = range(8 + pc_group * 3, 11 + pc_group * 3)
            mouths = range(39 + pc_group * 6, 45 + pc_group * 6)
            for slot, expected_index in enumerate([*eyes, *mouths]):
                frame = by_offset[offset]
                self.assertEqual(frame['pc_index'], expected_index)
                self.assertEqual(len(frame['saturn_offsets']), 2 if pc_group == 0 else 1)
                dimensions = (48, height) if slot < 3 else (24, 24)
                self.assertEqual(frame['saturn_size'], list(dimensions))
                if slot < 3:
                    self.assertEqual(frame['pc_size'], [104, [63, 71, 71, 71, 71, 71, 79][pc_group]])
                else:
                    self.assertEqual(frame['pc_size'], [80, 63 if pc_group < 4 else 55])
                offset += dimensions[0] * dimensions[1]
        self.assertEqual(offset, 93712)


if __name__ == '__main__':
    unittest.main()
