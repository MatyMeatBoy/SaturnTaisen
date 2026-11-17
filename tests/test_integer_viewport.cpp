// Original presentation geometry tests. No game assets.
#include "integer_viewport.h"
#include <cassert>
#include <cstdio>

int main() {
    using port::FitInteger;
    auto hd=FitInteger(1920,1080,320,224);
    assert(hd.scale==4 && hd.x==320 && hd.y==92 && hd.w==1280 && hd.h==896);
    auto ultra=FitInteger(3440,1440,320,224);
    assert(ultra.scale==6 && ultra.x==760 && ultra.y==48);
    assert(port::PresentationWidth(3440,1440)==2560);
    assert(port::PresentationWidth(5120,1440)==2560);
    assert(port::PresentationWidth(1920,1080)==1920);
    assert(port::PresentationWidth(800,600)==800);
    auto movie=FitInteger(3440,1440,288,144);
    assert(movie.scale==8 && movie.w==2304 && movie.x==568);
    auto interlaced=FitInteger(1920,1080,640,448);
    assert(interlaced.scale==2 && interlaced.w==1280 && interlaced.h==896);
    auto small=FitInteger(200,100,320,224);
    assert(small.scale==1 && small.w==320 && small.h==224 && small.x<0 && small.y<0);
    assert(FitInteger(0,1080,320,224).scale==0);
    assert(FitInteger(1920,1080,0,224).scale==0);
    for (auto [width,height] : {std::pair{800,600}, {1280,720}, {1366,768}, {1920,1080}, {2560,1440}, {3440,1440}, {3840,2160}}) {
        for (auto [columns,lines] : {std::pair{320,224}, {352,224}, {320,240}, {352,240}, {640,448}, {704,480}}) {
            auto r=FitInteger(width,height,columns,lines);
            assert(r.scale>=1 && r.w==columns*r.scale && r.h==lines*r.scale);
            assert(r.w<=width && r.h<=height);
            assert(columns*(r.scale+1)>width || lines*(r.scale+1)>height);
            assert(r.x>=0 && r.y>=0 && r.x+r.w<=width && r.y+r.h<=height);
        }
    }
    std::puts("Integer-only viewport: native modes, 4K, 16:9 cap and undersized outputs passed");
}
