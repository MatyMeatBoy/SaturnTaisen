"""Setup helper (tools/taisen_setup.py): synthetic inputs only, plus consistency of the tracked patch data."""
import argparse
import configparser
import hashlib
import json
import struct
import sys
import tempfile
import unittest
import wave
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import taisen_setup as setup  # noqa: E402


def directory_record(name: bytes, lba: int, size: int, folder: bool = False) -> bytes:
    length = 33 + len(name) + (1 - len(name) % 2)
    record = bytearray(length)
    record[0] = length
    struct.pack_into('<I', record, 2, lba)
    struct.pack_into('>I', record, 6, lba)
    struct.pack_into('<I', record, 10, size)
    struct.pack_into('>I', record, 14, size)
    record[25] = 2 if folder else 0
    record[32] = len(name)
    record[33:33 + len(name)] = name
    return bytes(record)


def synthetic_image(entries: dict[str, bytes]) -> bytes:
    """A minimal ISO9660 volume: descriptor at sector 16, root directory at 18, files from 20."""
    sectors = {}
    records = directory_record(b'\0', 18, 2048, True) + directory_record(b'\1', 18, 2048, True)
    at = 20
    for name, data in entries.items():
        records += directory_record(name.encode('ascii') + b';1', at, len(data))
        for index in range(0, max(len(data), 1), 2048):
            sectors[at + index // 2048] = data[index:index + 2048].ljust(2048, b'\0')
        at += max(1, -(-len(data) // 2048))
    volume = bytearray(2048)
    volume[0:6] = b'\x01CD001'
    volume[156:156 + 34] = directory_record(b'\0', 18, 2048, True)
    sectors[16] = bytes(volume)
    sectors[18] = records.ljust(2048, b'\0')
    return b''.join(sectors.get(index, bytes(2048)) for index in range(at))


def raw_mode1(image: bytes) -> bytes:
    out = bytearray()
    for index in range(0, len(image), 2048):
        out += setup.SYNC + bytes(3) + b'\x01' + image[index:index + 2048] + bytes(288)
    return bytes(out)


def saturn_track(number: int, sectors: int = 24, product: str = 'GS-9037') -> bytes:
    """A stand-in data track: a Saturn header naming the product and disc number, then filler."""
    header = bytearray(2048)
    header[0:16] = setup.SATURN
    header[0x20:0x2A] = product.ljust(10).encode('ascii')
    header[0x2A:0x30] = b'V1.005'
    header[0x38:0x40] = f'CD-{number}/2 '.encode('ascii').ljust(8)
    return bytes(header) + bytes((index * 7 + number) % 251 for index in range((sectors - 1) * 2048))


def arguments(**values):
    names = ('program', 'patches', 'xdelta', 'unshield', 'runtime', 'recipe', 'provenance', 'output', 'hd_output', 'home')
    return argparse.Namespace(**{name: values.get(name) for name in names})


class DiscContainers(unittest.TestCase):
    """The same data track must come out of every container the player may have."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        self.track = saturn_track(2)
        self.audio = bytes(range(256)) * 9 * 4  # four sectors of "audio"
        self.audio = self.audio[:2352 * 3]

    def tearDown(self):
        self.folder.cleanup()

    def extracted(self, path: Path) -> tuple[bytes, setup.Disc, int]:
        disc = setup.Disc(path)
        target = self.root / 'out.iso'
        sectors = disc.extract(target)
        return target.read_bytes(), disc, sectors

    def test_plain_iso(self):
        path = self.root / 'disc.iso'
        path.write_bytes(self.track)
        data, disc, _ = self.extracted(path)
        self.assertEqual(data, self.track)
        self.assertEqual((disc.number, disc.product, disc.version), (2, 'GS-9037', 'V1.005'))
        self.assertFalse(disc.write_audio(self.root / 'a.wav', 24, 44 + len(self.audio)))

    def test_two_file_cue_with_pregap(self):
        (self.root / 'd (Track 1).bin').write_bytes(raw_mode1(self.track))
        (self.root / 'd (Track 2).bin').write_bytes(bytes(2352) + self.audio)
        cue = self.root / 'd.cue'
        cue.write_text('FILE "d (Track 1).bin" BINARY\n  TRACK 01 MODE1/2352\n    INDEX 01 00:00:00\n'
                       'FILE "d (Track 2).bin" BINARY\n  TRACK 02 AUDIO\n    INDEX 00 00:00:00\n    INDEX 01 00:00:01\n',
                       encoding='ascii')
        data, disc, sectors = self.extracted(cue)
        self.assertEqual(data, self.track)
        self.assertTrue(disc.write_audio(self.root / 'a.wav', sectors, 44 + len(self.audio)))
        with wave.open(str(self.root / 'a.wav'), 'rb') as wav:
            self.assertEqual(wav.readframes(wav.getnframes()), self.audio)

    def test_single_raw_file_with_audio_tail(self):
        path = self.root / 'disc.img'
        path.write_bytes(raw_mode1(self.track) + bytes(2352 * 2) + self.audio)
        data, disc, sectors = self.extracted(path)
        self.assertEqual(data, self.track)
        self.assertEqual(sectors, 24)
        self.assertTrue(disc.write_audio(self.root / 'a.wav', sectors, 44 + len(self.audio)))
        with wave.open(str(self.root / 'a.wav'), 'rb') as wav:
            self.assertEqual(wav.readframes(wav.getnframes()), self.audio)

    def test_prepared_cue_with_wav(self):
        (self.root / 'Track 01.iso').write_bytes(self.track)
        setup.write_silence(self.root / 'Track 02.wav', 44 + 2352)
        (self.root / 'game.cue').write_text(setup.CUE, encoding='ascii')
        data, disc, sectors = self.extracted(self.root / 'game.cue')
        self.assertEqual(data, self.track)
        self.assertTrue(disc.write_audio(self.root / 'a.wav', sectors, 44 + 2352))
        self.assertEqual((self.root / 'a.wav').read_bytes(), (self.root / 'Track 02.wav').read_bytes())

    def test_other_games_and_non_discs_are_not_described(self):
        other = self.root / 'other.iso'
        other.write_bytes(saturn_track(1, product='T-12345G'))
        junk = self.root / 'junk.bin'
        junk.write_bytes(b'not a disc' * 400)
        self.assertIsNone(setup.describe(other))
        self.assertIsNone(setup.describe(junk))

    def test_scan_and_gather_find_discs_in_folders_and_zips(self):
        one = self.root / 'mis discos' / 'uno'
        one.mkdir(parents=True)
        (one / 'd1.bin').write_bytes(raw_mode1(saturn_track(1)))
        (one / 'd1.cue').write_text('FILE "d1.bin" BINARY\n  TRACK 01 MODE1/2352\n    INDEX 01 00:00:00\n', encoding='ascii')
        with zipfile.ZipFile(self.root / 'mis discos' / 'dos.zip', 'w') as archive:
            archive.writestr('carpeta/d2.iso', self.track)
            archive.writestr('carpeta/leeme.txt', 'x')
        found = setup.scan(self.root / 'mis discos')
        self.assertEqual(found['discs'], {'1': [str(one / 'd1.cue')]})  # the .bin is the cue's own track
        self.assertEqual(len(found['archives']), 1)
        work = self.root / 'work'
        work.mkdir()
        discs, pc = setup.gather([one / 'd1.cue'], work)  # disc 2 is found beside it, inside the zip
        self.assertEqual(sorted(discs), [1, 2])
        self.assertIsNone(pc)
        self.assertEqual(discs[2][0].read_bytes(), self.track)

    def test_missing_file_is_an_error(self):
        with self.assertRaises(setup.SetupError):
            setup.gather([self.root / 'nada.cue'])


class PcEdition(unittest.TestCase):
    def setUp(self):
        self.files = {'DATA1.CAB': b'cab-one' * 500, 'DATA1.HDR': b'header', 'DATA2.CAB': bytes(range(256)) * 20}
        self.plain = synthetic_image(self.files)

    def check(self, data: bytes):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'image.mdf'
            path.write_bytes(data)
            self.assertTrue(setup.is_pc_image(path))
            image = setup.Image(path)
            try:
                root = image.root()
                for name, expected in self.files.items():
                    target = Path(folder) / name
                    image.copy(*root[name], target)
                    self.assertEqual(target.read_bytes(), expected)
            finally:
                image.close()

    def test_plain_2048_sectors(self):
        self.check(self.plain)

    def test_raw_2352_sectors(self):
        self.check(raw_mode1(self.plain))

    def test_other_image_is_not_the_pc_edition(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'other.iso'
            path.write_bytes(synthetic_image({'README.TXT': b'hello'}))
            self.assertFalse(setup.is_pc_image(path))
            path.write_bytes(b'not a disc' * 5000)
            self.assertFalse(setup.is_pc_image(path))

    def test_folders_with_cabinets_or_an_installed_game(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cabinets = root / 'cd'
            cabinets.mkdir()
            for name in ('data1.cab', 'data1.hdr', 'Data2.cab'):
                (cabinets / name).write_bytes(b'x')
            game = root / 'instalado'
            (game / 'Sakura1' / 'Wall').mkdir(parents=True)
            (game / 'Sakura1' / 'System').mkdir()
            (game / 'Sakura1' / 'System' / 'kao.spr').write_bytes(b'x')
            self.assertEqual(setup.pc_folder_kind(cabinets), 'cabinets')
            self.assertEqual(setup.pc_folder_kind(game), 'game')
            self.assertIsNone(setup.pc_folder_kind(root))
            self.assertIn(setup.scan(root)['pc'], (str(cabinets), str(game)))


class Profile(unittest.TestCase):
    def test_language_switch_keeps_other_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('disc1', 'disc1-es'):
                (root / 'game' / name).mkdir(parents=True)
                (root / 'game' / name / 'game.cue').write_text(setup.CUE, encoding='ascii')
            home = root / 'user'
            home.mkdir()
            (home / 'launcher.ini').write_text('[launcher]\npreset_chosen=1\n\n[sakura]\nbackup=C:\\x\\save.bin\n',
                                               encoding='utf-8')
            paths = setup.Paths(arguments(program=root, output=root / 'game', home=home))
            for language, name in (('es', 'disc1-es'), ('en', 'disc1')):
                disc = setup.set_language(paths, language)
                self.assertEqual(disc, root / 'game' / name / 'game.cue')
                ini = configparser.ConfigParser(interpolation=None)
                ini.read(home / 'launcher.ini', encoding='utf-8')
                self.assertEqual(ini['game']['disc'], str(disc))
                self.assertEqual(ini['sakura']['language'], language)
                self.assertEqual(ini['sakura']['backup'], 'C:\\x\\save.bin')
                self.assertEqual(ini['launcher']['preset_chosen'], '1')
                self.assertEqual(setup.saved_language(paths), language)

    def test_default_home_is_the_launchers_portable_folder(self):
        import os
        saved = os.environ.pop('SATURN_TAISEN_FIRST_HOME', None)
        try:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                self.assertEqual(setup.default_home(root), root / 'user' / 'SaturnTaisen')
                (root / 'user').mkdir()
                (root / 'user' / 'launcher.ini').write_text('[game]\n', encoding='ascii')
                self.assertEqual(setup.default_home(root), root / 'user')  # a profile from an earlier release
                os.environ['SATURN_TAISEN_FIRST_HOME'] = str(root / 'otro')
                self.assertEqual(setup.default_home(root), (root / 'otro').resolve())
        finally:
            os.environ.pop('SATURN_TAISEN_FIRST_HOME', None)
            if saved is not None:
                os.environ['SATURN_TAISEN_FIRST_HOME'] = saved

    def test_unprepared_language_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = setup.Paths(arguments(program=root, output=root / 'game', home=root / 'user'))
            with self.assertRaises(setup.SetupError):
                setup.set_language(paths, 'es')
            self.assertFalse((root / 'user' / 'launcher.ini').exists())

    def test_receipt_decides_whether_a_disc_is_rebuilt(self):
        with tempfile.TemporaryDirectory() as folder:
            disc = Path(folder)
            layer = {'output_sha256': 'ab' * 32, 'output_subtitled_sha256': 'ef' * 32, 'output_bytes': 4096}
            self.assertIsNone(setup.finished(disc, layer))
            (disc / 'Track 01.iso').write_bytes(bytes(4096))
            (disc / 'Track 02.wav').write_bytes(b'RIFF')
            (disc / 'game.cue').write_text(setup.CUE, encoding='ascii')
            for digest in ('ab' * 32, 'ef' * 32):  # with or without the subtitled videos
                (disc / 'taisen.json').write_text(json.dumps({'output_sha256': digest}), encoding='utf-8')
                self.assertEqual(setup.finished(disc, layer), digest)
            self.assertEqual(setup.accepted(layer), {'ab' * 32: False, 'ef' * 32: True})
            self.assertIsNone(setup.finished(disc, {'output_sha256': 'cd' * 32, 'output_bytes': 4096}))
            (disc / 'Track 01.iso').write_bytes(bytes(2048))
            self.assertIsNone(setup.finished(disc, layer))

    def test_a_disc_is_identified_by_its_data_hash(self):
        record = {'original_sha256': 'aa', 'english': {'output_sha256': 'bb', 'output_subtitled_sha256': 'cc'},
                  'spanish': {'output_sha256': 'dd', 'output_subtitled_sha256': 'ee'}}
        self.assertEqual([setup.identify(record, value) for value in ('aa', 'bb', 'cc', 'dd', 'ee', 'ff')],
                         ['original', 'en', 'en', 'es', 'es', None])


class TrackedData(unittest.TestCase):
    def test_patch_manifest_matches_tracked_patches(self):
        manifest = json.loads((ROOT / 'parches/parches.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['schema'], 2)
        self.assertEqual(sorted(manifest['discs']), ['1', '2'])
        for record in manifest['discs'].values():
            for layer in ('english', 'spanish'):
                file = ROOT / 'parches' / record[layer]['patch']
                self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(), record[layer]['patch_sha256'])
                self.assertEqual(len(record[layer]['output_sha256']), 64)
                self.assertEqual(len(record[layer]['output_subtitled_sha256']), 64)
            self.assertEqual(len(record['spanish']['blank_sha256']), 64)
            self.assertTrue(record['videos']['optional'])
            self.assertFalse((ROOT / 'parches' / record['videos']['patch']).exists(),
                             'the video layer is a release asset, not a tracked file')

    def test_portrait_recipe_is_identifiers_only(self):
        recipe = json.loads((ROOT / 'config/hd-portrait-recipe.json').read_text(encoding='utf-8'))
        rows = recipe['portraits']
        self.assertEqual(len({row['id'] for row in rows}), len(rows))
        self.assertEqual(recipe['palette_hash'], setup.PALETTE_HASH)
        for row in rows:
            self.assertLessEqual(set(row), {'id', 'pc_index', 'dx', 'dy', 'native_raw_sha256', 'variants_rgba_sha256'})
            self.assertTrue(abs(row['dx']) <= 4 and abs(row['dy']) <= 4)

    def test_every_reviewed_portrait_reaches_the_release_recipe(self):
        """An approved HD portrait that is not in the recipe would be missing from every release."""
        recipe = {row['id']: row for row in
                  json.loads((ROOT / 'config/hd-portrait-recipe.json').read_text(encoding='utf-8'))['portraits']}
        reviewed = json.loads((ROOT / 'config/hd-portrait-reviewed.json').read_text(encoding='utf-8'))
        for match in reviewed['matches']:
            row = recipe.get(match['id'])
            self.assertIsNotNone(row, f"{match['id']} is approved but missing from the recipe; "
                                      'run tools/build_hd_recipe.py')
            for key in ('pc_index', 'dx', 'dy', 'native_raw_sha256', 'variants_rgba_sha256'):
                self.assertEqual(row[key], match[key], match['id'])
        progress = (ROOT / 'docs/HD_PROGRESS.md').read_text(encoding='utf-8')
        self.assertIn(f'{len(recipe)}/304', progress, 'HD_PROGRESS.md and the release recipe disagree')

    def test_frontend_manifest_names_the_packaged_entry_point(self):
        manifest = json.loads((ROOT / 'recomp-launcher.json').read_text(encoding='utf-8'))
        packager = (ROOT / 'tools/package_release.py').read_text(encoding='utf-8')
        self.assertTrue(manifest['single_entry_point'])
        self.assertIn(f"'{manifest['primary_executable']}'", packager)
        for internal in manifest['internal_executables']:
            # Internal programs live in data/; only the launcher sits at the release root.
            self.assertTrue(internal['file'].startswith('data/'), internal['file'])
            self.assertIn(f"'{internal['file'].removeprefix('data/')}'", packager)
        self.assertIn("app=destination/'data'", packager)
        self.assertIn("inputs=destination/'roms'", packager)
        self.assertNotIn('.bat', packager, 'the release ships no .bat files')
        for flag in ('--rom', '--no-launcher', '--setup', '--fullscreen', '--widescreen', '--integration-info', '--help'):
            self.assertIn(flag, manifest['cli'], flag)
            self.assertIn(flag, setup.HELP, flag)


class FullPcPack(unittest.TestCase):
    """T89: the HD pack takes every image, video and table the HD mod will need, and no audio."""

    def test_pack_takes_images_videos_and_tables_but_not_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('SAKURA1/BG/BG1001.SPR', 'SAKURA2/EVENT/E01.SPR', 'SAKURA3/CG/CG01.SPR', 'MOVIE/MOVIE000.MPG',
                         'SAKURA1/SYSTEM/KAO.SPR', 'SAKURA3/OD/A.OD', 'SAKURA1/VOICE/V.WAV', 'SAKURA1/VOICE/X.SPR',
                         'SAKURA1/BGM/B.WAV', 'SAKURA2/SE/S.WAV', 'OTHER/X.SPR', 'SAKURA1/SYSTEM/README.TXT'):
                file = root / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b'x')
            picked = sorted(name for _, name in setup.pc_pack_files(root))
            self.assertEqual(picked, ['MOVIE/MOVIE000.MPG', 'SAKURA1/BG/BG1001.SPR', 'SAKURA1/SYSTEM/KAO.SPR',
                                      'SAKURA2/EVENT/E01.SPR', 'SAKURA3/CG/CG01.SPR', 'SAKURA3/OD/A.OD'])
            target = root / 'pack'
            manifest = setup.build_pc_pack(root, target, 0, 1)
            self.assertEqual(manifest['files'], 6)
            self.assertEqual(manifest['videos'], 1)
            self.assertTrue((target / 'pc-manifest.json').is_file())
            self.assertTrue((target / 'SAKURA3/CG/CG01.SPR').is_file())

    def test_a_pack_without_the_full_pc_material_is_rebuilt(self):
        self.assertIn('pc-manifest.json', Path(setup.__file__).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
