"""Optional owner-data regression: actual SDL output for a night narrative scene."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest
try:
    from PIL import Image
except ImportError:
    Image=None

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'local/build/sakura'
STATE=ROOT/'local/work/sakura/iris-correct-room-3000.state'


@unittest.skipUnless(Image is not None and STATE.is_file() and (BUILD/'art/backgrounds/KABE01.png').is_file(),
                     'requires owner-supplied local scene and generated background')
class PresentationRuntimeTests(unittest.TestCase):
    def test_night_mode_uses_its_own_full_window_background(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as directory:
            folder=Path(directory);shot=folder/'night.png';backup=folder/'backup.bin'
            backup.write_bytes((ROOT/'local/work/sakura/prebattle-immutable-seed.bin').read_bytes())
            env={k:v for k,v in os.environ.items() if not k.startswith('SATRECOMP_')}
            env.update(PATH='C:/msys64/clang64/bin;'+env.get('PATH',''),SATRECOMP_WINDOW_HIDDEN='1',
                       SATRECOMP_WINDOW_KEYS=f'2:SIZE=1280x720,3:CHOICE=1,8:WINDOWSHOT={shot.as_posix()},12:QUIT')
            run=subprocess.run([str(BUILD/'sakura.exe'),'--disc',str(ROOT/'local/prepared/disc1/game.cue'),
                                '--video','software','--state-load','0:'+str(STATE),'--backup',str(backup),'--mute'],
                               env=env,capture_output=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stderr.decode(errors='replace'))
            with Image.open(shot) as image:
                self.assertEqual(image.size,(1280,720))
                r,g,b=image.getpixel((10,360))[:3]
                self.assertLess(r,110,'night scene still shows the cream exterior frame')
                self.assertGreater(b,r,'wrong theme used for the night scene')


if __name__=='__main__':unittest.main()
