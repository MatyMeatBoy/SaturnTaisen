"""Continuous replay must preserve the save-before-frame boundary."""
from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StitchReplayTests(unittest.TestCase):
    def load(self):
        spec = importlib.util.spec_from_file_location('stitch_battle_replay', ROOT/'tools/stitch_battle_replay.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def fixture(self, root, name, source, frames, movie):
        folder = root/name
        folder.mkdir()
        (folder/'input.movie').write_text(movie)
        (folder/'end.state').write_bytes(name.encode())
        (folder/'run.json').write_text(json.dumps(dict(command=['runtime', '--state-load', '0:'+str(source), '--movie', str(folder/'input.movie')],
            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), frames=frames,
            state_saved_at_frame=frames-1, exit=0)))
        return folder

    def test_chain_offsets_use_saved_frame_not_process_end(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); seed = root/'seed.state'; seed.write_bytes(b'seed')
            a = self.fixture(root, 'a', seed, 100, '10 0400 0\n14 0 0\n')
            b = self.fixture(root, 'b', a/'end.state', 80, '20 8000 0\n24 0 0\n')
            report, events = module.compose(b)
            self.assertEqual(report['initial_state'], str(seed))
            self.assertEqual(report['frames'], 179)
            self.assertEqual(report['final_state_at_frame'], 178)
            self.assertEqual(events[119], (0x8000, 0))
            self.assertEqual(events[123], (0, 0))
            self.assertEqual([row['offset'] for row in report['segments']], [0, 99])

    def test_changed_parent_state_is_rejected(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); seed = root/'seed.state'; seed.write_bytes(b'seed')
            folder = self.fixture(root, 'a', seed, 100, '10 0400 0\n14 0 0\n')
            seed.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'Source state changed'):
                module.compose(folder)

    def test_held_input_at_boundary_is_rejected(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); seed = root/'seed.state'; seed.write_bytes(b'seed')
            folder = self.fixture(root, 'a', seed, 100, '10 0400 0\n')
            with self.assertRaisesRegex(ValueError, 'released'):
                module.compose(folder)

    def test_ambiguous_last_frame_input_is_rejected(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); seed = root/'seed.state'; seed.write_bytes(b'seed')
            folder = self.fixture(root, 'a', seed, 100, '99 0400 0\n')
            with self.assertRaisesRegex(ValueError, 'boundary'):
                module.compose(folder)


if __name__ == '__main__':
    unittest.main()
