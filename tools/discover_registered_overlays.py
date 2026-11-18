"""Add byte-verified, runtime-attributed overlays to a private AOT candidate DB."""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
import subprocess

if __package__:
    from .audit_sdk import files
    from .discover_battle_overlays import ROOT,read_seed,merge_candidates,analyze_with_sdk
else:
    from audit_sdk import files
    from discover_battle_overlays import ROOT,read_seed,merge_candidates,analyze_with_sdk

REGISTRY={
    'EVT02':dict(file='/SAKURA2/EVT02.BIN',base=0x00204000,bytes=76180,
                 sha256='701d68ab48e67eabce1e1eb89bd4a8b790aa0f6a40ff68bbfa0600489b97c660',
                 evidence='Episode2 cold load: all 76180 bytes equal LowRAM at 00204000 in strict/interpreter state frame6688; strict first missing PC00204000'),
    'EVT06':dict(file='/SAKURA2/EVT06.BIN',base=0x00204000,bytes=77716,
                 sha256='3214506d26f1b9fbec18190e993acf4ef5502532522790d7a327efe7125c89e5',
                 evidence='Episode4 cold load: all 77716 bytes equal LowRAM at 00204000 in states6677-6680; strict first missing PC00204000 after6678 complete frames'),
}


def registered_module(name,raw,profile,registry=REGISTRY):
    spec=registry.get(name)
    if spec is None:raise ValueError('Overlay has no verified registry entry: '+name)
    if len(raw)!=spec['bytes'] or hashlib.sha256(raw).hexdigest()!=spec['sha256']:
        raise ValueError('Overlay bytes differ from the witnessed version: '+name)
    return dict(spec,profile=profile,raw=raw)


def build(image,names,seed,output,sdk):
    expected=json.loads((ROOT/'config/dependencies.json').read_text(encoding='utf-8'))['satrecomp']['commit']
    revision=subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip()
    if revision!=expected:raise ValueError('Use the pinned SDK revision')
    if not names or len(set(names))!=len(names) or any(name not in REGISTRY for name in names):
        raise ValueError('Select distinct registered overlays')
    paths={REGISTRY[name]['file']:name for name in names};modules=[]
    with image.open('rb') as source,mmap.mmap(source.fileno(),0,access=mmap.ACCESS_READ) as data:
        image_hash=hashlib.sha256(data).hexdigest();seen=set()
        for path,lba,size in files(data):
            if path not in paths:continue
            if path in seen or lba*2048+size>len(data):raise ValueError('Invalid registered overlay extent')
            seen.add(path)
            spec=REGISTRY[paths[path]]
            if size!=spec['bytes']:raise ValueError('Registered overlay extent size changed')
            module=registered_module(paths[path],bytes(data[lba*2048:lba*2048+size]),'owner-disc')
            module['lba']=lba;modules.append(module)
    if seen!=set(paths):raise ValueError('Registered overlay absent from image')
    before=read_seed(seed);extra,rows=analyze_with_sdk(modules,sdk);merged=merge_candidates(before,extra)
    output.mkdir(parents=True,exist_ok=False);database=output/'blocks.txt'
    with database.open('x',encoding='ascii',newline='\n') as stream:
        stream.write('# Owner-derived AOT candidates; keep local.\n')
        for pc,code in sorted(merged):stream.write(f'{pc:08X} {code.hex().upper()}\n')
    report=dict(schema=1,scope='static candidates from registered overlays, not executed campaign coverage',
                sdk_commit=revision,opcode_sha256=hashlib.sha256((sdk/'machine/sh2_ops.h').read_bytes()).hexdigest(),
                iso_sha256=image_hash,seed_sha256=hashlib.sha256(seed.read_bytes()).hexdigest(),
                profiles=rows,before=len(before),after=len(merged),added=len(merged)-len(before),
                candidate_database_sha256=hashlib.sha256(database.read_bytes()).hexdigest())
    (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,required=True)
    parser.add_argument('--module',action='append',choices=sorted(REGISTRY),required=True)
    parser.add_argument('--seed-blocks',type=Path,required=True)
    parser.add_argument('--sdk-root',type=Path,default=ROOT/'local/deps/satrecomp')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output.resolve()
    if (ROOT/'local/work').resolve() not in output.parents or output.exists():
        parser.error('--output must be a new directory under local/work')
    try:report=build(args.image,args.module,args.seed_blocks,output,args.sdk_root)
    except (OSError,ValueError,subprocess.SubprocessError) as error:parser.exit(1,str(error)+'\n')
    print(json.dumps({key:report[key] for key in ('before','after','added')},indent=2))


if __name__=='__main__':main()
