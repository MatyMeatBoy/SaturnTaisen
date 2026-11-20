#!/usr/bin/env python3
"""THD21: read which layer draws a saved menu screen and the palette fingerprints it uses.

Offline and read-only: a Sakura v9 state in, a JSON row out (no pixels, no state or capture is copied).
  python tools/menu_state_probe.py NAME=STATE [NAME=STATE ...] [--out config/hd-menu-state-evidence.json]
Per state: the VDP2 layer switches (BGON, priorities, CCCTL), the active VDP1 sprite commands grouped by
(colour mode, PMOD, COLR, size, palette fingerprint) with the number of commands and distinct textures, and the
FNV-1a 64 fingerprint of each non-empty 16-colour CRAM bank. The VDP2 register image sits at a fixed offset of the
serialized tail in the states of this runtime; a state whose offset does not read as a plausible image is refused.
"""
import argparse, collections, json, pathlib, struct, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_portrait_coverage import STATE_HEADER, STATE_VECTORS, active_commands  # noqa: E402

VDP2_AT = 590
REGS = {'BGON': 0x20, 'CHCTLA': 0x28, 'CHCTLB': 0x2A, 'SPCTL': 0xE0, 'CCCTL': 0xEC, 'PRISA': 0xF0, 'PRINA': 0xF8,
        'PRINB': 0xFA, 'CLOFEN': 0x110}
BPP = {0: 4, 1: 4, 2: 8, 3: 8, 4: 8, 5: 16}


def fnv(data):
    h = 0xcbf29ce484222325
    for byte in data:
        h = ((h ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return '%016X' % h


def load(path):
    blob = pathlib.Path(path).read_bytes()
    if blob[:len(STATE_HEADER)] != STATE_HEADER:
        raise SystemExit('%s: not a Sakura v9 state' % path)
    at, vectors = len(STATE_HEADER), []
    for size in STATE_VECTORS:
        if struct.unpack_from('<Q', blob, at)[0] != size:
            raise SystemExit('%s: unexpected vector size' % path)
        vectors.append(blob[at + 8:at + 8 + size]); at += 8 + size
    return vectors, blob[at:]


def probe(path):
    vectors, tail = load(path)
    vram, cram = vectors[3], vectors[7]
    if struct.unpack_from('<H', tail, VDP2_AT)[0] != 0x8000:
        raise SystemExit('%s: no plausible VDP2 register image at the expected offset' % path)
    regs = {k: '%04X' % struct.unpack_from('<H', tail, VDP2_AT + o)[0] for k, o in REGS.items()}
    layers = [n for n, bit in (('NBG0', 1), ('NBG1', 2), ('NBG2', 4), ('NBG3', 8), ('RBG0', 16), ('RBG1', 32))
              if int(regs['BGON'], 16) & bit]
    groups = collections.OrderedDict()
    for c in active_commands(vram):
        kind = c[0] & 15
        if kind not in (0, 1, 2, 4, 5, 6):
            continue
        mode = (c[2] >> 3) & 7
        bpp = BPP.get(mode, 4)
        w, h = ((c[5] >> 8) & 0x3f) * 8, c[5] & 255
        texture = vram[c[4] * 8:c[4] * 8 + w * h * bpp // 8]
        palette = b'' if bpp == 16 else cram[(c[3] & 0x7ff) * 2:(c[3] & 0x7ff) * 2 + (512 if bpp == 8 else 32)]
        key = (kind, '%04X' % c[2], '%04X' % c[3], '%dx%d' % (w, h), fnv(palette) if palette else '-')
        entry = groups.setdefault(key, {'commands': 0, 'textures': set()})
        entry['commands'] += 1
        entry['textures'].add(fnv(texture))
    rows = [{'kind': k[0], 'pmod': k[1], 'colr': k[2], 'size': k[3], 'palette_fnv': k[4], 'commands': g['commands'],
             'distinct_textures': len(g['textures']), 'texture_fnv': sorted(g['textures'])[0] if len(g['textures']) == 1 else None}
            for k, g in groups.items()]
    banks = {str(i): fnv(cram[i * 32:i * 32 + 32]) for i in range(128) if any(cram[i * 32:i * 32 + 32])}
    return {'vdp2_layers': layers, 'vdp2': regs, 'vdp1_groups': rows, 'cram_banks_nonempty': len(banks),
            'drawn_by': 'VDP1 sprites over VDP2 ' + '+'.join(layers) if rows else 'VDP2 only (' + '+'.join(layers) + ')'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('states', nargs='+', help='NAME=PATH')
    ap.add_argument('--out', type=pathlib.Path)
    a = ap.parse_args()
    result = {'schema': 1, 'screens': {}}
    for item in a.states:
        name, path = item.split('=', 1)
        result['screens'][name] = probe(path)
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if a.out:
        a.out.write_text(text, encoding='utf-8')
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
