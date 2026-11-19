import hashlib
import unittest

from tools.discover_battle_overlays import analyze_modules
from tools.discover_registered_overlays import observed_candidates, registered_module


class RegisteredOverlayTests(unittest.TestCase):
    def test_registered_slice_checks_whole_source_and_emits_only_copied_bytes(self):
        raw,spec=self.fixture()
        spec['EVT02'].update(slice_offset=8,slice_bytes=8,base=0x06002000)
        module=registered_module('EVT02',raw,'disc1',spec)
        self.assertEqual(module['raw'],raw[8:16])
        self.assertEqual(module['bytes'],8)
        self.assertEqual(module['source_bytes'],len(raw))
        self.assertEqual(module['source_sha256'],hashlib.sha256(raw).hexdigest())
        self.assertEqual(module['sha256'],hashlib.sha256(raw[8:16]).hexdigest())
        altered=raw[:-1]+bytes([raw[-1]^1])
        with self.assertRaises(ValueError):registered_module('EVT02',altered,'disc1',spec)
        for offset,size in [(-2,8),(1,8),(8,0),(8,7),(30,8)]:
            spec['EVT02'].update(slice_offset=offset,slice_bytes=size)
            with self.subTest(offset=offset,size=size),self.assertRaises(ValueError):
                registered_module('EVT02',raw,'disc1',spec)

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

    def test_observed_candidates_read_only_registered_ranges(self):
        module = dict(base=0x06080000, raw=bytes(range(16)))
        self.assertEqual(observed_candidates(module, [[2, 4], [8, 2]]), {
            (0x06080002, bytes(range(2, 6))), (0x06080008, bytes(range(8, 10)))})
        for ranges in ([], [[-2, 4]], [[1, 4]], [[2, 3]], [[14, 4]], [[2, 4], [2, 4]], [[True, 4]]):
            with self.subTest(ranges=ranges), self.assertRaises(ValueError):
                observed_candidates(module, ranges)
