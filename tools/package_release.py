"""Create a new portable Windows package; never copy game images, BIOS or saves."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def common_notice(owner_root=None):
    path=Path(owner_root or ROOT)/'local/licenses/recomp-common-28503a2e-NOTICES.md'
    expected='45df29fb27a3fbcdb4fec51aaa7cae96ead79b40b7623e9c6f4642400cbe93d9'
    if not path.is_file():
        url='https://raw.githubusercontent.com/tmcleroy/recomp-common/28503a2e6ae35d9a53c09001c2af07c6d892401c/THIRD_PARTY_NOTICES.md'
        data=urllib.request.urlopen(url,timeout=30).read()
        if hashlib.sha256(data).hexdigest()!=expected:
            raise RuntimeError('Pinned recomp-common notice checksum mismatch')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    if digest(path)!=expected:
        raise RuntimeError('Cached recomp-common notice checksum mismatch')
    return path


def digest(path):
    result=hashlib.sha256()
    with path.open('rb') as source:
        for data in iter(lambda:source.read(1024*1024),b''):
            result.update(data)
    return result.hexdigest()


def generated_backgrounds(folder,pc=False,screen=False,tactical=False):
    """Only manifest-pinned generated art may pass the package's resource gate."""
    folder=Path(folder)
    data=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
    if sum((pc,screen,tactical))>1:raise RuntimeError('Conflicting generated-art classes')
    if tactical and (data.get('generated_only') is not True or data.get('original_map_context_included') is not False or data.get('world_origin')!=[656,24] or data.get('logical_size')!=[39,224]):raise RuntimeError('Unverified generated tactical band')
    result={}
    for row in data['backgrounds']:
        name=row['file']
        if pc and screen:raise RuntimeError('Conflicting generated-art classes')
        pattern=r'STAGE01-right-v1\.png' if tactical else r'(?:OPENING|TITLE|STATUS|PAUSE01|LOADING)-v1\.png' if screen else r'KABE[0-9]{4}-v1\.png' if pc else r'KABE[0-9][01]\.png'
        if not re.fullmatch(pattern,name) or name in result:
            raise RuntimeError('Invalid/duplicate generated background identity')
        file=folder/name
        if file.is_symlink() or not file.is_file() or digest(file)!=row['sha256']:
            raise RuntimeError('Generated background checksum mismatch: '+name)
        with file.open('rb') as stream:header=stream.read(24)
        if header[:8]!=b'\x89PNG\r\n\x1a\n':
            raise RuntimeError('Generated background is not a PNG: '+name)
        if tactical and (len(header)!=24 or header[12:16]!=b'IHDR' or struct.unpack('>II',header[16:24])!=(39,224)):
            raise RuntimeError('Unexpected generated tactical image extent')
        result[name]=file
    if not result:
        raise RuntimeError('Empty generated background manifest')
    return result


