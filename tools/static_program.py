"""Expand AOT candidates from a local SH-2 image and its function pointers.

Uses satrecomp's pinned opcode definitions and block boundaries. Output contains
derived game code: keep it local. Candidates are not proof of executed coverage;
the runtime must still check their bytes and run with strict AOT enabled.
"""
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
DEP = ROOT / 'local/deps/satrecomp'
DELAYED = {'BRA', 'BRAF', 'BSR', 'BSRF', 'JMP', 'JSR', 'RTS', 'RTE'}
CONDITIONAL_DELAYED = {'BTS', 'BFS'}
INVALID = {'Illegal', 'TRAPA', 'SLEEP'}
BAD_SLOT = DELAYED | CONDITIONAL_DELAYED | INVALID | {'BT', 'BF'}


def read_first_program(path: Path):
    """Read the BIOS's first root file from a prepared MODE1/2048 ISO.

    The PVD volume size may include audio tracks, so validate each extent against
    the data image instead. No file named by the ISO is opened on the host.
    """
    size = path.stat().st_size
    with path.open('rb') as source:
        def read(at, count):
            if at < 0 or count < 0 or at+count > size:
                raise ValueError('ISO extent exceeds the data image')
            source.seek(at)
            result = source.read(count)
            if len(result) != count:
                raise ValueError('Truncated ISO read')
            return result

        def extent(record):
            if len(record) < 34:
                raise ValueError('Short ISO directory record')
            lba = struct.unpack_from('<I',record,2)[0]
            count = struct.unpack_from('<I',record,10)[0]
            if lba != struct.unpack_from('>I',record,6)[0] or count != struct.unpack_from('>I',record,14)[0]:
                raise ValueError('ISO directory endian copies disagree')
            return lba,count

        header = read(0,256)
        if header[:16] != b'SEGA SEGASATURN ':
            raise ValueError('Expected a Saturn data image')
        base = struct.unpack_from('>I',header,0xf0)[0]
        pvd = read(16*2048,2048)
        if pvd[:7] != b'\x01CD001\x01':
            raise ValueError('Expected an ISO9660 primary volume descriptor')
        lba,count = extent(pvd[156:156+pvd[156]])
        if count > 0x100000:
            raise ValueError('Unexpected root directory size')
        directory = read(lba*2048,count)
        p = 0
        while p < len(directory):
            length = directory[p]
            if not length:
                p = (p//2048+1)*2048
                continue
            if length < 34 or p+length > len(directory) or p%2048+length > 2048:
                raise ValueError('Invalid ISO directory record')
            record = directory[p:p+length]
            p += length
            if record[25]&2:
                continue
            if record[25]&0x80 or record[32]+33 > length:
                raise ValueError('Unsupported initial program directory record')
            lba,count = extent(record)
            if not count or count > 0x100000:
                raise ValueError('Unexpected initial program size')
            name = record[33:33+record[32]].decode('ascii','replace').split(';')[0]
            return read(lba*2048,count),base,{'file':name,'lba':lba,'bytes':count}
        raise ValueError('No initial program in the root directory')


@lru_cache(maxsize=1)
def opcode_kinds():
    sys.path.insert(0, str(DEP / 'tools'))
    from recomp import own_tables
    names, decode, _ = own_tables(DEP / 'machine/sh2_ops.h')
    return tuple(names[index] for index in decode[:65536])


def switch_targets(image: bytes, base: int) -> set[int]:
    """Recognize the bounded MOVA/MOV.W/ADD/JMP switch idiom in Sakura.

    Count comes from the unsigned CMP/HI guard; no sentinel or arbitrary scan
    through surrounding data. Other compiler idioms remain unresolved.
    """
    targets = set()
    def word(at):
        return struct.unpack_from('>H', image, at)[0]
    incoming = {}
    for at in range(0,len(image)-3,2):
        op,slot = word(at),word(at+2)
        if slot>>12 != 0xe or slot&255 >= 128:
            continue
        if op>>8 in (0x8d,0x8f):
            target = at+4+(((op&255)^128)-128)*2
        elif op>>12 in (0xa,0xb):
            target = at+4+(((op&4095)^2048)-2048)*2
        else:
            continue
        incoming.setdefault((target,(slot>>8)&15),set()).add(slot&255)
    for p in range(10, len(image)-9, 2):
        mova = word(p)
        if mova >> 8 != 0xc7 or word(p+6) != 0x402b or word(p+8) != 9:
            continue
        load = word(p+2)
        if load & 0xf00f != 0x000d:
            continue
        index, result = (load>>4)&15, (load>>8)&15
        if word(p+4) != 0x300c | (result<<4):
            continue
        if word(p-2) != 0x300c | (index<<8) | (index<<4):
            continue
        counts = set()
        move = word(p-4)
        if move & 0xff0f == 0x6003 | (index<<8):
            selector = (move>>4)&15
            for branch in (p-6,p-8):
                if branch < 4:
                    continue
                if word(branch)>>8 not in ((0x89,0x8d) if branch==p-6 else (0x8d,)):
                    continue
                compare, immediate = word(branch-2), word(branch-4)
                if compare & 0xff0f != 0x3006 | (selector<<8):
                    continue
                bound = (compare>>4)&15
                if immediate>>8 == 0xe0 | bound and (immediate&255)<128:
                    counts.add((immediate&255)+1)
        # Inverted guard around a BRA-to-default. The bound is supplied by
        # an incoming direct branch's delay slot immediately before the CMP.
        if p >= 12 and word(p-4) == 9 and word(p-6)>>12 == 0xa and word(p-10)>>8 == 0x8f:
            compare,move = word(p-12),word(p-8)
            selector = (move>>4)&15
            branch = word(p-10)
            target = p-10+4+(((branch&255)^128)-128)*2
            if (target == p-2 and move & 0xff0f == 0x6003 | (index<<8) and
                    compare & 0xff0f == 0x3006 | (selector<<8)):
                counts.update(value+1 for value in incoming.get((p-12,(compare>>4)&15),()))
        table = ((base+p)&~3)+4+(mova&255)*4
        offset = table-base
        if not counts or offset < p+10:
            continue
        for count in counts:
            if offset+count*2 > len(image):
                continue
            for i in range(count):
                target = table+struct.unpack_from('>h', image, offset+i*2)[0]
                if base <= target < base+len(image)-1 and not target&1:
                    targets.add(target)
    return targets


def discover(image: bytes, base: int, entries=(), *, eager=False) -> list[tuple[int, bytes]]:
    if base & 1 or base < 0 or base + len(image) > 0x100000000:
        raise ValueError('Image must have an aligned, bounded 32-bit address')
    kinds = opcode_kinds()
    limit = base + len(image)
    roots = {base, *entries} | switch_targets(image, base)
    aligned = image[(-base)&3:]
    for (pointer,) in struct.iter_unpack('>I', aligned[:len(aligned)//4*4]):
        if pointer >> 30 == 0:
            pointer &= 0x07ffffff  # the Saturn bus aliases used by cached/cache-through code
            if base <= pointer < limit and not pointer & 1:
                roots.add(pointer)
    todo = list(roots)
    seen = set()
    blocks = {}
    while todo:
        pc = todo.pop()
        if pc in seen or pc & 1 or not base <= pc < limit-1:
            continue
        seen.add(pc)
        start = pc-base
        ops = []
        cut_for_slot = False
        while len(ops) < 48 and start+len(ops)*2+2 <= len(image):
            op = struct.unpack_from('>H', image, start+len(ops)*2)[0]
            kind = kinds[op]
            if kind in INVALID:
                break
            if kind in DELAYED | CONDITIONAL_DELAYED:
                if len(ops)+2 > 48 or start+(len(ops)+2)*2 > len(image):
                    cut_for_slot = len(ops)+2 > 48
                    break
                slot = struct.unpack_from('>H', image, start+(len(ops)+1)*2)[0]
                if kinds[slot] in BAD_SLOT:
                    break
                ops.extend((op, slot))
                if kind in DELAYED:
                    break
            else:
                ops.append(op)
        if not ops:
            continue
        # A delayed transfer at instruction 48 cannot fit its slot. The runtime
        # validly returns a 47-instruction prefix; do not lose that entry point.
        complete = len(ops) >= 2 and kinds[ops[-2]] in DELAYED
        if not eager:
            if len(ops) > 2 and len(set(ops)) == 1:
                continue
            if not complete and len(ops) != 48 and not cut_for_slot:
                continue
        blocks[pc] = image[start:start+len(ops)*2]
        falls_through = True
        for i, op in enumerate(ops):
            kind = kinds[op]
            here = pc+i*2
            if kind in {'BT', 'BF', 'BTS', 'BFS'}:
                todo.append(here+4+(((op & 255) ^ 128)-128)*2)
            elif kind in {'BRA', 'BSR'}:
                todo.append(here+4+(((op & 4095) ^ 2048)-2048)*2)
                falls_through = kind == 'BSR'
            elif kind in DELAYED:
                falls_through = kind in {'JSR', 'BSRF'}
        if falls_through:
            todo.append(pc+len(ops)*2)
    return sorted(blocks.items())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--image', type=Path)
    source.add_argument('--disc-iso', type=Path, help='prepared 2048-byte-sector image; reads the BIOS first file')
    parser.add_argument('--base', type=lambda s: int(s, 0))
    parser.add_argument('--entry', type=lambda s: int(s, 0), action='append', default=[])
    parser.add_argument('--all-entries', action='store_true', help='try every aligned address; substantially larger candidate/build output')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.disc_iso:
        if args.base is not None:
            parser.error('--base is read from the disc header with --disc-iso')
        image,base,info = read_first_program(args.disc_iso)
    else:
        if args.base is None:
            parser.error('--base is required with --image')
        image,base,info = args.image.read_bytes(),args.base,{}
    entries = set(args.entry)
    if args.all_entries:
        entries.update(range(base,base+len(image),2))
    blocks = discover(image, base, entries, eager=args.all_entries)
    with args.output.open('x', encoding='ascii') as out:
        out.write('# statically discovered SH-2 candidates; not executed coverage\n')
        for pc, code in blocks:
            out.write(f'{pc:08X} {code.hex().upper()}\n')
    print(json.dumps({'image_sha256': hashlib.sha256(image).hexdigest(), 'base': base,
                      'bytes': len(image), 'candidate_blocks': len(blocks),
                      'entry_policy': 'all-aligned' if args.all_entries else 'control-flow-and-pointers', **info}))


if __name__ == '__main__':
    main()
