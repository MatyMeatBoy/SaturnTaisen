#include "palette_match.h"
#include <cassert>
#include <random>
int main() {
    const std::vector<uint32_t> tie{0xFF000002,0xFF000000,0x12000002};
    port::PaletteMatcher matcher(tie);
    assert(matcher.Color(0x00000001)==0xFF000002);
    assert(matcher.Color(0x00000002)==0xFF000002);
    assert(port::PaletteMatcher({}).Color(0)==0);
    std::mt19937 random(16546);
    for(int count:{1,2,16,256,1693}) {
        std::vector<uint32_t> palette;
        for(int i=0;i<count;i++)palette.push_back(0xFF000000u|(random()&0xFFFFFF));
        if(count>2)palette.back()=palette.front();
        port::PaletteMatcher tree(palette);
        for(int query=0;query<4096;query++) {
            const uint32_t pixel=random()&0xFFFFFF;int best=200000;uint32_t expected=0;
            for(auto color:palette) {
                const int r=int(pixel&255)-int(color&255),g=int((pixel>>8)&255)-int((color>>8)&255),b=int((pixel>>16)&255)-int((color>>16)&255);
                const int distance=r*r+g*g+b*b;
                if(distance<best){best=distance;expected=color;}
            }
            assert(tree.Color(pixel)==expected);
        }
    }
}
