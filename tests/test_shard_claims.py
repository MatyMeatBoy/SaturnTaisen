import datetime, pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import shard_claims as sc

UTC = datetime.timezone.utc
T0 = datetime.datetime(2026, 11, 19, 12, 0, tzinfo=UTC)
ROWS = ['| ID | P | Type | Status | Pending |', '| --- | --- | --- | --- | --- |',
        '| TW1 | P1 | shard | open | first job |', '| TW2 | P1 | shard | open | second job |', 'plain text']


class ShardClaims(unittest.TestCase):
    def test_claim_goes_into_the_status_cell(self):
        lines = sc.add_claim(ROWS, 'TW1', 'ana', 'pendientes/tw1', T0)
        self.assertEqual(lines[2], '| TW1 | P1 | shard | CLAIM[ana|pendientes/tw1|2026-11-19T12:00:00Z] open | first job |')
        self.assertEqual(lines[3], ROWS[3])

    def test_a_claimed_row_cannot_be_claimed_again(self):
        lines = sc.add_claim(ROWS, 'TW1', 'ana', 'b', T0)
        with self.assertRaises(ValueError):
            sc.add_claim(lines, 'TW1', 'bo', 'c', T0)

    def test_unknown_row(self):
        with self.assertRaises(ValueError):
            sc.add_claim(ROWS, 'TW9', 'ana', 'b', T0)

    def test_fresh_claim_stays(self):
        lines = sc.add_claim(ROWS, 'TW1', 'ana', 'b', T0)
        out, released = sc.release_stale(lines, T0 + datetime.timedelta(minutes=20), 30, lambda b: None)
        self.assertEqual((out, released), (lines, []))

    def test_old_claim_without_commits_is_released(self):
        lines = sc.add_claim(ROWS, 'TW1', 'ana', 'b', T0)
        out, released = sc.release_stale(lines, T0 + datetime.timedelta(minutes=31), 30, lambda b: None)
        self.assertEqual(released, [('TW1', 'ana', 'b', 31)])
        self.assertIn('open · released (stale claim of ana, 2026-11-19T12:00:00Z)', out[2])
        self.assertNotIn('CLAIM[', out[2])

    def test_recent_commit_keeps_an_old_claim(self):
        lines = sc.add_claim(ROWS, 'TW1', 'ana', 'b', T0)
        now = T0 + datetime.timedelta(minutes=90)
        out, released = sc.release_stale(lines, now, 30, lambda b: now - datetime.timedelta(minutes=10))
        self.assertEqual(released, [])

    def test_old_commit_does_not_keep_it(self):
        lines = sc.add_claim(ROWS, 'TW1', 'ana', 'b', T0)
        now = T0 + datetime.timedelta(minutes=90)
        out, released = sc.release_stale(lines, now, 30, lambda b: T0 + datetime.timedelta(minutes=5))
        self.assertEqual(len(released), 1)

    def test_only_queue_rows_are_touched(self):
        lines = ROWS + ['text with CLAIM[x|y|2026-11-19T10:00:00Z] inside a paragraph']
        out, released = sc.release_stale(lines, T0, 30, lambda b: None)
        self.assertEqual((out, released), (lines, []))


if __name__ == '__main__':
    unittest.main()
