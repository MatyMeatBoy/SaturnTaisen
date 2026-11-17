// Original, synthetic bus commands. No game, BIOS or extracted resource data.
#include "machine.h"
#include "hle_bios.h"
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
