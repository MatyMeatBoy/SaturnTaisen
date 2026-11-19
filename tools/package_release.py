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
    episode_pairs = {}
    episode_surrounds = {}
    for row in data['backgrounds']:
        name=row['file']
        if pc and screen:raise RuntimeError('Conflicting generated-art classes')
        pattern=r'STAGE01-right-v1\.png' if tactical else r'(?:OPENING|TITLE|STATUS|PAUSE01|LOADING)-v1\.png' if screen else r'KABE[0-9]{4}-v1\.png' if pc else r'KABE[0-9][01]\.png'
        episode_side = screen and re.fullmatch(r'(EPISODE(?:0[1-9]|10))-(left|right)-v1\.png', name)
        episode_surround = screen and re.fullmatch(r'(EPISODE(?:0[1-9]|10))-surround-v2\.png', name)
        if (not episode_side and not episode_surround and not re.fullmatch(pattern, name)) or name in result:
            raise RuntimeError('Invalid/duplicate generated background identity')
        file=folder/name
        if file.is_symlink() or not file.is_file() or digest(file)!=row['sha256']:
            raise RuntimeError('Generated background checksum mismatch: '+name)
        with file.open('rb') as stream:header=stream.read(26)
        if header[:8]!=b'\x89PNG\r\n\x1a\n':
            raise RuntimeError('Generated background is not a PNG: '+name)
        if tactical and (len(header)<24 or header[12:16]!=b'IHDR' or struct.unpack('>II',header[16:24])!=(39,224)):
            raise RuntimeError('Unexpected generated tactical image extent')
        if episode_side and (
            data.get('source_pixels_included') is not False
            or row.get('logical_grid') != [39, 224]
            or not re.fullmatch(r'[0-9A-F]{16}', row.get('palette_fnv', ''))
            or len(header) != 26
            or header[12:16] != b'IHDR'
            or struct.unpack('>II', header[16:24]) != (39, 224)
            or header[24:26] != bytes((8, 6))
        ):
            raise RuntimeError('Unexpected generated episode side: ' + name)
        if episode_side:
            episode, side = episode_side.groups()
            episode_pairs.setdefault(episode, {})[side] = row['palette_fnv']
        if episode_surround:
            if (
                data.get('source_pixels_included') is not False
                or row.get('logical_grid') != [640, 360]
                or row.get('native_center') != [160, 68, 320, 224]
                or not re.fullmatch(r'[0-9A-F]{16}', row.get('palette_fnv', ''))
                or len(header) != 26
                or header[12:16] != b'IHDR'
                or struct.unpack('>II', header[16:24]) != (640, 360)
                or header[24:26] != bytes((8, 6))
            ):
                raise RuntimeError('Unexpected generated episode surround: ' + name)
            from PIL import Image
            with Image.open(file) as image:
                if any(channel.getbbox() for channel in image.crop((160, 68, 480, 292)).split()):
                    raise RuntimeError('Generated episode surround contains center pixels: ' + name)
            episode_surrounds[episode_surround[1]] = row['palette_fnv']
        result[name]=file
    for episode, sides in episode_pairs.items():
        if set(sides) != {'left', 'right'} or sides['left'] != sides['right']:
            raise RuntimeError('Incomplete or mismatched generated episode side pair: ' + episode)
    if episode_surrounds:
        expected = {f'EPISODE{number:02}' for number in range(1, 11)}
        if set(episode_surrounds) != expected or any(
            episode_pairs.get(episode, {}).get('left') != fingerprint
            for episode, fingerprint in episode_surrounds.items()
        ):
            raise RuntimeError('Incomplete or mismatched generated episode surrounds')
    if not result:
        raise RuntimeError('Empty generated background manifest')
    return result


