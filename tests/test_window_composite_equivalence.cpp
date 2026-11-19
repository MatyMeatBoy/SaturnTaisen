// T86: the enhanced composite and the map crossfade work per native pixel or skip the native picture instead of
// visiting every window pixel. These loops are copies of the old and new forms in port/frontend_sdl.cpp
// (patch0056); they must give the same pixels for every window size, scale, crop and recipe tried here.
#include "map_crossfade.h"
#include "panel_compositing.h"
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <random>
#include <vector>

namespace {
std::mt19937 rng(1996);
uint32_t Random32() {return rng();}

struct Planes {
    std::vector<port::PanelMix> panelMix,underPanelMix,floralCoverMix,glyphMix;
    std::vector<uint8_t> erased;
    std::vector<uint32_t> source;
};

Planes RandomPlanes(bool withFloral) {
    Planes p;
    auto mix=[&] {
        port::PanelMix m;
        m.topRgb=Random32()&0xFFFFFF;
        m.lowerWeight=(rng()%3==0)?uint8_t(1+rng()%32):0;
        for(auto& o:m.postMixOffset)o=int16_t(int(rng()%64)-32);
        return m;
    };
    for(auto* v:{&p.panelMix,&p.underPanelMix,&p.glyphMix})for(int i=0;i<320*224;i++)v->push_back(mix());
    if(withFloral)for(int i=0;i<320*224;i++)p.floralCoverMix.push_back(mix());
    for(int i=0;i<320*224;i++)p.erased.push_back(uint8_t(rng()%5==0?(1+rng()%2):0));
    for(int i=0;i<320*224;i++)p.source.push_back((rng()%4?0xFF000000u:0)|(Random32()&0xFFFFFF));
    return p;
}

// The composite exactly as it was: every window pixel.
bool OldComposite(const Planes& p,const std::vector<uint32_t>& backdrop,int bgw,int bgh,int bgx,int bgy,int coverScale,
                  const port::IntegerViewport& fit,int cropX,int cropY,const port::PanelMix* solid,std::vector<uint32_t>& pixels) {
    pixels.assign(size_t(fit.w)*fit.h,0);
    bool hasMix=false;
    for(int py=0;py<fit.h;py++)for(int px=0;px<fit.w;px++) {
        const int sx=cropX+px/fit.scale,sy=cropY+py/fit.scale;
        if(sx<0 || sx>=320 || sy<0 || sy>=224) {pixels[size_t(py)*fit.w+px]=0;continue;}
        const size_t at=size_t(sy)*320+sx;
        const auto& baseRecipe=p.erased[at]==2?p.glyphMix[at]:(p.erased[at]?p.underPanelMix[at]:p.panelMix[at]);
        const auto& recipe=solid?*solid:(p.erased[at] || baseRecipe.lowerWeight || p.floralCoverMix.size()!=320*224?baseRecipe:p.floralCoverMix[at]);
        uint32_t pixel=solid?0xFF000000:p.source[at];
        if((pixel>>24) && recipe.lowerWeight)if(const auto below=port::SamplePanelBackdrop(backdrop,bgw,bgh,bgx,bgy,coverScale,fit.x+px,fit.y+py)) {
            pixel=port::CompositePanelPixel(recipe,*below,pixel);hasMix=true;
        }
        pixels[size_t(py)*fit.w+px]=pixel;
    }
    return hasMix;
}

// The composite as it is now: decided per native pixel, blocks copied, only mixed pixels sampled per window pixel.
bool NewComposite(const Planes& p,const std::vector<uint32_t>& backdrop,int bgw,int bgh,int bgx,int bgy,int coverScale,
                  const port::IntegerViewport& fit,int cropX,int cropY,const port::PanelMix* solid,std::vector<uint32_t>& pixels) {
    pixels.assign(size_t(fit.w)*fit.h,0xDEADBEEF);
    const auto recipeAt=[&](size_t at) -> const port::PanelMix& {
        const auto& baseRecipe=p.erased[at]==2?p.glyphMix[at]:(p.erased[at]?p.underPanelMix[at]:p.panelMix[at]);
        return solid?*solid:(p.erased[at] || baseRecipe.lowerWeight || p.floralCoverMix.size()!=320*224?baseRecipe:p.floralCoverMix[at]);
    };
    const int scale=fit.scale,left=cropX,top=cropY;
    const int columns=(fit.w+scale-1)/scale,lines=(fit.h+scale-1)/scale;
    bool mayMix=false;
    for(int ly=0;ly<lines && !mayMix;ly++) {
        const int sy=top+ly;if(sy<0 || sy>=224)continue;
        for(int lx=0;lx<columns;lx++) {
            const int sx=left+lx;if(sx<0 || sx>=320)continue;
            const size_t at=size_t(sy)*320+sx;
            const uint32_t pixel=solid?0xFF000000:p.source[at];
            if((pixel>>24) && recipeAt(at).lowerWeight) {mayMix=true;break;}
        }
    }
    bool hasMix=false;
    if(mayMix)for(int py=0;py<fit.h;py++) {
        const int sy=top+py/scale;
        uint32_t* row=pixels.data()+size_t(py)*fit.w;
        if(sy<0 || sy>=224) {std::fill_n(row,fit.w,0u);continue;}
        for(int px=0;px<fit.w;) {
            const int end=std::min(fit.w,(px/scale+1)*scale),sx=left+px/scale;
            if(sx<0 || sx>=320) {std::fill(row+px,row+end,0u);px=end;continue;}
            const size_t at=size_t(sy)*320+sx;
            const auto& recipe=recipeAt(at);
            const uint32_t source=solid?0xFF000000:p.source[at];
            if(!(source>>24) || !recipe.lowerWeight) {std::fill(row+px,row+end,source);px=end;continue;}
            for(;px<end;px++) {
                uint32_t pixel=source;
                if(const auto below=port::SamplePanelBackdrop(backdrop,bgw,bgh,bgx,bgy,coverScale,fit.x+px,fit.y+py)) {
                    pixel=port::CompositePanelPixel(recipe,*below,pixel);hasMix=true;
                }
                row[px]=pixel;
            }
        }
    }
    return hasMix;
}

void OldFade(const port::MapCrossfade& fade,const std::vector<uint32_t>& rows,const port::IntegerViewport& native,
             const std::vector<uint32_t>& backdrop,int bgw,int bgh,int bgx,int bgy,int coverScale,int canvasLeft,int canvasWidth,int high,
             std::vector<uint32_t>& out) {
    out.assign(size_t(canvasWidth)*high,0);
    for(int py=0;py<high;py++)for(int px=0;px<canvasWidth;px++) {
        const int screenX=canvasLeft+px;
        if(const auto floralPixel=port::SamplePanelBackdrop(backdrop,bgw,bgh,bgx,bgy,coverScale,screenX,py))
            if(const auto mixed=port::SampleMapCrossfade(fade,rows,native,screenX,py,*floralPixel))
                out[size_t(py)*canvasWidth+px]=*mixed;
    }
}

void NewFade(const port::MapCrossfade& fade,const std::vector<uint32_t>& rows,const port::IntegerViewport& native,
             const std::vector<uint32_t>& backdrop,int bgw,int bgh,int bgx,int bgy,int coverScale,int canvasLeft,int canvasWidth,int high,
             std::vector<uint32_t>& out) {
    out.assign(size_t(canvasWidth)*high,0);
    const int skipFrom=std::clamp(native.x-canvasLeft,0,canvasWidth),skipTo=std::clamp(native.x+native.w-canvasLeft,0,canvasWidth);
    for(int py=0;py<high;py++) {
        const bool insideRows=py>=native.y && py<native.y+native.h;
        for(int px=0;px<canvasWidth;px++) {
            if(insideRows && px>=skipFrom && px<skipTo) {px=skipTo-1;continue;}
            const int screenX=canvasLeft+px;
            if(const auto floralPixel=port::SamplePanelBackdrop(backdrop,bgw,bgh,bgx,bgy,coverScale,screenX,py))
                if(const auto mixed=port::SampleMapCrossfade(fade,rows,native,screenX,py,*floralPixel))
                    out[size_t(py)*canvasWidth+px]=*mixed;
        }
    }
}
}  // namespace

