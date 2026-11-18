"""Build/discover/recompile Sakura locally; original game code stays in local/."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DEP = ROOT / 'local/deps/satrecomp'
WORK = ROOT / 'local/work/sakura'
BUILD = ROOT / 'local/build/sakura'


def run(*args, env=None, **kwargs):
    subprocess.run([str(a) for a in args], cwd=ROOT, env=env, check=True, **kwargs)


def dependency():
    spec = json.loads((ROOT / 'config/dependencies.json').read_text())['satrecomp']
    if not DEP.exists():
        DEP.parent.mkdir(parents=True, exist_ok=True)
        run('git', 'clone', '--depth', '1', spec['repository'], DEP)
    head = subprocess.check_output(['git', '-C', str(DEP), 'rev-parse', 'HEAD'], text=True).strip()
    if head != spec['commit']:
        status = subprocess.check_output(['git', '-C', str(DEP), 'status', '--porcelain'], text=True)
        if status:
            raise RuntimeError('Dependency has local edits and a different commit; refusing checkout')
        run('git', '-C', DEP, 'fetch', '--depth', '1', 'origin', spec['commit'])
        run('git', '-C', DEP, 'checkout', '--detach', spec['commit'])
    # Later patches may edit context introduced by earlier ones. Validate the
    # composed tree, not each patch reversed against the final working tree.
    import tempfile
    with tempfile.TemporaryDirectory(prefix='dependency-index-') as folder:
        env=os.environ.copy()
        env['GIT_INDEX_FILE']=str(Path(folder)/'index')
        def git(*args,check=True):
            return subprocess.run(['git','-C',str(DEP),*map(str,args)],env=env,
                                  capture_output=True,check=check)
        git('read-tree',spec['commit'])
        trees=[git('write-tree').stdout.decode().strip()]
        for name in spec['patches']:
            git('apply','--cached','--whitespace=nowarn',ROOT/name)
            trees.append(git('write-tree').stdout.decode().strip())
        if git('diff','--quiet','--no-ext-diff',check=False).returncode==0:
            return
        for installed in range(len(trees)-2,-1,-1):
            git('read-tree',trees[installed])
            if git('diff','--quiet','--no-ext-diff',check=False).returncode:
                continue
            # --check refuses colliding new files and preserves local edits.
            for name in spec['patches'][installed:]:
                patch=ROOT/name
                result=git('apply','--check',patch,check=False)
                if result.returncode:
                    raise RuntimeError('Dependency has conflicting local edits: '+name)
                run('git','-C',DEP,'apply',patch)
            git('read-tree',trees[-1])
            if git('diff','--quiet','--no-ext-diff',check=False).returncode:
                raise RuntimeError('Dependency does not match composed patch tree')
            return
        raise RuntimeError('Dependency has local edits outside the recorded patch stack; preserve them and record a new patch first')



def build(toolchain: Path, env):
    WORK.joinpath('gen').mkdir(parents=True, exist_ok=True)
    run(sys.executable, DEP / 'tools/gamecfg.py', '--header', WORK / 'gen/game_info.h', 'sakura')
    run(toolchain / 'bin/cmake.exe', '-S', DEP, '-B', BUILD, '-G', 'Ninja',
        '-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_C_COMPILER={toolchain.as_posix()}/bin/clang.exe',
        f'-DCMAKE_CXX_COMPILER={toolchain.as_posix()}/bin/clang++.exe',
        '-DGAME=sakura', f'-DGAME_DIR={ROOT.as_posix()}/games/sakura',
        f'-DWORK_DIR={WORK.as_posix()}', f'-DCMAKE_PREFIX_PATH={toolchain.as_posix()}',
        '-DSATRECOMP_REFERENCE=OFF', env=env)
    run(toolchain / 'bin/cmake.exe', '--build', BUILD, '--parallel', '6', env=env)
    artwork=ROOT/'assets/generated/backgrounds'
    if not artwork.is_dir():artwork=ROOT/'art/backgrounds' # portable source package
    if artwork.is_dir():
        shutil.copytree(artwork,BUILD/'art/backgrounds',dirs_exist_ok=True)
    pc_artwork=ROOT/'assets/generated/pc-backgrounds'
    if pc_artwork.is_dir():shutil.copytree(pc_artwork,BUILD/'art/pc-backgrounds',dirs_exist_ok=True)
    screen_artwork=ROOT/'assets/generated/screen-backgrounds'
    if screen_artwork.is_dir():shutil.copytree(screen_artwork,BUILD/'art/screen-backgrounds',dirs_exist_ok=True)
    tactical_artwork=ROOT/'assets/generated/tactical-extensions'
    if tactical_artwork.is_dir():shutil.copytree(tactical_artwork,BUILD/'art/tactics',dirs_exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'discover', 'recompile', 'run', 'check-disc', 'check-video', 'check-machine'])
    parser.add_argument('--toolchain', type=Path, default=Path('C:/msys64/clang64'))
    parser.add_argument('--disc', type=Path, default=ROOT / 'local/prepared/disc1/game.cue')
    parser.add_argument('--frames', type=int, default=600)
    parser.add_argument('--movie', type=Path)
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()
    dependency()
    env = os.environ.copy()
    env['PATH'] = str(args.toolchain / 'bin') + os.pathsep + env.get('PATH', '')
    if args.action == 'check-machine':
        destination = ROOT / 'local/build/machine-tests'
        run(args.toolchain / 'bin/cmake.exe', '-S', ROOT / 'tests/native', '-B', destination, '-G', 'Ninja',
            '-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_CXX_COMPILER={args.toolchain.as_posix()}/bin/clang++.exe', env=env)
        run(args.toolchain / 'bin/cmake.exe', '--build', destination, '--parallel', '6', env=env)
        run(sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_machine_safety.py', '-v', env=env)
        return
    if args.action == 'check-video':
        executable = ROOT / 'local/vdp2-color-test.exe'
        sources = [DEP / 'video' / name for name in
                   ('renderer.cpp', 'regs.cpp', 'layers.cpp', 'vdp1.cpp', 'raster.cpp')]
        run(args.toolchain / 'bin/clang++.exe', '-std=c++20', '-O2',
            ROOT / 'tests/test_vdp2_color.cpp', *sources,
            '-I', DEP / 'video', '-I', DEP / 'runtime', '-lz', '-o', executable, env=env)
        run(executable, env=env)
        return
    if args.action == 'check-disc':
        executable = ROOT / 'local/disc-image-test.exe'
        run(args.toolchain / 'bin/clang++.exe', '-std=c++20', ROOT / 'tests/test_disc_image.cpp',
            DEP / 'port/disc_image.cpp', '-I', DEP / 'port', '-o', executable, env=env)
        run(executable, ROOT / 'local/test-disc', env=env)
        return
    if args.action == 'recompile':
        if not (WORK / 'blocks.txt').is_file():
            raise RuntimeError('No discovery database: build, then discover before recompiling')
        run(sys.executable, DEP / 'tools/recomp.py', '--blocks', WORK / 'blocks.txt',
            '--ops', DEP / 'machine/sh2_ops.h', '--out', WORK / 'gen',
            '--max-function-blocks', '1',
            '--append-order', WORK / 'block-order.json',
            '--region', '00200000-00300000', '--region', '06002000-08000000')
    build(args.toolchain, env)
    if args.action in ('build', 'recompile'):
        return
    executable = BUILD / 'sakura.exe'
    # Conservative AOT block dispatch matches the interpreter in the first parity route.
    env['SATRECOMP_NO_FUNCTIONS'] = '1'
    env['SATRECOMP_NO_CALLS'] = '1'
    # The software compositor is the validated original-resolution presentation.
    argv = [executable, '--disc', args.disc.resolve(), '--video', 'software', '--stats']
    if args.action == 'discover':
        env['SATRECOMP_NO_BLOCKS'] = '1'
        argv += ['--record-blocks', WORK / 'blocks.txt']
    else:
        env['SATRECOMP_STRICT_NATIVE'] = '1'
    if args.headless or args.action == 'discover':
        argv += ['--headless', '--frames', str(args.frames)]
    if args.movie:
        argv += ['--movie', args.movie.resolve()]
    argv += ['--backup', WORK / ('discovery-backup.bin' if args.action == 'discover' else 'backup.bin')]
    run(*argv, env=env)


if __name__ == '__main__':
    main()
