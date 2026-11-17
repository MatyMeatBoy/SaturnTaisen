"""Compile-test the real SH-2 emitter using original synthetic operands only."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'local/deps/satrecomp/tools'))
import sh2emit

def main():
    output=Path(sys.argv[1])
    lines=['// Generated from the production emitter; no game code.',
           '#include "machine.h"','using namespace satrecomp::machine;',
           '#define SN_RD32N(name,address) const uint32 name=c.Read32(address);',
           'void EmittedMacLong(SH2& c,bool sameRegister) {auto& R=c.R;']
    for opcode,condition in ((0x000F,'if(sameRegister)'),(0x001F,'else')):
        lines.append(condition+' {')
        lines.extend(sh2emit.emit('MACL',opcode,'c.PC','return;').lines)
        lines.append('}')
    lines.append('}')
    output.write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':main()
