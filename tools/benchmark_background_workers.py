"""Measure production CPU backdrop preparation at bounded worker counts.

Run alone, without builds or tests. Cold denotes only the derived resource cache.
Every run proves exact RGBA equivalence to the preserved sequential-loader binary.
"""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import statistics
import subprocess
import time
from benchmark_backgrounds import ROOT, WORK, PREFIX, environment, pixels, prepare_palettes


def process_peaks(process):
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD),
                  *[(name,ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize',
                    'QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage',
                    'QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]]
    counters=Counters();counters.cb=ctypes.sizeof(counters)
    query=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo
    query.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    if not query(int(process._handle),ctypes.byref(counters),counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return dict(peak_working_set_bytes=counters.PeakWorkingSetSize,
                peak_private_commit_bytes=counters.PeakPagefileUsage)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',type=int,default=3)
    args=parser.parse_args()
    if not 1<=args.runs<=10:raise ValueError('Use 1..10 repetitions')
    folder=WORK/('workers-'+str(time.time_ns()));folder.mkdir(parents=True)
    prepare_palettes(ROOT/'local/prepared/disc1/Track 01.iso')
    source=ROOT/'tests/benchmark_backgrounds.cpp';headers=ROOT/'local/deps/satrecomp/port'
    exe=folder/'workers.exe'
    subprocess.run([str(PREFIX/'bin/clang++.exe'),'-O3','-DNDEBUG','-std=c++20',str(source),
                    '-I',str(headers),'-I',str(PREFIX/'include'),'-L',str(PREFIX/'lib'),
                    '-lSDL3','-lz','-o',str(exe)],env=environment(),check=True)
    pc=ROOT/'local/work/v02-pc-game/_t_@_C__'
    baseline=folder/'baseline'
    subprocess.run([str(WORK/'final-packed.exe'),str(ROOT),str(baseline),str(pc)],
                   env=environment(),capture_output=True,check=True,timeout=60)
    expected=pixels(baseline);rows=[]
    def run(count,cache,number,state):
        start=time.perf_counter()
        with subprocess.Popen([str(exe),str(ROOT),str(cache),str(pc),str(count)],
                              env=environment(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) as process:
            try:stdout,stderr=process.communicate(timeout=60)
            except subprocess.TimeoutExpired:
                process.kill();process.communicate();raise
            if process.returncode:raise subprocess.CalledProcessError(process.returncode,process.args,stdout,stderr)
            peaks=process_peaks(process)
        elapsed=time.perf_counter()-start
        assert pixels(cache)==expected,'Worker count changed image pixels'
        (folder/f'{count}-{number}-{state}.csv').write_text(stdout,encoding='utf-8')
        rows.append(dict(workers=count,round=number,state=state,seconds=elapsed,
                         **peaks,
                         cache_bytes=sum(p.stat().st_size for p in cache.iterdir() if p.is_file())))
    for count in (1,2,4,8):run(count,folder/f'warmup-{count}',-1,'warmup')
    for number in range(args.runs):
        for count in (1,2,4,8) if number%2==0 else (8,4,2,1):
            cache=folder/f'{count}-{number}';run(count,cache,number,'cold-derived');run(count,cache,number,'warm-derived')
    report=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
                baseline_sha256=hashlib.sha256((WORK/'final-packed.exe').read_bytes()).hexdigest(),
                header_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in headers.glob('*back*.h')},
                pixels=expected,rows=rows,
                limits=['Derived cache cold/warm; OS file cache not flushed.',
                        'CPU-only preparation; excludes GPU upload, game frames and guest CD timing.'])
    report['median_seconds']={str(n):{state:statistics.median(row['seconds'] for row in rows if row['workers']==n and row['state']==state)
                                    for state in ('cold-derived','warm-derived')} for n in (1,2,4,8)}
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(report=str(folder/'report.json'),median_seconds=report['median_seconds']),indent=2))


if __name__=='__main__':main()
