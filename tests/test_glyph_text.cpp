#include "glyph_text.h"
#include <array>
#include <cassert>
#include <vector>
int main() {
    std::vector<uint8_t> atlas(32768);
    for(int c=32;c<=126;c++) for(int n=0;n<128;n++) atlas[(c-1)*128+n]=static_cast<uint8_t>(c+n);
    assert(!port::KnownEnglishAtlas(atlas)); // do not map Japanese/unknown fonts as ASCII
    auto tile=std::span<const uint8_t>(atlas.data()+('W'-1)*128,128);
    assert(port::DecodeGlyph(atlas,tile)=='W');
    std::array<uint8_t,128> changed{};std::memcpy(changed.data(),tile.data(),128);changed[3]^=1;
    assert(port::DecodeGlyph(atlas,changed)==0);
    assert(port::DecodeGlyph(atlas,std::span<const uint8_t>(changed.data(),127))==0);
    std::memcpy(atlas.data()+('V'-1)*128,tile.data(),128);
    assert(port::DecodeGlyph(atlas,tile)==0); // exact match alone must still be unique
    std::array<uint8_t,128> ellipsis{};ellipsis[70]=0x11;ellipsis[72]=0x11;ellipsis[74]=0x11;
    std::memcpy(atlas.data()+(133-1)*128,ellipsis.data(),128);
    assert(port::DecodeCodepoint(atlas,ellipsis)==U'\u2026');
    assert(port::GlyphUtf8(U'\u2026')=="\xE2\x80\xA6");
}
