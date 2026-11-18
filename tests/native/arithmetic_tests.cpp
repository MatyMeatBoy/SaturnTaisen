// Independent arithmetic expectation from Renesas SH-1/SH-2/SH-DSP manual 6.1.31.
// No third-party test vectors or game instructions are incorporated.
#include "machine.h"
#include <array>
#include <cstdint>
#include <cstdio>
using namespace satrecomp::machine;
void EmittedMacLong(SH2&,bool);
int MacLongOracle(Machine& machine,bool reference) {
    machine.Reset(true);
    constexpr std::array<int32_t,11> values={0,1,-1,2,-2,INT32_MAX,INT32_MIN,65536,-65536,32768,-32768};
    constexpr std::array<uint64_t,12> accumulators={0,0xFFFF000000000000ull,0x0001000000000000ull,
        1,UINT64_MAX,0x0000800000000000ull,0x00007FFFFFFFFFFFull,0x7FFF800000000000ull,
        0xFFFFFFFF00000000ull,0xFFFF800000000000ull,0x123456789ABCDEF0ull,0x8000000000000000ull};
    unsigned checked=0;
    for(auto* cpu:{&machine.masterSH2,&machine.slaveSH2})
    for(bool saturated:{false,true})for(bool same:{false,true})
    for(uint64_t initial:accumulators)for(int32_t a:values)for(int32_t b:values) {
        auto& c=*cpu;
        constexpr uint32_t left=0x06008000,right=0x06008010,code=0x06004000;
        c.PC=code;c.SR.u32=0x3F1u|(saturated?2u:0u);c.MAC.u64=initial;
        c.R[0]=left;c.R[1]=right;c.m_wbReg=0xFF;
        c.Write16(code,same?0x000F:0x001F);c.Write32(left,static_cast<uint32_t>(a));
        c.Write32(same?left+4:right,static_cast<uint32_t>(b));
        const __int128 product=static_cast<__int128>(a)*b;
        uint64_t expected;
        if(saturated) {
            // Read active high word as signed, independent of the production formula.
            const __int128 accumulator=static_cast<__int128>(static_cast<int16_t>(initial>>32))*0x100000000ull+static_cast<uint32_t>(initial);
            const __int128 sum=accumulator+product;
            const __int128 lo=-(__int128(1)<<47),hi=(__int128(1)<<47)-1;
            expected=static_cast<uint64_t>(sum<lo?lo:sum>hi?hi:sum);
        } else expected=initial+static_cast<uint64_t>(product);
        if(reference)c.RecompInterpretNext();else EmittedMacLong(c,same);
        const uint64_t mask=saturated?0x0000FFFFFFFFFFFFull:UINT64_MAX;
        if((c.MAC.u64&mask)!=(expected&mask) || c.R[0]!=left+(same?8:4) ||
           c.R[1]!=(same?right:right+4) || c.SR.u32!=(0x3F1u|(saturated?2u:0u))) {
            std::fprintf(stderr,"MAC.L %s failed S=%u same=%u initial=%016llX a=%d b=%d expected=%016llX got=%016llX\n",
                reference?"interpreter":"native",saturated,same,static_cast<unsigned long long>(initial),a,b,
                static_cast<unsigned long long>(expected),static_cast<unsigned long long>(c.MAC.u64));return 1;
        }
        checked++;
    }
    std::printf("MAC.L %s: %u arithmetic/address/flag cases passed on both SH-2s\n",reference?"interpreter":"native",checked);
    return 0;
}
