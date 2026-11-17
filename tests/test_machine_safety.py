"""Synthetic hardware regressions, built with tools/build_runtime.py check-machine."""
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / 'local/build/machine-tests/machine-tests.exe'


@unittest.skipUnless(EXE.is_file(), 'requires the local synthetic machine test build')
class MachineTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
