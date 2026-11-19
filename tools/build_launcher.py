"""Build the Sakura launcher beside the locally generated AOT runtime."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

from build_runtime import ROOT, DEP, dependency


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--toolchain',type=Path,default=Path('C:/msys64/clang64'))
    parser.add_argument('--title-image',type=Path,help='local screenshot of the title screen; never uploaded')
    parser.add_argument('--with-importer',action='store_true')
    parser.add_argument('--with-setup',action='store_true',help='also freeze tools/taisen_setup.py as preparar-juego.exe')
    parser.add_argument('--build-dir',type=Path,help='isolated CMake directory (default local/build/launcher)')
    parser.add_argument('--output-dir',type=Path,help='isolated output directory (default local/build/sakura)')
    args=parser.parse_args()
    dependency()
    env=os.environ.copy()
    env['PATH']=str(args.toolchain/'bin')+os.pathsep+env.get('PATH','')
    destination=(args.output_dir or ROOT/'local/build/sakura').resolve()
    build=(args.build_dir or ROOT/'local/build/launcher').resolve()
    version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    values={'GAME_NAME':'SaturnTaisen','GAME_EXE':'sakura','DISC_NAME':'Sakura Wars',
            'DISC_PRODUCT':'GS-9037','DISC_VERSION':'V1.005','APP_ID':'MatyMeatBoy.SaturnTaisen',
            'HOME_ENV':'SATURN_TAISEN_FIRST_HOME','GAME_VERSION':version,'DISCLAIMER':'Proyecto independiente'}
    command=[str(args.toolchain/'bin/cmake.exe'),'-S',str(DEP/'launcher'),'-B',str(build),'-G','Ninja',
             '-DCMAKE_BUILD_TYPE=Release','-DLAUNCHER_STATIC=ON',f'-DCMAKE_CXX_COMPILER={args.toolchain.as_posix()}/bin/clang++.exe',
             f'-DCMAKE_RUNTIME_OUTPUT_DIRECTORY:PATH={destination.as_posix()}',
             f'-DGAME_DIR:PATH={(ROOT/"games/sakura").as_posix()}',
             *[f'-D{key}:STRING={value}' for key,value in values.items()]]
    subprocess.run(command,cwd=ROOT,env=env,check=True)
    subprocess.run([str(args.toolchain/'bin/cmake.exe'),'--build',str(build),'--parallel','4'],cwd=ROOT,env=env,check=True)
    if args.title_image:
        data=args.title_image.read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            parser.error('--title-image must be a PNG screenshot')
        artwork=destination/'art'
        artwork.mkdir(parents=True,exist_ok=True)
        if args.title_image.resolve()!=(artwork/'title.png').resolve():
            shutil.copyfile(args.title_image,artwork/'title.png')
    if args.with_importer:
        python=ROOT/'local/venv-release/Scripts/python.exe'
        if not python.is_file():
            parser.error('Create local/venv-release and install PyInstaller 6.22.3 there first')
        subprocess.run([str(python),'-m','PyInstaller','--noconfirm','--onefile','--console','--name','import-saves',
                        '--distpath',str(destination),'--workpath',str(ROOT/'local/work/pyinstaller-import'),
                        '--specpath',str(ROOT/'local/work/pyinstaller-import'),str(ROOT/'tools/import_saves.py')],
                       cwd=ROOT,env=env,check=True)
    if args.with_setup:
        python=ROOT/'local/venv-release/Scripts/python.exe'
        if not python.is_file():
            parser.error('Create local/venv-release and install PyInstaller 6.22.3 there first')
        import PIL  # the HD portrait step needs Pillow; the frozen helper takes it from this interpreter
        packages=Path(PIL.__file__).resolve().parents[1]
        hidden=[item for name in ('hd_matching','PIL.Image','PIL.ImageChops','PIL.ImageStat','PIL.PngImagePlugin') for item in ('--hidden-import',name)]
        subprocess.run([str(python),'-m','PyInstaller','--noconfirm','--onefile','--console','--name','preparar-juego',
                        '--paths',str(packages),'--paths',str(ROOT/'tools'),*hidden,'--distpath',str(destination),
                        '--workpath',str(ROOT/'local/work/pyinstaller-preparar'),'--specpath',str(ROOT/'local/work/pyinstaller-preparar'),
                        str(ROOT/'tools/taisen_setup.py')],cwd=ROOT,env=env,check=True)
    print(destination/'sakura-launcher.exe')


if __name__=='__main__':
    main()
