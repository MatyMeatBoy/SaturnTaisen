import pathlib, struct, sys, tempfile, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import witness_sweep as ws


def record(name, extent, size, directory=False):
    raw = name.encode('latin1')
    length = 33 + len(raw)
    length += length % 2
    rec = bytearray(length)
    rec[0] = length
    struct.pack_into('<I', rec, 2, extent)
    struct.pack_into('<I', rec, 10, size)
    rec[25] = 2 if directory else 0
    rec[32] = len(raw)
    rec[33:33 + len(raw)] = raw
    return bytes(rec)


def synthetic_iso(path):
    """Root (sector 20) with a directory SAKURA1 (sector 21) holding BG2077.BIN at 30 (2 sectors) and IC02.BIN;1 at 40."""
    image = bytearray(2048 * 50)
    pvd = bytearray(2048)
    pvd[156:156 + 34] = record('\x00', 20, 2048, True)[:34]
    struct.pack_into('<I', pvd, 156 + 2, 20)
    struct.pack_into('<I', pvd, 156 + 10, 2048)
    image[16 * 2048:17 * 2048] = pvd
    image[20 * 2048:20 * 2048 + 40] = record('SAKURA1', 21, 2048, True)
    image[21 * 2048:21 * 2048 + 200] = record('BG2077.BIN;1', 30, 4096) + record('IC02.BIN;1', 40, 100)
    path.write_bytes(bytes(image))


class WitnessSweep(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.iso = pathlib.Path(self.dir.name) / 'a.iso'
        synthetic_iso(self.iso)
        self.table = ws.read_iso(self.iso)

    def tearDown(self):
        self.dir.cleanup()

    def test_iso_listing_and_fad_lookup(self):
        self.assertEqual([r[2] for r in self.table], ['/SAKURA1/BG2077.BIN', '/SAKURA1/IC02.BIN'])
        self.assertEqual(ws.file_at(self.table, 30 + 150), '/SAKURA1/BG2077.BIN')
        self.assertEqual(ws.file_at(self.table, 31 + 150), '/SAKURA1/BG2077.BIN')
        self.assertIsNone(ws.file_at(self.table, 32 + 150))
        self.assertEqual(ws.file_at(self.table, 40 + 150), '/SAKURA1/IC02.BIN')

    def test_classify(self):
        self.assertEqual(ws.classify('/SAKURA1/BG2077.BIN'), ('BG', 'BG2077'))
        self.assertEqual(ws.classify('/SAKURA1/IC1006.BIN'), ('IC', 'IC1006'))
        self.assertEqual(ws.classify('/SAKURA1/ENDING.BIN'), ('ENDING', 'ENDING'))
        self.assertEqual(ws.classify('/SAKURA2/EVE0101.BIN'), ('EVE', 'EVE0101'))
        self.assertIsNone(ws.classify('/SAKURA1/NC10.BIN'))

    def test_cd_trace_plays(self):
        lines = ['cd cmd 1082 87E6 0080 000C -> 0480 4101 0102 87E6 (HIRQ 0BC1)',   # play from FAD 0x287E6, 12 sectors
                 'cd cmd 0600 0000 0000 0000 -> 0300 0400 0000 0000 (HIRQ 0BC5)',   # not a play
                 'cd cmd 10FF FFFF 0000 0000 -> 0000 0000 0000 0000 (HIRQ 0000)',   # resume: no start
                 'cd cmd 1000 0001 0000 0001 -> 0000 0000 0000 0000 (HIRQ 0000)']   # track form: not a frame address
        self.assertEqual(list(ws.cd_plays(lines)), [(0, 0x287E6, 12)])

    def test_frames_in_hash_bytes(self):
        lines = ''.join('%d %016x\n' % (n, n) for n in range(1, 1201))
        self.assertEqual(ws.frames_in_hash_bytes(len(lines)), 1200)
        self.assertEqual(ws.frames_in_hash_bytes(len(lines) - 5), 1199)
        self.assertEqual(ws.frames_in_hash_bytes(0), 0)

    def test_attribution_picks_the_next_checkpoint(self):
        events = [{'frame_estimate': 10}, {'frame_estimate': 440}, {'frame_estimate': 990}]
        self.assertEqual(ws.attribute(events, 500, 60, 1200), [499, 999, None])

    def test_dedupe_and_summary(self):
        loads = [{'file': 'a', 'scene': 'BG2077', 'kind': 'BG', 'frame_estimate': 5}, {'file': 'a', 'scene': 'BG2077', 'kind': 'BG', 'frame_estimate': 9},
                 {'file': 'b', 'scene': 'IC02', 'kind': 'IC', 'frame_estimate': 20}]
        self.assertEqual(len(ws.dedupe(loads)), 2)
        summary = ws.summarise([{'seed': 3, 'loads': ws.dedupe(loads)}])
        self.assertEqual(summary['scenes']['IC02']['seed'], 3)
        self.assertIsNotNone(summary['targets']['BG2077'])
        self.assertIsNone(summary['targets']['BG1283'])
        self.assertEqual(summary['by_kind']['IC'], ['IC02'])

    def test_seeds(self):
        self.assertEqual(ws.parse_seeds('1-3,7'), [1, 2, 3, 7])


if __name__ == '__main__':
    unittest.main()
