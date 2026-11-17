"""Compare the production Saturn/HD backdrop loaders, without running guest code.

Requires local owner resources, SDL/Clang and Pillow. 'Cold' means an empty
derived-background cache, not an emptied operating-system file cache.
"""
import argparse
import hashlib
import json
import os
import mmap
import platform
from pathlib import Path
import re
import statistics
import struct
import subprocess
import time
import zlib
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'local/work/background-bench'
PREFIX=Path('C:/msys64/clang64')


def environment():
    env=os.environ.copy();env['PATH']=str(PREFIX/'bin')+os.pathsep+env.get('PATH','')
    env.pop('SATRECOMP_BACKGROUND_COMPRESSION',None)
    return env


def executable(label):
    if not re.fullmatch(r'[a-z0-9-]+',label):raise ValueError('Invalid benchmark label')
    return WORK/(label+'.exe')


def prepare_palettes(iso):
    from audit_sdk import files
    destination=WORK/'palettes';destination.mkdir(exist_ok=True)
    count=0
    with iso.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        for name,lba,size in files(data):
            if not re.fullmatch(r'KABE[0-9][01]\.BIN',Path(name).name):continue
            if size<512 or lba*2048+512>len(data):raise ValueError('Invalid native palette extent')
            (destination/(Path(name).stem+'.bin')).write_bytes(data[lba*2048:lba*2048+512]);count+=1
    if count!=20:raise ValueError('Expected the20 native KABE palettes')


