"""Prevent original/unpinned images or path escapes through generated-art packaging."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from package_release import generated_backgrounds, release_file_manifest


class PackageArtTests(unittest.TestCase):
    def test_tactical_asset_requires_generated_only_world_anchor_and_fixed_name(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);file=folder/'STAGE01-right-v1.png';Image.new('RGB',(39,224),'pink').save(file)
            report=dict(generated_only=True,original_map_context_included=False,world_origin=[656,24],logical_size=[39,224],
                backgrounds=[dict(file=file.name,sha256=hashlib.sha256(file.read_bytes()).hexdigest())])
            (folder/'provenance.json').write_text(json.dumps(report))
            self.assertEqual(list(generated_backgrounds(folder,tactical=True)),[file.name])
            Image.new('RGB',(940,448),'pink').save(file)
            report['backgrounds'][0]['sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
            (folder/'provenance.json').write_text(json.dumps(report))
            with self.assertRaises(RuntimeError):generated_backgrounds(folder,tactical=True)
            report['original_map_context_included']=True;(folder/'provenance.json').write_text(json.dumps(report))
            with self.assertRaises(RuntimeError):generated_backgrounds(folder,tactical=True)
    def test_intro_and_title_extensions_have_a_separate_bounded_allowlist(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);data=b'\x89PNG\r\n\x1a\nfixture'
            (folder/'TITLE-v1.png').write_bytes(data)
            (folder/'provenance.json').write_text(json.dumps({'backgrounds':[{'file':'TITLE-v1.png','sha256':hashlib.sha256(data).hexdigest()}]}))
            self.assertEqual(list(generated_backgrounds(folder,screen=True)),['TITLE-v1.png'])
            for name in ('STATUS-v1.png','PAUSE01-v1.png','LOADING-v1.png'):
                (folder/name).write_bytes(data)
                manifest=json.loads((folder/'provenance.json').read_text())
                manifest['backgrounds'].append({'file':name,'sha256':hashlib.sha256(data).hexdigest()})
                (folder/'provenance.json').write_text(json.dumps(manifest))
            self.assertEqual(len(generated_backgrounds(folder,screen=True)),4)
            with self.assertRaises(RuntimeError):generated_backgrounds(folder)
    def test_loading_art_accepts_only_transparent_white_ink_in_the_scroll_window(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            file = folder / 'LOAD-es-lettering-v1.png'
            report = folder / 'provenance.json'
            image = Image.new('RGBA', (48, 198), (255, 255, 255, 0))
            image.putpixel((10, 10), (255, 255, 255, 128))
            manifest = {'source_pixels_included': False, 'backgrounds': [{
                'file': file.name, 'kind': 'generated Spanish loading lettering only',
                'logical_grid': [48, 198], 'native_origin': [136, 13],
            }]}

            def write_fixture():
                image.save(file)
                manifest['backgrounds'][0]['sha256'] = hashlib.sha256(file.read_bytes()).hexdigest()
                report.write_text(json.dumps(manifest), encoding='utf-8')

            write_fixture()
            self.assertEqual(list(generated_backgrounds(folder, screen=True)), [file.name])
            image.putpixel((10, 10), (255, 0, 0, 128))
            write_fixture()
            with self.assertRaisesRegex(RuntimeError, 'loading lettering'):
                generated_backgrounds(folder, screen=True)

    def test_legacy_episode_strips_are_rejected(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            file = folder / 'EPISODE01-left-v1.png'
            Image.new('RGBA', (39, 224)).save(file)
            manifest = {'source_pixels_included': False, 'backgrounds': [
                {'file': file.name, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                 'logical_grid': [39, 224], 'palette_fnv': 'F84F4FA528984E99'}
            ]}
            (folder / 'provenance.json').write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, 'generated background identity'):
                generated_backgrounds(folder, screen=True)

    def test_episode_surrounds_require_an_empty_center_and_complete_set(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            report = folder / 'provenance.json'
            manifest = {'source_pixels_included': False, 'backgrounds': []}
            entries = manifest['backgrounds']

            def register(file, image, **fields):
                image.save(folder / file)
                entries.append(dict(file=file, sha256=hashlib.sha256((folder / file).read_bytes()).hexdigest(),
                                    palette_fnv=f'{number:016X}', **fields))

            for number in range(1, 11):
                surround = Image.new('RGBA', (640, 360), 'pink')
                surround.paste((0, 0, 0, 0), (160, 68, 480, 292))
                register(f'EPISODE{number:02}-surround-v2.png', surround,
                         logical_grid=[640, 360], native_center=[160, 68, 320, 224])
            report.write_text(json.dumps(manifest), encoding='utf-8')
            self.assertEqual(len(generated_backgrounds(folder, screen=True)), 10)
            entries.pop()
            report.write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, 'episode surrounds'):
                generated_backgrounds(folder, screen=True)
            surround.putpixel((160, 68), (1, 2, 3, 0))
            register('EPISODE10-surround-v2.png', surround,
                     logical_grid=[640, 360], native_center=[160, 68, 320, 224])
            report.write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, 'contains center pixels'):
                generated_backgrounds(folder, screen=True)

    def test_spanish_episode_lettering_requires_all_ten_generated_layers(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            report = folder / 'provenance.json'
            manifest = {'source_pixels_included': False, 'backgrounds': []}
            for number in range(1, 11):
                path = folder / f'EPISODE{number:02}-es-lettering-v1.png'
                Image.new('RGBA', (320, 224)).save(path)
                manifest['backgrounds'].append({
                    'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'logical_grid': [320, 224], 'kind': 'generated Spanish lettering only',
                })
            report.write_text(json.dumps(manifest), encoding='utf-8')
            self.assertEqual(len(generated_backgrounds(folder, screen=True)), 10)
            manifest['backgrounds'].pop()
            report.write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, 'Incomplete Spanish episode lettering'):
                generated_backgrounds(folder, screen=True)

    def test_only_manifest_pinned_files_are_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);data=b'\x89PNG\r\n\x1a\nfixture'
            (folder/'KABE00.png').write_bytes(data)
            (folder/'original-screenshot.png').write_bytes(data)
            manifest={'backgrounds':[{'file':'KABE00.png','sha256':hashlib.sha256(data).hexdigest()}]}
            (folder/'provenance.json').write_text(json.dumps(manifest),encoding='utf-8')
            self.assertEqual(list(generated_backgrounds(folder)),['KABE00.png'])
            (folder/'KABE00.png').write_bytes(data+b'tampered')
            with self.assertRaises(RuntimeError):generated_backgrounds(folder)

    def test_pc_generated_art_uses_its_own_allowlist_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);data=b'\x89PNG\r\n\x1a\nfixture'
            (folder/'KABE0100-v1.png').write_bytes(data)
            manifest={'backgrounds':[{'file':'KABE0100-v1.png','sha256':hashlib.sha256(data).hexdigest()}]}
            (folder/'provenance.json').write_text(json.dumps(manifest),encoding='utf-8')
            self.assertEqual(list(generated_backgrounds(folder,pc=True)),['KABE0100-v1.png'])
            with self.assertRaises(RuntimeError):generated_backgrounds(folder)
            manifest['backgrounds'][0]['file']='../KABE0100-v1.png'
            (folder/'provenance.json').write_text(json.dumps(manifest),encoding='utf-8')
            with self.assertRaises(RuntimeError):generated_backgrounds(folder,pc=True)

    def test_manifest_cannot_escape_or_repeat_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            for name in ('../KABE00.png','C:/KABE00.png','original.png'):
                (folder/'provenance.json').write_text(json.dumps({'backgrounds':[{'file':name,'sha256':'0'*64}]}),encoding='utf-8')
                with self.assertRaises(RuntimeError):generated_backgrounds(folder)

    def test_tracked_episode_card_layers_pass_the_active_gate(self):
        source = Path(__file__).resolve().parents[1] / 'assets/generated/screen-backgrounds'
        images = generated_backgrounds(source, screen=True)
        cards = {f'EPISODE{episode:02d}-{layer}.png'
                 for episode in range(1, 11) for layer in ('surround-v2', 'es-lettering-v1')}
        self.assertEqual({name for name in images if name.startswith('EPISODE')}, cards)

    def test_manifest_checks_the_staged_recipes_and_preparation_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            approved = {}
            names = ('config/film-fad-map.json', 'config/hd-scroll-pictures.json',
                     'preparar-juego.exe', 'herramientas/unshield.exe', 'herramientas/xdelta3.exe',
                     'licenses/unshield-MIT.txt', 'licenses/xdelta3-Apache-2.0.txt')
            for name in names:
                staged = root / 'data' / name
                staged.parent.mkdir(parents=True, exist_ok=True)
                staged.write_bytes(name.encode())
                approved[name] = hashlib.sha256(name.encode()).hexdigest()
            files = release_file_manifest(root, {}, {}, approved)
            self.assertEqual({row['path'] for row in files}, {'data/' + name for name in names})
            for name in names:
                with self.subTest(name=name):
                    staged = root / 'data' / name
                    staged.write_bytes(b'mismatched bytes')
                    with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
                        release_file_manifest(root, {}, {}, approved)
                    staged.unlink()
                    with self.assertRaisesRegex(RuntimeError, 'Missing approved'):
                        release_file_manifest(root, {}, {}, approved)
                    staged.write_bytes(name.encode())

    def test_public_tree_rejects_original_movies_assets_and_misplaced_art(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relative = 'art/screen-backgrounds/EPISODE01-surround-v2.png'
            data = b'generated fixture'
            art = root / 'data' / relative
            art.parent.mkdir(parents=True)
            art.write_bytes(data)
            allowed = {relative: hashlib.sha256(data).hexdigest()}
            self.assertEqual([row['path'] for row in release_file_manifest(root, allowed, {})],
                             ['data/' + relative])
            for unexpected in ('MOVIE000.MPG', 'data/OPENING.CPK', 'data/BG1001.SPR', relative, 'data/hd-resources/receipt.json'):
                file = root / unexpected
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(data)
                with self.subTest(unexpected=unexpected), self.assertRaisesRegex(RuntimeError, 'Unexpected'):
                    release_file_manifest(root, allowed, {})
                file.unlink()
            art.unlink()
            (root / 'data/hd-resources').rmdir()
            with self.assertRaisesRegex(RuntimeError, 'Missing approved'):
                release_file_manifest(root, allowed, {})


if __name__=='__main__':unittest.main()
