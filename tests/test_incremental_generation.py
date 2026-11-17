"""Adding AOT coverage must not rebuild unrelated generated translation units."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEP = ROOT / 'local/deps/satrecomp'


@unittest.skipUnless((DEP/'tools/recomp.py').is_file(), 'requires pinned generator')
class IncrementalGenerationTests(unittest.TestCase):
    def generate(self, folder, entries, per_file=1, ordered=True):
        database = folder/'blocks.txt'
        database.write_text('\n'.join(entries)+'\n')
        command=[sys.executable,str(DEP/'tools/recomp.py'),
            '--blocks',str(database),'--ops',str(DEP/'machine/sh2_ops.h'),
            '--out',str(folder/'gen'),'--per-file',str(per_file),
            '--max-function-blocks','1']
        if ordered:
            command+=['--append-order',str(folder/'order.json')]
        return subprocess.run(command,capture_output=True,text=True,timeout=20)

    def test_initial_order_matches_default_generator(self):
        with tempfile.TemporaryDirectory() as name:
            folder=Path(name)
            original=['06006000 E002000B0009','06005000 E001000B0009']
            for label,ordered in [('legacy',False),('ordered',True)]:
                target=folder/label
                target.mkdir()
                result=self.generate(target,original,ordered=ordered)
                self.assertEqual(result.returncode,0,result.stderr)
            legacy={p.name:p.read_bytes() for p in (folder/'legacy/gen').glob('*.cpp')}
            ordered={p.name:p.read_bytes() for p in (folder/'ordered/gen').glob('*.cpp')}
            self.assertEqual(legacy,ordered)

    def test_earlier_address_and_same_address_variant_keep_existing_cpp(self):
        with tempfile.TemporaryDirectory() as name:
            folder=Path(name)
            original=['06005000 E001000B0009','06006000 E002000B0009']
            result=self.generate(folder,original)
            self.assertEqual(result.returncode,0,result.stderr)
            files=[folder/'gen'/f'blocks_{i:03d}.cpp' for i in range(2)]
            kept=[(p.read_bytes(),p.stat().st_mtime_ns) for p in files]
            expanded=original+['00204000 E003000B0009','06005000 E004000B0009']
            result=self.generate(folder,expanded)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual([(p.read_bytes(),p.stat().st_mtime_ns) for p in files],kept)
            self.assertIn('0x00204000',(folder/'gen/blocks_002.cpp').read_text())
            self.assertIn('0x06005000',(folder/'gen/blocks_003.cpp').read_text())
            self.assertIn('4 blocks (4 with native code)',result.stdout)
            result=self.generate(folder,expanded)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('0 written',result.stdout)

    def test_changing_partition_size_fails_before_touching_cpp(self):
        with tempfile.TemporaryDirectory() as name:
            folder=Path(name)
            entries=['06005000 E001000B0009']
            first=self.generate(folder,entries)
            self.assertEqual(first.returncode,0,first.stderr)
            target=folder/'gen/blocks_000.cpp'
            before=(target.read_bytes(),target.stat().st_mtime_ns)
            result=self.generate(folder,entries,per_file=2)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('per-file',result.stderr)
            self.assertEqual((target.read_bytes(),target.stat().st_mtime_ns),before)

    def test_removing_known_variant_fails_before_touching_cpp(self):
        with tempfile.TemporaryDirectory() as name:
            folder=Path(name)
            first=self.generate(folder,['06005000 E001000B0009'])
            self.assertEqual(first.returncode,0,first.stderr)
            target=folder/'gen/blocks_000.cpp'
            before=target.read_bytes()
            result=self.generate(folder,['06006000 E002000B0009'])
            self.assertNotEqual(result.returncode,0)
            self.assertIn('missing',result.stderr)
            self.assertEqual(target.read_bytes(),before)

    def test_duplicate_manifest_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            folder=Path(name)
            entries=['06005000 E001000B0009']
            result=self.generate(folder,entries)
            self.assertEqual(result.returncode,0,result.stderr)
            manifest=folder/'order.json'
            data=json.loads(manifest.read_text())
            data['keys']*=2
            manifest.write_text(json.dumps(data))
            before=(folder/'gen/blocks_000.cpp').read_bytes()
            result=self.generate(folder,entries)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('duplicate',result.stderr)
            self.assertEqual((folder/'gen/blocks_000.cpp').read_bytes(),before)


if __name__=='__main__':
    unittest.main()
