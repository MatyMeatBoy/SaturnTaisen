"""Tests for tools/decode_saturn_units.py: synthetic banks always, hashes and sizes of the real banks when present.

No pixel is stored or printed: the real-data test only compares counts, sizes and SHA-256 of decoded images."""
import hashlib
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import decode_saturn_units as units  # noqa: E402

ISO1 = ROOT / 'local/prepared/disc1/Track 01.iso'
ISO2 = ROOT / 'local/prepared/disc2/Track 01.iso'
MAIN_ROOT = ROOT.parent / 'workspace'


def image_set(images):
    """A raw image set from [(w, h, fmt, pixels)]."""
    head = struct.pack('>H', len(images)) + bytes(14)
    data = b''
    for w, h, fmt, pixels in images:
        head += struct.pack('>HHHHII', w, h, fmt, 0x5F0 if fmt == 0 else 0, len(data), len(pixels))
        data += pixels
    return head + data


def literal_lz(raw):
    """The game's LZ stream made only of literals plus the end marker (flag bits 0,1 then L=H=0)."""
    out = bytearray()
    chunks = [raw[i:i + 8] for i in range(0, len(raw), 8)]
    for k, chunk in enumerate(chunks):
        flag = (1 << len(chunk)) - 1
        if k == len(chunks) - 1 and len(chunk) <= 6:
            flag |= 2 << len(chunk)
        out.append(flag)
        out += chunk
    if len(chunks[-1]) > 6:
        out.append(0x02)
    return bytes(out) + bytes([0, 0])


def bank(slots):
    """A bank from {slot: bytes}."""
    table, body, cursor = b'', b'', units.FIRST_ENTRY
    for slot in range(units.SLOTS):
        raw = slots.get(slot, b'')
        table += struct.pack('>II', cursor, len(raw))
        body += raw
        cursor += len(raw)
    return table + bytes(units.FIRST_ENTRY - len(table)) + body


class SyntheticTests(unittest.TestCase):
    def test_table_header_is_0xd0_bytes(self):
        self.assertEqual(units.TABLE_BYTES, 0xD0)
        self.assertEqual(units.FIRST_ENTRY, 0xD0)

    def test_image_set_8bpp_and_4bpp(self):
        raw = image_set([(2, 2, 4, bytes([0, 1, 2, 3])), (4, 2, 0, bytes([0x01, 0x23, 0x45, 0x67]))])
        records, base = units.image_set(raw)
        self.assertEqual(base, 16 + 32)
        self.assertEqual(units.image_indices(raw, records[0]), [bytes([0, 1]), bytes([2, 3])])
        self.assertEqual(units.image_indices(raw, records[1]), [bytes([0, 1, 2, 3]), bytes([4, 5, 6, 7])])
        self.assertEqual(units.silhouette(units.image_indices(raw, records[0])), [[0, 1], [1, 1]])

    def test_image_set_rejects_bad_size_and_extent(self):
        raw = bytearray(image_set([(2, 2, 4, bytes(4))]))
        raw[16 + 12:16 + 16] = struct.pack('>I', 5)
        with self.assertRaises(units.UnitError):
            units.image_set(bytes(raw))
        with self.assertRaises(units.UnitError):
            units.image_set(image_set([(2, 2, 4, bytes(4))])[:-1])
        with self.assertRaises(units.UnitError):
            units.image_set(b'\x00\x01' + b'\x01' * 14)

    def test_bank_entries_and_palette(self):
        palette = struct.pack('>4H', 0x8000, 0xFFFF, 0x801F, 0x83E0)
        data = bank({12: palette, 18: image_set([(2, 2, 4, bytes(4))])})
        pairs = units.entries(data)
        self.assertEqual(pairs[12][0], units.FIRST_ENTRY)
        self.assertEqual(units.palette_words(data, 12), [0x8000, 0xFFFF, 0x801F, 0x83E0])
        self.assertEqual(len(list(units.all_images(data))), 1)
        with self.assertRaises(units.UnitError):
            units.entries(data[:units.FIRST_ENTRY + 3])

    def test_compressed_slot_zero(self):
        raw = image_set([(2, 2, 4, bytes([0, 9, 9, 0]))])
        data = bank({0: literal_lz(raw)})
        slot, n, record, rows = next(units.all_images(data))
        self.assertEqual((slot, n, record[:2]), (0, 0, (2, 2)))
        self.assertEqual(rows, [bytes([0, 9]), bytes([9, 0])])


# Sizes recorded by `python tools/decode_saturn_units.py --inventory` (config/hd-saturn-unit-images.json).
REAL_BANKS = {
    (1, 'UNIT04.BIN'): (81420, 120),
}


@unittest.skipUnless(ISO1.exists() or (MAIN_ROOT / 'local/prepared/disc1/Track 01.iso').exists(), 'Saturn disc 1 not prepared')
class RealBankTests(unittest.TestCase):
    def setUp(self):
        import decode_saturn_bg as saturn
        path = ISO1 if ISO1.exists() else MAIN_ROOT / 'local/prepared/disc1/Track 01.iso'
        iso = saturn.Iso(path)
        self.addCleanup(iso.file.close)
        self.data = iso.content(dict(iso.files('SAKURA2'))['UNIT04.BIN'])

    def test_layout_sizes(self):
        size, count = REAL_BANKS[(1, 'UNIT04.BIN')]
        self.assertEqual(len(self.data), size)
        pairs = units.entries(self.data)
        self.assertEqual(pairs[0], (0xD0, 0x71AC))
        self.assertEqual([i for i, p in enumerate(pairs) if p[1]], [0, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24, 25])
        records, raw = units.entry_image_set(self.data, 0)
        self.assertEqual((len(records), len(raw)), (count, 66512))
        self.assertEqual(hashlib.sha256(raw).hexdigest()[:16], 'c809eea50acf4ff6')

    def test_all_images_decode(self):
        images = list(units.all_images(self.data))
        self.assertEqual(len(images), 307)
        self.assertLess(max(max(max(r) for r in rows if r) for _, _, _, rows in images), 64)


if __name__ == '__main__':
    unittest.main()
