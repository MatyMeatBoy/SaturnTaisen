#include "kabe.h"
#include <cassert>
int main() {
    std::vector<uint8_t> data(76672);
    data[2]=0x80;data[3]=0x1F; // palette 1 red
    for(size_t i=0x1380;i<data.size();i++)data[i]=1;
    std::vector<uint32_t> pixels;
    assert(port::DecodeKabe(data,pixels) && pixels.size()==320*224);
    for(auto value:pixels)assert((value&0xFFFFFF)==0x0000F8);
    data[0x202]=0x7F;data[0x203]=0xFF;
    assert(!port::DecodeKabe(data,pixels)); // invalid tile address cannot read beyond file
    data.resize(500);assert(!port::DecodeKabe(data,pixels));
}
