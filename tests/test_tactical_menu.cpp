#include "tactical_menu.h"
#include <algorithm>
#include <array>
#include <cassert>
#include <vector>

using port::TacticalMenuSprite;

// Hashes and viewport geometry from disc 1 VDP1 lists.
static constexpr std::array<uint64_t,5> tabs{
    0x9D8E240F6AB586BC,0x75F0B7757F6FCC84,0x242ACB24C7364114,
    0xACFE13240DF0957C,0xF91F81A1290CA869
};
static constexpr std::array<std::array<uint64_t,3>,5> labels{{
    {0x7FF4F719DAF08740}, {0x23ABA1E5F681994B,0xDC7CD3F64BAD9A36},
    {0xB430B4DEFA5702F6,0xEE580AB839732AFF,0x00396DF5443F4349},
    {0x745709153803CE04,0xBA095F71BC2889B2,0xBAA90DCC46388B80},
    {0x8F6274AF2C1E7779}
}};
static std::vector<TacticalMenuSprite> menu(unsigned tab,int x,int y,unsigned selected) {
    static constexpr std::array<uint64_t,3> frames{0x549B32456EF87DB3,0xD17D592842A221CD,0xD46C77EFDE420A6F};
    const unsigned rows=std::count_if(labels[tab].begin(),labels[tab].end(),[](uint64_t hash){return hash!=0;});
    const unsigned height=32+16*rows;
    const int tabX=x+8+16*static_cast<int>(tab),popupY=y+32-static_cast<int>(height);
    std::vector<TacticalMenuSprite> sprites{{0x18FDBFE27D4349D5,x,y,96,32,0,0x88,0xFFEC}};
    for(unsigned i=0;i<tabs.size();++i)sprites.push_back({tabs[i],x+8+16*static_cast<int>(i),y+8,16,16,0,0x88,0xFFEC});
    sprites.push_back({frames[rows-1],tabX-8,popupY,40,height,0,0x88,0xFFEC});
    sprites.push_back({0x02175A89080041A4,tabX,popupY+8+16*static_cast<int>(selected),24,16,0,0x88,0xFFF0});
    for(unsigned i=0;i<rows;++i)sprites.push_back({labels[tab][i],tabX,popupY+8+16*static_cast<int>(i),24,16,0,0x88,0xFFEC});
    sprites.push_back(sprites[tab+1]);
    return sprites;
}

int main() {
    for(unsigned tab=0;tab<5;++tab) {
        const auto sprites=menu(tab,112,56,0);
        const auto layout=port::FindTacticalMenuLayout(sprites);
        assert(layout && layout->frame==6 && layout->end==sprites.size()-1);
        assert(layout->frameHeight==sprites[6].height-24);
        assert(sprites[6].y+layout->deltaY+int(layout->frameHeight)==sprites[0].y);
        assert(layout->deltaY==-8);
        assert(!port::FindTacticalMenuLayout(std::span(sprites).first(sprites.size()-1)));
    }
    auto attack=menu(1,136,68,1);
    attack[1].hash=0x4ACD7121B85349BD;
    assert(port::FindTacticalMenuLayout(attack));
    attack[7].y+=1;
    assert(!port::FindTacticalMenuLayout(attack));
    attack=menu(1,136,68,1);
    attack[7].color=0xFFEC;
    assert(!port::FindTacticalMenuLayout(attack));
    attack=menu(1,136,68,1);
    attack[8].hash^=1;
    assert(!port::FindTacticalMenuLayout(attack));
    auto low=menu(3,112,40,0);
    assert(!port::FindTacticalMenuLayout(low));
    auto duplicate=menu(0,112,56,0);
    const auto more=menu(4,112,56,0);
    duplicate.insert(duplicate.end(),more.begin(),more.end());
    assert(!port::FindTacticalMenuLayout(duplicate));
    auto left=menu(0,0,48,0);
    assert(port::FindTacticalMenuLayout(left));
    auto right=menu(4,224,48,0);
    assert(port::FindTacticalMenuLayout(right));
}
