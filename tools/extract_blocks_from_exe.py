import mmap, struct, sys
exe = sys.argv[1]; out = sys.argv[2]
f = open(exe, 'rb'); m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
pe = struct.unpack_from('<I', m, 0x3c)[0]
assert m[pe:pe+4] == b'PE\0\0'
nsec = struct.unpack_from('<H', m, pe+6)[0]; opt = pe+24; osz = struct.unpack_from('<H', m, pe+20)[0]
magic = struct.unpack_from('<H', m, opt)[0]; base = struct.unpack_from('<Q', m, opt+24)[0]
print('magic', hex(magic), 'imagebase', hex(base), 'sections', nsec)
secs = []
for i in range(nsec):
    o = opt+osz+i*40
    name = m[o:o+8].rstrip(b'\0').decode(); vs, va, rs, ra = struct.unpack_from('<IIII', m, o+8)
    ch = struct.unpack_from('<I', m, o+36)[0]
    secs.append((name, va, vs, ra, rs, ch)); print(name, hex(va), vs, hex(ra), rs, hex(ch))
def rva2off(rva):
    for n, va, vs, ra, rs, ch in secs:
        if va <= rva < va+max(vs, rs): 
            o = ra+(rva-va)
            return o if o < ra+rs else None
    return None
text = [s for s in secs if s[0] == '.text'][0]
tlo, thi = base+text[1], base+text[1]+text[2]
n = 0
res = open(out, 'w')
for name, va, vs, ra, rs, ch in secs:
    if name in ('.text',): continue
    if not (ch & 0x40000000): continue   # initialised data only
    for off in range(ra, ra+rs-32, 8):
        pc, ni = struct.unpack_from('<IH', m, off)
        if not (1 <= ni <= 48): continue
        if not (pc < 0x100000 or 0x200000 <= pc < 0x300000 or 0x06000000 <= pc < 0x08000000): continue
        cp, fn, nat = struct.unpack_from('<QQQ', m, off+8)
        if not (base < cp < base+0x40000000): continue
        if fn and not (tlo <= fn < thi): continue
        if nat and not (tlo <= nat < thi): continue
        if not (fn or nat): continue
        co = rva2off(cp-base)
        if co is None: continue
        code = m[co:co+ni*2]
        if len(code) != ni*2: continue
        res.write('%08X %s\n' % (pc, code.hex().upper())); n += 1
print('records', n)
