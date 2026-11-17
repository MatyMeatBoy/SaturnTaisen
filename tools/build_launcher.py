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
    args=parser.parse_args()
    dependency()
    env=os.environ.copy()
    env['PATH']=str(args.toolchain/'bin')+os.pathsep+env.get('PATH','')
    destination=ROOT/'local/build/sakura'
    build=ROOT/'local/build/launcher'
    version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    values={'GAME_NAME':'SaturnTaisenFirst','GAME_EXE':'sakura','DISC_NAME':'Sakura Wars',
            'DISC_PRODUCT':'GS-9037','DISC_VERSION':'V1.005','APP_ID':'MatyMeatBoy.SaturnTaisenFirst',
            'HOME_ENV':'SATURN_TAISEN_FIRST_HOME','GAME_VERSION':version,'DISCLAIMER':'Proyecto independiente'}
    command=[str(args.toolchain/'bin/cmake.exe'),'-S',str(DEP/'launcher'),'-B',str(build),'-G','Ninja',
             '-DCMAKE_BUILD_TYPE=Release',f'-DCMAKE_CXX_COMPILER={args.toolchain.as_posix()}/bin/clang++.exe',
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
    print(destination/'sakura-launcher.exe')


if __name__=='__main__':
    main()
