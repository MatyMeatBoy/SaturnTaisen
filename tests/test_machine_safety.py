"""Synthetic hardware regressions, built with tools/build_runtime.py check-machine."""
import os
from pathlib import Path
import subprocess
import unittest
import tempfile
import hashlib

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / 'local/build/machine-tests/machine-tests.exe'


@unittest.skipUnless(EXE.is_file(), 'requires the local synthetic machine test build')
class MachineTests(unittest.TestCase):
    def test_invalid_existing_backup_is_rejected_without_reformatting(self):
        cases = [b'not a Saturn backup', b'x' * 32768,
                 b'BackUpRam Format' + b'\0' * 100,
                 b'BackUpRam Format' + b'\0' * (65536 - 16)]
        with tempfile.TemporaryDirectory(dir=ROOT / 'local') as directory:
            for i, data in enumerate(cases):
                with self.subTest(case=i):
                    path=Path(directory)/'supplied.bin'
                    path.write_bytes(data)
                    result=self.run_machine('backup-open',str(path))
                    self.assertEqual(hashlib.sha256(path.read_bytes()).digest(),hashlib.sha256(data).digest(),
                                     'existing save was modified while opening')
                    self.assertEqual(result.returncode,4,result.stderr)

    def run_machine(self, *args, strict=True, reference=False):
        env = {k: v for k, v in os.environ.items() if not k.startswith('SATRECOMP_')}
        env['PATH'] = 'C:/msys64/clang64/bin' + os.pathsep + env.get('PATH', '')
        if strict:
            env['SATRECOMP_STRICT_NATIVE'] = '1'
        if reference:
            env['SATRECOMP_NO_BLOCKS'] = '1'
        return subprocess.run([str(EXE), *args], env=env, capture_output=True, text=True, timeout=10)

    def test_cd_bus_seeks_track_fad_and_pause(self):
        result = self.run_machine()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_strict_bios_rejects_unimplemented_service_without_fake_success(self):
        result = self.run_machine('unsupported-bios')
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn('strict AOT: unsupported BIOS service 0600026C', result.stderr)

    def test_replacing_disc_reader_invalidates_same_fad_cache(self):
        result = self.run_machine('disc-cache')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_default_native_rejects_missing_translation_without_environment_flags(self):
        result = self.run_machine('untranslated-default', strict=False)
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn('strict AOT: untranslated', result.stderr)

    def test_default_native_rejects_unsupported_bios_without_environment_flags(self):
        result = self.run_machine('unsupported-bios', strict=False)
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn('strict AOT: unsupported BIOS service 0600026C', result.stderr)

    def test_explicit_reference_mode_can_interpret_synthetic_guest(self):
        result = self.run_machine('untranslated-default', strict=False, reference=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_overlays_in_both_ram_banks_follow_byte_word_and_long_writes(self):
        for bank in ('high','low'):
            with self.subTest(bank=bank):
                result=self.run_machine('overlay',bank)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('Exact overlay variants survived all write widths',result.stdout)

    def test_cache_purge_rejects_stale_translation_after_other_cpu_write(self):
        for bank in ('high', 'low'):
            for method in ('cp', 'byte', 'word', 'long'):
                with self.subTest(bank=bank, method=method):
                    result = self.run_machine('overlay-purge', bank, method)
                    self.assertEqual(result.returncode, 4, result.stderr)
                    self.assertIn('strict AOT: untranslated', result.stderr)

    def test_overlay_with_uncompiled_bytes_never_reuses_previous_translation(self):
        for bank in ('high','low'):
            with self.subTest(bank=bank):
                result=self.run_machine('overlay-invalid',bank)
                self.assertEqual(result.returncode,4,result.stderr)
                self.assertIn('strict AOT: untranslated',result.stderr)


if __name__ == '__main__':
    unittest.main()
