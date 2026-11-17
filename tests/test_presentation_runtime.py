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
    def test_corrupt_derived_cache_regenerates_without_changing_the_background(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as directory:
            folder=Path(directory);backup=folder/'backup.bin';seed=(ROOT/'local/work/sakura/prebattle-immutable-seed.bin').read_bytes()
            def capture(name):
                backup.write_bytes(seed);shot=folder/(name+'.png')
                env={k:v for k,v in os.environ.items() if not k.startswith('SATRECOMP_')}
                env.update(PATH='C:/msys64/clang64/bin;'+env.get('PATH',''),SATRECOMP_WINDOW_HIDDEN='1',
                           SATRECOMP_WINDOW_KEYS=f'2:SIZE=1280x720,3:CHOICE=1,8:WINDOWSHOT={shot.as_posix()},12:QUIT')
                run=subprocess.run([str(BUILD/'sakura.exe'),'--disc',str(ROOT/'local/prepared/disc1/game.cue'),
                                    '--state-load','0:'+str(STATE),'--settings',str(folder/'settings.ini'),
                                    '--backup',str(backup),'--mute'],env=env,capture_output=True,timeout=30)
                self.assertEqual(run.returncode,0,run.stderr.decode(errors='replace'))
                with Image.open(shot) as image:return [image.getpixel((x,y)) for x in range(0,150,3) for y in range(0,720,3)]
            original=capture('original');cached=list(folder.rglob('*.stfb'));self.assertEqual(len(cached),1)
            expected=cached[0].read_bytes();broken=bytearray(expected);broken[-1]^=1;cached[0].write_bytes(broken)
            self.assertEqual(capture('regenerated'),original)
            self.assertEqual(cached[0].read_bytes(),expected)

    @unittest.skipUnless((ROOT/'local/work/v02-pc-game/_t_@_C__/SAKURA1/WALL/KABE0101.SPR').is_file()
                         and (BUILD/'art/pc-backgrounds/KABE0101-v1.png').is_file(),
                         'requires owner PC resources and generated PC extension')
    def test_pc_background_is_optional_and_rejects_modified_source(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'local/work') as directory:
            folder=Path(directory);pc=ROOT/'local/work/v02-pc-game/_t_@_C__'
            bad=folder/'modified-source/SAKURA1/WALL';bad.mkdir(parents=True)
            data=bytearray((pc/'SAKURA1/WALL/KABE0101.SPR').read_bytes());data[-1]^=1
            (bad/'KABE0101.SPR').write_bytes(data)
            samples={}
            for name,source,disabled in [('pc',pc,0),('disabled',pc,1),('modified',folder/'modified-source',0)]:
                profile=folder/name;profile.mkdir();shot=profile/'window.png'
                backup=profile/'backup.bin';backup.write_bytes((ROOT/'local/work/sakura/prebattle-immutable-seed.bin').read_bytes())
                settings=profile/'settings.ini';settings.write_text(f'[features]\npc_hd_backgrounds={disabled}\n',encoding='utf-8')
                env={k:v for k,v in os.environ.items() if not k.startswith('SATRECOMP_')}
                env.update(PATH='C:/msys64/clang64/bin;'+env.get('PATH',''),SATRECOMP_WINDOW_HIDDEN='1',
                           SATRECOMP_WINDOW_KEYS=f'2:SIZE=1280x720,3:CHOICE=1,8:WINDOWSHOT={shot.as_posix()},12:QUIT')
                run=subprocess.run([str(BUILD/'sakura.exe'),'--disc',str(ROOT/'local/prepared/disc1/game.cue'),
                                    '--pc-assets',str(source),'--state-load','0:'+str(STATE),'--backup',str(backup),
                                    '--settings',str(settings),'--mute'],env=env,capture_output=True,timeout=30)
                self.assertEqual(run.returncode,0,run.stderr.decode(errors='replace'))
                with Image.open(shot) as image:
                    samples[name]=[image.getpixel((x,y)) for x in range(0,150,3) for y in range(0,720,3)]
                cached=list(profile.rglob('*pc864*.stfb'))
                self.assertEqual(bool(cached),name=='pc','only a verified, enabled PC source may create the PC cache')
            self.assertGreater(sum(a!=b for a,b in zip(samples['pc'],samples['disabled'])),1000)
            self.assertEqual(samples['disabled'],samples['modified'],'modified PC data must fall back to Saturn')

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
