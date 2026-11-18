#include "tactical_extension.h"
#include <cassert>
#include <vector>
#include <algorithm>
int main() {
    assert(!port::KeepStage01Sprite(2,0x80,0x2500,623,65,0x2B12B3C4BC5A3266ull));
    assert(port::KeepStage01Sprite(2,0x80,0x2200,623,65,0x2B12B3C4BC5A3266ull));
    assert(port::KeepStage01Sprite(2,0x80,0x2500,400,65,0x2B12B3C4BC5A3266ull));
    assert(port::KeepStage01Sprite(2,0x80,0x2500,623,65,123));
    std::vector<uint32_t> canvas(398*224,0xFF010203),patch(41*224,0xFF112233);
    std::vector<uint8_t> source(320*224,4);
    std::vector<std::array<uint32_t,2>> world(224);
    for(unsigned y=0;y<224;y++)world[y]={273,48+y};
    assert(port::ApplyTacticalExtension(canvas,398,source,39,world,patch,41,224,655,48));
    assert(canvas[381]==0xFF010203 && canvas[382]==0xFF112233);
    // Moving the camera shifts the extension in the opposite screen direction.
    std::fill(canvas.begin(),canvas.end(),0xFF010203);
    for(unsigned y=0;y<224;y++)world[y]={300,48+y};
    source[316]=0; // a native foreground unit must remain above the extension
    assert(port::ApplyTacticalExtension(canvas,398,source,39,world,patch,41,224,655,48));
    assert(canvas[354]==0xFF010203 && canvas[355]==0xFF010203 && canvas[356]==0xFF112233);
    const auto protectedCanvas=canvas;
    assert(!port::ApplyTacticalExtension(canvas,398,source,39,world,std::span<const uint32_t>(patch).first(1),41,224,655,48));
    assert(canvas==protectedCanvas);
    std::fill(canvas.begin(),canvas.end(),0xFF010203);
    assert(port::ApplyTacticalExtension(canvas,398,source,39,world,patch,41,224,655,48,{-256,-256,-256}));
    assert(canvas[356]==0xFF000000); // extension must fade with its terrain
    std::fill(canvas.begin(),canvas.end(),0xFF010203);
    std::vector<uint8_t> spriteMask(canvas.size());spriteMask[356]=1;
    assert(port::ApplyTacticalExtension(canvas,398,source,39,world,patch,41,224,655,48,{},spriteMask));
    assert(canvas[356]==0xFF010203 && canvas[357]==0xFF112233);
}
