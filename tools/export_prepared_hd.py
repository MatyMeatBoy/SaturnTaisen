"""Export only validated, processed HD assets; no original PC SPR files are copied."""
import argparse,configparser,hashlib,json,os,re,shutil,struct,subprocess,tempfile
from pathlib import Path
from hd_matching import fnv64,load_image
ROOT=Path(__file__).resolve().parents[1]
SOURCE_BYTES=5505346
SOURCE_HASH=17275614850567186526

def export_prepared(pc_root,portrait_pack,output,runtime):
    pc_root=Path(pc_root).resolve();portrait_pack=Path(portrait_pack).resolve();output=Path(output).resolve()
    if output.exists():raise ValueError('Prepared output already exists; choose a new folder')
    manifest=portrait_pack/'manifest.ini';ini=configparser.ConfigParser();ini.read(manifest,encoding='utf-8')
    count=int(ini['pack']['count'])
    if not 1<=count<=394 or int(ini['pack']['source_bytes'])!=SOURCE_BYTES or int(ini['pack']['source_hash'])!=SOURCE_HASH:
        raise ValueError('Unknown portrait source or count')
    source=(pc_root/'SAKURA1/SYSTEM/KAO.SPR').read_bytes()
    if len(source)!=SOURCE_BYTES or fnv64(source)!=SOURCE_HASH:raise ValueError('Unknown original portrait file')
    portraits={ini['pack']['native_file']:int(ini['pack']['native_hash'])}
    for number in range(count):
        row=ini[f'portrait-{number}']
        for density in (1,2):portraits[row[f'file{density}']]=int(row[f'hash{density}'])
    for name,expected in portraits.items():
        if not re.fullmatch(r'(?:native-[0-9a-f]{64}\.bin|[0-9a-f]{64}\.png)',name):raise ValueError('Unsafe prepared portrait filename')
        file=portrait_pack/name
        if file.is_symlink() or not file.is_file() or file.stat().st_size>2097152 or fnv64(file.read_bytes())!=expected:
            raise ValueError('Modified portrait: '+name)
    provenance=json.loads((ROOT/'assets/generated/pc-backgrounds/provenance.json').read_text(encoding='utf-8'))
    rows=provenance['backgrounds']
    if len(rows)!=19:raise ValueError('Expected the19 validated decorative backgrounds')
    for row in rows:
        file=pc_root/'SAKURA1/WALL'/(row['id']+'.SPR')
        if hashlib.sha256(file.read_bytes()).hexdigest()!=row['source_spred_sha256']:raise ValueError('Modified PC background')
    env=os.environ.copy();env['PATH']='C:/msys64/clang64/bin;'+env.get('PATH','')
    with tempfile.TemporaryDirectory(prefix='prepared-hd-',dir=ROOT/'local/work') as tmp:
        cache=Path(tmp)
        result=subprocess.run([str(Path(runtime).resolve()),'--prepare-pc-backgrounds',str(pc_root),str(cache)],env=env,capture_output=True,timeout=90)
        if result.returncode:raise ValueError(result.stderr.decode(errors='replace'))
        output.mkdir(parents=True);(output/'backgrounds').mkdir();(output/'portraits').mkdir()
        entries=[]
        for row in rows:
            identity=row['id'];matches=list(cache.glob(identity+'-pc864-v3-*.stfb'))
            if len(matches)!=1:raise ValueError('Missing prepared cache: '+identity)
            blob=matches[0].read_bytes();shutil.copy2(matches[0],output/'backgrounds'/(identity+'.stfb'))
            source_hash=fnv64((pc_root/'SAKURA1/WALL'/(identity+'.SPR')).read_bytes())
            entries.append(struct.pack('<8sQQQ',identity.encode('ascii'),source_hash,fnv64(blob),len(blob)))
        shutil.copy2(manifest,output/'portraits/manifest.ini')
        for name in portraits:shutil.copy2(portrait_pack/name,output/'portraits'/name)
        receipt=struct.pack('<8sIIQQQII',b'STFHD01\0',1,len(entries),SOURCE_BYTES,SOURCE_HASH,fnv64(manifest.read_bytes()),count,0)+b''.join(entries)
        (output/'hd-pack.stfp').write_bytes(receipt)
    files=[dict(path=file.relative_to(output).as_posix(),bytes=file.stat().st_size,sha256=hashlib.sha256(file.read_bytes()).hexdigest()) for file in sorted(output.rglob('*')) if file.is_file()]
    report=dict(schema=1,original_pc_files_included=False,backgrounds=len(entries),portraits=count,files=files)
    (output/'prepared-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pc-root',type=Path,required=True);p.add_argument('--portrait-pack',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--runtime',type=Path,default=ROOT/'local/build/sakura/sakura.exe');a=p.parse_args()
    report=export_prepared(a.pc_root,a.portrait_pack,a.output,a.runtime)
    print(json.dumps({k:v for k,v in report.items() if k!='files'}),flush=True)
if __name__=='__main__':main()
