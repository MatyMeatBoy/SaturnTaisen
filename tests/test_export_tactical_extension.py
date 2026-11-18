import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from export_tactical_extension import export
class TacticalExportTests(unittest.TestCase):
    def fixture(self,folder):
        source=folder/'source';source.mkdir()
        image=Image.new('RGB',(940,448),'blue');ImageDraw.Draw(image).rectangle((0,0,813,447),fill='red')
        image.save(source/'composite-v2.png')
        report={'status':'approved-preliminary','protected_columns':[0,814],'replace_columns':[814,896],
            'logical_density':2,'max_aspect':'16:9','files':{'composite-v2.png':hashlib.sha256((source/'composite-v2.png').read_bytes()).hexdigest()}}
        (source/'approved.json').write_text(json.dumps(report));return source,report
    def test_only_generated_band_is_exported_and_source_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);source,report=self.fixture(folder);out=folder/'out'
            result=export(source,out)
            with Image.open(out/'STAGE01-right-v1.png') as image:
                self.assertEqual(image.size,(39,224));self.assertEqual(image.convert('RGB').getextrema(),((0,0),(0,0),(255,255)))
            self.assertTrue(result['generated_only']);self.assertEqual(result['world_origin'],[656,24])
            self.assertEqual(hashlib.sha256((source/'composite-v2.png').read_bytes()).hexdigest(),report['files']['composite-v2.png'])
            with self.assertRaises(FileExistsError):export(source,out)
    def test_modified_source_or_unapproved_geometry_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);source,report=self.fixture(folder)
            (source/'composite-v2.png').write_bytes(b'changed')
            with self.assertRaises(ValueError):export(source,folder/'out')
            self.assertFalse((folder/'out').exists())
