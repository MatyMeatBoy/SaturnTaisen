"""Original synthetic save containers; no downloaded game progress in fixtures."""
import struct
import subprocess
import sys
from pathlib import Path
import unittest
import zlib
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from import_saves import decode_saves, decode_ssf_single, make_backup


def container(kind, payload=b'original synthetic progress'):
    header = bytearray(64)
    header[16:28] = b'SAKURA___01\0'
    if kind == 'bup':
        header[:4] = b'Vmem'
        header[28:39] = b'SYNTHETIC\0\0'
        header[39] = 1
        struct.pack_into('>II', header, 40, 1234, len(payload))
    else:
        header[:8] = b'SSAVERAW'
        struct.pack_into('>I', header, 28, len(payload))
        header[32:43] = b'SYNTHETIC\0\0'
        header[43] = 1
        struct.pack_into('>I', header, 44, 1234)
        struct.pack_into('>I', header, 12, zlib.crc32(header[16:] + payload))
    return bytes(header) + payload


class ImportTests(unittest.TestCase):
    def test_ssf_single_requires_explicit_format_and_preserves_date(self):
        # Jan 1 1980, 20:34 = 1234 minutes from the Saturn epoch.
        stamp = (1 << 19) | (1 << 14) | (20 << 9) | (34 << 3)
        data = b'SYNTHETIC\0\0\x01' + struct.pack('<I', stamp) + b'original synthetic progress'
        self.assertEqual(decode_ssf_single(data, b'SAKURA___01'), decode_saves(container('bup')))
        with self.assertRaises(ValueError):
            decode_saves(data)
        broken = data[:12] + struct.pack('<I', stamp & ~(15 << 19)) + data[16:]
        with self.assertRaises(ValueError):
            decode_ssf_single(broken, b'SAKURA___01')

    def test_bup_and_saroo_preserve_metadata_and_payload(self):
        a, b = [decode_saves(container(kind))[0] for kind in ('bup', 'saroo')]
        self.assertEqual(a, b)
        self.assertEqual(a.name, b'SAKURA___01')
        self.assertEqual(a.date, 1234)
        self.assertEqual(a.language, 1)
        self.assertEqual(a.data, b'original synthetic progress')

    def test_native_and_interleaved_internal_images_round_trip(self):
        saves = decode_saves(container('bup', bytes(range(256)) * 23))
        native = make_backup(saves)
        self.assertEqual(len(native), 32768)
        self.assertEqual(decode_saves(native), saves)
        physical = bytearray(65536)
        physical[1::2] = native
        self.assertEqual(decode_saves(bytes(physical)), saves)

    def test_truncation_and_saroo_crc_errors_are_rejected(self):
        for data in (container('bup')[:-1], container('saroo')[:-1], b'unknown'):
            with self.subTest(data=data[:8]), self.assertRaises(ValueError):
                decode_saves(data)
        data = bytearray(container('saroo'))
        data[-1] ^= 1
        with self.assertRaises(ValueError):
            decode_saves(bytes(data))

    def test_cyclic_or_truncated_native_chain_is_rejected(self):
        raw = bytearray(make_backup(decode_saves(container('bup', b'x' * 200))))
        struct.pack_into('>H', raw, 2 * 64 + 34, 2)
        with self.assertRaises(ValueError):
            decode_saves(bytes(raw))
        with self.assertRaises(ValueError):
            decode_saves(bytes(raw[:-64]))

    def test_oversized_import_cannot_silently_truncate(self):
        saves = decode_saves(container('bup', b'x' * 32768))
        with self.assertRaises(ValueError):
            make_backup(saves)

    def test_cli_keeps_source_and_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'supplied.BUP'
            target = Path(directory) / 'active.bin'
            data = container('bup')
            source.write_bytes(data)
            target.write_bytes(b'existing progress')
            script = Path(__file__).resolve().parents[1] / 'tools/import_saves.py'
            result = subprocess.run([sys.executable, str(script), str(source), '--output', str(target)],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_bytes(), b'existing progress')
            self.assertEqual(source.read_bytes(), data)
            new_target = Path(directory) / 'imported.bin'
            result = subprocess.run([sys.executable, str(script), str(source), '--output', str(new_target)],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(decode_saves(new_target.read_bytes()), decode_saves(data))
            self.assertEqual(source.read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
