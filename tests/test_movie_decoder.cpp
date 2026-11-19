// T53/S2: MovieDecoder decodes an MPEG-1/MP2 clip on a worker thread. The clip is any MPEG-1 program stream given as the first
// argument (the PC edition's MOVIE*.MPG when the owner has them); without one the test checks the failure path only.
#define PL_MPEG_IMPLEMENTATION
#include "movie_decoder.h"
#include <cassert>
#include <cstdio>
#include <thread>
int main(int argc,char** argv) {
    port::MovieDecoder missing;
    assert(!missing.Open("this-file-does-not-exist.mpg"));
    if(argc<2){std::puts("movie decoder: failure path ok (no clip given)");return 0;}
    port::MovieDecoder d;
    if(!d.Open(argv[1])){std::puts("cannot open the clip");return 1;}
    assert(d.Width()>0 && d.Height()>0 && d.Fps()>1.0 && d.Duration()>0.1);
    size_t frames=0,audioFloats=0;double last=-1;float samples[4096];
    port::MovieDecoder::Frame f;
    // Plays the first two seconds of the clip against a wall clock (what the runtime does against the guest clock).
    const auto start=std::chrono::steady_clock::now();
    while(true) {
        const double now=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        if(now>2.0)break;
        if(d.FrameAt(now,f)) {
            assert(f.width==d.Width() && f.height==d.Height() && f.rgba.size()==size_t(f.width)*size_t(f.height));
            assert(f.time>last);last=f.time;frames++;
        }
        const size_t due = size_t(now * 44100) * 2;
        if (due > audioFloats) audioFloats += d.Audio(samples, std::min(size_t(4096), due - audioFloats));
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }
    d.Close();
    std::printf("movie decoder: %zu frames, %zu audio floats in 2 s, last frame time %.3f\n",frames,audioFloats,last);
    assert(frames>=double(d.Fps())*1.5);     // the worker keeps up with real time
    if (audioFloats < 44100*2*1.8) return 2;  // same real-time interval as the video
    return 0;
}
