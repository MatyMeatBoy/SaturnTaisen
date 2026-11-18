#include "background_cache.h"
#include <cassert>
#include <fstream>
int main(int argc,char** argv) {
    assert(argc==2);const auto file=std::filesystem::path(argv[1])/"test.stfb";
    auto* surface=SDL_CreateSurface(4,3,SDL_PIXELFORMAT_ABGR8888);assert(surface);
    for(int y=0;y<3;y++)for(int x=0;x<4;x++)reinterpret_cast<uint32_t*>(static_cast<uint8_t*>(surface->pixels)+y*surface->pitch)[x]=0x12345678u+x+y*4;
    assert(port::WriteBackgroundCache(file,surface));
    auto* loaded=port::ReadBackgroundCache(file,4,3);assert(loaded);
    for(int y=0;y<3;y++)for(int x=0;x<4;x++)assert(reinterpret_cast<uint32_t*>(static_cast<uint8_t*>(loaded->pixels)+y*loaded->pitch)[x]==0x12345678u+x+y*4);
    SDL_DestroySurface(loaded);
    assert(!port::ReadBackgroundCache(file,5,3));
    assert(!port::WriteBackgroundCache(file,nullptr));
    loaded=port::ReadBackgroundCache(file,4,3);assert(loaded);SDL_DestroySurface(loaded);
    SDL_FillSurfaceRect(surface,nullptr,0xFFAABBCC);
    assert(port::WriteBackgroundCache(file,surface)); // atomic replacement of an existing cache
    loaded=port::ReadBackgroundCache(file,4,3);assert(loaded);assert(static_cast<uint32_t*>(loaded->pixels)[0]==0xFFAABBCC);SDL_DestroySurface(loaded);
    {std::fstream edit(file,std::ios::in|std::ios::out|std::ios::binary);edit.seekg(33);const auto value=edit.get();edit.seekp(33);edit.put(char(value^1));}
    assert(!port::ReadBackgroundCache(file,4,3)); // payload corruption
    assert(port::WriteBackgroundCache(file,surface));
    {std::fstream edit(file,std::ios::in|std::ios::out|std::ios::binary);edit.seekp(8);edit.put(char(255));}
    assert(!port::ReadBackgroundCache(file,4,3)); // invalid width before allocation
    assert(port::WriteBackgroundCache(file,surface));
    {std::ofstream append(file,std::ios::binary|std::ios::app);append.put(0);}
    assert(!port::ReadBackgroundCache(file,4,3));
    const auto png=std::filesystem::path(argv[1])/"master.png";
    assert(SDL_SavePNG(surface,png.string().c_str()));
    std::vector<uint8_t> bytes;assert(port::ReadBackgroundPng(png,bytes));
    assert(!port::ValidBackgroundPng(bytes,5,3));
    assert(port::ValidBackgroundPng(bytes,4,3));
    bytes[16]=255;bytes[17]=255;bytes[18]=255;bytes[19]=255;
    assert(!port::ValidBackgroundPng(bytes));
    assert(!port::DecodeBackgroundPng(bytes));
    std::vector<uint8_t> legacy(32+4*12);
    std::memcpy(legacy.data(),"STFBG001",8);
    auto put=[&](int at,uint64_t n,int count){for(int i=0;i<count;i++)legacy[at+i]=uint8_t(n>>(8*i));};
    put(8,4,4);put(12,3,4);put(16,48,4);
    for(int pixel=0;pixel<12;pixel++)put(32+pixel*4,0xFFAABBCC,4);
    put(24,port::BackgroundPayloadHash(std::span<const uint8_t>(legacy.data()+32,48)),8);
    {std::ofstream old(file,std::ios::binary|std::ios::trunc);old.write(reinterpret_cast<const char*>(legacy.data()),legacy.size());}
    loaded=port::ReadBackgroundCache(file,4,3);assert(loaded);
    assert(static_cast<uint32_t*>(loaded->pixels)[0]==0xFFAABBCC);SDL_DestroySurface(loaded);
    {std::ofstream truncate(file,std::ios::binary|std::ios::trunc);truncate<<"STFBG001";}
    assert(!port::ReadBackgroundCache(file,4,3));
    SDL_DestroySurface(surface);
}
