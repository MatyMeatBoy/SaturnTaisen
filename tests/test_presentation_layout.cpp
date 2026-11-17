#include "presentation_layout.h"
#include <cassert>
#include <vector>
int main() {
    std::vector<unsigned char> source(320*224,5);
    auto fill=[&](int x,int y,int w,int h,unsigned char layer) {
        for(int j=y;j<y+h;j++)for(int i=x;i<x+w;i++)source[j*320+i]=layer;
    };
    fill(16,8,288,144,1); fill(9,153,302,63,0);
    // Mimic empty frame edges rather than a solid sprite textbox.
    fill(55,165,230,39,3);
    auto layout=port::AnalyzePresentation(source,320,224);
    assert(layout.recognized && layout.movieOnly);
    fill(80,170,6,8,0); // actual dialogue means retain the entire group
    layout=port::AnalyzePresentation(source,320,224);
    assert(layout.recognized && !layout.movieOnly);
    fill(25,0,20,8,0); // actor overhang at native top must survive
    fill(310,219,1,1,3); // native textbox shadow must also remain visible
    layout=port::AnalyzePresentation(source,320,224);
    assert(layout.y==0);
    auto fit=port::FitInteger(1920,1080,layout.w,layout.h);
    assert(fit.h<=1080 && fit.w<=1920 && fit.scale==4);
    fill(40,8,200,144,0); // large character covers most of the picture plane
    assert(port::AnalyzePresentation(source,320,224).recognized);
    assert(!port::AnalyzePresentation(source,352,224).recognized);
    for(int w: {320,640,1366,1920,2560,3840,7680})for(int h: {224,480,768,1080,1440,2160}) {
        auto cover=port::CoverInteger(w,h,416,234);
        assert(cover.w>=w && cover.h>=h && cover.scale>=1);
        assert(cover.w==416*cover.scale && cover.h==234*cover.scale);
    }
}
