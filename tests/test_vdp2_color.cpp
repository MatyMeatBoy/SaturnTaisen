// Invented VDP2 bitmaps; exercise the actual renderer, not a duplicate blend formula.
#include "renderer.h"
#include <array>
#include <cstdint>
#include <cstdio>
#include <vector>

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
    puts("VDP2 opaque, half blend, ratio endpoint and additive composition passed");
}
