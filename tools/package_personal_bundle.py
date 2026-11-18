"""LOCAL PERSONAL archive only: release + owner disc1 + processed HD, never upload."""
import argparse,configparser,hashlib,json,re,zipfile,struct
from pathlib import Path,PurePosixPath
from package_release import digest
ROOT=Path(__file__).resolve().parents[1]
DISC_FILES={'game.cue','Track 01.iso','Track 02.wav'}

def verified_disc_entries(folder,number):
    folder=Path(folder);spec=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if spec.get('translation')!='supplied-v2_1' or spec.get('product')!='GS-9037' or spec.get('version')!='V1.005' or spec.get('disc')!=f'CD-{number}/2' or not spec.get('xdelta_output_checksums_verified'):
        raise ValueError('Requires the verified owner English v2.1 disc')
    if set(spec['outputs'])!=DISC_FILES:raise ValueError('Unexpected files in disc manifest')
    result=[]
    for name in sorted(DISC_FILES):
        file=folder/name
        if file.is_symlink() or not file.is_file() or digest(file)!=spec['outputs'][name]:raise ValueError('Modified translated disc: '+name)
        result.append((f'game/disc{number}/'+name,file))
    return result

def prepared_entries(folder):
    folder=Path(folder);report=json.loads((folder/'prepared-manifest.json').read_text(encoding='utf-8'))
    if report.get('original_pc_files_included') is not False or report.get('backgrounds')!=19:raise ValueError('Not a processed-only HD export')
    result=[];seen=set()
    for row in report['files']:
        name=row['path'];path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name or name in seen:raise ValueError('Unsafe prepared resource path')
        if not (name=='hd-pack.stfp' or name=='portraits/manifest.ini' or re.fullmatch(r'backgrounds/KABE[0-9]{4}\.stfb',name) or re.fullmatch(r'portraits/(?:native-)?[0-9a-f]{64}\.(?:png|bin)',name)):
            raise ValueError('Original or unexpected file in processed pack: '+name)
        file=folder/name
        if file.is_symlink() or not file.is_file() or file.stat().st_size!=row['bytes'] or digest(file)!=row['sha256']:raise ValueError('Modified processed resource')
        seen.add(name);result.append(('hd-resources/'+name,file))
    required={'hd-pack.stfp','portraits/manifest.ini'}
    provenance=json.loads((ROOT/'assets/generated/pc-backgrounds/provenance.json').read_text(encoding='utf-8'))
    required.update('backgrounds/'+row['id']+'.stfb' for row in provenance['backgrounds'])
    portrait=configparser.ConfigParser();portrait.read(folder/'portraits/manifest.ini',encoding='utf-8')
    count=int(portrait['pack']['count'])
    if count!=report['portraits'] or not 1<=count<=394:raise ValueError('Prepared portrait inventory mismatch')
    required.add('portraits/'+portrait['pack']['native_file'])
    for number in range(count):
        for density in (1,2):required.add('portraits/'+portrait[f'portrait-{number}'][f'file{density}'])
    if seen!=required:raise ValueError('Prepared HD inventory is incomplete or contains unused files')
    result.append(('hd-resources/prepared-manifest.json',folder/'prepared-manifest.json'))
    return result,report

