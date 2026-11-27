"""Checks the SDK patch stack of config/dependencies.json before a PR: numbers unique and increasing, every patch file listed,
and the whole stack applies cleanly on the pinned commit (temporary index, nothing in the dependency tree is touched).

    python tools/check_patch_stack.py
    python tools/check_patch_stack.py --platform   # also apply the GA36/R36S platform patches on top, in PLATFORM_ORDER

Needs local/deps/satrecomp (the pinned SDK checkout). Exit 1 with the reason on any problem. If two PRs took the same number, rebase on
origin/main, `git mv` your patch to the next free number and list it last in config/dependencies.json.
"""
import json, os, pathlib, re, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEP = pathlib.Path(os.environ.get('SATRECOMP_DEP_DIR', ROOT / 'local/deps/satrecomp'))
# Documented order of the SDK-side handheld patches (docs/research/ga36-handoff.md); the ga36-sdl3-*.patch files are for the
# SDL3 tree. r36s-aot-pages and ga36-aot-fast-dispatch are kept for rebuilding the 0.3.8 RCs only: patch 0340 of the stack
# now registers blocks by page and checks the pending page inline, which is what they did.
PLATFORM_ORDER = ['r36s-original-only', 'ga36-armhf-state', 'ga36-hd-2x-pilot', 'ga36-diagnostic-wide',
                  'ga36-perf-sh2', 'ga36-perf-sound', 'ga36-perf-vdp', 'ga36-idle-skip', 'ga36-video-thread', 'ga36-sound-thread',
                  'ga36-compose-thread-machine', 'ga36-lean-compose', 'ga36-sprite-line', 'ga36-frame-skip', 'ga36-compose-thread']


def main():
    spec = json.loads((ROOT / 'config/dependencies.json').read_text(encoding='utf8'))['satrecomp']
    patches = spec['patches']
    problems = []
    numbers = [int(re.match(r'patches/(\d+)-', p).group(1)) for p in patches]
    if len(set(numbers)) != len(numbers):
        problems.append('duplicate patch numbers: %s' % sorted({n for n in numbers if numbers.count(n) > 1}))
    if numbers != sorted(numbers):
        problems.append('patch numbers are not in increasing order')
    on_disk = {'patches/' + p.name for p in (ROOT / 'patches').glob('*.patch')}
    for extra in sorted(on_disk - set(patches)):
        problems.append('patch file not listed in config/dependencies.json: ' + extra)
    for missing in sorted(set(patches) - on_disk):
        problems.append('listed patch missing on disk: ' + missing)
    if not problems and DEP.is_dir():
        with tempfile.TemporaryDirectory() as folder:
            env = os.environ.copy()
            env['GIT_INDEX_FILE'] = str(pathlib.Path(folder) / 'index')
            def git(*args):
                return subprocess.run(['git', '-C', str(DEP), *map(str, args)], env=env, capture_output=True, text=True)
            git('read-tree', spec['commit'])
            for patch in patches:
                result = git('apply', '--cached', '--whitespace=nowarn', ROOT / patch)
                if result.returncode:
                    problems.append('%s does not apply on the stack before it: %s' % (patch, result.stderr.strip()[:200]))
                    break
            if not problems and '--platform' in sys.argv[1:]:
                for name in PLATFORM_ORDER:
                    result = git('apply', '--cached', '--whitespace=nowarn', ROOT / 'patches/platform' / (name + '.patch'))
                    if result.returncode:
                        problems.append('platform %s does not apply on the current stack: %s' % (name, result.stderr.strip()[:200]))
                        break
                if not problems:
                    print('platform patches ok: %d applied on top' % len(PLATFORM_ORDER))
    elif not DEP.is_dir():
        print('note: local/deps/satrecomp is absent, only the numbering was checked')
    for problem in problems:
        print('PROBLEM:', problem)
    if not problems:
        print('patch stack ok: %d patches, last %s' % (len(patches), patches[-1]))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
