"""Re-anchors an SDK patch whose context moved because other patches landed first (coordinator and worker tool).

    python tools/rebase_patch.py patches/00NN-name.patch

The stack before the patch (the entries of config/dependencies.json that come before it, or all of them if it is not listed yet). With
--author-ref=REF (the branch the patch came from) a real context clash is merged three ways against the author's own stack is applied
in a temporary index, then the patch with the context reduced (git apply -C0), and the patch file is rewritten as the exact difference, so
it applies strictly again. Reduced context can place a hunk where a line was moved: ALWAYS compile and run a replay afterwards. Nothing in
the dependency tree is touched. Exit 1 if even the reduced context does not apply.
"""
import json, os, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEP = ROOT / 'local/deps/satrecomp'


def rebase(patch_rel, stack_before):
    """New patch bytes, or (None, reason)."""
    spec = json.loads((ROOT / 'config/dependencies.json').read_text(encoding='utf-8'))['satrecomp']
    with tempfile.TemporaryDirectory() as folder:
        env = os.environ.copy()
        env['GIT_INDEX_FILE'] = str(pathlib.Path(folder) / 'index')
        def git(*args):
            return subprocess.run(['git', '-C', str(DEP), *map(str, args)], env=env, capture_output=True)
        git('read-tree', spec['commit'])
        for entry in stack_before:
            result = git('apply', '--cached', '--whitespace=nowarn', ROOT / entry)
            if result.returncode:
                return None, 'the stack before the patch does not apply at %s' % entry
        base = git('write-tree').stdout.decode().strip()
        result = git('apply', '--cached', '-C0', '--whitespace=nowarn', ROOT / patch_rel)
        if result.returncode:
            return None, result.stderr.decode(errors='replace')[:300]
        return git('diff', '--cached', '--binary', base).stdout, result.stderr.decode(errors='replace').strip()


def rebase3(patch_rel, stack_new, stack_author):
    """Three-way: the files the patch touches are merged between the author's base (A), the author's result (R = A + patch) and the
    current stack (B), both sides' additions kept; fails on a real conflict. New patch bytes, or (None, reason)."""
    spec = json.loads((ROOT / 'config/dependencies.json').read_text(encoding='utf-8'))['satrecomp']
    with tempfile.TemporaryDirectory() as folder:
        folder = pathlib.Path(folder)
        def make(stack, patch=None):
            env = os.environ.copy()
            env['GIT_INDEX_FILE'] = str(folder / ('index-%d' % len(os.listdir(folder))))
            def git(*args, data=None):
                return subprocess.run(['git', '-C', str(DEP), *map(str, args)], env=env, capture_output=True, input=data)
            git('read-tree', spec['commit'])
            for entry in stack:
                if git('apply', '--cached', '--whitespace=nowarn', ROOT / entry).returncode:
                    return None, git
            if patch and git('apply', '--cached', '--whitespace=nowarn', ROOT / patch).returncode:
                return None, git
            return env, git
        envA, gitA = make(stack_author)
        envR, gitR = make(stack_author, patch_rel)
        envB, gitB = make(stack_new)
        if not (envA and envR and envB):
            return None, 'one of the three stacks does not apply'
        names = [n for n in gitR('diff', '--cached', '--name-only', gitA('write-tree').stdout.decode().strip()).stdout.decode().split() if n]
        base_tree = gitB('write-tree').stdout.decode().strip()
        for name in names:
            blobs = {}
            for key, git in (('a', gitA), ('r', gitR), ('b', gitB)):
                shown = git('show', ':' + name)
                blobs[key] = shown.stdout.replace(b'\r\n', b'\n') if shown.returncode == 0 else b''
            for key in blobs:
                (folder / key).write_bytes(blobs[key])
            merged = subprocess.run(['git', 'merge-file', '-p', str(folder / 'r'), str(folder / 'a'), str(folder / 'b')], capture_output=True)
            if merged.returncode:
                return None, 'conflict merging %s' % name
            oid = gitB('hash-object', '-w', '--stdin', data=merged.stdout).stdout.decode().strip()
            gitB('update-index', '--add', '--cacheinfo', '100644,%s,%s' % (oid, name))
        return gitB('diff', '--cached', '--binary', base_tree).stdout, 'three-way merge of ' + ', '.join(names)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--author-ref=')]
    refs = [a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--author-ref=')]
    if len(args) != 1:
        sys.exit(__doc__)
    patch = args[0].replace(chr(92), '/')
    spec = json.loads((ROOT / 'config/dependencies.json').read_text(encoding='utf-8'))['satrecomp']['patches']
    before = spec[:spec.index(patch)] if patch in spec else spec
    data, note = rebase(patch, before)
    if data is None and refs:
        # the context moved too far: merge the files three ways against the author's own stack (config/dependencies.json at the ref)
        shown = subprocess.run(['git', 'show', refs[0] + ':config/dependencies.json'], cwd=ROOT, capture_output=True, text=True)
        if shown.returncode == 0:
            theirs = json.loads(shown.stdout)['satrecomp']['patches']
            author_before = theirs[:theirs.index(patch)] if patch in theirs else [p for p in theirs if p != patch]
            data, note = rebase3(patch, before, author_before)
    if data is None:
        print('cannot rebase:', note)
        return 1
    (ROOT / patch).write_bytes(data)
    print('rebased', patch, '-', note or 'applied with reduced context', '- compile and replay before trusting it')
    return 0


if __name__ == '__main__':
    sys.exit(main())
