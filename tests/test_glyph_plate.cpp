#include "renderer.h"

#include <array>
#include <vector>

#include <cassert>

static void ownership() {
    constexpr uint16_t bevel=0x95AA;
    constexpr uint16_t ink=0xC51D;
    satrecomp::video::GlyphPlateStamp edge;
    edge.RecordWrite(9,bevel,ink);
    assert(edge.Owner(ink)==9);
    assert(edge.before==bevel);
    assert(edge.Owner(ink^1)==0);
    edge.RecordWrite(9,ink,ink);
    assert(edge.Owner(ink)==9 && edge.before==bevel);

    // A later draw of the same word can still own this pixel.
    edge.RecordWrite(0,ink,ink);
    assert(edge.Owner(ink)==0);
    edge.RecordWrite(10,ink,ink);
    assert(edge.Owner(ink)==0);

    satrecomp::video::GlyphPlateStamp overlap;
    overlap.RecordWrite(1,bevel,ink);
    overlap.RecordWrite(2,ink,ink);
    assert(overlap.Owner(ink)==2 && overlap.underOwner==1 && overlap.before==bevel);
    overlap.RecordWrite(2,ink,ink);
    assert(overlap.Owner(ink)==2 && overlap.underOwner==1 && overlap.before==bevel);
    overlap.RecordWrite(3,ink,ink);
    assert(overlap.Owner(ink)==0);

    satrecomp::video::GlyphPlateStamp floral;
    floral.RecordWrite(0,0,0);
    floral.RecordWrite(1,0,ink);
    assert(floral.Owner(ink)==1 && floral.before==0);
}

using namespace satrecomp::video;

static void restoreBevel() {
    std::vector<uint8> vram1(0x80000),vram2(0x80000),cram(0x1000),fb0(0x40000),fb1(0x40000);
    Renderer render({vram1.data(),{fb0.data(),fb1.data()},vram2.data(),cram.data()});
    const uint32* shown=nullptr;
    render.SetMode(Renderer::Mode::Software,[&](uint32* pixels,uint32,uint32){shown=pixels;});
    render.SetResolution(320,224,false);
    render.WriteVdp2Reg(0x00,0x8000);
    render.WriteVdp2Reg(0xE0,0x23);
    render.WriteVdp2Reg(0xF0,0x0707);
    render.WriteVdp2Reg(0xF2,0x0707);
    render.LatchDisplayMode();
    render.CapturePresentation(true);
    render.CaptureGlyphPlate(true);

    auto put = [&](size_t at,uint16 value) {
        vram1[at]=uint8(value>>8);vram1[at+1]=uint8(value);
    };
    auto command = [&](size_t at,const std::array<uint16,16>& words) {
        for(size_t i=0;i<words.size();++i)put(at+i*2,words[i]);
    };
    constexpr unsigned x=304,y=176;
    constexpr uint16 bevel=0x95AA,ink=0xC51D;
    constexpr uint32 bevelABGR=0xFF286850;
    command(0,{9,0,0,0,0,0,0,0,0,0,319,223});
    command(32,{0,0,0xA8,0,0x200,0x0101,x,y});
    command(64,{0,0,0x80,0xC510,0x210,0x0210,x-8,y-4});
    command(96,{0,0,0xA8,0,0x220,0x0101,x,y});
    command(128,{0,0,0x80,0xC510,0x210,0x0210,x-8,y-4});
    put(0x1000,bevel);
    vram1[0x1080+4*8+4]=0xD0;
    put(0x1100,ink);
    auto frame = [&](bool laterDraw,bool guestWrite,bool secondGlyph=false) {
        render.BeginDrawing();
        render.DrawCommand(0);
        render.DrawCommand(32);
        render.DrawCommand(64);
        if(laterDraw)render.DrawCommand(96);
        if(secondGlyph)render.DrawCommand(128);
        render.EndDrawing();
        if(guestWrite)render.Vdp1FramebufferWritten();
        render.SwapFramebuffer();
        render.BeginFrame();
        for(unsigned line=0;line<224;++line)render.RenderLine(line);
        render.EndFrame();
        assert(shown);
        return render.PresentationFrame().glyphPlate[y*320+x];
    };
    auto plate=frame(false,false);
    assert(plate.owner==3 && plate.nativeRgb==bevelABGR && plate.foregroundRgba==bevelABGR);
    assert(plate.panelMix.lowerWeight==0);
    constexpr uint32 inkBgr=((ink&31)<<3)|(((ink>>5)&31)<<11)|(((ink>>10)&31)<<19);
    assert((shown[y*320+x]&0xFFFFFF)==inkBgr);
    // Compose the same saved-under pixel under the native sprite color offset.
    render.WriteVdp2Reg(0x110,0x0040);
    render.WriteVdp2Reg(0x114,0x01FC);
    render.WriteVdp2Reg(0x116,0x01FC);
    render.WriteVdp2Reg(0x118,0x01FC);
    plate=frame(false,false);
    assert(plate.owner==3 && plate.nativeRgb==0xFF24644C);
    assert(plate.foregroundRgba==plate.nativeRgb && plate.panelMix.lowerWeight==0);
    plate=frame(false,false,true);
    assert(plate.owner==4 && plate.underOwner==3 && plate.nativeRgb==0xFF24644C);
    assert(frame(true,false).owner==0);
    assert(frame(false,true).owner==0);
}

int main() {
    ownership();
    restoreBevel();
}
