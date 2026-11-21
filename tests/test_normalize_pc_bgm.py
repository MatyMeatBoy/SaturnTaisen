import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from normalize_pc_bgm import normalize


def wave(payload, prefix=b''):
    # Minimal observed RIFF envelope. Decoder validity is tested on local assets.
    chunk = b'data' + struct.pack('<I', len(payload)) + prefix + payload
    return b'RIFF' + struct.pack('<I', 4 + 8 + len(payload)) + b'WAVE' + chunk


class NormalizeTests(unittest.TestCase):
    def test_keeps_standard_wave(self):
        data = wave(b'01234567')
        self.assertEqual(normalize(data), (data, None))

    def test_removes_prefix_and_preserves_uninterpreted_loop_value(self):
        payload = b'01234567'
        self.assertEqual(normalize(wave(payload, b'loop' + struct.pack('<I', 1234))),
                         (wave(payload), 1234))

    def test_rejects_inconsistent_extent(self):
        for data in (wave(b'01234567')[:-1], wave(b'01234567', b'x' * 8)):
            with self.assertRaises(ValueError):
                normalize(data)


if __name__ == '__main__':
    unittest.main()
