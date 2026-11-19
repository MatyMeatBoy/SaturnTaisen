"""The composed patch stack must leave port/main.cpp with clean UTF-8 feature texts and Zoom as the scene_view default."""
from pathlib import Path
import json
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEP = ROOT / 'local' / 'deps' / 'satrecomp'
# a UTF-8 text saved as Windows-1252 shows lead characters (A-tilde, A-circumflex, a-circumflex) before a continuation
MOJIBAKE = re.compile('[ÂÃâ][\u0080-¿ŒŠŽŸƒˆ˜–-›€™]')


class RuntimeTextTests(unittest.TestCase):
    @unittest.skipUnless((DEP / '.git').exists(), 'needs the local satrecomp checkout to clone the base commit from')
    def test_composed_main_cpp_has_clean_text_and_zoom_default(self):
        cfg = json.loads((ROOT / 'config' / 'dependencies.json').read_text(encoding='utf-8'))['satrecomp']
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / 'sdk'
            subprocess.check_call(['git', 'clone', '-q', '--no-checkout', str(DEP), str(work)])
            subprocess.check_call(['git', '-C', str(work), 'checkout', '-q', cfg['commit']])
            for patch in cfg['patches']:
                subprocess.check_call(['git', '-C', str(work), 'apply', '--whitespace=nowarn', str(ROOT / patch)])
            text = (work / 'port' / 'main.cpp').read_text(encoding='utf-8')
        bad = [line.strip()[:80] for line in text.splitlines() if MOJIBAKE.search(line)]
        self.assertEqual(bad, [])
        self.assertIn('"Visualización de escena"', text)
        match = re.search(r'\{"scene_view",[^;]*?\n\s*(\d), \{"Original", "Zoom"\}\}\)', text)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), '1')


if __name__ == '__main__':
    unittest.main()
