"""Build small original fixtures against the actual native frontend helpers."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
PREFIX=Path('C:/msys64/clang64')
DEP=ROOT/'local/deps/satrecomp'


@unittest.skipUnless(sys.platform=='win32' and (PREFIX/'bin/clang++.exe').is_file()
                     and (DEP/'port/integer_viewport.h').is_file(),
                     'requires the locally patched Windows SDL/Clang dependency')
class FrontendTests(unittest.TestCase):
    def fixture(self,name,extra=()):
        with tempfile.TemporaryDirectory(dir=ROOT/'local') as directory:
            folder=Path(directory).resolve()
            self.assertTrue(folder.is_relative_to((ROOT/'local').resolve()))
            exe=folder/(name+'.exe')
            command=[str(PREFIX/'bin/clang++.exe'),'-std=c++20',str(ROOT/'tests'/('test_'+name+'.cpp')),
                     *map(str,extra),'-I',str(DEP/'port'),'-I',str(DEP/'recomp-common'),
                     '-I',str(DEP/'recomp-common/launcher/src'),'-I',str(PREFIX/'include'),
                     '-L',str(PREFIX/'lib'),'-lSDL3','-o',str(exe)]
            result=subprocess.run(command,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stderr)
            env=os.environ.copy()
            env['PATH']=str(PREFIX/'bin')+os.pathsep+env.get('PATH','')
            result=subprocess.run([str(exe),str(folder)],env=env,capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_integer_scaling_native_modes_and_all_window_shapes(self):
        self.fixture('integer_viewport')

    def test_launcher_child_outlives_observer_without_freed_memory_access(self):
        self.fixture('launcher_lifetime',[DEP/'recomp-common/launcher/src/game_process.cpp'])

    def test_launcher_disc_detection_trailing_separator_and_revision(self):
        self.fixture('launcher_disc',[DEP/'recomp-common/settings.cpp'])


if __name__=='__main__':
    unittest.main()