int main() {
    int cases=0;
    // (the suite builds this unoptimized: large windows were checked with -O2 when the change was made)
    const int sizes[][2]={{640,480},{1280,720},{1000,999},{333,250}};
    for(const auto& size:sizes) {
        const int wide=size[0],high=size[1];
        const int scale=std::max(1,std::min(wide/320,high/224));
        const port::IntegerViewport native{(wide-320*scale)/2,(high-224*scale)/2,320*scale,224*scale,scale};
        const int bgw=288+int(rng()%300),bgh=160+int(rng()%200),coverScale=1+int(rng()%6);
        std::vector<uint32_t> backdrop(size_t(bgw)*bgh);
        for(auto& px:backdrop)px=Random32()|0xFF000000;
        const int bgx=int(rng()%200)-100,bgy=int(rng()%200)-100;
        for(bool floral:{false,true})for(int crop=0;crop<3;crop++)for(int solidCase=0;solidCase<2;solidCase++) {
            const Planes planes=RandomPlanes(floral);
            const int cropX=crop==0?0:crop==1?16:-8,cropY=crop==0?0:crop==1?24:-4;
            const int cw=crop==1?288:320,ch=crop==1?152:224;
            const int s2=std::max(1,std::min(wide/cw,high/ch));
            const port::IntegerViewport fit{(wide-cw*s2)/2,(high-ch*s2)/2,cw*s2+(crop==2?s2/2:0),ch*s2,s2};
            port::PanelMix solid{0x505050,12,{-3,2,1}};
            std::vector<uint32_t> a,b;
            const bool ma=OldComposite(planes,backdrop,bgw,bgh,bgx,bgy,coverScale,fit,cropX,cropY,solidCase?&solid:nullptr,a);
            const bool mb=NewComposite(planes,backdrop,bgw,bgh,bgx,bgy,coverScale,fit,cropX,cropY,solidCase?&solid:nullptr,b);
            assert(ma==mb);
            if(ma)assert(a==b);  // (the layer is only uploaded when something mixed)
            cases++;
        }
        std::vector<uint32_t> rows(16*224);
        for(auto& px:rows)px=Random32();
        for(const port::MapCrossfade fade:{port::MapCrossfade{16,{-1,0,0}},port::MapCrossfade{32,{5,-7,0}},port::MapCrossfade{}}) {
            for(int canvas=0;canvas<2;canvas++) {
                const int canvasWidth=canvas?std::min(wide,high*16/9):wide,canvasLeft=(wide-canvasWidth)/2;
                std::vector<uint32_t> a,b;
                OldFade(fade,rows,native,backdrop,bgw,bgh,bgx,bgy,coverScale,canvasLeft,canvasWidth,high,a);
                NewFade(fade,rows,native,backdrop,bgw,bgh,bgx,bgy,coverScale,canvasLeft,canvasWidth,high,b);
                assert(a==b);
                cases++;
            }
        }
    }
    std::printf("window composite equivalence: %d cases identical\n",cases);
    return 0;
}
