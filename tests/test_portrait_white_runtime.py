"""An owner-data white-fade witness; synthetic fixtures cover all accepted weights."""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OWNER=Path(os.environ.get('SAKURA_OWNER_ROOT',ROOT))
EXE=Path(os.environ.get('SAKURA_WHITE_TEST_EXE',OWNER/'local/build/visual-fixes-candidate/sakura.exe'))
STATE=OWNER/'local/work/sakura/morning-9000.state'
PACK=OWNER/'local/work/v012-prepared-hd'
ART=OWNER/'local/releases/SaturnTaisenFirst-v0.2.0-test.1-win64/art'


@unittest.skipUnless(EXE.is_file() and STATE.is_file() and (PACK/'prepared-manifest.json').is_file() and ART.is_dir(),
                     'requires owner white-fade state, prepared HD and candidate')
class PortraitWhiteRuntimeTests(unittest.TestCase):
    def test_proven_white_mix_keeps_guest_state_and_native_fade_pixels(self):
        self.assertEqual(hashlib.sha256(STATE.read_bytes()).hexdigest(),
                         '81de5f7ba12e092b174ee98a64e386c979460cc17d8c0b13b9407850668ca2b8')
        (ROOT/'local/work').mkdir(parents=True,exist_ok=True)
        hashes=[];images=[]
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as temporary:
            for disabled in (0,1):
                folder=Path(temporary)/str(disabled);folder.mkdir();shot=folder/'shot.png'
                shutil.copytree(ART,folder/'art')
                (folder/'settings.ini').write_text('[features]\npresentation_mode=1\nscene_view=1\n'
                    f'pc_hd_portraits={disabled}\npc_hd_backgrounds=0\nhd_preload=0\nrun_ahead=0\n',encoding='ascii')
                shutil.copy2(OWNER/'local/work/sakura/prebattle-immutable-seed.bin',folder/'backup.bin')
                env={key:value for key,value in os.environ.items() if not key.startswith('SATRECOMP_')}
                env.update(PATH='C:/msys64/clang64/bin;'+env.get('PATH',''),SATRECOMP_STRICT_NATIVE='1',
                    SATRECOMP_WINDOW_HIDDEN='1',SATRECOMP_SKIP_CHOOSER='1',SATRECOMP_BACKGROUND_WORKERS='0',
                    SATRECOMP_HD_STATS='1',SATRECOMP_WINDOW_KEYS=f'2:SIZE=2560x1440,8:WINDOWSHOT={shot.as_posix()},12:QUIT')
                run=subprocess.run([str(EXE),'--disc',str(OWNER/'local/prepared/disc1/game.cue'),
                    '--pc-assets',str(PACK),'--state-load','0:'+str(STATE),'--backup',str(folder/'backup.bin'),
                    '--settings',str(folder/'settings.ini'),'--hash-log',str(folder/'frames.hash'),
                    '--stats','--mute','--unthrottled'],env=env,capture_output=True,timeout=50)
                self.assertEqual(run.returncode,0,run.stderr.decode(errors='replace'))
                self.assertIn(b'interpreted 0 (0.00%)',run.stderr)
                if not disabled:self.assertIn(b'density=2 white_mix=25',run.stderr)
                else:self.assertNotIn(b'portrait viewport:',run.stderr)
                hashes.append((folder/'frames.hash').read_bytes())
                with Image.open(shot) as image:images.append(image.convert('RGB').tobytes())
            self.assertEqual(hashes[0],hashes[1])
            # This accepted PC portrait yields the native colors for this fade;
            # retain exact equality rather than inventing a quality difference.
            self.assertEqual(images[0],images[1])
