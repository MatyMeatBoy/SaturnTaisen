"""Owner-data integration: validated portrait replacement and safe fallback."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import shutil
import unittest
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
PROJECT=ROOT/'local/work/hd-matcher-project/project.json'
STATE=ROOT/'local/work/sakura/iris-correct-room-3000.state'
EXE=ROOT/'local/build/sakura/sakura.exe'

@unittest.skipUnless(PROJECT.exists() and STATE.exists() and EXE.exists(),'requires owner assets and local runtime')
class PortraitRuntimeTests(unittest.TestCase):
    def capture(self,folder,pc_root,width,height,enabled,preload=False):
        folder.mkdir(parents=True,exist_ok=True)
        settings=folder/'settings.ini';shot=folder/'shot.png'
        settings.write_text(f'[features]\npresentation_mode=1\nscene_view=0\nhd_preload={int(preload)}\ntext_style=0\npc_hd_portraits={0 if enabled else 1}\n')
        backup=folder/'backup.bin';backup.write_bytes((ROOT/'local/work/sakura/prebattle-immutable-seed.bin').read_bytes())
        env={k:v for k,v in os.environ.items() if not k.startswith('SATRECOMP_')}
        env.update(PATH='C:/msys64/clang64/bin;'+env.get('PATH',''),SATRECOMP_WINDOW_HIDDEN='1',SATRECOMP_BACKGROUND_WORKERS='0',SATRECOMP_HD_STATS='1',
                   SATRECOMP_WINDOW_KEYS=f'2:SIZE={width}x{height},3:CHOICE=1,8:WINDOWSHOT={shot.as_posix()},12:QUIT')
        run=subprocess.run([str(EXE),'--disc',str(ROOT/'local/prepared/disc1/game.cue'),'--state-load','0:'+str(STATE),
                            '--pc-assets',str(pc_root),'--settings',str(settings),'--backup',str(backup),'--mute'],env=env,capture_output=True,timeout=30)
        self.assertEqual(run.returncode,0,run.stderr.decode(errors='replace'))
        with Image.open(shot) as image:return image.convert('RGB'),run.stderr

    @unittest.skipUnless((ROOT/'local/work/v012-prepared-hd/hd-pack.stfp').is_file(),'requires a local processed-only export')
    def test_processed_only_pack_matches_originals_without_any_pc_spr_files(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as directory:
            folder=Path(directory);prepared=folder/'hd-resources'
            shutil.copytree(ROOT/'local/work/v012-prepared-hd',prepared)
            self.assertFalse(list(prepared.rglob('*.SPR')))
            raw_profile=folder/'raw';shutil.copytree(ROOT/'local/profiles/v02-dev/mods',raw_profile/'mods')
            project=json.loads(PROJECT.read_text(encoding='utf-8'))
            original=Path(project['source']['path']).parent.parent.parent
            raw,_=self.capture(raw_profile,original,2560,1440,True,True)
            ready,log=self.capture(folder/'ready',prepared,2560,1440,True,True)
            self.assertIn(b'source=prepared',log)
            self.assertIn(b'HD preload: backgrounds=38/38 portrait_variants=382',log)
            self.assertEqual(raw.tobytes(),ready.tobytes())
            receipt=prepared/'hd-pack.stfp';data=bytearray(receipt.read_bytes());data[0]^=1;receipt.write_bytes(data)
            fallback,_=self.capture(folder/'invalid',prepared,2560,1440,True,True)
            native,_=self.capture(folder/'native',folder/'missing',2560,1440,True,True)
            self.assertEqual(fallback.tobytes(),native.tobytes())

    def test_verified_portraits_use_integer_density_and_corrupt_resources_fall_back(self):
        from hd_matching import export_pack
        project=json.loads(PROJECT.read_text(encoding='utf-8'))
        project['rows']=[row for row in project['rows'] if row['id']=='0015']
        pc_root=Path(project['source']['path']).parent.parent.parent
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as directory:
            folder=Path(directory);profile=folder/'profile';pack=profile/'mods/hd-portraits'
            project['output']=str(pack);export_pack(project,PROJECT.parent)
            for width,height in ((1280,720),(1600,900),(1920,1080),(2560,1440),(3840,2160),(3440,1440)):
                off,_=self.capture(profile,pc_root,width,height,False)
                on,log=self.capture(profile,pc_root,width,height,True)
                scale=min(width//306,height//212);density=2 if scale%2==0 else 1
                self.assertIn(f'id=0015 density={density}'.encode(),log)
                bbox=ImageChops.difference(off,on).getbbox();self.assertIsNotNone(bbox)
                x=(width-306*scale)//2+7*scale;y=(height-212*scale)//2+152*scale
                self.assertGreaterEqual(bbox[0],x);self.assertGreaterEqual(bbox[1],y)
                self.assertLessEqual(bbox[2],x+40*scale);self.assertLessEqual(bbox[3],y+48*scale)
                if width==2560:reference=on
                if width==3440:
                    self.assertIsNone(on.crop((0,0,440,1440)).getbbox())
                    self.assertIsNone(on.crop((3000,0,3440,1440)).getbbox())
                    # The HD font's float coordinates may round one coverage level differently.
                    delta=ImageChops.difference(reference,on.crop((440,0,3000,1440)))
                    self.assertLessEqual(max(high for low,high in delta.getextrema()),2)
            lazy,_=self.capture(profile,pc_root,2560,1440,True)
            eager,log=self.capture(profile,pc_root,2560,1440,True,True)
            self.assertEqual(lazy.tobytes(),eager.tobytes())
            self.assertIn(b'HD preload: backgrounds=',log)
            self.assertIn(b'portrait preload: variants=2 failed=0',log)
            # Alter derived PNG bytes without updating the recorded hash in the manifest.
            for png in pack.glob('*.png'):png.write_bytes(b'corrupt derived resource')
            off,_=self.capture(profile,pc_root,1280,720,False)
            on,_=self.capture(profile,pc_root,1280,720,True)
            self.assertEqual(off.tobytes(),on.tobytes())
            (pack/'manifest.ini').unlink()
            on,_=self.capture(profile,pc_root,1280,720,True)
            self.assertEqual(off.tobytes(),on.tobytes())

