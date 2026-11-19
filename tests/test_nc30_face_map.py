"""Check the offline NC30 face table without proprietary inputs."""
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Nc30FaceMapTest(unittest.TestCase):
    def test_body_and_face_table(self):
        data = json.loads((ROOT / 'config/hd-nc30-face-map.json').read_text(encoding='utf-8'))
        body, frames = data['body'], data['frames']
        self.assertEqual(data['schema'], 1)
        self.assertEqual(len(frames), 54)
        self.assertEqual(len({row['saturn_sha256'] for row in frames}), 54)
        for digest in (data['assets']['saturn_sha256'], data['assets']['pc_sha256'], body['saturn_sha256'],
                       *(row['saturn_sha256'] for row in frames)):
            self.assertRegex(digest, r'^[0-9a-f]{64}$')
        self.assertEqual(body['saturn_offset'], 0x610)
        self.assertEqual(body['saturn_size'], [176, 144])
        self.assertEqual(body['pc_index'], 0)
        self.assertEqual(body['pc_size'], [368, 320])
        offset = body['saturn_offset'] + 176 * 144
        for repetition in range(6):
            eye_frames = range(6 + repetition * 3, 9 + repetition * 3)
            mouth_frames = range(30 + repetition * 6, 36 + repetition * 6)
            for slot, pc_index in enumerate([*eye_frames, *mouth_frames]):
                row = frames[repetition * 9 + slot]
                self.assertEqual(row['saturn_offset'], offset)
                self.assertEqual(row['saturn_size'], [32 if slot < 3 else 24, 16])
                self.assertEqual(row['pc_index'], pc_index)
                self.assertEqual(row['pc_size'], [96, 47] if pc_index <= 53 else [80, 63])
                w, h = row['saturn_size']
                offset += w * h
        self.assertEqual(offset, 49936)


if __name__ == '__main__':
    unittest.main()
