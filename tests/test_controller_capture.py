from pathlib import Path
import os,subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
CLANG=Path('C:/msys64/clang64/bin/clang++.exe')
@unittest.skipUnless(CLANG.is_file(),'requires local Windows compiler')
class ControllerCaptureTests(unittest.TestCase):
    def test_physical_capture_release_duplicates_layouts_and_report(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'local') as folder:
            exe=Path(folder)/'test.exe'
            result=subprocess.run([str(CLANG),'-std=c++20',str(ROOT/'tests/test_controller_capture.cpp'),'-I',str(ROOT/'tools'),'-o',str(exe)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            env=os.environ.copy();env['PATH']='C:/msys64/clang64/bin;'+env.get('PATH','')
            result=subprocess.run([str(exe)],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