def release_file_manifest(destination, allowed_art, allowed_patches):
    """Validate the staged public tree and record the exact bytes that will ship."""
    protected_suffixes = {
        '.iso', '.cue', '.bin', '.img', '.mdf', '.mds', '.chd', '.cdd', '.ccd', '.bup',
        '.sro', '.xdelta', '.state', '.png', '.jpg', '.jpeg', '.bmp', '.wav', '.flac', '.mp3',
        '.mpg', '.mpeg', '.spr', '.stfb', '.stfp', '.zip', '.7z', '.rar',
    }
    private_folders = {'data/game', 'data/hd-resources', 'data/user'}
    allowed = {f'data/{path}': checksum for path, checksum in (allowed_art | allowed_patches).items()}
    files = []
    for file in sorted(destination.rglob('*')):
        relative = file.relative_to(destination).as_posix()
        normalized = relative.casefold()
        if file.is_symlink() or any(normalized == folder or normalized.startswith(folder + '/')
                                    for folder in private_folders):
            raise RuntimeError(f'Unexpected game/resource file in package: {relative}')
        if not file.is_file():
            continue
        checksum = digest(file)
        if relative in allowed:
            if allowed[relative] != checksum:
                raise RuntimeError(f'Approved package file checksum mismatch: {relative}')
        elif (file.suffix.casefold() in protected_suffixes or normalized.startswith('roms/')
              and relative != 'roms/LEEME.txt'):
            raise RuntimeError(f'Unexpected game/resource file in package: {relative}')
        files.append({'path': relative, 'bytes': file.stat().st_size, 'sha256': checksum})
    missing = allowed.keys() - {row['path'] for row in files}
    if missing:
        raise RuntimeError(f'Missing approved package files: {", ".join(sorted(missing))}')
    return files


