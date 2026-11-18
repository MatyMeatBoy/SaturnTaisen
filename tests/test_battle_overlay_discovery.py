import unittest
from pathlib import Path
import tempfile
import sys
from unittest.mock import patch

from tools.discover_battle_overlays import BASE, analyze_modules, overlay_module, merge_candidates, read_seed, analyze_with_sdk


class BattleOverlayDiscoveryTests(unittest.TestCase):
    def test_sdk_analysis_disables_bytecode_and_restores_process_flag_after_failure(self):
        previous=sys.dont_write_bytecode
        def fail(*args):
            self.assertTrue(sys.dont_write_bytecode)
            raise ValueError('synthetic analyzer failure')
        with patch('tools.discover_battle_overlays.analyze_modules',side_effect=fail):
            with self.assertRaises(ValueError):analyze_with_sdk([],Path('unused-sdk'))
        self.assertEqual(sys.dont_write_bytecode,previous)
    def test_seed_parser_keeps_versions_and_rejects_unaligned_or_malformed_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'seed.txt'
            valid='# synthetic\n06078000 000B0009\n06078000 E0010009\n'
            path.write_text(valid,encoding='ascii')
            self.assertEqual(len(read_seed(path)),2)
            self.assertEqual(path.read_text(encoding='ascii'),valid)
            for bad in ('06078001 0009','06078000 009','06078000 FFFFFF','garbage','# empty'):
                path.write_text(bad,encoding='ascii')
                with self.subTest(seed=bad),self.assertRaises(ValueError):read_seed(path)
    def image(self, marker=16):
        data=bytearray(32)
        data[marker:marker+4]=(BASE+8).to_bytes(4,'big')
        data[:4]=bytes.fromhex('000b0009')
        return bytes(data)

    def test_only_known_family_and_valid_self_pointer_are_admitted(self):
        module=overlay_module('/SAKURA2/K002.BIN',self.image(),'disc1')
        self.assertEqual(module['base'],BASE)
        self.assertEqual(module['self_pointer_count'],1)
        self.assertIsNone(overlay_module('/SAKURA1/K002.BIN',self.image(),'disc1'))
        self.assertIsNone(overlay_module('/SAKURA2/DATA.BIN',self.image(),'disc1'))
        self.assertIsNone(overlay_module('/SAKURA2/K099.BIN',self.image(),'disc1'))
        for invalid in (b'\0'*32,self.image()[:-1],b'\0'*65538):
            with self.assertRaises(ValueError):overlay_module('/SAKURA2/K002.BIN',invalid,'disc1')

    def test_deduplication_keeps_all_profiles_and_same_pc_variants(self):
        first=overlay_module('/SAKURA2/K002.BIN',self.image(),'disc1')
        duplicate=overlay_module('/SAKURA2/K002.BIN',self.image(),'disc2')
        changed=bytearray(self.image());changed[:2]=bytes.fromhex('e001')
        other=overlay_module('/SAKURA2/K003.BIN',bytes(changed),'disc2')
        calls=[]
        def discover(raw,base,entries,*,eager):
            calls.append(raw);self.assertTrue(eager);self.assertEqual(list(entries),list(range(BASE,BASE+32,2)))
            return [(BASE,raw[:4])]
        blocks,rows=analyze_modules([first,duplicate,other],discover)
        self.assertEqual(len(calls),2);self.assertEqual(len(rows),3)
        self.assertEqual(blocks,{(BASE,self.image()[:4]),(BASE,bytes(changed[:4]))})
        seed={(BASE,b'\x00\x09')}
        merged=merge_candidates(seed,blocks)
        self.assertEqual(len(merged),3);self.assertEqual(seed,{(BASE,b'\x00\x09')})

    def test_analyzer_cannot_publish_bytes_or_addresses_not_in_the_overlay(self):
        module=overlay_module('/SAKURA2/K002.BIN',self.image(),'disc1')
        for bad in ([(BASE+1,b'\0\x0b')],[(BASE+32,b'\0\x0b')],[(BASE,b'\xff\xff')],[(BASE,b'\0')]):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                analyze_modules([module],lambda *a,**k:bad)
