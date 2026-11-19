"""TS12 gate: whole-tree generated-art checks, scroll table checks and forbidden-file rejection."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from package_release import (release_file_manifest, verify_generated_art_tree, verify_scroll_table)  # noqa: E402

ART = ROOT / 'assets/generated'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RealArtTests(unittest.TestCase):
    @unittest.skipUnless((ART / 'screen-backgrounds/provenance.json').is_file(), 'generated art not in the checkout')
    def test_real_generated_art_passes_and_counts_are_pinned(self):
        result = verify_generated_art_tree(ART)
        self.assertEqual({k: len(v) for k, v in result.items()},
                         {'backgrounds': 20, 'pc-backgrounds': 19, 'screen-backgrounds': 26, 'tactical-extensions': 1})
        self.assertIn('EPISODE10-surround-v2.png', result['screen-backgrounds'])

    @unittest.skipUnless((ART / 'screen-backgrounds/provenance.json').is_file(), 'generated art not in the checkout')
    def test_real_art_rejects_missing_provenance_unlisted_file_and_size_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'generated'
            shutil.copytree(ART, root)
            verify_generated_art_tree(root)
            extra = root / 'tactical-extensions/original-map.png'
            extra.write_bytes(b'\x89PNG\r\n\x1a\nx')
            with self.assertRaisesRegex(RuntimeError, 'Unlisted file'):
                verify_generated_art_tree(root)
            extra.unlink()
            # A same-name image with a different size must fail even when the provenance hash is updated to match.
            from PIL import Image
            target = root / 'tactical-extensions/STAGE01-right-v1.png'
            Image.new('RGBA', (80, 224)).save(target)
            report = json.loads((root / 'tactical-extensions/provenance.json').read_text())
            report['backgrounds'][0]['sha256'] = sha(target)
            (root / 'tactical-extensions/provenance.json').write_text(json.dumps(report))
            with self.assertRaisesRegex(RuntimeError, 'tactical image extent'):
                verify_generated_art_tree(root)
            shutil.copy2(ART / 'tactical-extensions/STAGE01-right-v1.png', target)
            shutil.copy2(ART / 'tactical-extensions/provenance.json', root / 'tactical-extensions/provenance.json')
            (root / 'screen-backgrounds/provenance.json').unlink()
            with self.assertRaisesRegex(RuntimeError, 'Missing provenance'):
                verify_generated_art_tree(root)

    @unittest.skipUnless((ART / 'screen-backgrounds/provenance.json').is_file(), 'generated art not in the checkout')
    def test_real_episode_surround_size_change_is_rejected(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'generated'
            shutil.copytree(ART, root)
            folder = root / 'screen-backgrounds'
            target = folder / 'EPISODE03-surround-v2.png'
            Image.new('RGBA', (80, 224)).save(target)
            report = json.loads((folder / 'provenance.json').read_text(encoding='utf-8'))
            for row in report['backgrounds']:
                if row['file'] == target.name:
                    row['sha256'] = sha(target)
            (folder / 'provenance.json').write_text(json.dumps(report), encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError, 'episode surround'):
                verify_generated_art_tree(root)

    @unittest.skipUnless((ROOT / 'config/hd-scroll-pictures.json').is_file(), 'scroll table missing')
    def test_real_scroll_table_matches_the_runtime_patches(self):
        names = verify_scroll_table(ROOT / 'config/hd-scroll-pictures.json', ROOT / 'patches')
        self.assertGreaterEqual(len(names), 18)


class ScrollTableTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(name='BG1207', axis='x', width=512, height=144, native_bytes=1, native_fnv='B348FED200EB5F33',
                   palette='6EE7138F39DF8CFE', cells='7F3401C09AF54AA3', pc_file='SAKURA1/BG/BG1207.SPR', pc_bytes=2,
                   pc_fnv='79337C665113FFEA', pc_width=1024, pc_height=320, crop_cross=16, min_crop_correlation=0.95)
        row.update(changes)
        return row

    def check(self, rows, window=(288, 144)):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 's.json'
            path.write_text(json.dumps({'window': list(window), 'rows': rows}))
            return verify_scroll_table(path)

    def test_valid_and_each_corruption(self):
        self.assertEqual(self.check([self.row()]), ['BG1207'])
        for bad in ([], [self.row(), self.row()], [self.row(native_fnv='xyz')], [self.row(axis='z')],
                    [self.row(pc_file='C:/PC/BG1207.SPR')], [self.row(pixels='AAAA')], [self.row(width=-1)]):
            with self.assertRaises(RuntimeError):
                self.check(bad)
        with self.assertRaises(RuntimeError):
            self.check([self.row()], window=(320, 224))


class ForbiddenFileTests(unittest.TestCase):
    def stage(self, directory, relative, data=b'x'):
        file = Path(directory) / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)

    def test_game_resources_are_rejected_wherever_they_hide(self):
        for relative in ('data/disc1.bin', 'data/Saturn BIOS.bios', 'data/art/backgrounds/orig.png', 'data/MOVIE/x.dat',
                         'data/art/extra/KABE.png', 'data/clips/intro.mpg', 'data/SAKURA1/BG/BG1.SPR',
                         'data/local/note.txt', 'data/save.bkr', 'roms/disc.cue', 'data/film.avi'):
            with self.subTest(relative), tempfile.TemporaryDirectory() as directory:
                self.stage(directory, 'data/ok.txt')
                self.stage(directory, relative)
                with self.assertRaisesRegex(RuntimeError, 'Unexpected'):
                    release_file_manifest(Path(directory), {}, {})

    def test_approved_art_and_clean_tree_pass_and_tampering_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            data = b'\x89PNG\r\n\x1a\nfixture'
            self.stage(directory, 'data/art/screen-backgrounds/TITLE-v1.png', data)
            self.stage(directory, 'roms/LEEME.txt')
            allowed = {'art/screen-backgrounds/TITLE-v1.png': hashlib.sha256(data).hexdigest()}
            self.assertEqual(len(release_file_manifest(Path(directory), allowed, {})), 2)
            self.stage(directory, 'data/art/screen-backgrounds/TITLE-v1.png', data + b'!')
            with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
                release_file_manifest(Path(directory), allowed, {})


if __name__ == '__main__':
    unittest.main()
