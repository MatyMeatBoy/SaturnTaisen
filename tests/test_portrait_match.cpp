#include "portrait_match.h"
#include <cassert>
#include <algorithm>
int main() {
    std::array<uint8_t,3200> atlas{};
    for(size_t i=0;i<atlas.size();i++)atlas[i]=uint8_t(1+((i*71+i/40*17)%251));
    std::array<uint8_t,1920> frame{};std::copy_n(atlas.begin(),frame.size(),frame.begin());
    auto match=port::MatchPortraitFrame(atlas,frame);assert(match && match->part==0);
    for(int part=1;part<=2;part++)for(int y:{0,7,19,32}) {
        std::copy_n(atlas.begin(),frame.size(),frame.begin());
        std::copy_n(atlas.begin()+(48+(part-1)*16)*40,640,frame.begin()+y*40);
        match=port::MatchPortraitFrame(atlas,frame);assert(match && match->part==part && match->y==y);
    }
    frame[0]^=127;frame[1000]^=73;frame[1919]^=34;
    assert(!port::MatchPortraitFrame(atlas,frame));
    for(size_t i=48*40;i<64*40;i+=5)atlas[i]=0;
    std::copy_n(atlas.begin(),frame.size(),frame.begin());
    for(size_t i=0;i<640;i++)if(atlas[48*40+i])frame[7*40+i]=atlas[48*40+i];
    match=port::MatchPortraitFrame(atlas,frame);
    assert(match && match->part==1 && match->y==7 && match->masked);
    std::copy_n(atlas.begin()+48*40,640,atlas.begin()+64*40);
    match=port::MatchPortraitFrame(atlas,frame);assert(match && match->ambiguous);
    assert(!port::MatchPortraitFrame(std::span<const uint8_t>(atlas.data(),10),frame));
    assert(port::PortraitDensity(1)==1 && port::PortraitDensity(3)==1 && port::PortraitDensity(4)==2);
    std::array<uint8_t,512> palette{};palette[3]=31; // colour 1: native RGB555 red
    frame.fill(1);std::array<uint32_t,320*224> pixels{};pixels.fill(0xFF0000F8);
    assert(port::PortraitPixelsVisible(frame,palette,pixels,320,224,16,160));
    pixels[160*320+16]=0xFF00FF00;
    assert(!port::PortraitPixelsVisible(frame,palette,pixels,320,224,16,160));
    frame[0]=0;assert(port::PortraitPixelsVisible(frame,palette,pixels,320,224,16,160));
    frame.fill(0);assert(!port::PortraitPixelsVisible(frame,palette,pixels,320,224,16,160));
}
