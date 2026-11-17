#include "presentation_layout.h"
#include <cassert>
#include <vector>
int main() {
    for(auto [w,h]: {std::pair{1280,720},std::pair{1920,1080},std::pair{2560,1440},std::pair{3840,2160},std::pair{3440,1440},std::pair{2044,1440}}) {
        auto zoom=port::FitSceneZoom(w,h,306,67,212,2);
        assert(zoom.valid && zoom.picture.y>0);
        assert(zoom.picture.w==288*zoom.picture.scale && zoom.picture.h==144*zoom.picture.scale);
        assert(zoom.dialogue.w==306*zoom.dialogue.scale);
        assert(zoom.dialogue.y==zoom.picture.y+zoom.picture.h+zoom.gap);
        assert(zoom.dialogue.y+zoom.dialogue.h<=h+2*zoom.dialogue.scale);
        assert(zoom.picture.x+zoom.picture.w+zoom.shadow<=w);
    }
    auto zoom=port::FitSceneZoom(2560,1440,306,67,212,2);
    assert(zoom.picture.scale==7 && zoom.dialogue.scale==6 && zoom.shadow==28 && zoom.gap==11 && zoom.picture.y==29 && zoom.dialogue.y==1048);
    auto noClip=port::FitSceneZoom(2560,1440,306,67,212);
    assert(noClip.dialogue.y+noClip.dialogue.h<=1440 && noClip.picture.y==23);
    assert(!port::FitSceneZoom(100,100,306,67,212).valid);
    assert(port::IsOldPictureShadow(20,153,3));
    assert(port::IsOldPictureShadow(307,155,3));
    assert(!port::IsOldPictureShadow(20,156,3));
    assert(!port::IsOldPictureShadow(20,153,0)); // preserve golden ornament
    assert(!port::IsOldPictureShadow(308,153,3));
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
