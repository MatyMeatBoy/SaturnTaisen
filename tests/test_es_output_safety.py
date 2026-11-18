"""Invented discs, states, and profiles for output safety checks."""
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/es'))
import iso
import parchear_estado
import perfil_es


def disc_image():
    raw = bytearray(20 * iso.SECTOR)
    pvd = 16 * iso.SECTOR
    raw[pvd:pvd + 7] = b'\x01CD001\x01'
    raw[pvd + 80:pvd + 88] = iso.both(20)
    root = pvd + 156
    raw[root] = 34
    raw[root + 25] = 2
    raw[root + 32] = 1
    raw[root + 2:root + 10] = iso.both(18)
    raw[root + 10:root + 18] = iso.both(iso.SECTOR)
    name = b'DEMOTBL.BIN;1'
    at = 18 * iso.SECTOR
    raw[at] = 34 + len(name)
    raw[at + 32] = len(name)
    raw[at + 33:at + 33 + len(name)] = name
    raw[at + 2:at + 10] = iso.both(19)
    raw[at + 10:at + 18] = iso.both(4)
    raw[19 * iso.SECTOR:19 * iso.SECTOR + 4] = b'Test'
    return raw


class OutputSafety(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)

    def test_iso_rejects_hardlink_to_source(self):
        source, target = (self.root / name for name in ('source.iso', 'target.iso'))
        raw = disc_image()
        source.write_bytes(raw)
        os.link(source, target)
        with self.assertRaises(ValueError):
            iso.build(source, target, {'/DEMOTBL.BIN': b'Prueba'})
        self.assertEqual(source.read_bytes(), raw)

    def test_iso_rejects_truncated_extent_and_slot_overflow(self):
        source, target = (self.root / name for name in ('source.iso', 'target.iso'))
        raw = disc_image()
        raw[18 * iso.SECTOR + 10:18 * iso.SECTOR + 18] = iso.both(iso.SECTOR + 1)
        source.write_bytes(raw)
        with self.assertRaises(ValueError):
            iso.build(source, target, {})
        self.assertFalse(target.exists())
        source.write_bytes(disc_image())
        with self.assertRaises(ValueError):
            iso.build(source, target, {'/DEMOTBL.BIN': b'x' * (iso.SLOT_SECTORS * iso.SECTOR + 1)})
        self.assertFalse(target.exists())
        target.write_bytes(b'previous build')
        with patch.object(iso, 'directory_records', side_effect=[list(iso.directory_records(disc_image())), ValueError('bad read-back')]):
            with self.assertRaisesRegex(ValueError, 'bad read-back'):
                iso.build(source, target, {'/DEMOTBL.BIN': b'Prueba'})
        self.assertEqual(target.read_bytes(), b'previous build')
        iso.build(source, target, {'/DEMOTBL.BIN': b'Prueba'})
        [(name, _, lba, size)] = list(iso.directory_records(target.read_bytes()))
        self.assertEqual((name, lba, size), ('/DEMOTBL.BIN', 20, 6))
        self.assertEqual(source.read_bytes(), disc_image())

    def test_state_rejects_alias_and_length_change(self):
        source, target = (self.root / name for name in ('source.state', 'target.state'))
        source.write_bytes(b'header original footer')
        with patch.object(parchear_estado, 'pairs', return_value=[('demo', b'original', b'replaced')]):
            with self.assertRaises(ValueError):
                parchear_estado.main(source, source)
            parchear_estado.main(source, target)
        with patch.object(parchear_estado, 'pairs', return_value=[('demo', b'original', b'longer-than-original')]):
            with self.assertRaises(ValueError):
                parchear_estado.main(source, target)
        self.assertEqual(source.read_bytes(), b'header original footer')
        self.assertEqual(target.read_bytes(), b'header replaced footer')

    def test_short_missing_state_prefix_is_not_replaced(self):
        source, target = (self.root / name for name in ('source.state', 'target.state'))
        src = b'header' + b'a' * 256 + b'footer'
        source.write_bytes(src)
        with patch.object(parchear_estado, 'pairs', return_value=[('demo', b'a' * 1024, b'b' * 1024)]):
            parchear_estado.main(source, target)
        self.assertEqual(target.read_bytes(), src)

    def test_profile_refuses_base_and_nonprivate_destination(self):
        local = self.root / 'local'
        disc = local / 'prepared/disc1-es/game.cue'
        disc.parent.mkdir(parents=True)
        disc.touch()
        base = local / 'profiles/owner'
        base.mkdir(parents=True)
        original = b'[game]\ndisc=owner.cue\n'
        (base / 'launcher.ini').write_bytes(original)
        (base / 'settings.ini').write_bytes(b'[features]\npreset=custom\n')
        app = local / '100% release \u03a9'
        app.mkdir()
        (app / 'SaturnTaisenFirst.exe').touch()
        def create(target):
            argv = ['perfil_es.py', '--base', str(base), '--perfil', str(target), '--app', str(app)]
            with patch.object(perfil_es, 'OWNER', self.root), patch.object(sys, 'argv', argv):
                perfil_es.main()
        for bad in (base, self.root / 'public'):
            with self.assertRaises(SystemExit):
                create(bad)
        self.assertEqual((base / 'launcher.ini').read_bytes(), original)
        profile = local / 'profiles/spanish'
        create(profile)
        self.assertIn(f'disc={disc}', (profile / 'launcher.ini').read_text(encoding='utf-8'))
        aliased_profile = local / 'profiles/aliased'
        aliased_profile.mkdir()
        os.link(base / 'launcher.ini', aliased_profile / 'launcher.ini')
        with self.assertRaises(SystemExit):
            create(aliased_profile)
        self.assertEqual((base / 'launcher.ini').read_bytes(), original)
        self.assertEqual((profile / 'settings.ini').read_bytes(), (base / 'settings.ini').read_bytes())
        local_settings = b'[controller]\nprofile=M30\n'
        (profile / 'settings.ini').write_bytes(local_settings)
        (profile / 'launcher.ini').write_text(
            '[game]\ndisc=old-es.cue\nquality=integer\n[other]\ndisc=other.cue\n',
            encoding='utf-8',
        )
        create(profile)
        self.assertEqual((profile / 'settings.ini').read_bytes(), local_settings)
        self.assertEqual(
            (profile / 'launcher.ini').read_text(encoding='utf-8'),
            f'[game]\ndisc={disc}\nquality=integer\n[other]\ndisc=other.cue\n',
        )
        shortcut = (self.root / 'Jugar en espa\u00f1ol.bat').read_bytes()
        self.assertIn(b'100%% release ', shortcut)
        self.assertIn('Ω'.encode('utf-8'), shortcut)
        self.assertNotIn(b'\r\r\n', shortcut)
