"""Prevent original/unpinned images or path escapes through generated-art packaging."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from package_release import generated_backgrounds


class PackageArtTests(unittest.TestCase):
    def test_only_manifest_pinned_files_are_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);data=b'\x89PNG\r\n\x1a\nfixture'
            (folder/'KABE00.png').write_bytes(data)
            (folder/'original-screenshot.png').write_bytes(data)
            manifest={'backgrounds':[{'file':'KABE00.png','sha256':hashlib.sha256(data).hexdigest()}]}
            (folder/'provenance.json').write_text(json.dumps(manifest),encoding='utf-8')
            self.assertEqual(list(generated_backgrounds(folder)),['KABE00.png'])
            (folder/'KABE00.png').write_bytes(data+b'tampered')
            with self.assertRaises(RuntimeError):generated_backgrounds(folder)

    def test_manifest_cannot_escape_or_repeat_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            for name in ('../KABE00.png','C:/KABE00.png','original.png'):
                (folder/'provenance.json').write_text(json.dumps({'backgrounds':[{'file':name,'sha256':'0'*64}]}),encoding='utf-8')
                with self.assertRaises(RuntimeError):generated_backgrounds(folder)


if __name__=='__main__':unittest.main()
