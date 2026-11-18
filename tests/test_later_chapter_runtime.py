"""Optional owner-data regressions around observed later-chapter boundaries."""
from pathlib import Path
import hashlib
import os
import subprocess
import tempfile
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OWNER=Path(os.environ.get('SAKURA_OWNER_ROOT',ROOT))
EXE=Path(os.environ.get('SAKURA_LATER_TEST_EXE',OWNER/'local/build/sakura/sakura-episode4.exe'))
STATE=OWNER/'local/work/later-chapter-audit/ep2-strict-anchor/state-6688.bin'
SEED=OWNER/'local/work/later-chapter-audit/episode2-test-copy.bin'
STATE4=OWNER/'local/work/later-chapter-audit/chapter-sweep/bank-4-battle-reference/state-6678.bin'
SEED4=OWNER/'local/work/later-chapter-audit/chapter-sweep/seeds/bank-4-battle.bin'


@unittest.skipUnless(EXE.is_file(),'requires private candidate runtime')
class LaterChapterRuntimeTests(unittest.TestCase):
    def test_episode2_overlay_boundary_keeps_native_hashes_and_pixels(self):
        if not STATE.is_file() or not SEED.is_file():self.skipTest('requires episode2 fixtures')
        self.assertEqual(hashlib.sha256(STATE.read_bytes()).hexdigest(),
                         '61b8cbb898f59c116509640a496ce8fb25e8b4d9d85c46d9ccef2d3533c05333')
        self.compare(STATE,1200)

    def test_episode4_overlay_boundary_keeps_native_hashes_and_pixels(self):
        if not STATE4.is_file() or not SEED4.is_file():self.skipTest('requires episode4 fixtures')
        self.assertEqual(hashlib.sha256(STATE4.read_bytes()).hexdigest(),
                         '42ab8d52f4b844bd45ae80ca799b98a7732e84f8e0814164a4b89a1f718cba14')
        self.compare(STATE4,1200,seed=SEED4)

    @unittest.skipUnless(os.environ.get('SAKURA_LATER_COLD')=='1','opt-in longer cold-load replay')
    def test_episode2_cold_continue_matches_interpreter(self):
        if not SEED.is_file():self.skipTest('requires episode2 SRAM')
        self.assertEqual(hashlib.sha256(SEED.read_bytes()).hexdigest(),
                         '4c22bf1edd1437b082ccd05e12df5bbf46bdcc5c9058fa3cc869db281f043908')
        self.compare(None,9501,ROOT/'tests/cold-load.movie')

    def compare(self,state,frames,movie=None,seed=SEED):
        hashes=[];pictures=[]
        (ROOT/'local/work').mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as temporary:
            for mode in ('native','interpreter'):
                folder=Path(temporary)/mode;folder.mkdir()
                (folder/'backup.bin').write_bytes(seed.read_bytes())
                env={key:value for key,value in os.environ.items() if not key.startswith('SATRECOMP_')}
                env['PATH']='C:/msys64/clang64/bin;'+env.get('PATH','')
                env.update(SATRECOMP_NO_CALLS='1',SATRECOMP_NO_FUNCTIONS='1')
                env['SATRECOMP_STRICT_NATIVE' if mode=='native' else 'SATRECOMP_NO_BLOCKS']='1'
                args=[str(EXE),'--disc',str(OWNER/'local/prepared/disc1/game.cue'),
                    '--backup',str(folder/'backup.bin'),'--headless','--frames',str(frames),
                    '--hash-log',str(folder/'frames.hash'),'--shot-every',str(frames)+':'+str(folder/'frame-'),
                    '--stats','--mute']
                if state:args+=['--state-load','0:'+str(state)]
                if movie:args+=['--movie',str(movie)]
                run=subprocess.run(args,env=env,capture_output=True,timeout=max(90,frames/30))
                self.assertEqual(run.returncode,0,run.stderr.decode(errors='replace'))
                if mode=='native':self.assertIn(b'interpreted 0 (0.00%)',run.stderr)
                hashes.append((folder/'frames.hash').read_bytes())
                with Image.open(folder/f'frame-{frames:06d}.png') as image:pictures.append(image.convert('RGB').tobytes())
            self.assertEqual(len(hashes[0].splitlines()),frames)
            self.assertEqual(hashes[0],hashes[1]);self.assertEqual(pictures[0],pictures[1])