def tactical_entries(folder):
    folder=Path(folder);report=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
    if report.get('generated_only') is not True or report.get('original_map_context_included') is not False or report.get('stage_map_signature')!='1CAF3218B4B0F9F0' or report.get('world_origin')!=[656,24] or report.get('logical_size')!=[39,224]:
        raise ValueError('Unverified tactical band identity/anchor')
    rows=report.get('files',[])
    if len(rows)!=1 or rows[0].get('path')!='STAGE01-right-v1.png':raise ValueError('Only the generated band may enter the personal pack')
    row=rows[0];file=folder/row['path']
    if file.is_symlink() or not file.is_file() or file.stat().st_size!=row['bytes'] or digest(file)!=row['sha256']:raise ValueError('Modified tactical extension')
    header=file.read_bytes()[:24]
    if len(header)!=24 or header[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',header[16:24])!=(39,224):raise ValueError('Unexpected tactical image extent')
    return [('art/tactics/'+file.name,file),('art/tactics/provenance.json',folder/'provenance.json')]

def unique_entries(entries):
    """ZIP readers disagree on duplicates; admit one identical resource only."""
    result=[];seen={}
    for name,file in entries:
        path=PurePosixPath(name)
        if not name or path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name or path.as_posix()!=name:
            raise ValueError('Unsafe archive resource path: '+name)
        key=name.casefold()
        if key in seen:
            previous_name,previous=seen[key]
            if previous_name!=name or previous.stat().st_size!=file.stat().st_size or digest(previous)!=digest(file):
                raise ValueError('Conflicting archive resource: '+name)
            continue
        seen[key]=(name,file);result.append((name,file))
    return result

def build(release,prepared,output,tactical=None,owner_root=None):
    owner=Path(owner_root or ROOT).resolve()
    release=Path(release).resolve();output=Path(output).resolve();manifest=json.loads((release/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('game_assets_included') is not False:raise ValueError('Expected the clean code release')
    entries=[]
    for row in manifest['files']:
        file=release/row['path']
        if file.stat().st_size!=row['bytes'] or digest(file)!=row['sha256']:raise ValueError('Modified release file')
        entries.append((row['path'],file))
    entries.append(('manifest.json',release/'manifest.json'))
    entries.extend(verified_disc_entries(owner/'local/prepared/disc1',1))
    hd,report=prepared_entries(prepared);entries.extend(hd)
    if tactical:entries.extend(tactical_entries(tactical))
    for name in ('title.png','presentation-original.png','presentation-enhanced.png'):
        entries.append(('user/art/'+name,owner/'local/build/sakura/art'/name))
    for name,source in (('iris.state','iris-correct-room-3000.state'),('battle.state','chapter1-first-attack.state'),('backup-seed.bin','prebattle-immutable-seed.bin')):
        entries.append(('test-data/'+name,owner/'local/work/sakura'/source))
    defaults='[features]\npreset=custom\npresentation_mode=1\nscene_view=1\ntext_style=0\npc_hd_backgrounds=0\npc_hd_portraits=0\nhd_preload=1\npad_profile=0\nrun_ahead=0\n'
    defaults+='\n[controller_profiles]\n0300fa675e0400008e02000014017801=m30\n'
    generated={'personal-defaults.ini':defaults}
    for label,state in (('Probar escena HD','iris.state'),('Probar combate','battle.state')):
        generated[label+'.bat']=f'@echo off\nsetlocal\nset "SATURN_TAISEN_FIRST_HOME=%~dp0user"\nset "SATRECOMP_HD_STATS=1"\nset "SATRECOMP_STRICT_NATIVE=1"\nif not exist "%~dp0user\\tests\\{state}" mkdir "%~dp0user\\tests\\{state}"\nif not exist "%~dp0user\\settings.ini" copy /y "%~dp0personal-defaults.ini" "%~dp0user\\settings.ini" >nul\nif not exist "%~dp0user\\tests\\{state}\\backup.bin" copy /y "%~dp0test-data\\backup-seed.bin" "%~dp0user\\tests\\{state}\\backup.bin" >nul\nstart "" /d "%~dp0" "%~dp0SaturnTaisenFirst.exe" --play -- --backup "%~dp0user\\tests\\{state}\\backup.bin" --state-load "0:%~dp0test-data\\{state}" --stats\n'
    generated['LEEME-PERSONAL.txt']='PAQUETE PERSONAL DE PRUEBA - NO PUBLICAR\n\nExtrae esta carpeta completa en tu otro PC y abre Jugar.bat. No necesitas instalar Python, MSYS2, compiladores ni SDK; las DLL necesarias van incluidas. Esta build no necesita BIOS externa.\n\nIncluye solo tu disco1 Saturn con ingles v2.1 ya aplicado y el HD procesado. No incluye la instalacion PC, archivos SPR originales ni disco2. Los recursos HD se detectan junto al ejecutable.\n\nPara probar rapido: Probar escena HD.bat o Probar combate.bat. Usan backups de prueba separados. Ver logs.bat abre los diagnosticos. Las partidas normales van en user/saves.\n\nOriginal/Mejorado y visualizacion Original/Zoom siguen disponibles. Maximo16:9. M30 automatico o perfil manual para XInput generico.\n\nEs una prerelease limitada: capitulo1/campana completos, cuerposHD, videosPC y RA siguen pendientes. Las opciones inglesas de dos/tres filas ya tienen textoHD en las rutas verificadas. Tactico16:9 y menus corregidos estan probados en rutas concretas; no todo el combate/capitulo. El release final unificado requerira ambos discos; este paquete de un disco es una prueba privada. RX6900XT requiere prueba fisica en destino.\n'
    entries=unique_entries(entries)
    if set(name.casefold() for name,_ in entries)&set(name.casefold() for name in generated):raise ValueError('Generated archive resource collision')
    summary=dict(version=manifest['version'],source_commit=manifest['source_commit'],personal_only=True,never_publish=True,disc_numbers=[1],translation='English supplied v2.1 already applied',original_pc_files_included=False,processed_backgrounds=report['backgrounds'],processed_portraits=report['portraits'],files=[dict(path=name,bytes=file.stat().st_size,sha256=digest(file)) for name,file in entries])
    summary['generated_files']=[dict(path=name,bytes=len(text.encode('utf-8')),sha256=hashlib.sha256(text.encode('utf-8')).hexdigest()) for name,text in sorted(generated.items())]
    generated['personal-manifest.json']=json.dumps(summary,indent=2)+'\n'
    output.parent.mkdir(parents=True,exist_ok=True);prefix=release.name
    with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as archive:
        for name,file in entries:
            print('Adding',name,flush=True) if name.endswith('.iso') else None
            archive.write(file,prefix+'/'+name)
        for name,text in generated.items():archive.writestr(prefix+'/'+name,text.encode('utf-8'))
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:raise ValueError('ZIP CRC verification failed')
    checksum=digest(output);output.with_suffix(output.suffix+'.sha256').write_text(checksum+'  '+output.name+'\n',encoding='ascii')
    return dict(output=str(output),bytes=output.stat().st_size,sha256=checksum,disc_numbers=[1],processed_hd_only=True,personal_only=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--prepared-hd',type=Path,required=True);p.add_argument('--tactical-extension',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--owner-root',type=Path,help='owner workspace with private disc, previews and test fixtures');a=p.parse_args();print(json.dumps(build(a.release,a.prepared_hd,a.output,a.tactical_extension,a.owner_root),indent=2))
if __name__=='__main__':main()
