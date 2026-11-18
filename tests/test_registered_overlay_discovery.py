import hashlib
import unittest

from tools.discover_battle_overlays import analyze_modules
from tools.discover_registered_overlays import registered_module


class RegisteredOverlayTests(unittest.TestCase):
    def fixture(self):
        raw=bytes.fromhex('000b0009')+bytes(28)
        spec={'EVT02':dict(file='/SAKURA2/EVT02.BIN',base=0x204000,bytes=len(raw),
                           sha256=hashlib.sha256(raw).hexdigest(),evidence='synthetic full RAM match')}
        return raw,spec

    def test_registered_identity_requires_exact_size_hash_and_known_name(self):
        raw,spec=self.fixture()
        module=registered_module('EVT02',raw,'disc1',spec)
        self.assertEqual(module['base'],0x204000)
        self.assertEqual(module['raw'],raw)
        for name,data in [('EVT99',raw),('EVT02',raw[:-1]),('EVT02',bytes(32))]:
            with self.subTest(name=name),self.assertRaises(ValueError):registered_module(name,data,'disc1',spec)

    def test_same_bytes_at_distinct_registered_bases_are_not_deduplicated(self):
        raw,spec=self.fixture();a=registered_module('EVT02',raw,'one',spec)
        b=dict(a,base=0x6004000,profile='two');calls=[]
        def discover(data,base,entries,*,eager):
            calls.append(base);self.assertEqual(min(entries),base)
            return [(base,data[:4])]
        blocks,rows=analyze_modules([a,b],discover)
        self.assertEqual(calls,[0x204000,0x6004000])
        self.assertEqual(blocks,{(0x204000,raw[:4]),(0x6004000,raw[:4])})
        self.assertEqual([row['base'] for row in rows],['00204000','06004000'])
