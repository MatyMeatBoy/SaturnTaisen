"""Apply Spanish menu data to an English savestate for quick visual checks.

  python parchear_estado.py ENTRADA.state SALIDA.state

Savestates are uncompressed: program tables live in RAM and decompressed menu tiles in
VRAM. For every patched region, the exact English bytes are searched and replaced by
the Spanish ones. Only for testing: a real playthrough loads the files from the disc.
"""
import argparse
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from decodificar import Disc, ISO  # noqa: E402
from red_lz import decompress  # noqa: E402

from _rutas import WORK, distinct_output, private_path, write_bytes  # noqa: E402
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
        en, es = disc.read(name), Path(path).read_bytes()
        if kind == 'raw':
            yield name, en[offset:offset + extra], es[offset:offset + extra]
        else:
            yield name, decompress(en[offset:extra]), decompress(es[offset:extra])


def main(src, dst):
    src, dst = Path(src), Path(dst)
    distinct_output(dst, src)
    state = bytearray(src.read_bytes())
    for name, old, new in pairs():
        if not old or len(old) != len(new):
            raise ValueError(f'{name}: los datos del estado deben tener la misma longitud y no estar vacíos')
        if old == new:
            continue
        at = state.find(old)
        if at < 0:  # VRAM may hold only the start of a long strip.
            length = len(old) // 2
            while length >= 512:
                at = state.find(old[:length])
                if at >= 0:
                    old, new = old[:length], new[:length]
                    break
                length //= 2
        hits = 0
        while at >= 0:
            state[at:at + len(old)] = new
            hits += 1
            at = state.find(old, at + len(old))
        print(f'{name}: {len(old)} bytes, {hits} sustituciones')
    write_bytes(dst, state)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        main(args.source, private_path(args.destination))
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')
