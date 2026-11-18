// Invented VDP2 bitmaps; exercise the actual renderer, not a duplicate blend formula.
#include "renderer.h"
#include "portrait_match.h"
#include <array>
#include <cstdint>
#include <cstdio>
#include <vector>
#include <cassert>
#include <algorithm>

using namespace satrecomp::video;
int main() {
    std::vector<uint8_t> vram1(0x80000), vram2(0x80000), cram(0x1000), fb0(0x40000), fb1(0x40000);
    // NBG0: opaque red; NBG1: opaque blue, each in its own VRAM bank.
    vram2[0]=0x80;vram2[1]=0x1f;
    vram2[0x20000]=0xfc;vram2[0x20001]=0x00;
    Renderer renderer({vram1.data(),{fb0.data(),fb1.data()},vram2.data(),cram.data()});
    uint32_t pixel=0;
    renderer.SetMode(Renderer::Mode::Software,[&](uint32_t* pixels,uint32_t,uint32_t){pixel=pixels[0]&0xffffff;});
    renderer.Reset(true);
    auto reg=[&](unsigned address,unsigned value){renderer.WriteVdp2Reg(address,value);};
    reg(0x00,0x8000);reg(0x0e,0x0100); // display; split VRAM-A banks
    reg(0x10,0x4444);reg(0x12,0x4444);reg(0x14,0x5555);reg(0x16,0x5555);
    reg(0x20,3);reg(0x28,0x3232);reg(0x3c,0x0010);reg(0xf8,0x0102);
    renderer.SetResolution(320,224,false);renderer.LatchDisplayMode();
    auto draw=[&](unsigned cc,unsigned ratio){reg(0xec,cc);reg(0x108,ratio);renderer.BeginFrame();renderer.RenderLine(0);renderer.EndFrame();return pixel;};
    if(draw(0,15)!=0x0000f8){fprintf(stderr,"opaque layer setup failed: %06x\n",pixel);return 1;}
    if(draw(1,15)!=0x7c007c){fprintf(stderr,"half blend failed: %06x\n",pixel);return 1;}
    if(draw(1,31)!=0xf80000){fprintf(stderr,"transparent ratio failed: %06x\n",pixel);return 1;}
    if(draw(0x101,15)!=0xf800f8){fprintf(stderr,"additive blend failed: %06x\n",pixel);return 1;}
    // Offset applies after blending, using the top layer's selection only.
    reg(0x110,1);reg(0x114,32);
    if(draw(1,15)!=0x7c009c){fprintf(stderr,"post-blend offset failed: %06x\n",pixel);return 1;}
    reg(0x110,0);
    renderer.CapturePresentation(true);
    renderer.CaptureScrollExtension(39);
    draw(0,15);
    assert(renderer.PresentationFrame().scrollWidth==398);
    assert(renderer.PresentationFrame().scrollPixels.size()==398*224);
    assert((renderer.PresentationFrame().scrollPixels[39]&0xFFFFFF)==pixel);
    assert((renderer.PresentationFrame().scrollPixels[39]>>24)==255);
    assert((renderer.PresentationFrame().scrollPixels[0]&0xFFFFFF)==0x0000f8);
    renderer.CaptureScrollExtension(0);
    // Decorative extension observes NBG3's signed 9-bit offset, including bank B.
    reg(0x110,8);reg(0x112,8);reg(0x11a,0x100);reg(0x11c,0x1ff);reg(0x11e,255);
    if(renderer.BackgroundColorOffset()!=std::array<int16_t,3>{-256,-1,255}) {
        fprintf(stderr,"background extension offset selection/sign failed\n");return 1;
    }
    reg(0x110,0);reg(0x112,0);
    if(renderer.BackgroundColorOffset()!=std::array<int16_t,3>{})return 1;
    // VDP1 direct RGB blue over NBG0 red, sprite priority 3.
    fb1[0]=0xfc;fb1[1]=0;reg(0xf0,3);reg(0xe0,0x0320);reg(0x100,15);
    if(draw(0x40,0)!=0x7c007c){fprintf(stderr,"sprite RGB blend failed: %06x\n",pixel);return 1;}
    // Proven white-blend metadata must describe the actual native compositor,
    // and the HD transform must produce that same RGB without modifying alpha.
    vram2[0]=0xFF;vram2[1]=0xFF;
    for(unsigned weight:{5u,15u,25u}) {
        reg(0x100,weight-1);draw(0x40,0);
        assert(renderer.PresentationFrame().spriteWhiteWeight[0]==weight);
        assert(pixel==(port::ApplyPortraitWhiteMix(0xFFF80000,uint8_t(weight))&0xFFFFFF));
    }
    draw(0x140,0);assert(renderer.PresentationFrame().spriteWhiteWeight[0]==255);
    vram2[0]=0x80;vram2[1]=0x1F;reg(0x100,15);
    reg(0xe0,0x0220); // priority 3 exceeds the threshold: no blend
    if(draw(0x40,0)!=0xf80000){fprintf(stderr,"sprite priority gate failed: %06x\n",pixel);return 1;}
    // Indexed sprite type 0: ratio selector in bits 11..13, palette entry 1 blue.
    fb1[0]=0x08;fb1[1]=1;cram[2]=0x7c;cram[3]=0;reg(0xe0,0x0300);reg(0x100,0x1f00);
    if(draw(0x40,0)!=0x0000f8){fprintf(stderr,"sprite ratio selector failed: %06x\n",pixel);return 1;}
    reg(0x100,0x0f00);reg(0xe0,0x3000); // mode 3 uses the palette entry's MSB
    if(draw(0x40,0)!=0xf80000){fprintf(stderr,"sprite palette MSB-off gate failed: %06x\n",pixel);return 1;}
    cram[2]=0xfc;
    if(draw(0x40,0)!=0x7c007c){fprintf(stderr,"sprite palette MSB-on gate failed: %06x\n",pixel);return 1;}
    reg(0xe0,0x1300); // mode 1: priority equal to 3
    if(draw(0x40,0)!=0x7c007c){fprintf(stderr,"sprite equality gate failed: %06x\n",pixel);return 1;}
    reg(0xe0,0x2400); // mode 2: priority 3 is below threshold 4
    if(draw(0x40,0)!=0xf80000){fprintf(stderr,"sprite greater-than gate failed: %06x\n",pixel);return 1;}
    reg(0xe0,0x2300);
    if(draw(0x40,0)!=0x7c007c){fprintf(stderr,"sprite greater-or-equal gate failed: %06x\n",pixel);return 1;}
    reg(0xd6,0x0200); // window 0 excludes colour calculation at (0,0)
    if(draw(0x40,0)!=0xf80000){fprintf(stderr,"colour-calculation window failed: %06x\n",pixel);return 1;}
    reg(0xd6,0x0300); // inverted window includes (0,0)
    if(draw(0x40,0)!=0x7c007c){fprintf(stderr,"inverted colour-calculation window failed: %06x\n",pixel);return 1;}
    reg(0xd6,0);fb1[0]=0;fb1[1]=0; // transparent sprite cannot blend or occlude
    if(draw(0x40,0)!=0x0000f8){fprintf(stderr,"transparent sprite failed: %06x\n",pixel);return 1;}
    // Text/portrait replacements must use the displayed framebuffer's immutable
    // commands and texels, not a newer draw or subsequently edited live VRAM.
    renderer.CapturePresentation(true);renderer.Reset(true);
    renderer.SetResolution(320,224,false);reg(0,0x8000);renderer.LatchDisplayMode();
    auto word=[&](size_t offset,uint16_t value){vram1[offset]=value>>8;vram1[offset+1]=value&255;};
    word(0,0);word(4,0x80);word(6,0xC510);word(8,0x200);word(10,0x210);
    std::fill_n(vram1.begin()+0x1000,128,0x11);
    renderer.BeginDrawing();renderer.DrawCommand(0);renderer.EndDrawing();
    std::fill_n(vram1.begin()+0x1000,128,0x22);
    draw(0,0);assert(renderer.PresentationFrame().sprites.empty());
    renderer.SwapFramebuffer();draw(0,0);
    assert(renderer.PresentationFrame().sprites.size()==1);
    assert(renderer.PresentationFrame().sprites[0].pixels.size()==128);
    assert(renderer.PresentationFrame().sprites[0].pixels[0]==0x11);
    std::fill_n(vram1.begin()+0x1000,128,0x33);
    renderer.BeginDrawing();renderer.DrawCommand(0);renderer.EndDrawing();
    draw(0,0);assert(renderer.PresentationFrame().sprites[0].pixels[0]==0x11);
    renderer.SwapFramebuffer();cram[0x800]=0x12;draw(0,0);cram[0x800]=0x34;
    assert(renderer.PresentationFrame().sprites[0].pixels[0]==0x33);
    assert(renderer.PresentationFrame().palette[0x800]==0x12);
    // A sprite crossing the original left edge must continue into the extended
    // viewport, while the native framebuffer and native clip retain their size.
    renderer.Reset(true);renderer.CaptureScrollExtension(39);
    std::fill(fb0.begin(),fb0.end(),0);std::fill(fb1.begin(),fb1.end(),0);
    reg(0,0x8000);reg(0x20,0x0103);reg(0x28,0x3232);reg(0x3c,0x0010);reg(0xf8,0x0102);
    reg(0xe0,0x20);reg(0xf0,3);renderer.LatchDisplayMode();draw(0,0);
    std::fill(vram1.begin(),vram1.begin()+64,0);
    word(0,9);word(20,319);word(22,223);
    word(32,0);word(36,0xA8);word(40,0x200);word(42,0x210);word(44,0x1FFC);
    for(unsigned i=0;i<256;i++)word(0x1000+i*2,0xFC00);
    renderer.BeginDrawing();renderer.DrawCommand(0);renderer.DrawCommand(32);renderer.EndDrawing();
    renderer.SwapFramebuffer();draw(0,0);
    assert((renderer.PresentationFrame().scrollPixels[38]&0xFFFFFF)==0xF80000);
    assert((renderer.PresentationFrame().scrollPixels[34]&0xFFFFFF)!=0xF80000);
    renderer.SetScrollSpriteFilter([](const auto&,auto,int,int){return false;});
    renderer.BeginDrawing();renderer.DrawCommand(0);renderer.DrawCommand(32);renderer.EndDrawing();
    renderer.SwapFramebuffer();draw(0,0);
    assert((renderer.PresentationFrame().scrollPixels[38]&0xFFFFFF)!=0xF80000);
    assert((renderer.PresentationFrame().scrollPixels[39]&0xFFFFFF)==0xF80000); // original framebuffer is unchanged
    puts("VDP2 blending and coherent displayed sprite snapshots passed");
}
