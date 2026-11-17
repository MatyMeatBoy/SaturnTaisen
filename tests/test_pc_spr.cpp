#include "pc_spr.h"
#include <cassert>
int main() {
    std::vector<uint8_t> data(100);
    std::memcpy(data.data(),"SEGA SPRED 02.0M",16);
    auto put=[&](int at,unsigned value,int size){for(int i=0;i<size;i++)data[at+i]=value>>(8*(size-i-1));};
    put(16,64,4);put(20,36,4);put(24,2,4);
    put(64,1,2);put(80,2,2);put(82,1,2);put(84,5,2);put(92,4,4);
    data[96]=0;data[97]=0x7C;data[98]=0x1F;data[99]=0;
    std::vector<port::PcSprite> images;std::string error;
    assert(port::DecodePcSprites(data,images,error));assert(images.size()==1);
    assert(images[0].pixels[0]==0xFF0000FF && images[0].pixels[1]==0xFFFF0000);
    data[12]='9';assert(!port::DecodePcSprites(data,images,error));data[12]='2';
    put(84,0x25,2);assert(!port::DecodePcSprites(data,images,error));put(84,5,2);
    // Four literal RGB555 bytes, with a flag byte. Verify real compressed decoding too.
    data.resize(101);put(20,37,4);put(92,5,4);put(84,0x15,2);
    data[96]=15;data[97]=0;data[98]=0x7C;data[99]=0x1F;data[100]=0;
    assert(port::DecodePcSprites(data,images,error));
    assert(images[0].pixels[0]==0xFF0000FF && images[0].pixels[1]==0xFFFF0000);
    data.resize(100);put(20,36,4);put(92,4,4);
    data[96]=0;data[97]=0x7C;data[98]=0x1F;data[99]=0;
    put(84,0x15,2);assert(!port::DecodePcSprites(data,images,error)); // malformed compressed stream
    put(92,10000,4);assert(!port::DecodePcSprites(data,images,error));
    data.resize(12);assert(!port::DecodePcSprites(data,images,error));
}
