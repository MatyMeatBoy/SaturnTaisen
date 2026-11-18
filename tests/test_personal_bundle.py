"""The private transfer pack selects only validated, explicit disc outputs."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
class PersonalBundleTests(unittest.TestCase):
    def test_archive_entry_names_are_unique_safe_and_collision_checked(self):
        from package_personal_bundle import unique_entries
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'a';b=Path(tmp)/'b';a.write_bytes(b'same');b.write_bytes(b'same')
            self.assertEqual(unique_entries([('art/tactics/x.png',a),('art/tactics/x.png',b)]),[('art/tactics/x.png',a)])
            b.write_bytes(b'changed')
            with self.assertRaises(ValueError):unique_entries([('x',a),('x',b)])
            for unsafe in ('../x','/x','C:/x','a\\x','./x','a//x'):
                with self.subTest(name=unsafe),self.assertRaises(ValueError):unique_entries([(unsafe,a)])
            with self.assertRaises(ValueError):unique_entries([('A',a),('a',b)])

    def test_generated_tactical_band_is_pinned_and_excludes_native_map_context(self):
        from package_personal_bundle import tactical_entries
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);file=root/'STAGE01-right-v1.png';Image.new('RGB',(39,224),'pink').save(file)
            report=dict(schema=1,generated_only=True,original_map_context_included=False,stage_map_signature='1CAF3218B4B0F9F0',world_origin=[656,24],logical_size=[39,224],
                files=[dict(path=file.name,bytes=file.stat().st_size,sha256=hashlib.sha256(file.read_bytes()).hexdigest())])
            (root/'provenance.json').write_text(json.dumps(report))
            self.assertEqual(len(tactical_entries(root)),2)
            report['files'][0]['path']='composite-v2.png';(root/'provenance.json').write_text(json.dumps(report))
            with self.assertRaises(ValueError):tactical_entries(root)
    def fixture(self,root):
        outputs={}
        for name in ('game.cue','Track 01.iso','Track 02.wav'):
            data=('fixture '+name).encode();(root/name).write_bytes(data);outputs[name]=hashlib.sha256(data).hexdigest()
        spec=dict(translation='supplied-v2_1',product='GS-9037',version='V1.005',disc='CD-1/2',xdelta_output_checksums_verified=True,outputs=outputs)
        (root/'manifest.json').write_text(json.dumps(spec));return spec
    def test_disc_payload_matches_pinned_translation_and_rejects_changed_data(self):
        from package_personal_bundle import verified_disc_entries
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            self.assertEqual(len(verified_disc_entries(root,1)),3)
            (root/'Track 01.iso').write_bytes(b'changed')
            with self.assertRaises(ValueError):verified_disc_entries(root,1)
    def test_unknown_outputs_and_wrong_disc_cannot_enter_personal_zip(self):
        from package_personal_bundle import verified_disc_entries
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);spec=self.fixture(root)
            with self.assertRaises(ValueError):verified_disc_entries(root,2)
            spec['outputs']['../secret.bin']='0'*64;(root/'manifest.json').write_text(json.dumps(spec))
            with self.assertRaises(ValueError):verified_disc_entries(root,1)

    def test_processed_pack_cannot_smuggle_original_pc_files(self):
        from package_personal_bundle import prepared_entries
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=b'original PC resource';(root/'KAO.SPR').write_bytes(data)
            report=dict(original_pc_files_included=False,backgrounds=19,portraits=1,files=[dict(path='KAO.SPR',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())])
            (root/'prepared-manifest.json').write_text(json.dumps(report))
            with self.assertRaises(ValueError):prepared_entries(root)