def package(destination,toolchain,archive=True,runtime=None,owner_root=None,build_dir=None,controller_mapper=None,video_patches=None):
    owner=Path(owner_root or ROOT).resolve()
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode('utf-8').split('\0'))
    destination=destination.resolve()
    destination.mkdir(parents=True,exist_ok=False)
    # The release root shows only what the player touches: SaturnTaisen.exe (the launcher, linked statically so
    # it needs nothing beside it), roms/ for their files and recomp-launcher.json for frontends. Everything else
    # (game, helpers, DLLs, licences, prepared discs, HD pack, saves) is in data/, where the launcher looks.
    app=destination/'data';app.mkdir()
    build=Path(build_dir).resolve() if build_dir else owner/'local/build/sakura'
    shutil.copy2(build/'sakura-launcher.exe',destination/'SaturnTaisen.exe')
    executables={'sakura.exe':'sakura.exe','import-saves.exe':'import-saves.exe','preparar-juego.exe':'preparar-juego.exe'}
    for source,name in executables.items():
        selected=Path(runtime) if runtime is not None and source=='sakura.exe' else build/source
        shutil.copy2(selected,app/name)
    if controller_mapper is not None:
        shutil.copy2(Path(controller_mapper),app/'Mapear M30.exe')
    # Resolve the actual PE imports, including dependencies of toolchain DLLs.
    available={p.name.casefold():p for p in (toolchain/'bin').glob('*.dll')}
    pending=list(app.glob('*.exe'))
    # The launcher at the top is static: it must import system libraries only (checked below).
    starter=destination/'SaturnTaisen.exe'
    pending.append(starter)
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
            if key in available and file==starter:
                raise RuntimeError(f'The launcher at the top must be static, but it imports {name}')
            if key in available:
                source=available[key]
                target=app/source.name
                shutil.copy2(source,target)
                pending.append(target)
                copied.append(source.name)
            elif not (system/name).is_file() and not key.startswith(('api-ms-','ext-ms-')):
                raise RuntimeError(f'Unresolved non-system DLL: {name}')
    licenses=app/'licenses'
    licenses.mkdir()
    for name in ['LICENSE','THIRD_PARTY_NOTICES.md','VERSION']:
        shutil.copy2(ROOT/name,app/name)
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
    # Setup tools the helper runs on the player's PC, with their licenses.
    helpers=app/'herramientas';helpers.mkdir()
    for name,source,notice,licence in (
        ('xdelta3.exe',owner/'local/tools/xdelta3-3.2.2/xdelta3-3.2.2-windows-x86_64/xdelta3.exe','xdelta3-Apache-2.0.txt',owner/'local/licenses/xdelta3-LICENSE.txt'),
        ('unshield.exe',owner/'local/build/unshield/src/unshield.exe','unshield-MIT.txt',owner/'.research/upstream/twogood--unshield/LICENSE')):
        for file in (source,licence):
            if not file.is_file():raise RuntimeError(f'Missing setup tool or license: {file}')
        shutil.copy2(source,helpers/name);shutil.copy2(licence,licenses/notice)
    # Language patches: differences only, each pinned by parches.json. The video layer is a release asset.
    patch_manifest=json.loads((ROOT/'parches/parches.json').read_text(encoding='utf-8'))
    patch_target=app/'parches';patch_target.mkdir()
    allowed_patches={}
    for name in ('parches.json','CREDITOS.md'):shutil.copy2(ROOT/'parches'/name,patch_target/name)
    for record in patch_manifest['discs'].values():
        for layer in ('english','spanish','videos'):
            if layer=='videos' and not video_patches:continue
            entry=record[layer];source=(Path(video_patches) if layer=='videos' else ROOT/'parches')/entry['patch']
            if not source.is_file() or digest(source)!=entry['patch_sha256']:
                raise RuntimeError('Language patch missing or different from parches.json: '+entry['patch'])
            shutil.copy2(source,patch_target/entry['patch']);allowed_patches['parches/'+entry['patch']]=entry['patch_sha256']
    shutil.copy2(ROOT/'recomp-launcher.json',destination/'recomp-launcher.json')
    inputs=destination/'roms';inputs.mkdir()
    # What the programs read at run time (the HD recipe, the game's configuration). The sources, patches, tests and
    # notes are not copied: CODIGO-FUENTE.txt names the repository and the exact commit this package was built from
    # (GPL-3.0 section 6(d): the Corresponding Source offered from a network server).
    for folder,patterns in {'config':['*.json'],'games/sakura':['game.cfg']}.items():
        target=app/folder
        target.mkdir(parents=True,exist_ok=True)
        for pattern in patterns:
            for source in (ROOT/folder).glob(pattern):
                if source.relative_to(ROOT).as_posix() not in tracked:continue
                shutil.copy2(source,target/source.name)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    (app/'CODIGO-FUENTE.txt').write_text(
        'SaturnTaisen es software libre (GPL-3.0). Su codigo fuente completo, con los parches del SDK, las\n'
        'herramientas y los tests, esta en:\n\n  https://github.com/MatyMeatBoy/SaturnTaisen\n\n'
        f'Este paquete se construyo desde el commit {commit}:\n'
        f'  https://github.com/MatyMeatBoy/SaturnTaisen/tree/{commit}\n\n'
        'Las licencias de terceros estan en la carpeta licenses.\n',encoding='ascii',newline='\r\n')
    art_source=ROOT/'assets/generated/backgrounds'
    if not art_source.is_dir():art_source=ROOT/'art/backgrounds'
    generated=generated_backgrounds(art_source)
    art=app/'art/backgrounds'
    art.mkdir(parents=True)
    allowed_art={}
    for name,source in generated.items():
        shutil.copy2(source,art/name)
        allowed_art['art/backgrounds/'+name]=digest(source)
    for name in ('provenance.json','PROMPTS.md'):
        source=art_source/name
        if source.is_file():shutil.copy2(source,art/name)
    for source_name, target_name, art_class in (
        ('pc-backgrounds', 'pc-backgrounds', 'pc'),
        ('screen-backgrounds', 'screen-backgrounds', 'screen'),
        ('tactical-extensions', 'tactics', 'tactical'),
    ):
        source_folder = ROOT / 'assets/generated' / source_name
        images = generated_backgrounds(source_folder, **{art_class: True})
        if art_class == 'screen':
            episode_sides = {f'EPISODE{episode:02d}-{side}-v1.png'
                             for episode in range(1, 11) for side in ('left', 'right')}
            if missing := episode_sides - images.keys():
                raise RuntimeError(f'Missing generated episode sides: {", ".join(sorted(missing))}')
        art_folder = app / 'art' / target_name
        art_folder.mkdir()
        for name, source in images.items():
            shutil.copy2(source, art_folder / name)
            allowed_art[f'art/{target_name}/{name}'] = digest(source)
        shutil.copy2(source_folder / 'provenance.json', art_folder / 'provenance.json')
    # One profile however the game is started: the launcher's own portable folder (user/SaturnTaisen). A profile an
    # earlier release kept directly in user/ is still used, so its saves and settings are not left behind.
    (app/'portable.txt').write_text('',encoding='ascii')
    version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    (inputs/'LEEME.txt').write_text(f'''SaturnTaisen {version}

Solo necesitas **tus propios archivos**: los dos discos originales de Sakura Taisen para Saturn (Japón, `.cue` con sus pistas) y, si quieres el mod HD, la imagen del disco de la edición de PC (`.mdf` o `.iso`). Todo lo demás viene aquí: no hace falta instalar ni descargar nada.

1. Descomprime la carpeta en un lugar donde puedas guardar archivos (unos 3 GB libres).
2. Abre **SaturnTaisen.exe**.
3. Copia en esta carpeta `roms` tus tres archivos (los dos discos de Saturn y, para el mod HD, la imagen de PC): el launcher los reconoce y prepara el juego solo (unos minutos, una sola vez). También puedes elegirlos en **Preparar juego**.
4. Pulsa **Jugar**. F11 cambia pantalla completa; Esc/F1 o Start+Select abre los ajustes.

**Idiomas.** «Inglés v0.1 Taisen» y «Español v0.1 Taisen» se aplican sobre una copia de tus discos; cada paso se comprueba con SHA-256 y tus archivos solo se leen. El idioma se cambia en el launcher al instante. Créditos de la traducción inglesa y detalle de las capas: `parches/CREDITOS.md`. En español siguen en inglés los rótulos de episodio, la pantalla LOADING, el menú de extras y los subtítulos de vídeo.

**Mod HD.** Con tu edición de PC se prepara una sola vez todo el material HD (imágenes de fondos, escenas, eventos, CG, mapas, unidades, personajes, menús y las películas) en `data/hd-resources`, solo en tu PC y nunca compartido. Hoy ya se ven 19 fondos y los retratos HD; el resto se irá activando en próximas versiones sin volver a preparar nada.

**Presentación.** Escala entera sin suavizado. Original conserva la composición de Saturn; Mejorada recompone las escenas reconocidas hasta 16:9 y vuelve a la original cuando no reconoce la escena. Los fondos generados son preliminares.

**Partidas.** Importa desde la sección Tus partidas: se crea una copia separada y los originales no se modifican.

**Otros frontends.** `recomp-launcher.json` describe la entrada única (`SaturnTaisen.exe`, el único programa a la vista) y la preparación por línea de comandos (`data/preparar-juego.exe`).

Esta versión no certifica toda la campaña ni todos los mandos; el cambio automático de disco y RetroAchievements siguen pendientes. Consulta las notas de versión.

En la carpeta solo verás `SaturnTaisen.exe`, `roms` y `data`. Dentro de `data`, `user/` contiene tus partidas, ajustes y `logs/`, y `game/` y `hd-resources/` lo ya preparado. No las borres al actualizar: puedes descomprimir una versión nueva encima y no se rehace nada que siga vigente.
''',encoding='utf-8',newline='\n')
    files=release_file_manifest(destination,allowed_art,allowed_patches)
    manifest={'version':(ROOT/'VERSION').read_text().strip(),
              'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'source_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
              'dlls':sorted(copied),'files':files,'game_assets_included':False,
              'generated_backgrounds':allowed_art}
    (app/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
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
    parser.add_argument('--video-patches',type=Path,help='folder with the optional subtitled-video layer listed in parches/parches.json')
    args=parser.parse_args()
    result=package(args.output,args.toolchain,not args.no_archive,args.runtime,args.owner_root,args.build_dir,args.controller_mapper,args.video_patches)
    print(json.dumps({'output':str(args.output.resolve()),'files':len(result['files']),'dlls':result['dlls']}))


if __name__=='__main__':
    main()
