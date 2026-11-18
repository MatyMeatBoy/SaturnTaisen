"""Synthetic checks for applying independently reviewed portrait matches."""
from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import apply_reviewed_hd_portraits as reviewed
import hd_matching as matching


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ReviewTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.workspace = self.root / 'original'
        self.workspace.mkdir()
        archive = self.workspace / 'KAO.spr'
        archive.write_bytes(b'synthetic KAO bytes')
        native = bytes([1] * 3200)
        (self.workspace / 'raw.bin').write_bytes(native)
        Image.new('RGBA', (40, 80), 'white').save(self.workspace / 'native.png')
        candidate = Image.new('RGBA', (80, 160), 'red')
        candidate.save(self.workspace / 'pc.png')
        self.project = {
            'schema': 1, 'kind': 'sakura-narrative-portraits',
            'output': str(self.root / 'original-pack'), 'palette_hash': 0,
            'source': {'path': str(archive), 'bytes': len(archive.read_bytes()),
                       'sha256': sha(archive.read_bytes()), 'fnv64': matching.fnv64(archive.read_bytes())},
            'candidates': [{'index': 18, 'path': 'pc.png', 'sha256': matching.fingerprint(self.workspace / 'pc.png')}],
            'rows': [{'id': '0013', 'status': 'pending', 'selected': 18, 'dx': 0, 'dy': 0,
                      'path': 'native.png', 'raw': 'raw.bin', 'raw_sha256': sha(native)}],
        }
        self.lock = {
            'schema': 1, 'source': {k: self.project['source'][k] for k in ('bytes', 'sha256', 'fnv64')},
            'matches': [{'id': '0013', 'pc_index': 18, 'native_raw_sha256': sha(native),
                         'pc_rgba_sha256': sha(candidate.tobytes()), 'dx': 0, 'dy': 0,
                         'parts': ['base', 'eyes', 'mouth'],
                         'variants_rgba_sha256': {
                             str(i): sha(matching.prepare_variant(candidate, native, i).tobytes()) for i in (1, 2)
                         }}],
        }
        self.project_file = self.workspace / 'project.json'
        matching.atomic_json(self.project_file, self.project)
        self.output = self.root / 'new' / 'project.json'

    def test_copies_and_exports_without_modifying_input(self):
        before = self.project_file.read_bytes()
        result = reviewed.write_reviewed_project(self.project_file, self.output, self.lock, export=True)
        self.assertEqual(result['portraits'], 1)
        self.assertEqual(self.project_file.read_bytes(), before)
        self.assertTrue(self.output.is_file())
        self.assertTrue((self.output.parent / 'portrait-pack/manifest.ini').is_file())
        with self.assertRaises(ValueError):
            reviewed.write_reviewed_project(self.project_file, self.output, self.lock)
        self.assertEqual(self.project_file.read_bytes(), before)

    def test_rejects_wrong_locked_identity_or_variant_without_output(self):
        for field, value in (('native_raw_sha256', '0' * 64), ('pc_rgba_sha256', '0' * 64),
                             ('pc_index', 19), ('variants_rgba_sha256', {'1': '0' * 64, '2': '0' * 64}),
                             ('parts', ['base', 'eyes'])):
            lock = deepcopy(self.lock)
            lock['matches'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                reviewed.write_reviewed_project(self.project_file, self.output, lock, export=True)
            self.assertFalse(self.output.parent.exists())

    def test_rejects_source_file_change_even_if_project_metadata_is_unchanged(self):
        (self.workspace / 'KAO.spr').write_bytes(b'tampered PC source')
        with self.assertRaises(ValueError):
            reviewed.write_reviewed_project(self.project_file, self.output, self.lock)
        self.assertFalse(self.output.parent.exists())
