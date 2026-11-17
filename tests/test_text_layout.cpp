#include "narrative_text.h"
#include "integer_viewport.h"
#include <cassert>
#include <array>
#include <cmath>
int main() {
    std::array<uint8_t,128> tile{};
    for(int y=0;y<12;y++)for(int x=0;x<4;x++)tile[y*8+x]=0x11;
    // A 16-pixel texture may have only 8 ink pixels. The last letter still fits.
    assert(port::NarrativeInkFits(296,196,tile));
    assert(!port::NarrativeInkFits(297,196,tile));
    assert(!port::NarrativeInkFits(296,197,tile));
    assert(!port::NarrativeInkFits(55,160,tile));
    assert(!port::NarrativeInkFits(56,159,tile));
    assert(!port::NarrativeInkFits(56,160,std::span<const uint8_t>(tile.data(),4)));
    // Use a single affine scale for the entire font. A narrow i must not be
    // stretched to a native bitmap's different width or height.
    const auto natural=port::NaturalTextPlacement(7.5f,1,3,9,0,2,11,3);
    assert(natural.scale>0);
    const float wide=7*natural.scale,narrow=natural.scale;
    assert(std::abs(wide/narrow-7)<0.0001f);
    assert(std::abs((12*natural.scale+natural.offsetY)-(3*natural.scale+natural.offsetY)-9*natural.scale)<0.0001f);
    assert(std::abs(1*natural.scale+natural.offsetX)<0.0001f);
    assert(std::abs(3*natural.scale+natural.offsetY-6)<0.0001f);
    assert(9*natural.scale<=11*3);
    for(const auto [w,h]:std::array<std::pair<int,int>,5>{{{640,480},{1280,720},{1920,1080},{3840,2160},{3440,1440}}}) {
        const auto fit=port::FitInteger(w,h,320,224);
        const auto clip=port::NarrativeClip(fit.x,fit.y,fit.scale,0,0);
        assert(clip[0]>=0 && clip[1]>=0 && clip[2]<=w && clip[3]<=h);
        assert(clip[2]-clip[0]==248*fit.scale && clip[3]-clip[1]==48*fit.scale);
        const auto cropped=port::NarrativeClip(fit.x,fit.y,fit.scale,8,12);
        assert(cropped[0]==clip[0]-8*fit.scale && cropped[1]==clip[1]-12*fit.scale);
    }
}
