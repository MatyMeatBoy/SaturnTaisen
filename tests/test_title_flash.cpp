#include "title_flash.h"
#include <array>
#include <cassert>
#include <vector>
struct Sprite {
    struct {std::array<uint16_t,16> words{};} command;
    std::vector<uint8_t> pixels;
    int x=0,y=0;
};
int main() {
    std::vector<uint32_t> frame(320*224,0xffe6d4e6);
    std::vector<uint8_t> source(frame.size(),0);
    Sprite flash;
    flash.command.words[0]=0x1000;
    flash.command.words[2]=0x00a8;
    flash.command.words[5]=0x28e0;
    flash.pixels.resize(320*224*2);
    for(size_t i=0;i<flash.pixels.size();i+=2) {flash.pixels[i]=0xff;flash.pixels[i+1]=0xbf;}
    std::vector<Sprite> sprites{flash};
    auto read=[&] {return port::AnalyzeTitleFlash(frame,source,0x91E480C617AD7F6Cull,std::span<const Sprite>(sprites));};
    assert(read()==frame[0]);
    frame.back()^=1;assert(!read());frame.back()^=1;
    source.back()=5;assert(!read());source.back()=0;
    sprites[0].pixels.back()^=1;assert(!read());sprites[0].pixels.back()^=1;
    sprites[0].pixels.pop_back();assert(!read());sprites[0]=flash;
    sprites[0].x=1;assert(!read());sprites[0]=flash;
    sprites[0].command.words[2]=0x00a0;assert(!read());sprites[0]=flash;
    sprites[0].command.words[3]=1;assert(!read());sprites[0]=flash;
    sprites[0].command.words[5]=0x28df;assert(!read());sprites[0]=flash;
    sprites.push_back({});assert(!read());sprites.pop_back();
    Sprite clipping;clipping.command.words[0]=9;sprites.push_back(clipping);assert(read());sprites.pop_back();
    assert(!port::AnalyzeTitleFlash(frame,source,0,std::span<const Sprite>(sprites)));
    frame.pop_back();assert(!read());frame.push_back(0xffe6d4e6);
    source.pop_back();assert(!read());source.push_back(0);
    sprites.clear();assert(!read());
}
