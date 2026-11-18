#include "presentation_layout.h"
#include "screen_backdrop.h"
#include <cassert>
#include <vector>
int main() {
    for(auto [w,h]:{std::pair{1280,720},std::pair{1920,1080},std::pair{2560,1440},std::pair{3440,1440},std::pair{705,513},std::pair{1281,721},std::pair{2559,1439}}) {
        const auto native=port::FitInteger(w,h,320,224);
        const auto anchored=port::FitAnchoredBackdrop(w,h);
        assert(anchored.scale==native.scale && anchored.x+240*anchored.scale==native.x);
        assert(anchored.y+113*anchored.scale==native.y);
        assert(anchored.w>=port::PresentationWidth(w,h) && anchored.h>=h);
    }
    // DiscFiles indexes ISO entries by their basename, not their full ISO path.
    for(const auto& spec:port::kScreenBackdrops)
        assert(std::string(spec.resource).find('/')==std::string::npos);
    std::vector<uint32_t> mapPixels(320*224);
    std::vector<uint8_t> mapSources(320*224,2);
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<320;x++)mapPixels[y*320+x]=0xFF000000|y;
    std::vector<uint32_t> rows;
    assert(port::AnalyzeRowBackdrop(mapPixels,mapSources,rows) && rows.size()==224*16 && rows[123*16]==(0xFF000000|123));
    mapPixels[16]=0xFF123456; // the central map can differ freely
    assert(port::AnalyzeRowBackdrop(mapPixels,mapSources,rows));
    mapPixels[3]=0xFF123456;
    assert(!port::AnalyzeRowBackdrop(mapPixels,mapSources,rows) && rows.empty());
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<320;x++)mapPixels[y*320+x]=0xFF000000|y|((x&1)<<16);
    assert(port::AnalyzeRowBackdrop(mapPixels,mapSources,rows)); // native night gradient has ordered dithering
    assert(rows[0]!=rows[1] && rows[0]==rows[2]);
    for(unsigned x=304;x<320;x++)mapPixels[117*320+x]^=0x00080810;
    assert(port::AnalyzeRowBackdrop(mapPixels,mapSources,rows)); // separate native edge phases
    for(unsigned y=0;y<224;y++)mapPixels[y*320+4]=0xFF987654; // map artwork can begin four pixels from the border
    assert(port::AnalyzeRowBackdrop(mapPixels,mapSources,rows));
    for(unsigned x=0;x<8;x++)mapPixels[218*320+x]=0xFF8070D0+x*0x010101;
    for(unsigned x=312;x<320;x++)mapPixels[218*320+x]=0xFF8070D0+(x-312)*0x010101;
    assert(port::AnalyzeRowBackdrop(mapPixels,mapSources,rows)); // irregular low-contrast ordered dither row
    std::vector<uint8_t> resource(1024);
    for(size_t i=512;i<resource.size();i++)resource[i]=uint8_t(i*17+i/13);
    port::ScreenBackdropSpec screen{"TEST","/TEST",{512,0},port::AtlasFingerprint(std::span<const uint8_t>(resource).subspan(512,512))};
    assert(port::ScreenPalette(resource,screen).size()==512);
    resource.back()^=1;assert(port::ScreenPalette(resource,screen).empty());
    assert(port::ScreenPalette(std::span<const uint8_t>(resource).first(600),screen).empty());
    for(auto [w,h]: {std::pair{1280,720},std::pair{1920,1080},std::pair{2560,1440},std::pair{3840,2160},std::pair{3440,1440},std::pair{705,513},std::pair{1281,721},std::pair{2559,1439},std::pair{2044,1440}}) {
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
    fill(16,8,288,144,4);fill(120,8,120,144,0); // dialogue scenery uses NBG2, not just movie planes
    assert(port::AnalyzePresentation(source,320,224).recognized);
    fill(25,0,20,8,0); // actor overhang at native top must survive
    fill(310,219,1,1,3); // native textbox shadow must also remain visible
    layout=port::AnalyzePresentation(source,320,224);
    assert(layout.y==0);
    auto fit=port::FitInteger(1920,1080,layout.w,layout.h);
    assert(fit.h<=1080 && fit.w<=1920 && fit.scale==4);
    fill(40,8,200,144,0); // large character covers most of the picture plane
    assert(port::AnalyzePresentation(source,320,224).recognized);
    fill(16,8,288,144,0); // a letter/photo can occupy the whole VDP1 picture
    assert(port::AnalyzePresentation(source,320,224).recognized);
    assert(!port::AnalyzePresentation(source,352,224).recognized);
    source.assign(320*224,5);
    fill(16,24,288,144,1);fill(40,151,240,12,0); // opening lyrics stay inside the video
    auto opening=port::AnalyzeOpeningPresentation(source,320,224);
    assert(opening.recognized && opening.movieOnly && opening.y==24 && opening.h==144);
    auto film=port::FitInteger(2560,1440,opening.w,opening.h);
    assert(film.scale==8 && film.w==2304 && film.h==1152);
    fill(0,200,20,10,0); // do not crop unknown labels outside the opening movie
    assert(!port::AnalyzeOpeningPresentation(source,320,224).recognized);
    for(int w: {320,640,1366,1920,2560,3840,7680})for(int h: {224,480,768,1080,1440,2160}) {
        auto cover=port::CoverInteger(w,h,416,234);
        assert(cover.w>=w && cover.h>=h && cover.scale>=1);
        assert(cover.w==416*cover.scale && cover.h==234*cover.scale);
    }
}
