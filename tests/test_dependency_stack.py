"""Overlapping dependency patches must validate as one composed tree."""
from pathlib import Path
import difflib
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build_runtime


class DependencyStackTests(unittest.TestCase):
    def test_composed_overlapping_stack_is_repeatable_and_preserves_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);dep=root/'dep';dep.mkdir();(root/'config').mkdir()
            def git(*args):return subprocess.check_output(['git','-C',str(dep),*args],stderr=subprocess.DEVNULL)
            git('init');git('config','core.autocrlf','false')
            source=dep/'fixture.txt';source.write_text('alpha\n',encoding='utf-8')
            git('add','.');git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','base')
            commit=git('rev-parse','HEAD').decode().strip()
            names=[]
            for i,(a,b) in enumerate([('alpha\n','beta\n'),('beta\n','gamma\n')]):
                name=f'{i}.patch';names.append(name)
                text=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/fixture.txt',tofile='b/fixture.txt'))
                (root/name).write_text(text,encoding='utf-8')
            (root/'config/dependencies.json').write_text(json.dumps({'satrecomp':{'commit':commit,'patches':names}}),encoding='utf-8')
            with patch.object(build_runtime,'ROOT',root),patch.object(build_runtime,'DEP',dep):
                build_runtime.dependency();self.assertEqual(source.read_text(),'gamma\n')
                build_runtime.dependency();self.assertEqual(source.read_text(),'gamma\n')
                source.write_text('local work\n',encoding='utf-8')
                with self.assertRaisesRegex(RuntimeError,'local edits'):build_runtime.dependency()
                self.assertEqual(source.read_text(),'local work\n')


if __name__=='__main__':unittest.main()
