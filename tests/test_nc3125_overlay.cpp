#include "registered_body_overlay.h"
#include <array>
#include <cassert>
using namespace port::registered_body;
int main() {
    std::array<uint8_t, 200*96> indices{};
    std::array<uint8_t, 512> palette{};
    std::array<uint32_t, 320*224> screen{};
    std::array<uint8_t, 320*224> source{}, white{};
    const auto at = 30*320 + 80;
    indices[14*200+32]=2;
    palette[5]=31;
    screen[at]=248;
    assert(Visible(kEntries[1],indices,palette,screen,source,white,48,16));
    screen[at]=0;
    assert(!Visible(kEntries[1],indices,palette,screen,source,white,48,16));
    const std::vector<uint32_t> donor(398*205,0xFF0000FF);
    indices[0]=2;
    const auto crop=Register(kEntries[1],indices,palette,donor);
    assert(crop.size()==400*192 && crop[0]==0);
    assert(crop[28*400+64]==0xFF0000FF);
    assert(crop[28*400+66]==0);
    indices[8*200+40]=2;
    const auto feather=Register(kEntries[1],indices,palette,donor);
    assert(feather[16*400+80]!=0xFF0000FF);
}
