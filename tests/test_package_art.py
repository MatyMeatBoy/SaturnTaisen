"""Prevent original/unpinned images or path escapes through generated-art packaging."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from package_release import generated_backgrounds


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
    def test_episode_side_requires_a_generated_only_native_strip(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            file = folder / 'EPISODE01-left-v1.png'
            manifest = {'source_pixels_included': False, 'backgrounds': []}
            report = folder / 'provenance.json'

            def register(size):
                Image.new('RGBA', size, (12, 30, 50, 255)).save(file)
                manifest['backgrounds'] = [{
                    'file': file.name, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                    'logical_grid': [39, 224], 'palette_fnv': 'F84F4FA528984E99',
                }]
                report.write_text(json.dumps(manifest), encoding='utf8')

            register((39, 224))
            self.assertEqual(list(generated_backgrounds(folder, screen=True)), [file.name])
            register((398, 224))
            with self.assertRaises(RuntimeError):
                generated_backgrounds(folder, screen=True)
            register((39, 224))
            manifest['source_pixels_included'] = True
            report.write_text(json.dumps(manifest), encoding='utf8')
            with self.assertRaises(RuntimeError):
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


if __name__=='__main__':unittest.main()
