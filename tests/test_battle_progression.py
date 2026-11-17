"""Owner-data regression for an actual chapter-one normal attack."""
from pathlib import Path
import os,subprocess,tempfile,unittest,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'local/work/sakura/chapter1-first-attack.state'
EXE=ROOT/'local/build/sakura/sakura.exe'
@unittest.skipUnless(STATE.exists() and EXE.exists(),'requires the local owner battle fixture')
class BattleProgressionTests(unittest.TestCase):
    def test_first_normal_attack_matches_reference_for_every_frame(self):
        self.assertEqual(hashlib.sha256(STATE.read_bytes()).hexdigest(),'ab5dbeb1e5f65f44d95f9ec9c895672ff0443de46ed55e8529b056958f3ac8ea')
        outputs=[];pictures=[]
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as directory:
            for mode in ('native','reference'):
                folder=Path(directory)/mode;folder.mkdir();backup=folder/'backup.bin'
                backup.write_bytes((ROOT/'local/work/sakura/prebattle-immutable-seed.bin').read_bytes())
                env={k:v for k,v in os.environ.items() if not k.startswith('SATRECOMP_')}
                env['PATH']='C:/msys64/clang64/bin;'+env.get('PATH','')
                if mode=='native':env['SATRECOMP_STRICT_NATIVE']='1'
                else:env.update(SATRECOMP_NO_BLOCKS='1',SATRECOMP_NO_CALLS='1',SATRECOMP_NO_FUNCTIONS='1')
                result=subprocess.run([str(EXE),'--disc',str(ROOT/'local/prepared/disc1/game.cue'),'--headless','--frames','1200',
                    '--state-load','0:'+str(STATE),'--movie',str(ROOT/'tests/battle-first-attack.movie'),
                    '--hash-log',str(folder/'frames.hash'),'--shot-every','1200:'+str(folder/'frame-'),
                    '--backup',str(backup),'--stats','--mute'],env=env,capture_output=True,text=True,timeout=90)
                self.assertEqual(result.returncode,0,result.stderr)
                if mode=='native':self.assertIn('interpreted 0 (0.00%)',result.stderr)
                outputs.append((folder/'frames.hash').read_text().splitlines())
                with Image.open(folder/'frame-001200.png') as image:pictures.append(image.convert('RGB').tobytes())
        self.assertEqual(len(outputs[0]),1200);self.assertEqual(len(outputs[1]),1200)
        mismatch=next((i for i,(left,right) in enumerate(zip(*outputs)) if left!=right),None)
        self.assertIsNone(mismatch,f'AOT/reference diverged at frame {mismatch}')
        self.assertEqual(hashlib.sha256(pictures[0]).digest(),hashlib.sha256(pictures[1]).digest())
