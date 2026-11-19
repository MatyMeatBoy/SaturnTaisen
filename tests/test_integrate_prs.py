import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import integrate_prs as ip


class IntegratePrsTests(unittest.TestCase):
    def test_union_markdown_keeps_both_sides(self):
        text = 'a\n<<<<<<< HEAD\nrow mine\n=======\nrow theirs\n>>>>>>> origin/main\nz\n'
        self.assertEqual(ip.union_markdown(text), 'a\nrow mine\nrow theirs\nz\n')

    def test_union_markdown_without_conflict_is_unchanged(self):
        self.assertEqual(ip.union_markdown('x\n\ny\n'), 'x\n\ny\n')

    def test_merge_json_dicts_and_lists(self):
        ours = {'a': ['BG2', 'BG1'], 'b': {'x': 1}}
        theirs = {'a': ['BG3', 'BG1'], 'b': {'y': 2}, 'c': 3}
        self.assertEqual(ip.merge_json(ours, theirs), {'a': ['BG1', 'BG2', 'BG3'], 'b': {'x': 1, 'y': 2}, 'c': 3})

    def test_merge_json_mixed_list_keeps_order(self):
        self.assertEqual(ip.merge_json([{'k': 1}], [{'k': 2}, {'k': 1}]), [{'k': 1}, {'k': 2}])

    def test_patch_lists_keep_main_and_append_new(self):
        main = ['patches/0001-a.patch', 'patches/0002-b.patch']
        branch = ['patches/0001-a.patch', 'patches/0003-c.patch']
        merged, renames = ip.merge_patch_lists(main, branch)
        self.assertEqual(merged, main + ['patches/0003-c.patch'])
        self.assertEqual(renames, {})

    def test_patch_number_clash_is_renumbered(self):
        main = ['patches/0001-a.patch', 'patches/0002-b.patch', 'patches/0003-main.patch']
        branch = ['patches/0001-a.patch', 'patches/0002-b.patch', 'patches/0003-mine.patch']
        merged, renames = ip.merge_patch_lists(main, branch)
        self.assertEqual(merged[-1], 'patches/0004-mine.patch')
        self.assertEqual(renames, {'patches/0003-mine.patch': 'patches/0004-mine.patch'})

    def test_two_clashing_patches_get_distinct_numbers(self):
        main = ['patches/0001-a.patch']
        branch = ['patches/0002-x.patch', 'patches/0001-y.patch']
        merged, _ = ip.merge_patch_lists(['patches/0001-a.patch', 'patches/0002-m.patch'], branch)
        self.assertEqual(len({ip.patch_number(p) for p in merged}), len(merged))


if __name__ == '__main__':
    unittest.main()
