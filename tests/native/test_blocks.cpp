// Synthetic MOV immediate / RTS / NOP blocks for dispatch and overlay-cache tests.
// These instructions and native stubs contain no game or BIOS code.
#include "blocks.h"
#include "access.h"

namespace satrecomp {
namespace {
constexpr uint8_t code1[]={0xE0,0x01,0x00,0x0B,0x00,0x09};
constexpr uint8_t code2[]={0xE0,0x02,0x00,0x0B,0x00,0x09};
template<unsigned value> void immediate_return(SH2 &cpu,uint64_t,unsigned) {
    Access::R(cpu)[0]=value;
    cpu.m_wbReg=0xFF;
    Access::SetPC(cpu,Access::PR(cpu));
    Access::AddCycles(cpu,4);
}
const BlockDesc variants[]={
    {0x06004000,3,code1,nullptr,immediate_return<1>},
    {0x06004000,3,code2,nullptr,immediate_return<2>},
    {0x00204000,3,code1,nullptr,immediate_return<1>},
    {0x00204000,3,code2,nullptr,immediate_return<2>},
};
}
const BlockTable g_blockTables[]={{variants,4,nullptr,0}};
const size_t g_blockTableCount=1;
}
