"""Synthetic SH-2 programs for ahead-of-time coverage analysis."""
import importlib.util
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x06004000


@unittest.skipUnless((ROOT / 'local/deps/satrecomp/machine/sh2_ops.h').is_file(),
                     'requires the pinned satrecomp opcode definitions')
class StaticProgramTests(unittest.TestCase):
    def analyzer(self):
        source = ROOT / 'tools/static_program.py'
        self.assertTrue(source.is_file(), 'static program analyzer is missing')
        spec = importlib.util.spec_from_file_location('static_program', source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_discovers_function_pointer_and_return_from_indirect_call(self):
        module = self.analyzer()
        data = bytearray(64)
        data[:10] = bytes.fromhex('d107410b0009000b0009')
        data[16:22] = bytes.fromhex('e007000b0009')
        struct.pack_into('>I', data, 32, BASE + 16)
        result = module.discover(bytes(data), BASE)
        blocks = dict(result)
        self.assertEqual(blocks[BASE], bytes.fromhex('d107410b0009'))
        self.assertEqual(blocks[BASE+6], bytes.fromhex('000b0009'))
        self.assertEqual(blocks[BASE+16], bytes.fromhex('e007000b0009'))
        self.assertNotIn(BASE+32, blocks, 'literal pool was treated as an entry point')

    def test_follows_call_branch_and_conditional_targets(self):
        module = self.analyzer()
        data = bytearray(64)
        # BSR +16; return at +4; BT at +16 goes to +24; BRA skips to +32.
        data[:8] = bytes.fromhex('b0060009000b0009')
        data[16:24] = bytes.fromhex('8902a00500090009')
        data[24:28] = bytes.fromhex('000b0009')
        data[32:36] = bytes.fromhex('000b0009')
        blocks = dict(module.discover(bytes(data), BASE))
        self.assertTrue({BASE, BASE+4, BASE+16, BASE+24, BASE+32}.issubset(blocks))

    def test_rejects_truncated_or_illegal_delay_slot(self):
        module = self.analyzer()
        self.assertEqual(module.discover(bytes.fromhex('000b'), BASE), [])
        self.assertEqual(module.discover(bytes.fromhex('a000a000'), BASE), [])

    def test_follows_bounded_relative_switch_table(self):
        module = self.analyzer()
        data = bytearray(96)
        data[:22] = bytes.fromhex('e10238168d1c00096183311cc704011d301c402b0009')
        struct.pack_into('>3h', data, 32, 16, 32, 48)
        for address in (48,64,80):
            data[address:address+6] = bytes.fromhex('e007000b0009')
        blocks = dict(module.discover(bytes(data), BASE))
        self.assertTrue({BASE+48,BASE+64,BASE+80}.issubset(blocks),
                        'computed switch targets were missed')
        data[:2] = bytes.fromhex('0009')
        blocks = dict(module.discover(bytes(data), BASE))
        self.assertNotIn(BASE+48, blocks, 'guessed an unbounded table')
        # Same switch, but the index copy is in BT/S's delay slot.
        data[:22] = bytes.fromhex('e10238168d1c6183311cc705011d301c402b00090000')
        blocks = dict(module.discover(bytes(data), BASE))
        self.assertTrue({BASE+48,BASE+64,BASE+80}.issubset(blocks))

    def test_reads_first_root_program_and_header_load_address_from_iso(self):
        module = self.analyzer()
        with tempfile.TemporaryDirectory() as directory:
            iso = bytearray(23*2048)
            iso[:16] = b'SEGA SEGASATURN '
            struct.pack_into('>I',iso,0xf0,BASE)
            iso[16*2048:16*2048+7] = b'\x01CD001\x01'
            def record(lba,size,name,flags=0):
                result = bytearray(34+len(name)+(len(name)&1))
                result[0]=len(result);result[25]=flags;result[32]=len(name)
                struct.pack_into('<I',result,2,lba);struct.pack_into('>I',result,6,lba)
                struct.pack_into('<I',result,10,size);struct.pack_into('>I',result,14,size)
                result[33:33+len(name)] = name
                return result
            root = record(20,2048,b'\x00',2)
            iso[16*2048+156:16*2048+156+len(root)] = root
            first = record(21,6,b'FIRST;1')
            iso[20*2048:20*2048+len(root+first)] = root+first
            iso[21*2048:21*2048+6] = bytes.fromhex('e007000b0009')
            path = Path(directory)/'disc.iso';path.write_bytes(iso)
            code,base,info = module.read_first_program(path)
            self.assertEqual((base,code),(BASE,bytes.fromhex('e007000b0009')))
            self.assertEqual(info['file'],'FIRST')
            path.write_bytes(iso[:21*2048+2])
            with self.assertRaises(ValueError):
                module.read_first_program(path)

    def test_switch_bound_loaded_in_incoming_branch_delay_slot(self):
        module = self.analyzer()
        data = bytearray(160)
        data[:8] = bytes.fromhex('8d0ee102000b0009')
        data[32:54] = bytes.fromhex('38168f026183a02b0009311cc704011d301c402b0009')
        struct.pack_into('>3h',data,64,16,32,48)
        for address in (80,96,112,128):
            data[address:address+4] = bytes.fromhex('000b0009')
        blocks = dict(module.discover(bytes(data),BASE))
        self.assertTrue({BASE+80,BASE+96,BASE+112}.issubset(blocks))
        data[2:4] = bytes.fromhex('0009')
        self.assertNotIn(BASE+80,dict(module.discover(bytes(data),BASE)))

    def test_eager_cli_includes_unreferenced_aligned_code(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'main.bin'
            output = Path(directory)/'blocks.txt'
            image = bytearray(32)
            image[:4] = bytes.fromhex('000b0009')
            image[16:20] = bytes.fromhex('000b0009')
            source.write_bytes(image)
            result = subprocess.run([sys.executable,str(ROOT/'tools/static_program.py'),
                '--image',str(source),'--base',hex(BASE),'--all-entries','--output',str(output)],
                capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn(f'{BASE+16:08X} ',output.read_text())
            self.assertIn(f'{BASE+2:08X} ',output.read_text(),
                          'eager mode discarded a valid instruction before an unsupported opcode')
            self.assertEqual(source.read_bytes(),image)

    def test_keeps_47_instruction_prefix_before_delayed_branch_at_block_limit(self):
        module = self.analyzer()
        ops = [0xe001 if i&1 else 0xe102 for i in range(47)]+[0x000b,0x0009]
        image = struct.pack('>49H',*ops)
        blocks = dict(module.discover(image,BASE,range(BASE,BASE+len(image),2)))
        self.assertIn(BASE,blocks,'valid block truncated before a delay slot was discarded')
        self.assertEqual(blocks[BASE],image[:94])


if __name__ == '__main__':
    unittest.main()
