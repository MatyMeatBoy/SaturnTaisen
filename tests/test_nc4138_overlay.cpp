#include "registered_body_overlay.h"
#include <array>
#include <cassert>
using namespace port::registered_body;
int main() {
    const auto& entry=kEntries[0];
    constexpr auto kSize=kEntries[0].width;
    std::array<uint8_t, kSize*kSize> indices{};
    std::array<uint8_t, 512> palette{};
    std::array<uint32_t, 320*224> screen{};
    std::array<uint8_t, 320*224> source{}, white{};
    const auto at = (16+14)*320 + 100+12;
    indices[14*kSize+12]=2;
    palette[5]=0x1F;
    screen[at]=248;
    assert(Visible(entry,indices,palette,screen,source,white,100,16));
    source[at]=4;
    assert(!Visible(entry,indices,palette,screen,source,white,100,16));
    source[at]=0;
    white[at]=1;
    assert(!Visible(entry,indices,palette,screen,source,white,100,16));
    white[at]=0;
    screen[at]=0;
    assert(!Visible(entry,indices,palette,screen,source,white,100,16));
    assert(!Visible(entry,indices,palette,screen,source,white,200,16));
    const std::vector<uint32_t> donor(230*254,0xFF332211);
    const auto crop=Register(entry,indices,palette,donor);
    assert(crop.size()==4*kSize*kSize);
    assert(crop[28*kSize*2+24]==0xFF332211);
    assert(crop[0]==0 && crop[28*kSize*2+26]==0);
    indices[0]=1;
    assert(Register(entry,indices,palette,donor).empty());
}