def pixels(folder):
    result={}
    for file in sorted(folder.iterdir()):
        if file.suffix=='.png':
            with Image.open(file) as image:
                size=image.size;raw=image.convert('RGBA').tobytes()
        elif file.suffix=='.stfb':
            data=file.read_bytes();assert data[:8] in (b'STFBG001',b'STFBG002')
            width,height,length,flags=struct.unpack_from('<4I',data,8);size=(width,height)
            assert flags&~0x103==0
            packed=data[32:]
            if flags&0x100:
                decoder=zlib.decompressobj();packed=decoder.decompress(packed)
                assert decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
            assert len(packed)==length
            format=flags&3
            if format==0:
                assert length==width*height*4;raw=packed
            elif format==1:
                count=struct.unpack_from('<H',packed)[0];offset=2+4*count
                assert 1<=count<=256 and len(packed)==offset+width*height
                image=Image.frombytes('P',size,packed[offset:]);image.putpalette(packed[2:offset],'RGBA')
                raw=image.convert('RGBA').tobytes()
            else:
                assert length==width*height*2
                image=Image.frombytes('RGB',size,packed,'raw','BGR;15')
                if format==2:
                    levels={n*255//31:n<<3 for n in range(32)}
                    image=image.point([levels.get(n,n) for n in range(256)]*3)
                raw=image.convert('RGBA').tobytes()
        else:continue
        result[file.stem.split('-')[0]]={'size':list(size),'sha256_rgba':hashlib.sha256(raw).hexdigest()}
    assert len(result)==38,len(result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    command=parser.add_mutually_exclusive_group(required=True)
    command.add_argument('--build',metavar='LABEL')
    command.add_argument('--compare',nargs=2,metavar=('BASELINE','CHANGE'))
    parser.add_argument('--runs',type=int,default=3)
    parser.add_argument('--compression',type=int,choices=(0,1),help='override the production writer policy for a candidate')
    parser.add_argument('--pc-root',type=Path,default=ROOT/'local/work/v02-pc-game/_t_@_C__')
    parser.add_argument('--saturn-iso',type=Path,default=ROOT/'local/prepared/disc1/Track 01.iso')
    args=parser.parse_args();WORK.mkdir(parents=True,exist_ok=True)
    if args.build:
        output=executable(args.build)
        if output.exists():raise FileExistsError('Preserve existing benchmark binary: '+str(output))
        prepare_palettes(args.saturn_iso)
        compression=[] if args.compression is None else [f'-DSATRECOMP_BACKGROUND_COMPRESSION_DEFAULT={args.compression}']
        subprocess.run([str(PREFIX/'bin/clang++.exe'),'-O3','-DNDEBUG','-std=c++20',*compression,
                        str(ROOT/'tests/benchmark_backgrounds.cpp'),'-I',str(ROOT/'local/deps/satrecomp/port'),
                        '-I',str(PREFIX/'include'),'-L',str(PREFIX/'lib'),'-lSDL3','-lz','-o',str(output)],
                       env=environment(),check=True)
        headers=ROOT/'local/deps/satrecomp/port'
        identity=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                      compiler=subprocess.check_output([str(PREFIX/'bin/clang++.exe'),'--version'],text=True).splitlines()[0],
                      flags=['-O3','-DNDEBUG','-std=c++20',*compression],
                      headers={name:hashlib.sha256((headers/name).read_bytes()).hexdigest() for name in
                               ['backdrop.h','pc_backdrop.h','pc_spr.h','pc_backdrop_ids.h','background_cache.h','background_codec.h','palette_match.h'] if (headers/name).is_file()})
        output.with_suffix('.json').write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8')
        print(output);return
    if not 1<=args.runs<=20:raise ValueError('Use 1..20 repetitions')
    folder=WORK/('comparison-'+str(time.time_ns()));folder.mkdir()
    rows=[];expected=None
    def run(label,cache,round_number,state):
        nonlocal expected
        start=time.perf_counter()
        process=subprocess.run([str(executable(label)),str(ROOT),str(cache),str(args.pc_root.resolve())],
                               env=environment(),capture_output=True,text=True,check=True,timeout=60)
        elapsed=time.perf_counter()-start
        work={'saturn':0,'pc_hd':0};assets=[]
        (folder/f'{label}-{round_number}-{state}.csv').write_text(process.stdout,encoding='utf-8')
        for line in process.stdout.splitlines():
            kind,id,microseconds=line.split(',');work[kind]+=int(microseconds)
            assets.append(dict(kind=kind,id=id,microseconds=int(microseconds)))
        actual=pixels(cache)
        if expected is None:expected=actual
        assert actual==expected,'Normalized pixels changed: '+label
        rows.append(dict(label=label,round=round_number,cache=state,seconds=elapsed,
                         loader_ms={kind:value/1000 for kind,value in work.items()},assets=assets,
                         cache_bytes=sum(file.stat().st_size for file in cache.iterdir() if file.is_file())))
    for label in args.compare:run(label,folder/('warmup-'+label),-1,'warmup')
    for number in range(args.runs):
        for label in args.compare if number%2==0 else reversed(args.compare):
            cache=folder/(label+'-'+str(number))
            run(label,cache,number,'cold-derived');run(label,cache,number,'warm-derived')
    summary={}
    for label in args.compare:
        summary[label]={}
        for state in ('cold-derived','warm-derived'):
            subset=[row for row in rows if row['label']==label and row['cache']==state]
            summary[label][state]=dict(runs=len(subset),median_seconds=statistics.median(row['seconds'] for row in subset),
                                      median_loader_ms={kind:statistics.median(row['loader_ms'][kind] for row in subset) for kind in ('saturn','pc_hd')})
    input_hashes={file.relative_to(ROOT).as_posix():hashlib.sha256(file.read_bytes()).hexdigest() for base,pattern in
                  [(ROOT/'assets/generated/backgrounds','*.png'),(ROOT/'assets/generated/pc-backgrounds','*.png'),(WORK/'palettes','*.bin')]
                  for file in base.glob(pattern)}
    report=dict(cache_scope='derived cache only; OS file cache not flushed',renderer='SDL software renderer',
                platform=platform.platform(),processor=platform.processor(),input_sha256=input_hashes,
                identical_rgba_images=38,binaries={label:hashlib.sha256(executable(label).read_bytes()).hexdigest() for label in args.compare},
                rows=rows,summary=summary,pixels=expected)
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(report=str(folder/'report.json'),summary=summary),indent=2))


if __name__=='__main__':main()
