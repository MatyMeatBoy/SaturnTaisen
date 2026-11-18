#include "panel_compositing.h"

#include <cassert>
#include <cstdint>

namespace {
constexpr uint32_t Rgb(unsigned r, unsigned g, unsigned b) {
    return 0xFF000000u | r | (g << 8) | (b << 16);
}
}

int main() {
    const port::PanelMix white{Rgb(248, 248, 248), 11, {}};
    constexpr uint32_t original = Rgb(12, 34, 56);

    // Native hall sample with a pale panel and floral backdrop.
    assert(port::CompositePanelPixel(white, Rgb(232, 232, 184), original) == Rgb(242, 242, 226));
    assert(port::CompositePanelPixel(white, Rgb(112, 88, 144), original) == Rgb(201, 193, 212));
    // The same panel recipes retain two observed shadow colors.
    assert(port::CompositePanelPixel(white, Rgb(112,88,144), 0)==0); // erased image shadow stays erased
    const port::PanelMix dark{Rgb(80, 80, 80), 11, {}};
    assert(port::CompositePanelPixel(dark, Rgb(224, 240, 192), original) == Rgb(129, 135, 118));

    const port::PanelMix dim{Rgb(248, 248, 248), 11, {-16, -16, -16}};
    assert(port::CompositePanelPixel(dim, Rgb(112, 88, 144), original) == Rgb(185, 177, 196));
    const port::PanelMix extremes{Rgb(224, 16, 80), 11, {255, -256, -100}};
    assert(port::CompositePanelPixel(extremes, Rgb(240, 48, 240), original) == Rgb(255, 0, 35));
    const port::PanelMix allBelow{Rgb(255, 255, 255), 32, {}};
    assert(port::CompositePanelPixel(allBelow, Rgb(5, 15, 25), original) == Rgb(5, 15, 25));

    const uint32_t flowers[]={Rgb(1,2,3),Rgb(4,5,6),Rgb(7,8,9),Rgb(10,11,12)};
    // A panel samples the same screen-space flower as the surrounding backdrop,
    // independently of the panel's own source coordinate and integer scale.
    assert(port::SamplePanelBackdrop(flowers,2,2,-2,-1,3,1,2)==flowers[3]);
    assert(port::SamplePanelBackdrop(flowers,2,2,-2,-1,3,0,1)==flowers[0]);
    assert(!port::SamplePanelBackdrop(flowers,2,2,-2,-1,3,4,2));
    assert(!port::SamplePanelBackdrop(flowers,2,2,0,0,0,0,0));
    assert(!port::SamplePanelBackdrop(flowers,3,2,0,0,1,0,0));
    std::vector<port::PanelMix> shadows(320*224),covers(320*224);
    for(int y=12;y<152;y++)for(int x=304;x<308;x++)shadows[y*320+x]=dark;
    assert(port::UniformPictureShadowRecipe(shadows,covers).has_value());
    shadows[80*320+305].lowerWeight=12;
    assert(!port::UniformPictureShadowRecipe(shadows,covers));
    shadows[80*320+305]={};
    covers[80*320+305]=dark;
    assert(port::UniformPictureShadowRecipe(shadows,covers).has_value());
    covers[80*320+305].topRgb=Rgb(248,248,248);
    assert(!port::UniformPictureShadowRecipe(shadows,covers));
    std::vector<uint32_t> storage;
    assert(port::ResizePanelBuffer(storage,16) && storage.size()==16);
    assert(!port::ResizePanelBuffer(storage,16*1024*1024+1) && storage.size()==16);
    assert(port::CompositePanelPixel({}, 0, original) == original);
    assert(port::CompositePanelPixel({0, 33, {}}, 0, original) == original);
    assert(port::CompositePanelPixel({0, 11, {0, 256, 0}}, 0, original) == original);
}
