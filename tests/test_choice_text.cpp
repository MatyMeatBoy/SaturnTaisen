#include "choice_text.h"

#include <array>
#include <cassert>
#include <vector>

struct Command {std::array<uint16_t,16> words{};};
struct Sprite {Command command;std::array<uint8_t,128> pixels{};int x=0,y=0;};
struct Plate {uint16_t owner=0,underOwner=0;};

int main() {
    std::array<uint8_t,32768> atlas{};
    atlas[('A'-1)*128]=0x10;
    atlas[('B'-1)*128]=0x20;
    atlas[(' '-1)*128+1]=0x10;
    std::vector<Sprite> sprites{{{{1,0,0xA0,0xC500,0,0x0110}},{},160,32}};
    std::vector<uint8_t> source(320*224,5);
    std::vector<uint32_t> screen(320*224,0xFFFFFFFF);
    std::vector<Plate> plate(320*224);
    auto letter=[&](int y,int x,char c,uint16_t color) {
        Sprite sprite{{{0,0,0x80,color,0,0x0210}},{},x,y};
        std::copy_n(atlas.begin()+(c-1)*128,128,sprite.pixels.begin());
        sprites.push_back(sprite);
        const auto at=y*320+x;
        source[at]=0;screen[at]=color==0xC570?0xFF303030:0xFF101010;
        plate[at].owner=uint16_t(sprites.size());
    };
    auto row=[&](int y,uint16_t color) {
        letter(y,160,'A',color);letter(y,168,'B',color);
    };
    auto recognize=[&] {return port::MatchChoiceText(std::span<const Sprite>(sprites),atlas,source,screen,std::span<const Plate>(plate));};
    row(62,0xC570);row(94,0xC510);
    auto match=recognize();
    assert(match && match->lines.size()==2 && match->ink.size()==4);
    assert(match->lines[0].x==160 && match->lines[0].y==62 && match->lines[0].text==U"AB" && match->lines[0].color==0xFF303030);
    assert(match->lines[1].y==94 && match->lines[1].color==0xFF101010);
    const size_t shared=62*320+168;
    atlas[('A'-1)*128+4]=0x10;
    sprites[1].pixels[4]=0x10;
    sprites[3].pixels[4]=0x10;
    const size_t other=94*320+168;
    plate[shared].underOwner=2;
    plate[other].underOwner=4;
    match=recognize();assert(match && match->ink.size()==4);
    plate[shared].owner=1;assert(!recognize());plate[shared].owner=3;
    plate[shared].underOwner=1;assert(!recognize());plate[shared].underOwner=2;
    plate[shared].owner=0;assert(!recognize());plate[shared].owner=3;
    atlas[('A'-1)*128+4]=0;
    sprites[1].pixels[4]=0;
    sprites[3].pixels[4]=0;
    plate[shared].underOwner=0;
    plate[other].underOwner=0;
    source[62*320+160]=3;assert(!recognize());source[62*320+160]=0;
    sprites[0].command.words[5]=0;assert(!recognize());sprites[0].command.words[5]=0x0110;
    sprites[2].x+=8;assert(!recognize());sprites[2].x-=8;
    const auto old=sprites[2].pixels;
    sprites[2].pixels.fill(0xFF);assert(!recognize());sprites[2].pixels=old;
    letter(94,160,'A',0xC510);assert(!recognize());

    sprites.resize(1);
    row(54,0xC510);row(78,0xC570);row(102,0xC510);
    match=recognize();assert(match && match->lines.size()==3);
    assert(match->lines[1].y==78 && match->lines[1].color==0xFF303030);
    sprites[5].command.words[3]=0xC570;sprites[6].command.words[3]=0xC570;
    assert(!recognize());

    assert((port::ChoiceTextClip(20,30,3,16,8)==std::array<int,4>{20,150,884,426}));
}
