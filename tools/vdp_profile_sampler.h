// Temporary measurement aid for the VDP speed work (T103); never part of a patch.
//   1. Copy to satrecomp/video/prof_tmp.h and `#include "prof_tmp.h"` in renderer.cpp / layers.cpp / raster.cpp.
//   2. PROF_TIMED("name") at the top of a function adds per-call time (SATRECOMP_VDP_PROF=1 prints totals at exit).
//   3. `g_sampler.Start();` at the top of Renderer::RenderLine samples the emulation thread's RIP every ~150 us;
//      SATRECOMP_SAMPLE=PATH writes the histogram, resolved with tools/symbolize_samples.py.
// The timed scopes cost about 0.3 ms per frame, so take either timings or samples, not both at once.
#pragma once
#include <chrono>
#include <thread>
#include <atomic>
#include <map>
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <windows.h>
namespace satrecomp::video {
struct ProfAcc { const char* n; uint64_t ns=0,c=0; };
inline ProfAcc g_prof[32];
inline int g_profN=0;
struct ProfReport { ~ProfReport(){ if(!getenv("SATRECOMP_VDP_PROF"))return; for(int i=0;i<g_profN;i++) fprintf(stderr,"vdpprof %-22s total=%8.1f ms calls=%9llu avg=%8.3f us\n",g_prof[i].n,g_prof[i].ns/1e6,(unsigned long long)g_prof[i].c,g_prof[i].c?g_prof[i].ns/1e3/g_prof[i].c:0.0);} };
inline ProfReport g_profReport;
struct ProfScope { ProfAcc* a; std::chrono::steady_clock::time_point t;
  explicit ProfScope(ProfAcc* x):a(x),t(std::chrono::steady_clock::now()){}
  ~ProfScope(){ a->ns+=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-t).count(); a->c++; } };
#define PCAT2(a,b) a##b
#define PCAT(a,b) PCAT2(a,b)
#define PROF_TIMED(name) static ProfAcc* PCAT(_pa,__LINE__)=[]{g_prof[g_profN].n=name;return &g_prof[g_profN++];}(); ProfScope PCAT(_ps,__LINE__)(PCAT(_pa,__LINE__))

struct Sampler {
  HANDLE th=nullptr; std::thread t; std::atomic<bool> stop{false}; std::map<uintptr_t,uint64_t> hist; uint64_t n=0;
  void Start(){
    if(th||!getenv("SATRECOMP_SAMPLE"))return;
    DuplicateHandle(GetCurrentProcess(),GetCurrentThread(),GetCurrentProcess(),&th,0,FALSE,DUPLICATE_SAME_ACCESS);
    t=std::thread([this]{
      LARGE_INTEGER f,a,b; QueryPerformanceFrequency(&f);
      while(!stop){
        QueryPerformanceCounter(&a);
        do{QueryPerformanceCounter(&b);}while((b.QuadPart-a.QuadPart)*1000000/f.QuadPart<150 && !stop);
        if(SuspendThread(th)==(DWORD)-1)continue;
        CONTEXT c; c.ContextFlags=CONTEXT_CONTROL;
        if(GetThreadContext(th,&c)){hist[(uintptr_t)c.Rip]++;n++;}
        ResumeThread(th);
      }
    });
  }
  ~Sampler(){
    if(!th)return; stop=true; t.join();
    FILE* f=fopen(getenv("SATRECOMP_SAMPLE"),"w");
    fprintf(f,"base %llx total %llu\n",(unsigned long long)(uintptr_t)GetModuleHandle(NULL),(unsigned long long)n);
    HMODULE self=GetModuleHandle(NULL);
    for(auto&kv:hist){
      HMODULE m=nullptr; GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,(LPCSTR)kv.first,&m);
      if(m&&m!=self){ char nm[260]="?"; GetModuleFileNameA(m,nm,260); fprintf(f,"DLL %s %llx %llu\n",nm,(unsigned long long)(kv.first-(uintptr_t)m),(unsigned long long)kv.second); }
      else fprintf(f,"%llx %llu\n",(unsigned long long)kv.first,(unsigned long long)kv.second);
    }
    fclose(f);
  }
};
inline Sampler g_sampler;
}
