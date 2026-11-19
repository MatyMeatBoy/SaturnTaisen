"""Integrates the open pull requests one by one (coordinator tool).

For each open PR: check out its branch, merge origin/main, resolve the conflicts the workers always cause in the shared files, run
tools/check_patch_stack.py, push, and merge the PR. A PR with any conflict this tool does not know how to resolve is left alone and
reported. Pure helpers are unit-tested in tests/test_integrate_prs.py.

    python tools/integrate_prs.py [--dry-run] [--only 184,185]

Resolution rules
  *.md                 both sides kept (conflict markers removed): rows and sections are additive.
  *.json               union: dict keys merged recursively, lists as an ordered union (sorted when the items are comparable).
  config/dependencies.json   main's patch list first, then the branch's own new patches; a branch patch whose number is already taken
                       on main is renamed to the next free number (file and list entry).
Never run it with someone else's uncommitted work in the checkout: it switches branches.
"""
import argparse, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def union_markdown(text):
    """Both sides of every conflict, markers removed (a worker's rows and a worker's sections never exclude each other)."""
    return re.sub(r'^(<<<<<<< .*|>>>>>>> .*)\n', '', re.sub(r'^=======\n', '', text, flags=re.M), flags=re.M)


def merge_json(ours, theirs):
    """Recursive union of two JSON values: dicts by key, lists as an ordered union; on a scalar clash theirs wins."""
    if isinstance(ours, dict) and isinstance(theirs, dict):
        merged = dict(ours)
        for key, value in theirs.items():
            merged[key] = merge_json(ours[key], value) if key in ours else value
        return merged
    if isinstance(ours, list) and isinstance(theirs, list):
        merged = list(ours)
        for item in theirs:
            if item not in merged:
                merged.append(item)
        try:
            return sorted(merged)
        except TypeError:
            return merged
    return theirs


def patch_number(path):
    return int(re.match(r'patches/(\d+)-', path).group(1))


def merge_patch_lists(main_list, branch_list):
    """(merged list, {old path: new path}). Main's patches keep their numbers; the branch's new ones go last, renumbered on a clash."""
    merged = list(main_list)
    taken = {patch_number(p) for p in merged}
    renames = {}
    for path in branch_list:
        if path in merged:
            continue
        number = patch_number(path)
        if number in taken:
            number = max(taken) + 1
            new = re.sub(r'^patches/\d+-', 'patches/%04d-' % number, path)
            renames[path] = new
            path = new
        taken.add(number)
        merged.append(path)
    return merged, renames


def run(*args, check=True, cwd=ROOT):
    result = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True)
    if check and result.returncode:
        raise RuntimeError('%s failed: %s' % (' '.join(map(str, args)), (result.stderr or result.stdout).strip()[:300]))
    return result


def stage(n, path):
    return run('git', 'show', ':%d:%s' % (n, path)).stdout


def resolve(path):
    """Resolves one conflicted file in the working tree; returns False if the tool does not know how."""
    full = ROOT / path
    if path.endswith('.md'):
        full.write_text(union_markdown(full.read_text(encoding='utf8')), encoding='utf8', newline='\n')
    elif path == 'config/dependencies.json':
        main, branch = json.loads(stage(3, path)), json.loads(stage(2, path))
        merged = merge_json(main, branch)
        patches, renames = merge_patch_lists(main['satrecomp']['patches'], branch['satrecomp']['patches'])
        merged['satrecomp']['patches'] = patches
        for old, new in renames.items():
            run('git', 'mv', old, new)
        full.write_text(json.dumps(merged, indent=2) + '\n', encoding='utf8', newline='\n')
    elif path.endswith('.json'):
        merged = merge_json(json.loads(stage(3, path)), json.loads(stage(2, path)))
        full.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + '\n', encoding='utf8', newline='\n')
    else:
        return False
    run('git', 'add', path)
    return True


def integrate(number, dry):
    info = json.loads(run('gh', 'pr', 'view', str(number), '--json', 'headRefName,title').stdout)
    branch = info['headRefName']
    run('git', 'fetch', '-q', 'origin')
    run('git', 'checkout', '-q', '-B', 'integrate-%d' % number, 'origin/' + branch)
    merge = run('git', 'merge', 'origin/main', '-q', '-m', 'Merge main', check=False)
    if merge.returncode:
        for path in run('git', 'diff', '--name-only', '--diff-filter=U').stdout.split():
            if not resolve(path):
                run('git', 'merge', '--abort', check=False)
                return 'manual: ' + path
        run('git', 'commit', '-q', '-m', 'Merge main; shared files unioned by tools/integrate_prs.py')
    stack = run(sys.executable, 'tools/check_patch_stack.py', check=False)
    if stack.returncode:
        return 'patch stack: ' + stack.stdout.strip()[:200]
    if dry:
        return 'ready (dry run)'
    run('git', 'push', '-q', 'origin', 'HEAD:' + branch)
    merged = run('gh', 'pr', 'merge', str(number), '--merge', check=False)
    return 'merged' if merged.returncode == 0 else 'not merged: ' + merged.stderr.strip()[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    numbers = [p['number'] for p in json.loads(run('gh', 'pr', 'list', '--state', 'open', '--json', 'number').stdout)]
    if a.only:
        numbers = [n for n in numbers if str(n) in a.only.split(',')]
    for number in sorted(numbers):
        try:
            print('#%d: %s' % (number, integrate(number, a.dry_run)), flush=True)
        except RuntimeError as error:
            print('#%d: error %s' % (number, error), flush=True)
            run('git', 'merge', '--abort', check=False)
        run('git', 'checkout', '-q', 'main', check=False)
        run('git', 'pull', '-q', check=False)


if __name__ == '__main__':
    main()
