"""Synthetic NC metadata, with signed and mirrored coordinates retained."""
import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
class NativeCharacterTests(unittest.TestCase):
    def test_native_metadata_keeps_signed_geometry_and_separates_palette_from_pixels(self):
        from audit_native_characters import inspect_native_character
        raw=bytearray(0x610+192*144);raw[1]=2;raw[16]=2
        struct.pack_into('>B4h',raw,17,60,74,-1,175,37)
        struct.pack_into('>B4h',raw,26,61,153,132,148,136)
        raw[0x410]=0x80;raw[0x610]=7
        row=inspect_native_character(raw)
        self.assertEqual(row['parts'][0]['coordinates'],[74,-1,175,37])
        self.assertEqual(row['parts'][1]['coordinates'],[153,132,148,136])
        self.assertEqual(row['pixel_offset'],0x610)
        self.assertEqual(row['pixel_bytes'],192*144)
        self.assertEqual(row['part_count'],2)
        raw[16]=0;self.assertEqual(inspect_native_character(raw)['parts'],[])
    def test_unknown_or_truncated_data_rejected(self):
        from audit_native_characters import inspect_native_character
        for raw in (bytes(20),bytes(0x610),b'unknown'+bytes(2000)):
            with self.assertRaises(ValueError):inspect_native_character(raw)
        raw=bytearray(0x610);raw[1]=2;raw[16]=255
        with self.assertRaises(ValueError):inspect_native_character(raw)
