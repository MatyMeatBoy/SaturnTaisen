"""Spanish translation tooling: synthetic checks plus optional checks against the owner's disc."""
import mmap
import os
import random
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER = Path(os.environ.get('SAKURA_OWNER_ROOT', ROOT))
DISC = OWNER / 'local/prepared/disc1/Track 01.iso'
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools/es'))

import combate  # noqa: E402
import tablas  # noqa: E402
from red_lz import compress, decompress  # noqa: E402


def english_table(texts, footer=b'.a.e\0\0'):
    """Synthetic table in the English 32-bit TBL.BIN layout."""
    body, entries = bytearray(), []
    for i, text in enumerate(texts):
        raw = text.replace('\n', '\r').encode('cp1252')
        raw += b' ' * (len(raw) % 2)
        entries.append(struct.pack('>II', 0x2711 + i, len(body)))
        body += b'\0\0\0\0' + raw + b'\0\0'
    head = 8 + 8 * len(texts)
    return struct.pack('>II', head // 2, (head + len(body)) // 2) + b''.join(entries) + bytes(body) + footer


class RedLzTest(unittest.TestCase):
    def test_round_trip_varied_data(self):
        rng = random.Random(7)
        samples = [b'', b'a', bytes(300), bytes(range(256)) * 4,
                   bytes(rng.randrange(256) for _ in range(3000)),
                   b''.join(bytes([rng.randrange(4)]) * rng.randrange(1, 40) for _ in range(500))]
        for data in samples:
            self.assertEqual(decompress(compress(data)), data)


class DialogueTableTest(unittest.TestCase):
    def test_rebuild_keeps_bytes_and_replaces_text(self):
        original = english_table(['Hello there.', 'Odd', 'Two\nlines'])
        self.assertTrue(tablas.rebuild_identical(original))
        spanish = tablas.build_table(original, {0: '¡Hola, señor Ogami!', 2: 'Dos\nlíneas'})
        records = tablas.parse_table(spanish)
        self.assertEqual([r.display_text.rstrip() for r in records], ['¡Hola, señor Ogami!', 'Odd', 'Dos\nlíneas'])
        self.assertTrue(spanish.endswith(b'.a.e\0\0'))

    def test_wrap_and_limits(self):
        self.assertEqual(tablas.wrap('uno dos tres', keep_lines=False), ['uno dos tres'])
        self.assertTrue(all(len(line) <= 30 for line in tablas.wrap('palabra ' * 12)))
        self.assertEqual(tablas.check('x' * 31), ["line over 30: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'"])
        self.assertTrue(tablas.check('Taishō'))  # ō is outside CP1252
        self.assertEqual(tablas.check('Opción A\nOpción B', keep_lines=True), [])


class BattleTableTest(unittest.TestCase):
    def test_round_trip_and_accents(self):
        words = [0, 0] + combate.encode('Ready~') + [0]
        data = struct.pack('>HH', 4, 4 + len(words)) + struct.pack('>HH', 0xBA, 0) + struct.pack(f'>{len(words)}H', *words) + b'\x00n'
        # header: record area starts after one 4-byte entry -> 8 bytes = 4 words
        self.assertTrue(combate.rebuild_identical(data))
        out = combate.build(data, {0: '¡Ya está!\nVamos'})
        _, _, records = combate.parse(out)
        self.assertEqual(combate.decode(records[0]['words']), '¡Ya está!\nVamos')


@unittest.skipUnless(DISC.is_file(), 'requires the owner prepared English disc 1')
class OwnerDiscTest(unittest.TestCase):
    def test_every_english_table_rebuilds_byte_for_byte(self):
        from audit_sdk import files
        with DISC.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
            for path, lba, size in files(iso):
                data = bytes(iso[lba * 2048:lba * 2048 + size])
                if path.endswith('TBL.BIN'):
                    self.assertTrue(tablas.rebuild_identical(data), path)
                elif path.endswith('MES.BIN'):
                    self.assertTrue(combate.rebuild_identical(data), path)


if __name__ == '__main__':
    unittest.main()
