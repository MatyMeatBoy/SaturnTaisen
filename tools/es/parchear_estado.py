"""Apply Spanish menu data to an English savestate for quick visual checks.

  python parchear_estado.py ENTRADA.state SALIDA.state

Savestates are uncompressed: program tables live in RAM and decompressed menu tiles in
VRAM. For every patched region, the exact English bytes are searched and replaced by
the Spanish ones. Only for testing: a real playthrough loads the files from the disc.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from decodificar import Disc, ISO  # noqa: E402
from red_lz import decompress  # noqa: E402

from _rutas import WORK  # noqa: E402
OUT = os.path.join(WORK, 'builds', 'es-cap1', 'files')

# (file, kind, offset, length or stream end): 'raw' compares file bytes, 'lz' compares decompressed streams
REGIONS = [
    ('/SAKURA', 'raw', 0x5F5C8, 36),
    ('/SAKURA1/ICATALL.DAT', 'lz', 0x2800, 0x3800),
    ('/SAKURA1/LOGO.SH2', 'raw', 0x6086, 0x6234 - 0x6086),
    ('/SAKURA1/LOGO.SH2', 'lz', 0xFF20, 0x10808),
    ('/SAKURA1/LOGO.SH2', 'lz', 0x10808, 0x11770),
    ('/SAKURA1/LOGO.SH2', 'lz', 0x25410, 0x29940),
    ('/SAKURA', 'lz', 0x5B320, 0x5C654),
    ('/SAKURA', 'lz', 0x59878, 0x59C70),
    ('/SAKURA', 'lz', 0x5AE38, 0x5B320),
    ('/SAKURA', 'raw', 0x5A09E, 0x5A4B4 - 0x5A09E),
    ('/SAKURA', 'lz', 0x5C654, 0x5E190),
]


def pairs():
    disc = Disc(ISO)
    for name, kind, offset, extra in REGIONS:
        path = os.path.join(OUT, *name.strip('/').split('/'))
        if not os.path.exists(path):
            continue
        en, es = disc.read(name), open(path, 'rb').read()
        if kind == 'raw':
            yield name, en[offset:offset + extra], es[offset:offset + extra]
        else:
            yield name, decompress(en[offset:extra]), decompress(es[offset:extra])


def main(src, dst):
    state = bytearray(open(src, 'rb').read())
    for name, old, new in pairs():
        if old == new:
            continue
        if state.find(old) < 0:  # VRAM may hold only the start of a long strip
            length = len(old)
            while length >= 512 and state.find(old[:length]) < 0:
                length //= 2
            old, new = old[:length], new[:length]
        hits, at = 0, state.find(old)
        while at >= 0:
            state[at:at + len(new)] = new
            hits += 1
            at = state.find(old, at + len(new))
        print(f'{name}: {len(old)} bytes, {hits} sustituciones')
    open(dst, 'wb').write(state)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
