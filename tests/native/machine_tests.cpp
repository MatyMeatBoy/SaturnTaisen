// Original, synthetic bus commands. No game, BIOS or extracted resource data.
#include "machine.h"
#include "hle_bios.h"
#include "lift.h"
#include "recomp.h"
#include <algorithm>
#include <cstdio>
#include <string>

using satrecomp::machine::Machine;

static void command(Machine &m, uint16_t a, uint16_t b, uint16_t c=0, uint16_t d=0) {
    m.BusWrite16(0x05890018,a);m.BusWrite16(0x0589001c,b);
    m.BusWrite16(0x05890020,c);m.BusWrite16(0x05890024,d);
}
static uint32_t position(Machine &m) {
    return ((m.BusRead16(0x05890020)&255u)<<16)|m.BusRead16(0x05890024);
}
int main(int argc, char **argv) {
    Machine m;
    if (argc>1 && std::string(argv[1])=="unsupported-bios") {
        satrecomp::hle::Install(m,{});
        m.masterSH2.PR=0x06004000;
        satrecomp::hle::Run(m.masterSH2,0x226c);
        return 0; // a strict runtime must not reach this after an unsupported BIOS call
    }
    if (argc>1 && std::string(argv[1])=="disc-cache") {
        satrecomp::hle::Install(m,{});
        m.Reset(true);
        m.masterSH2.PC=0x1014; // native BIOS idle: advance hardware, execute no guest instructions
        satrecomp::Options options;
        options.mode=satrecomp::Mode::Native;
        satrecomp::Attach(m,options);
        unsigned char content=0x11;
        auto reader=[&](uint32_t, uint8_t *out) {std::fill_n(out,2048,content);return true;};
        satrecomp::SetDiscSectorReader(reader);
        m.SetDisc({{{1,4,150}},1800});
        auto sector=[&]() {
            command(m,0x1080,150,0x0080,1);
            m.RunFrame();
            command(m,0x6300,0,0,1);
            return m.BusRead16(0x05818000);
        };
        if(sector()!=0x1111) {std::fputs("first synthetic medium read failed\n",stderr);return 1;}
        command(m,0x0600,0);
        content=0x22;
        satrecomp::SetDiscSectorReader(reader);
        m.SetDisc({{{1,4,150}},1800});
        const auto changed=sector();
        satrecomp::Finish();
        if(changed!=0x2222) {std::fprintf(stderr,"new media reused old sector at FAD150: %04X\n",changed);return 1;}
        std::puts("CD media replacement invalidates same-FAD sector cache");
        return 0;
    }
    m.SetDisc({{{1,4,150},{2,0,1200}},1800});
    command(m,0x1100,0x0200);
    if(position(m)!=1200 || m.BusRead16(0x0589001c)!=0x0102) {
        std::fputs("track seek did not move to the audio track\n",stderr);return 1;
    }
    command(m,0x1180,555);
    if(position(m)!=555 || m.BusRead16(0x0589001c)!=0x4101) {
        std::fputs("FAD seek did not move to the data track\n",stderr);return 1;
    }
    command(m,0x11ff,0xffff);
    if(position(m)!=555 || (m.BusRead16(0x05890018)>>8)!=1) {
        std::fputs("pause did not retain the pickup position\n",stderr);return 1;
    }
    command(m,0x1100,0xff00);
    if((m.BusRead16(0x05890018)>>8)!=2) {
        std::fputs("invalid track did not enter standby\n",stderr);return 1;
    }
    std::puts("CD track/FAD seek, pause and invalid-track bus regressions passed");
}
