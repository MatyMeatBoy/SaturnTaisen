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
    std::copy_n(atlas.begin(),frame.size(),frame.begin());
    std::copy_n(atlas.begin()+48*40,640,frame.begin()+4*40);
    std::copy_n(atlas.begin()+64*40,640,frame.begin()+25*40);
    match=port::MatchPortraitFrame(atlas,frame);
    assert(match && !match->ambiguous && match->part==1 && match->y==4 && match->part2==2 && match->y2==25);
    for(size_t i=48*40;i<64*40;i+=5)atlas[i]=0;
    std::copy_n(atlas.begin(),frame.size(),frame.begin());
    for(size_t i=0;i<640;i++)if(atlas[48*40+i])frame[7*40+i]=atlas[48*40+i];
    match=port::MatchPortraitFrame(atlas,frame);
    assert(match && match->part==1 && match->y==7 && match->masked);
    std::copy_n(atlas.begin()+48*40,640,atlas.begin()+64*40);
    match=port::MatchPortraitFrame(atlas,frame);assert(match && match->ambiguous);
    assert(!port::MatchPortraitFrame(std::span<const uint8_t>(atlas.data(),10),frame));
    assert(port::PortraitDensity(1)==1);
    for(int scale:{2,3,4,5,6})assert(port::PortraitDensity(scale)==2);
    std::array<uint8_t,512> palette{};palette[3]=31; // colour 1: native RGB555 red
    frame.fill(1);std::array<uint32_t,320*224> pixels{};pixels.fill(0xFF0000F8);
    assert(port::PortraitPixelsVisible(frame,palette,pixels,320,224,16,160));
    pixels[160*320+16]=0xFF00FF00;
    assert(!port::PortraitPixelsVisible(frame,palette,pixels,320,224,16,160));
    frame[0]=0;assert(port::PortraitPixelsVisible(frame,palette,pixels,320,224,16,160));
    frame.fill(0);assert(!port::PortraitPixelsVisible(frame,palette,pixels,320,224,16,160));

    // Trusted VDP2 metadata describes exactly one white mix across opaque pixels.
    using port::MatchPortraitVisibility;
    std::array<uint8_t,320*224> whiteWeights{};
    frame.fill(1);
    frame[0]=0;
    pixels.fill(0xFF0000F8);
    assert(MatchPortraitVisibility(frame,palette,pixels,320,224,16,160,whiteWeights)==0);
    assert(!port::PortraitWhiteWeight(33) && !port::PortraitWhiteWeight(255));
    for(int fade=1;fade<=32;++fade) { // every step of the Saturn fade, not only 5/15/25
        const uint8_t weight=uint8_t(fade);
        const auto channel=uint32_t((248*weight)>>5);
        const uint32_t mixed=0xFF0000F8|(channel<<8)|(channel<<16);
        for(int row=0;row<48;++row)for(int column=0;column<40;++column) {
            const auto at=(160+row)*320+16+column;
            pixels[at]=mixed;whiteWeights[at]=weight;
        }
        const auto at=160*320+16;
        pixels[at]=0xFF00FF00;whiteWeights[at]=0; // original transparency is ignored
        assert(!port::PortraitPixelsVisible(frame,palette,pixels,320,224,16,160));
        assert(MatchPortraitVisibility(frame,palette,pixels,320,224,16,160,whiteWeights)==weight);
        pixels[at+1]^=1;
        assert(!MatchPortraitVisibility(frame,palette,pixels,320,224,16,160,whiteWeights));
        pixels[at+1]^=1;
        whiteWeights[at+1]=0;
        assert(!MatchPortraitVisibility(frame,palette,pixels,320,224,16,160,whiteWeights));
        whiteWeights[at+1]=weight;
        const uint32_t rgba=0x7FA06020;
        assert(port::ApplyPortraitWhiteMix(rgba,weight)==(0x7F000000u |
               ((32*(32-weight)+248*weight)>>5) |
               (((96*(32-weight)+248*weight)>>5)<<8) |
               (((160*(32-weight)+248*weight)>>5)<<16)));
        assert(port::ApplyPortraitWhiteMix(0x00A06020,weight)==0x00A06020);
    }
    whiteWeights.fill(24);
    assert(!MatchPortraitVisibility(frame,palette,pixels,320,224,16,160,whiteWeights));
    assert(!MatchPortraitVisibility(frame,palette,pixels,320,224,16,160,std::span(whiteWeights).first(1)));
    // Exact white is ambiguous from RGB alone. Only the renderer's weight is used.
    palette[2]=0x7F;palette[3]=0xFF;
    pixels.fill(0xFFF8F8F8);whiteWeights.fill(15);
    assert(MatchPortraitVisibility(frame,palette,pixels,320,224,16,160,whiteWeights)==15);
    frame.fill(0);
    assert(!MatchPortraitVisibility(frame,palette,pixels,320,224,16,160,whiteWeights));
}