def package(destination,toolchain,archive=True,runtime=None,owner_root=None,build_dir=None,controller_mapper=None):
    owner=Path(owner_root or ROOT).resolve()
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode('utf-8').split('\0'))
    destination=destination.resolve()
    destination.mkdir(parents=True,exist_ok=False)
    build=Path(build_dir).resolve() if build_dir else owner/'local/build/sakura'
    executables={'sakura-launcher.exe':'SaturnTaisenFirst.exe','sakura.exe':'sakura.exe',
                 'import-saves.exe':'import-saves.exe'}
    for source,name in executables.items():
        selected=Path(runtime) if runtime is not None and source=='sakura.exe' else build/source
        shutil.copy2(selected,destination/name)
    if controller_mapper is not None:
        shutil.copy2(Path(controller_mapper),destination/'Mapear M30.exe')
    # Resolve the actual PE imports, including dependencies of toolchain DLLs.
    available={p.name.casefold():p for p in (toolchain/'bin').glob('*.dll')}
    pending=list(destination.glob('*.exe'))
    seen=set()
    copied=[]
    env=os.environ.copy()
    env['PATH']=str(toolchain/'bin')+os.pathsep+env.get('PATH','')
    system=Path(os.environ.get('SystemRoot','C:/Windows'))/'System32'
    while pending:
        file=pending.pop()
        text=subprocess.check_output([str(toolchain/'bin/llvm-readobj.exe'),'--coff-imports',str(file)],
                                     env=env,text=True,encoding='utf-8')
        for name in re.findall(r'^\s+Name: ([^\r\n]+\.dll)\s*$',text,re.MULTILINE|re.IGNORECASE):
            key=name.casefold()
            if key in seen:
                continue
            seen.add(key)
            if key in available:
                source=available[key]
                target=destination/source.name
                shutil.copy2(source,target)
                pending.append(target)
                copied.append(source.name)
            elif not (system/name).is_file() and not key.startswith(('api-ms-','ext-ms-')):
                raise RuntimeError(f'Unresolved non-system DLL: {name}')
    licenses=destination/'licenses'
    licenses.mkdir()
    for name in ['LICENSE','THIRD_PARTY_NOTICES.md','README.md','VERSION']:
        shutil.copy2(ROOT/name,destination/name)
    for name in ['SDL3','zlib','libc++','libunwind','libiconv','compiler-rt','llvm-libs']:
        source=toolchain/'share/licenses'/name
        if source.is_dir():
            shutil.copytree(source,licenses/name)
    for name,source in {
        'satrecomp-NOTICES.md':owner/'local/deps/satrecomp/THIRD_PARTY_NOTICES.md',
        'recomp-common-NOTICES.md':common_notice(owner),
        'Inter-OFL.txt':owner/'local/build/launcher/_deps/inter-src/LICENSE.txt',
        'Dear-ImGui-MIT.txt':owner/'local/build/launcher/_deps/imgui-src/LICENSE.txt',
        'Python-PSF.txt':Path(sys.base_prefix)/'LICENSE.txt',
        'PyInstaller-COPYING.txt':owner/'local/venv-release/Lib/site-packages/pyinstaller-6.22.3.dist-info/licenses/COPYING.txt',
    }.items():
        if not source.is_file():
            raise RuntimeError(f'Missing required license: {source}')
        shutil.copy2(source,licenses/name)
    # Only original project sources and reproducible patches, no generated code.
    for folder,patterns in {'tools':['*.py','controller_mapper.cpp','controller_capture.h'],'patches':['*.patch'],'config':['*.json'],
                            'tests':['*.py','*.cpp','*.movie'],'tests/native':['*.cpp','CMakeLists.txt'],
                            'games/sakura':['game.cfg'],'docs/superpowers/specs':['*.md'],
                            'docs/superpowers/plans':['*.md'],
                            'docs':['PENDIENTES.md','HANDOFF.md','ESTADO_ACTUAL.md'],
                            'docs/research':['*.md','*.json'],'docs/releases':['*.md','*-validation.json']}.items():
        target=destination/folder
        target.mkdir(parents=True,exist_ok=True)
        for pattern in patterns:
            for source in (ROOT/folder).glob(pattern):
                if source.relative_to(ROOT).as_posix() not in tracked:continue
                shutil.copy2(source,target/source.name)
    art_source=ROOT/'assets/generated/backgrounds'
    if not art_source.is_dir():art_source=ROOT/'art/backgrounds'
    generated=generated_backgrounds(art_source)
    art=destination/'art/backgrounds'
    art.mkdir(parents=True)
    allowed_art={}
    for name,source in generated.items():
        shutil.copy2(source,art/name)
        allowed_art['art/backgrounds/'+name]=digest(source)
    for name in ('provenance.json','PROMPTS.md'):
        source=art_source/name
        if source.is_file():shutil.copy2(source,art/name)
    pc_art_source=ROOT/'assets/generated/pc-backgrounds'
    if pc_art_source.is_dir():
        pc_art=destination/'art/pc-backgrounds';pc_art.mkdir(parents=True)
        for name,source in generated_backgrounds(pc_art_source,pc=True).items():
            shutil.copy2(source,pc_art/name);allowed_art['art/pc-backgrounds/'+name]=digest(source)
        shutil.copy2(pc_art_source/'provenance.json',pc_art/'provenance.json')
    screen_source=ROOT/'assets/generated/screen-backgrounds'
    if screen_source.is_dir():
        screen_art=destination/'art/screen-backgrounds';screen_art.mkdir(parents=True)
        for name,source in generated_backgrounds(screen_source,screen=True).items():
            shutil.copy2(source,screen_art/name);allowed_art['art/screen-backgrounds/'+name]=digest(source)
        shutil.copy2(screen_source/'provenance.json',screen_art/'provenance.json')
    tactical_source=ROOT/'assets/generated/tactical-extensions'
    if tactical_source.is_dir():
        tactical_art=destination/'art/tactics';tactical_art.mkdir(parents=True)
        for name,source in generated_backgrounds(tactical_source,tactical=True).items():
            shutil.copy2(source,tactical_art/name);allowed_art['art/tactics/'+name]=digest(source)
        shutil.copy2(tactical_source/'provenance.json',tactical_art/'provenance.json')
    (destination/'Jugar.bat').write_text('@echo off\nsetlocal\nset "SATURN_TAISEN_FIRST_HOME=%~dp0user"\nset "SATRECOMP_HD_STATS=1"\nset "SATRECOMP_BACKGROUND_STATS=1"\nif not exist "%~dp0user" mkdir "%~dp0user"\nif not exist "%~dp0user\\settings.ini" if exist "%~dp0personal-defaults.ini" copy /y "%~dp0personal-defaults.ini" "%~dp0user\\settings.ini" >nul\nstart "" /d "%~dp0" "%~dp0SaturnTaisenFirst.exe"\n',encoding='ascii')
    (destination/'Ver logs.bat').write_text('@echo off\nif not exist "%~dp0user\\logs" mkdir "%~dp0user\\logs"\nstart "" "%~dp0user\\logs"\n',encoding='ascii')
    (destination/'portable.txt').write_text('',encoding='ascii')
    version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    (destination/'LEEME.md').write_text(f'''# SaturnTaisenFirst {version} · Desarrollo

1. Descomprime la carpeta en un lugar donde puedas guardar archivos.
2. Abre **SaturnTaisenFirst.exe** y elige tu archivo `.cue` (con sus pistas al lado) o `.iso` de Sakura Wars 1 para Saturn.
3. Para inglés, utiliza tus discos ya parcheados con la traducción v2.1. No se incluyen discos, BIOS ni parches binarios.
4. La captura del título se prepara localmente a partir de tu disco. No necesita descargar imágenes.
5. Pulsa **Jugar**. F11 cambia pantalla completa; Esc/F1 o Start+Select abre los ajustes.
6. Elige presentación Original o Mejorada en el launcher y al iniciar el juego. La fuente nítida se puede cambiar en ajustes; su disponibilidad depende de los recursos de la traducción y la fuente del sistema.

El juego usa exclusivamente escala entera, sin suavizado, y un marco adaptable. Los dos discos se pueden seleccionar manualmente; el cambio automático de disco aún está pendiente.

El modo mejorado amplía en enteros las escenas reconocidas sobre fondos decorativos generados. Conserva la composición original cuando no reconoce la escena. Los fondos generados son preliminares. La ejecución PC y su traducción siguen pendientes. El mod HD Saturn puede usar tus fondos y un pack local de retratos PC emparejados; requiere tus recursos extraídos. Los cuerpos HD completos y las extensiones tácticas de mapa siguen en desarrollo.

**Opciones de desarrollo:** Pantalla → Visualización de escena conserva Original o permite Zoom. MOD HD → Precargar mod HD al iniciar prepara los recursos habilitados antes de jugar. Mandos → Perfil de mando ofrece Automático, Estándar SDL y M30 / Saturn 6 botones. El modo mejorado se limita a16:9 máximo.

**Partidas:** importa desde la sección Tus partidas. Se crea una copia separada y puedes activarla o volver a tu partida habitual. Los originales no se modifican. Guarda el nombre original al importar un archivo individual de SSF.

Esta versión no certifica toda la campaña ni todos los mandos. Consulta las notas de versión y la validación. RetroAchievements y el mod HD completo siguen pendientes.

`user/` contiene tus partidas y ajustes en este modo portátil. No la borres al actualizar; conserva una copia antes de sustituir el programa.
''',encoding='utf-8',newline='\n')
    forbidden={'.iso','.cue','.bin','.bup','.sro','.xdelta','.state','.png','.jpg','.wav'}
    files=[]
    for file in sorted(destination.rglob('*')):
        if not file.is_file():
            continue
        relative=file.relative_to(destination).as_posix()
        generated_match=relative in allowed_art and digest(file)==allowed_art[relative]
        if file.suffix.casefold() in forbidden and not generated_match:
            raise RuntimeError(f'Unexpected game/resource file in package: {file}')
        files.append({'path':file.relative_to(destination).as_posix(),'bytes':file.stat().st_size,'sha256':digest(file)})
    manifest={'version':(ROOT/'VERSION').read_text().strip(),
              'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'source_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
              'dlls':sorted(copied),'files':files,'game_assets_included':False,
              'generated_backgrounds':allowed_art}
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    if archive:
        target=destination.parent/(destination.name+'.zip')
        with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=7) as output:
            for file in sorted(destination.rglob('*')):
                if file.is_file():
                    output.write(file,(Path(destination.name)/file.relative_to(destination)).as_posix())
        target.with_suffix('.zip.sha256').write_text(digest(target)+'  '+target.name+'\n',encoding='ascii')
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='new directory; existing targets are refused')
    parser.add_argument('--toolchain',type=Path,default=Path('C:/msys64/clang64'))
    parser.add_argument('--no-archive',action='store_true')
    parser.add_argument('--runtime',type=Path,help='isolated candidate executable; avoids replacing another tester runtime')
    parser.add_argument('--owner-root',type=Path,help='owner workspace with private build dependencies and licenses; sources remain in this checkout')
    parser.add_argument('--build-dir',type=Path,help='isolated directory with launcher and importer binaries')
    parser.add_argument('--controller-mapper',type=Path,help='optional verified portable controller reporting utility')
    args=parser.parse_args()
    result=package(args.output,args.toolchain,not args.no_archive,args.runtime,args.owner_root,args.build_dir,args.controller_mapper)
    print(json.dumps({'output':str(args.output.resolve()),'files':len(result['files']),'dlls':result['dlls']}))


if __name__=='__main__':
    main()
