"""Create a new portable Windows package; never copy game images, BIOS or saves."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def common_notice():
    path=ROOT/'local/licenses/recomp-common-28503a2e-NOTICES.md'
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


def generated_backgrounds(folder):
    """Only manifest-pinned generated art may pass the package's resource gate."""
    folder=Path(folder)
    data=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
    result={}
    for row in data['backgrounds']:
        name=row['file']
        if not re.fullmatch(r'KABE[0-9][01]\.png',name) or name in result:
            raise RuntimeError('Invalid/duplicate generated background identity')
        file=folder/name
        if file.is_symlink() or not file.is_file() or digest(file)!=row['sha256']:
            raise RuntimeError('Generated background checksum mismatch: '+name)
        if file.read_bytes()[:8]!=b'\x89PNG\r\n\x1a\n':
            raise RuntimeError('Generated background is not a PNG: '+name)
        result[name]=file
    if not result:
        raise RuntimeError('Empty generated background manifest')
    return result


def package(destination,toolchain,archive=True):
    destination=destination.resolve()
    destination.mkdir(parents=True,exist_ok=False)
    build=ROOT/'local/build/sakura'
    executables={'sakura-launcher.exe':'SaturnTaisenFirst.exe','sakura.exe':'sakura.exe',
                 'import-saves.exe':'import-saves.exe'}
    for source,name in executables.items():
        shutil.copy2(build/source,destination/name)
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
        'satrecomp-NOTICES.md':ROOT/'local/deps/satrecomp/THIRD_PARTY_NOTICES.md',
        'recomp-common-NOTICES.md':common_notice(),
        'Inter-OFL.txt':ROOT/'local/build/launcher/_deps/inter-src/LICENSE.txt',
        'Dear-ImGui-MIT.txt':ROOT/'local/build/launcher/_deps/imgui-src/LICENSE.txt',
        'Python-PSF.txt':Path(sys.base_prefix)/'LICENSE.txt',
        'PyInstaller-COPYING.txt':ROOT/'local/venv-release/Lib/site-packages/pyinstaller-6.22.3.dist-info/licenses/COPYING.txt',
    }.items():
        if not source.is_file():
            raise RuntimeError(f'Missing required license: {source}')
        shutil.copy2(source,licenses/name)
    # Only original project sources and reproducible patches, no generated code.
    for folder,patterns in {'tools':['*.py'],'patches':['*.patch'],'config':['*.json'],
                            'tests':['*.py','*.cpp','*.movie'],'tests/native':['*.cpp','CMakeLists.txt'],
                            'games/sakura':['game.cfg'],'docs/superpowers/specs':['*.md'],
                            'docs/superpowers/plans':['*.md'],
                            'docs/research':['*.md','*.json'],'docs/releases':['*.md']}.items():
        target=destination/folder
        target.mkdir(parents=True,exist_ok=True)
        for pattern in patterns:
            for source in (ROOT/folder).glob(pattern):
                shutil.copy2(source,target/source.name)
    generated=generated_backgrounds(ROOT/'assets/generated/backgrounds')
    art=destination/'art/backgrounds'
    art.mkdir(parents=True)
    allowed_art={}
    for name,source in generated.items():
        shutil.copy2(source,art/name)
        allowed_art['art/backgrounds/'+name]=digest(source)
    for name in ('provenance.json','PROMPTS.md'):
        source=ROOT/'assets/generated/backgrounds'/name
        if source.is_file():shutil.copy2(source,art/name)
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

El modo mejorado amplía en enteros las escenas reconocidas sobre fondos decorativos generados. Conserva la composición original cuando no reconoce la escena. Los fondos generados son preliminares. La ejecución PC, su traducción y el pack HD de recursos PC están en desarrollo y no forman parte de las funciones jugables verificadas.

**Partidas:** importa desde la sección Tus partidas. Se crea una copia separada y puedes activarla o volver a tu partida habitual. Los originales no se modifican. Guarda el nombre original al importar un archivo individual de SSF.

Esta versión no certifica toda la campaña ni todos los mandos. Consulta las notas de versión y la validación. RA, packs HD y otras funciones pendientes no se presentan como disponibles.

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
    args=parser.parse_args()
    result=package(args.output,args.toolchain,not args.no_archive)
    print(json.dumps({'output':str(args.output.resolve()),'files':len(result['files']),'dlls':result['dlls']}))


if __name__=='__main__':
    main()
