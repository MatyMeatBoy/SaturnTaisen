#include "disc_files.h"
#include <array>
#include <cassert>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <vector>

// Synthetic ISO only; no game data. Deliberately impossible and truncated extents
// exercise rejection before allocation and clearing after a partial read.
int main(int argc, char** argv) {
    assert(argc == 2);
    std::vector<uint8_t> iso(24 * 2048);
    auto le32 = [&](size_t at, uint32_t value) {
        for (int n = 0; n < 4; ++n) iso[at+n] = uint8_t(value >> (8*n));
    };
    std::memcpy(iso.data(), "SEGA SEGASATURN ", 16);
    std::memcpy(iso.data()+16*2048+1, "CD001", 5);
    le32(16*2048+158, 18);
    le32(16*2048+166, 2048);
    size_t next = 18*2048;
    auto entry = [&](const char* name, uint32_t lba, uint32_t size) {
        auto len = std::strlen(name);
        iso[next] = uint8_t(34+len);
        le32(next+2,lba); le32(next+10,size);
        iso[next+32] = uint8_t(len);
        std::memcpy(iso.data()+next+33,name,len);
        next += 34+len;
    };
    entry("GOOD.BIN;1",20,4);
    entry("HUGE.BIN;1",21,0xffffffff);
    entry("PART.BIN;1",23,3000);
    iso[20*2048]=1; iso[20*2048+1]=2;
    iso[20*2048+2]=3; iso[20*2048+3]=4;
    auto path = std::filesystem::path(argv[1]) / "bounded.iso";
    { std::ofstream out(path,std::ios::binary); out.write(reinterpret_cast<const char*>(iso.data()),iso.size()); }
    port::DiscFiles files;
    assert(files.Open(path.string()));
    std::vector<uint8_t> bytes{99};
    assert(!files.ReadBounded("huge.bin",bytes,8*1024*1024) && bytes.empty());
    bytes={99};
    assert(!files.ReadBounded("good.bin",bytes,3) && bytes.empty());
    assert(files.ReadBounded("good.bin",bytes,4));
    assert((bytes==std::vector<uint8_t>{1,2,3,4}));
    assert(!files.ReadBounded("missing.bin",bytes,4) && bytes.empty());
    bytes={99};
    assert(!files.ReadBounded("part.bin",bytes,3000) && bytes.empty());
}
