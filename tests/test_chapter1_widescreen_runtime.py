"""Owner-data presentation controls: scene entry points and untouched guest state."""
from pathlib import Path
import os,subprocess,tempfile,unittest
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/'local/build/sakura/sakura.exe'
STATE=ROOT/'local/work/sakura/chapter1-first-attack.state'
@unittest.skipUnless(EXE.is_file() and STATE.is_file(),'requires owner chapter1 fixtures and local runtime')
class WidescreenRuntimeTests(unittest.TestCase):
    def capture(self,folder,state,mode=1,probe=False,frames=12,movie=None):
        folder.mkdir(parents=True);shot=folder/'shot.png'
        (folder/'settings.ini').write_text(f'[features]\npreset=custom\npresentation_mode={mode}\nscene_view=1\ntext_style=0\nrun_ahead=0\n')
        (folder/'backup.bin').write_bytes((ROOT/'local/work/sakura/prebattle-immutable-seed.bin').read_bytes())
        env={k:v for k,v in os.environ.items() if not k.startswith('SATRECOMP_')}
        env.update(PATH='C:/msys64/clang64/bin;'+env.get('PATH',''),SATRECOMP_WINDOW_HIDDEN='1',SATRECOMP_SKIP_CHOOSER='1',
            SATRECOMP_BACKGROUND_WORKERS='0',SATRECOMP_STRICT_NATIVE='1',SATRECOMP_PRESENTATION_TRACE='1',
            SATRECOMP_WINDOW_KEYS=f'2:SIZE=2560x1440,{frames-4}:WINDOWSHOT={shot.as_posix()},{frames}:QUIT')
        if probe:env['SATRECOMP_TACTICAL_WIDE_PROBE']='1'
        command=[str(EXE),'--disc',str(ROOT/'local/prepared/disc1/game.cue'),
            '--settings',str(folder/'settings.ini'),'--backup',str(folder/'backup.bin'),'--state-load','0:'+str(state),
            '--hash-log',str(folder/'frames.hash'),'--stats','--mute','--unthrottled']
        if movie:command+=['--movie',str(movie)]
        run=subprocess.run(command,env=env,capture_output=True,timeout=max(40,frames/20))
        self.assertEqual(run.returncode,0,run.stderr.decode(errors='replace'))
        self.assertIn(b'interpreted 0 (0.00%)',run.stderr)
        with Image.open(shot) as image:pixels=image.convert('RGB').copy()
        return pixels,(folder/'frames.hash').read_bytes(),run.stderr
    def test_tactical_widescreen_preserves_every_guest_frame_and_original_center(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as temp:
            folder=Path(temp)
            original,oldHash,_=self.capture(folder/'original',STATE,0)
            wide,newHash,log=self.capture(folder/'wide',STATE,1)
            self.assertEqual(oldHash,newHash)
            self.assertIn(b'presentation layout: tactical',log)
            center=(320,48,2240,1392)
            changed=ImageChops.difference(original.crop(center),wide.crop(center)).getbbox()
            self.assertIsNotNone(changed,'the recognized overlapping menu should be relaid out')
            # Only the popup frame/labels may move; original scene pixels remain exact.
            allowed=(672,192,912,528)  # native x112..152,y32..88 at scale6
            self.assertGreaterEqual(changed[0],allowed[0]);self.assertGreaterEqual(changed[1],allowed[1])
            self.assertLessEqual(changed[2],allowed[2]);self.assertLessEqual(changed[3],allowed[3])
            self.assertNotEqual(original.crop((86,48,320,1392)).tobytes(),wide.crop((86,48,320,1392)).tobytes())
    def test_attack_and_camera_replay_keep_guest_state_identical_with_extended_sprites(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as temp:
            movie=ROOT/'tests/battle-first-attack.movie';hashes=[]
            for mode in (0,1):
                _,guest,log=self.capture(Path(temp)/str(mode),STATE,mode,frames=1200,movie=movie)
                hashes.append(guest)
                if mode:self.assertIn(b'presentation layout: tactical',log)
            self.assertEqual(len(hashes[0].splitlines()),1200)
            self.assertEqual(hashes[0],hashes[1])
    def test_opening_title_status_pause_and_both_theater_maps_use_extended_layouts(self):
        scenes=[('local/work/worker-wide-transitions/title-start/loading.state','anchored-menu'),
            ('local/work/intro-enhanced/intro1799.state','opening'),('local/work/intro-enhanced/title-final.state','title'),
            ('local/work/sakura/theater.state','row-gradient'),('local/work/sakura/leave-dressing.state','row-gradient'),
            ('local/work/sakura/exit-battle-save.state','anchored-menu'),
            ('local/work/sakura/intermission-down.state','anchored-menu'),
            ('local/work/sakura/intermission-up.state','anchored-menu'),
            ('local/work/sakura/night-patrol-12000.state','anchored-menu'),('local/work/sakura/intermission-save.state','narrative')]
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as temp:
            for i,(name,kind) in enumerate(scenes):
                with self.subTest(scene=name):
                    state=ROOT/name
                    if not state.is_file():
                        self.skipTest('requires private scene fixture: '+name)
                    _,_,log=self.capture(Path(temp)/str(i),state)
                    self.assertIn(('presentation layout: '+kind).encode(),log)
