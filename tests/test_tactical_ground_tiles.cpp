#include "tactical_ground.h"

#include <cassert>

using port::PcSprite;
using namespace port::tactical_ground;

void putWord(std::vector<uint8_t>& bytes, size_t where, unsigned value) {
    bytes.at(where) = static_cast<uint8_t>(value >> 8);
    bytes.at(where + 1) = static_cast<uint8_t>(value);
}

std::vector<uint8_t> descriptor() {
    std::vector<uint8_t> bytes(128);
    putWord(bytes, 18, 64);  // chunk offset
    putWord(bytes, 22, 64);  // chunk size
    putWord(bytes, 26, 13);
    putWord(bytes, 64, 3);
    putWord(bytes, 66, 1);
    putWord(bytes, 80 + 4, 64);
    putWord(bytes, 96, 1);
    putWord(bytes, 112 + 6, 64);
    return bytes;
}

int main() {
    const Entry entry{"fixture", 0, 0, 0, 0x40000, 64, 64, 64};
    PcSprite color{0,64,64,0,std::vector<uint32_t>(4096,0xFF302010)};
    color.pixels[0]=0xFFFFFF00;
    PcSprite invisible{1,64,64,0,std::vector<uint32_t>(4096,0x00302010)};
    const std::vector<PcSprite> sprites{color,invisible};
    const auto bytes=descriptor();
    const auto world=AssembleGroundTiles(bytes,sprites,entry);
    assert(world.size()==4096);
    assert(world[32]==0 && world[33]==0xFF302010);
    assert(world[32*64]==0 && world[32*64+1]==0xFF302010);
    assert(world[33*64+40]==0);

    auto duplicate=bytes;
    putWord(duplicate,112+4,64);
    putWord(duplicate,112+6,0);
    assert(AssembleGroundTiles(duplicate,sprites,entry).empty());
    auto invalidIndex=bytes;
    putWord(invalidIndex,112,2);
    assert(AssembleGroundTiles(invalidIndex,sprites,entry).empty());
    auto offGrid=bytes;
    putWord(offGrid,112+4,1);
    assert(AssembleGroundTiles(offGrid,sprites,entry).empty());
    putWord(offGrid,112+4,128);
    assert(AssembleGroundTiles(offGrid,sprites,entry).empty());
    auto truncated=bytes;
    truncated.pop_back();
    assert(AssembleGroundTiles(truncated,sprites,entry).empty());
    auto extra=bytes;
    putWord(extra,64,2);
    assert(AssembleGroundTiles(extra,sprites,entry).empty());
    auto reserved=bytes;
    putWord(reserved,112+8,1);
    assert(AssembleGroundTiles(reserved,sprites,entry).empty());
}
