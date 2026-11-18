"""Reproduce local AOT candidates for Sakura's verified battle-overlay family.

Outputs contain owner-derived SH-2 bytes: only a new local/work directory is
accepted by the CLI. Inputs and the live discovery database are never changed.
"""
import argparse
import hashlib
import importlib.util
import json
import mmap
from pathlib import Path
import re
import struct
import subprocess
import sys

if __package__:
    from .audit_sdk import files
else:
    from audit_sdk import files

ROOT=Path(__file__).resolve().parents[1]
BASE=0x06078000
FAMILY=re.compile(r'/SAKURA2/K0(?:0[1-9]|1[0-9])\.BIN\Z')
MAX_MODULE=65536
MAX_BLOCK=96
MAX_CANDIDATES=2_000_000


def overlay_module(path,raw,profile):
    if not FAMILY.fullmatch(path):return None
    if not 16<=len(raw)<=MAX_MODULE or len(raw)%2:
        raise ValueError('Invalid battle overlay size/alignment: '+path)
    pointers=sum(BASE<=value<BASE+len(raw) and value%2==0
                 for (value,) in struct.iter_unpack('>I',raw[:len(raw)//4*4]))
    if not pointers:raise ValueError('Battle overlay has no supporting absolute self pointers: '+path)
    return dict(profile=profile,file=path,base=BASE,bytes=len(raw),
                sha256=hashlib.sha256(raw).hexdigest(),self_pointer_count=pointers,raw=raw)


def analyze_modules(modules,discover):
    unique={};blocks=set();rows=[]
    for module in modules:
        base=module['base'];key=(base,module['sha256']);raw=module['raw']
        if base%2 or base<0 or base+len(raw)>0x100000000:raise ValueError('Invalid module address')
        if key not in unique:
            candidates=discover(raw,base,range(base,base+len(raw),2),eager=True)
            checked=set()
            for pc,code in candidates:
                offset=pc-base
                if (pc%2 or offset<0 or not 0<len(code)<=MAX_BLOCK or len(code)%2
                        or offset+len(code)>len(raw) or raw[offset:offset+len(code)]!=code):
                    raise ValueError('Analyzer emitted an invalid overlay candidate')
                checked.add((pc,code))
            unique[key]=checked;blocks.update(checked)
        row={key:value for key,value in module.items() if key!='raw'}
        row['base']=f'{base:08X}';row['candidate_blocks']=len(unique[key]);rows.append(row)
    return blocks,rows


def merge_candidates(seed,extra):
    merged=set(seed)|set(extra)
    if len(merged)>MAX_CANDIDATES:raise ValueError('Candidate budget exceeded')
    return merged


def read_seed(path):
    if path.stat().st_size>512*1024*1024:raise ValueError('Seed database exceeds byte budget')
    candidates=set()
    with path.open(encoding='ascii') as stream:
        for line in stream:
            line=line.strip()
            if not line or line.startswith('#'):continue
            if not re.fullmatch(r'[0-9A-Fa-f]{8} [0-9A-Fa-f]{4,192}',line):
                raise ValueError('Malformed seed candidate')
            address,hex_bytes=line.split(' ');pc=int(address,16);code=bytes.fromhex(hex_bytes)
            if pc%2 or len(code)%2:raise ValueError('Unaligned seed candidate')
            candidates.add((pc,code))
            if len(candidates)>MAX_CANDIDATES:raise ValueError('Seed candidate budget exceeded')
    if not candidates:raise ValueError('Empty seed database')
    return candidates


def scan_iso(path,profile):
    modules=[];seen=set()
    with path.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        image_hash=hashlib.sha256(data).hexdigest()
        for name,lba,size in files(data):
            if not FAMILY.fullmatch(name):continue
            if name in seen or lba*2048+size>len(data):raise ValueError('Invalid/duplicate overlay extent')
            seen.add(name)
            if not 16<=size<=MAX_MODULE or size%2:raise ValueError('Invalid battle overlay extent size')
            module=overlay_module(name,bytes(data[lba*2048:lba*2048+size]),profile)
            module['lba']=lba;modules.append(module)
    if not modules:raise ValueError('No verified battle overlay family found in '+profile)
    return modules,dict(profile=profile,image_name=path.name,sha256=image_hash,modules=len(modules))


def analyze_with_sdk(modules,sdk):
    previous=sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode=True  # SDK imports must not populate its __pycache__.
        module_spec=importlib.util.spec_from_file_location('battle_static_analyzer',ROOT/'tools/static_program.py')
        analyzer=importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(analyzer)
        analyzer.DEP=sdk
        return analyze_modules(modules,analyzer.discover)
    finally:
        sys.dont_write_bytecode=previous


def build(discs,seed,output,sdk):
    if not discs or len(set(discs))!=len(discs):raise ValueError('Expected distinct input profiles')
    spec=json.loads((ROOT/'config/dependencies.json').read_text(encoding='utf-8'))['satrecomp']
    revision=subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip()
    if revision!=spec['commit']:raise ValueError('Use the pinned SDK revision')
    opcode_file=sdk/'machine/sh2_ops.h'
    before=read_seed(seed);modules=[];inputs=[]
    for profile,path in sorted(discs.items()):
        selected,info=scan_iso(path,profile);modules.extend(selected);inputs.append(info)
    extra,rows=analyze_with_sdk(modules,sdk)
    merged=merge_candidates(before,extra)
    output.mkdir(parents=True,exist_ok=False)
    database=output/'blocks.txt'
    with database.open('x',encoding='ascii',newline='\n') as stream:
        stream.write('# Static/observed candidates; owner-derived bytes, keep local.\n')
        for pc,code in sorted(merged):stream.write(f'{pc:08X} {code.hex().upper()}\n')
    report=dict(schema=1,base=f'{BASE:08X}',scope='static candidates, not executed coverage',
                base_evidence='K002 witnessed at PC060783FC, file offset03FC; absolute self pointers support family placement',
                sdk_commit=revision,opcode_sha256=hashlib.sha256(opcode_file.read_bytes()).hexdigest(),
                seed_sha256=hashlib.sha256(seed.read_bytes()).hexdigest(),inputs=inputs,
                unique_modules=len({module['sha256'] for module in modules}),profiles=rows,
                before=len(before),after=len(merged),added=len(merged)-len(before),
                candidate_database_sha256=hashlib.sha256(database.read_bytes()).hexdigest())
    (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disc',action='append',required=True,metavar='PROFILE=ISO')
    parser.add_argument('--seed-blocks',type=Path,required=True)
    parser.add_argument('--sdk-root',type=Path,default=ROOT/'local/deps/satrecomp')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();discs={}
    for item in args.disc:
        profile,separator,name=item.partition('=')
        if not separator or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',profile) or profile in discs:
            parser.error('each --disc needs a distinct PROFILE=ISO')
        discs[profile]=Path(name).resolve()
    output=args.output.resolve();private=(ROOT/'local/work').resolve()
    if private not in output.parents or output.exists():parser.error('--output must be a new directory inside local/work')
    try:report=build(discs,args.seed_blocks.resolve(),output,args.sdk_root.resolve())
    except (OSError,ValueError,subprocess.SubprocessError) as error:parser.exit(1,str(error)+'\n')
    print(json.dumps({key:report[key] for key in ('unique_modules','before','after','added')},indent=2))
    print(output)


if __name__=='__main__':main()
