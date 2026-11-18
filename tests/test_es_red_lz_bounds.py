import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools/es"))
from red_lz import compress,decompress_ex,FormatError

class RedLzBoundsTests(unittest.TestCase):
    def test_literal_stream_obeys_limit(self):
        packed=compress(b"abc")
        with self.assertRaises(FormatError):decompress_ex(packed,limit=2)
        self.assertEqual(decompress_ex(packed,limit=3)[0],b"abc")
    def test_empty_output_and_copy_stream_limits(self):
        self.assertEqual(decompress_ex(compress(b""),limit=0)[0],b"")
        with self.assertRaises(FormatError):decompress_ex(compress(b"a"*300),limit=299)
    def test_invalid_start_and_negative_limit_are_rejected(self):
        packed=compress(b"abc")
        for start,limit in [(-1,20),(len(packed)+1,20),(0,-1)]:
            with self.assertRaises(FormatError):decompress_ex(packed,start,limit)
