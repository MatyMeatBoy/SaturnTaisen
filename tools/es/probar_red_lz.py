"""Prueba de ida y vuelta de red_lz sobre todos los flujos conocidos del disco 1.

Para cada flujo x: decompress(compress(decompress(x))) == decompress(x).
Informa tambien tamano original frente al recomprimido y si coincide byte a byte.

Uso: python tools/test_red_lz.py [--iso RUTA] [--rapido]
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from red_lz import compress, decompress_ex  # noqa: E402
from decodificar import Disc, ISO  # noqa: E402

# (archivo, offset) de cada flujo comprimido localizado
STREAMS = [('/SAKURA1/ICATALL.DAT', o) for o in (0x0, 0x2800, 0x3800, 0x6800, 0x8000, 0x8800, 0xE000, 0x12000, 0x13800, 0x15000)]
STREAMS += [('/SAKURA1/OMALL.DAT', o) for o in (0x0, 0x1000, 0x3000, 0x3800, 0x79000)]
STREAMS += [('/SAKURA1/LDSVALL.DAT', o) for o in (0x0, 0x1000, 0x3000, 0x3800)]
STREAMS += [('/SAKURA1/LOADBGR.DAT', 0), ('/SAKURA1/SISBG.ALL', 0), ('/SAKURA1/LPCHK.SH2', 0x20BC)]
STREAMS += [('/SAKURA', o) for o in (0x5940C, 0x595BC, 0x59700, 0x59878, 0x5AE38, 0x5B320, 0x5C654, 0x5E190, 0x5EB4C)]
STREAMS += [('/SAKURA2/SLG.BIN', o) for o in (0x4A258, 0x4A740)]
STREAMS += [('/SAKURA1/LOGO.SH2', o) for o in (
    0x6700, 0x7C8C, 0x819C, 0x9248, 0x962C, 0xA6B8, 0xAAA0, 0xB7D8, 0xBB00, 0xCB40, 0xCF18, 0xE224, 0xE6F4,
    0xF990, 0xFF20, 0x10808, 0x11770, 0x18604, 0x19498, 0x1C85C, 0x23D30, 0x24B8C, 0x25410, 0x29940, 0x29DB8,
    0x31130, 0x323CC, 0x32D3C, 0x32EDC, 0x349C8, 0x34D5C, 0x35754, 0x35924, 0x35C30, 0x35D20, 0x3729C,
    0x37B78, 0x39D3C, 0x3A0E8, 0x3B3C4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--iso', default=ISO)
    ap.add_argument('--rapido', action='store_true', help='omite flujos de mas de 40000 bytes')
    a = ap.parse_args()
    disc = Disc(a.iso)
    bad = 0
    tot_o = tot_n = 0
    for f, off in STREAMS:
        raw = disc.read(f)
        x, used = decompress_ex(raw, off)
        if a.rapido and len(x) > 40000:
            continue
        t = time.time()
        c = compress(x)
        y, used2 = decompress_ex(c)
        ok = y == x and used2 == len(c)
        bad += not ok
        tot_o += used
        tot_n += len(c)
        print('%-22s %#07x  salida %6d  orig %6d  nuevo %6d  %s%s  %.1fs' % (
            f, off, len(x), used, len(c), 'OK' if ok else 'FALLO',
            ' (identico)' if c == raw[off:off + used] else '', time.time() - t), flush=True)
    print('flujos con fallo: %d; comprimido original %d bytes, nuevo %d bytes' % (bad, tot_o, tot_n))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
