#include "background_codec.h"
#include <cassert>
#include <random>
int main() {
    auto verify=[](const std::vector<uint32_t>& pixels,unsigned expected) {
        auto packed=port::PackBackgroundPixels(pixels);assert(packed.format==expected);
        std::vector<uint32_t> decoded;
        assert(port::UnpackBackgroundPixels(packed.bytes,packed.format,pixels.size(),decoded));assert(decoded==pixels);
        for(bool compress:{false,true}) {
            auto stored=port::CompressBackgroundPixels(packed.bytes,compress);
            std::vector<uint8_t> raw;
            assert(port::DecompressBackgroundPixels(stored.bytes,stored.codec,packed.bytes.size(),raw));assert(raw==packed.bytes);
            if(stored.codec) {
                auto extra=stored.bytes;extra.push_back(0);
                assert(!port::DecompressBackgroundPixels(extra,stored.codec,packed.bytes.size(),raw));
                stored.bytes.pop_back();assert(!port::DecompressBackgroundPixels(stored.bytes,stored.codec,packed.bytes.size(),raw));
            }
        }
        packed.bytes.pop_back();assert(!port::UnpackBackgroundPixels(packed.bytes,packed.format,pixels.size(),decoded));
    };
    std::vector<uint32_t> indexed(8192);
    for(size_t i=0;i<indexed.size();i++)indexed[i]=i%2?0xFF0000F8:0xFF00F800;
    verify(indexed,1);
    auto badIndex=port::PackBackgroundPixels(indexed);badIndex.bytes.back()=255;
    std::vector<uint32_t> rejected;
    assert(!port::UnpackBackgroundPixels(badIndex.bytes,badIndex.format,indexed.size(),rejected));
    std::vector<uint32_t> shift,full;
    for(unsigned i=0;i<4096;i++) {
        const unsigned r=(i>>10)&31,g=(i>>5)&31,b=i&31;
        shift.push_back(0xFF000000u|(r<<3)|(g<<11)|(b<<19));
        full.push_back(0xFF000000u|(r*255/31)|(g*255/31<<8)|(b*255/31<<16));
    }
    verify(shift,2);verify(full,3);
    std::mt19937 random(16546);std::vector<uint32_t> rgba;
    for(int i=0;i<1024;i++)rgba.push_back(random());
    verify(rgba,0);
    std::vector<uint32_t> decoded;
    assert(!port::UnpackBackgroundPixels({},99,4,decoded));
    std::vector<uint8_t> raw;
    assert(!port::DecompressBackgroundPixels({},99,4,raw));
    assert(!port::DecompressBackgroundPixels({},0,864*486*4+1,raw));
}
