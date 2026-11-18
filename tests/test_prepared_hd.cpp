#include "prepared_hd.h"
#include <cassert>
#include <fstream>
#include <cstring>
int main(int argc,char** argv) {
    assert(argc==2);const auto root=std::filesystem::path(argv[1]);std::filesystem::create_directories(root/"backgrounds");
    const std::string pixel="prepared";
    std::vector<uint8_t> raw(80);std::memcpy(raw.data(),"STFHD01",8);
    auto put=[&](size_t at,uint64_t value,int bytes){for(int i=0;i<bytes;i++)raw[at+i]=uint8_t(value>>(i*8));};
    put(8,1,4);put(12,1,4);put(16,5505346,8);put(24,17275614850567186526ull,8);put(32,17,8);put(40,1,4);
    std::memcpy(raw.data()+48,"KABE0100",8);put(56,42,8);put(64,port::PreparedHash(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(pixel.data()),pixel.size())),8);put(72,pixel.size(),8);
    auto write=[&] {std::ofstream f(root/"hd-pack.stfp",std::ios::binary);f.write(reinterpret_cast<char*>(raw.data()),raw.size());};write();
    port::PreparedHdPack pack;assert(port::ReadPreparedHd(root,pack));assert(pack.portraitCount==1);
    const auto* entry=port::FindPreparedBackdrop(pack,"KABE0100",42);assert(entry && entry->bytes==pixel.size());
    assert(!port::FindPreparedBackdrop(pack,"KABE0100",43));assert(!port::FindPreparedBackdrop(pack,"../../xx",42));
    const auto file=root/"backgrounds/KABE0100.stfb";{std::ofstream f(file);f<<pixel;}
    assert(port::PreparedFileMatches(file,entry->bytes,entry->hash,2097152));
    {std::ofstream f(file);f<<"changed";}assert(!port::PreparedFileMatches(file,entry->bytes,entry->hash,2097152));
    raw[44]=1;write();assert(!port::ReadPreparedHd(root,pack));raw[44]=0;
    raw.push_back(0);write();assert(!port::ReadPreparedHd(root,pack));raw.pop_back();
    raw[48]='.';write();assert(!port::ReadPreparedHd(root,pack));
}
