"""Generate the intermission (IC) recogniser table the runtime uses to draw the PC plates (TP1, T96).

The intermission screens of chapters 2-10 share one layout with IC0501, the first one witnessed in game
(docs/research/ic0501-intermission-witness.md): a 320x224 picture on VDP2 layer 4, the Save/Status/Resume panel in the
native rectangle (184,16)-(296,144) on layer 0, and a signed -16 colour offset while it fades. The game paints the
picture's 8 bpp cells with the palette of ICLOGO.BIN (not the palette stored in the IC file), so the visible RGB
of every IC picture follows from its cells and that one palette. This tool derives, from the decoded disc-1 files (disc 2 is not derived: its witnessed IC06 uses its own palette):

  * `plate`: FNV-1a 64 of the RGB bytes (red, green, blue per pixel, five bits shifted up by three) of the 320x224
    plate outside the panel rectangle, with no colour offset, and `plate_dark` with the -16 offset.
    The IC0501 values equal the ones patch 0144 measured in game and IC03 (patch 0162) (`WITNESSED`), which is what makes the other
    rows trustworthy;
  * the PC file size and FNV-1a (what `PcBackdropHash` checks at run time);
  * a registration check: the 640x480 PC picture sampled the way patch 0144 does (rows (2y+1)*480/896, 2x2 means)
    is compared with the Saturn plate under shifts of up to three native pixels, and a picture whose best shift is not
    (0,0) is left out of the table (reported, never drawn).

IC01 is not in the table: its witnessed composition has its own palette key and anchored draw (patch 0107).

Usage:
  python tools/gen_ic_table.py build --iso1 "local/prepared/disc1/Track 01.iso" --iso2 "local/prepared/disc2/Track 01.iso" \
      --pc local/work/ic-pc --map config/hd-screen-map.json --out config/hd-ic-table.json
  python tools/gen_ic_table.py header config/hd-ic-table.json OUT.h [--check]

`build` needs the owner's discs and PC edition and writes names, sizes and hashes only. `header` needs neither.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

FNV_BASIS = 14695981039346656037
FNV_PRIME = 1099511628211
MASK = 0xFFFFFFFFFFFFFFFF
MENU = (184, 16, 296, 144)  # x0, y0, x1, y1, half open: the native Save/Status/Resume panel and emblem
DARKEN = -16
WIDTH, HEIGHT = 320, 224
MAX_SHIFT = 3
# Measured in game by patch 0144 on IC0501 (disc 1): (offset 0, offset -16), PC file size and FNV-1a.
WITNESSED = {'IC0501': {'plate': 0xA5E3498BEDDC1305, 'plate_dark': 0x1F7A14C347473045,
                        'pc_bytes': 218568, 'pc_fnv': 0x4A23AE5B5939DE76},
             # IC03, patch 0162 (disc 1): unshifted plate only.
             'IC03': {'plate': 0x6469CD72E7963265, 'pc_bytes': 185398, 'pc_fnv': 0x7A7ED93DF49A6CE5}}
LOGO_PALETTE_FNV = 0xE9107F892185CCC8  # what BackgroundPaletteFingerprint(4) reports for the IC layer
# Not in the table: own palette key and anchored draw (patch 0107).
SEPARATE = {'IC01': 'handled by patch 0107 (own palette key, anchored backdrop)'}


def fnv1a(data, state=FNV_BASIS):
    for byte in data:
        state = ((state ^ byte) * FNV_PRIME) & MASK
    return state


def screen_cells(data):
    """(palette words, 224 rows of 320 palette indices) of a Saturn full-screen picture (variant D), or None."""
    import decode_saturn_bg as saturn
    if not saturn._screen_ok(data):
        return None
    entries = struct.unpack_from('>1120I', data, 512)
    tiles = (len(data) - 512 - 4480) // 64
    words = struct.unpack_from('>256H', data, 0)
    rows = [[0] * WIDTH for _ in range(HEIGHT)]
    for cell, entry in enumerate(entries):
        tile = entry >> 1
        if tile >= tiles:
            continue
        base = 512 + 4480 + tile * 64
        left, top = (cell % 40) * 8, (cell // 40) * 8
        for y in range(8):
            rows[top + y][left:left + 8] = data[base + y * 8: base + y * 8 + 8]
    return words, rows


def rgb_of(word, offset=0):
    """The visible colour of one palette word: five bits shifted up by three, then the signed offset, clamped."""
    return tuple(max(0, min(255, (((word >> shift) & 31) << 3) + offset)) for shift in (0, 5, 10))


def plate_rgb(rows, words, offset=0):
    return [[rgb_of(words[index], offset) for index in row] for row in rows]


def in_menu(x, y):
    return MENU[0] <= x < MENU[2] and MENU[1] <= y < MENU[3]


def plate_fnv(rows, words, offset=0):
    """FNV-1a of the RGB bytes outside the panel rectangle, raster order: the runtime's check."""
    state = FNV_BASIS
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if in_menu(x, y):
                continue
            for channel in rgb_of(words[rows[y][x]], offset):
                state = ((state ^ channel) * FNV_PRIME) & MASK
    return state


def pc_plate(pixels, width=640, height=480):
    """The 640x480 PC picture as the runtime samples it: rows (2y+1)*480/896, then 2x2 means down to 320x224."""
    if (width, height) != (640, 480):
        raise ValueError('expected 640x480, got %dx%d' % (width, height))
    sampled = [pixels[(2 * y + 1) * 480 // 896] for y in range(448)]
    out = []
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            row.append(tuple(sum(sampled[2 * y + dy][2 * x + dx][c] for dy in (0, 1) for dx in (0, 1)) / 4
                             for c in range(3)))
        out.append(row)
    return out


def registration(saturn, pc, max_shift=MAX_SHIFT):
    """Mean absolute difference outside the panel per (dx, dy) shift; the registered fit is the unshifted one."""
    import numpy as np
    s = np.asarray(saturn, dtype=np.float64)
    p = np.asarray(pc, dtype=np.float64)
    mask = np.ones((HEIGHT, WIDTH), bool)
    mask[MENU[1]:MENU[3], MENU[0]:MENU[2]] = False
    scores = {}
    for dy in range(-max_shift, max_shift + 1):
        for dx in range(-max_shift, max_shift + 1):
            scores[(dx, dy)] = float(np.abs(np.roll(np.roll(p, dy, 0), dx, 1) - s)[mask].mean())
    best = min(scores, key=scores.get)
    others = [v for k, v in scores.items() if k != (0, 0)]
    return {'mad': round(scores[(0, 0)], 2), 'best_shift': list(best), 'registered': best == (0, 0),
            'margin': round(min(others) - scores[(0, 0)], 2)}


def entry_id(saturn_file):
    return Path(saturn_file).stem


def build(iso1, iso2, pc_root, screen_map):
    import decode_saturn_bg as saturn
    import decode_spred
    discs = [saturn.Iso(iso1)] + ([saturn.Iso(iso2)] if iso2 else [])
    files = [{name: extent for name, extent in disc.files('SAKURA1')} for disc in discs]
    logo = discs[0].content(files[0]['ICLOGO.BIN'])
    if fnv1a(logo[:512]) != LOGO_PALETTE_FNV:
        raise SystemExit('ICLOGO.BIN palette is not the shared logo palette %016X' % LOGO_PALETTE_FNV)
    logo_words = struct.unpack_from('>256H', logo, 0)
    rows, skipped = [], {}
    for pair in screen_map['pairs']:
        name = Path(pair['saturn_file']).name
        ident = entry_id(name)
        if not (name.startswith('IC') and pair.get('tier') == 'content' and name != 'ICLOGO.BIN'):
            continue
        if ident in SEPARATE:
            skipped[ident] = SEPARATE[ident]
            continue
        data = [disc.content(table[name]) for disc, table in zip(discs, files) if name in table]
        if len(data) != len(discs) or any(blob != data[0] for blob in data):
            skipped[ident] = 'not byte-identical on both discs'
            continue
        cells = screen_cells(data[0])
        if cells is None:
            skipped[ident] = 'not a full-screen picture'
            continue
        _, indices = cells
        raw = (Path(pc_root) / pair['pc_file']).read_bytes()
        image = dict(decode_spred.decode(raw)).get(pair['pc_image_index'])
        if image is None or image.size != (640, 480):
            skipped[ident] = 'PC picture is not 640x480'
            continue
        rgb = image.convert('RGB')
        pixels = [[rgb.getpixel((x, y)) for x in range(640)] for y in range(480)]
        fit = registration(plate_rgb(indices, logo_words), pc_plate(pixels))
        if not fit['registered']:
            skipped[ident] = 'registration: best shift %s' % (fit['best_shift'],)
            continue
        row = {'id': ident, 'saturn_file': pair['saturn_file'], 'saturn_sha256': hashlib.sha256(data[0]).hexdigest(),
               'pc_file': pair['pc_file'], 'pc_image_index': pair['pc_image_index'], 'pc_bytes': len(raw),
               'pc_fnv': '%016X' % fnv1a(raw), 'plate': '%016X' % plate_fnv(indices, logo_words),
               'plate_dark': '%016X' % plate_fnv(indices, logo_words, DARKEN), 'registration': fit,
               'discs': len(discs)}
        witnessed = WITNESSED.get(ident)
        if witnessed:
            got = {'plate': int(row['plate'], 16), 'plate_dark': int(row['plate_dark'], 16),
                   'pc_bytes': row['pc_bytes'], 'pc_fnv': int(row['pc_fnv'], 16)}
            got = {key: got[key] for key in witnessed}
            if got != witnessed:
                raise SystemExit('%s no longer reproduces the in-game measurement of patch 0144: %r vs %r' %
                                 (ident, got, witnessed))
            row['reproduces_witness'] = 'patches 0144 / 0162, disc 1'
        rows.append(row)
    return finish(rows, skipped)


def finish(rows, skipped):
    seen = {}
    for row in rows:
        for key in ('plate', 'plate_dark'):
            if row[key] in seen:
                raise SystemExit('%s and %s share a %s hash, the recogniser could not tell them apart' %
                                 (row['id'], seen[row[key]], key))
            seen[row[key]] = row['id']
    return {'schema': 1, 'scope': 'Intermission plate recogniser (names, sizes and hashes only).',
            'logo_palette_fnv': '%016X' % LOGO_PALETTE_FNV, 'menu': list(MENU), 'darken': DARKEN,
            'entries': sorted(rows, key=lambda r: r['id']), 'not_in_table': dict(sorted(skipped.items()))}


def render_header(table):
    lines = ['// SPDX-License-Identifier: GPL-3.0-only',
             '// Generated by tools/gen_ic_table.py from config/hd-ic-table.json. Do not edit.',
             '#pragma once', '#include <cstddef>', '#include <cstdint>', 'namespace port {',
             '// Disc-1 intermission plates: the picture is painted with the ICLOGO palette (kIcLogoPalette).',
             '// Disc 2 shows at least IC06 with its own palette and another RGB (witnessed), so it is not derived here.',
             'struct IcPlate {',
             '    int disc;',
             '    uint64_t palette;     // BackgroundPaletteFingerprint(4) while the plate is shown',
             '    const char* file;     // path below the PC assets folder',
             '    size_t bytes;         // size of the PC file',
             '    uint64_t fileHash;    // PcBackdropHash of the PC file',
             '    uint64_t nativeRgb;   // native RGB outside the panel, no colour offset',
             '    uint64_t darkRgb;     // the same with the -16 offset',
             '};',
             'inline constexpr uint64_t kIcLogoPalette = 0x%sull;' % table['logo_palette_fnv'],
             'inline constexpr IcPlate kIcPlates[] = {']
    for row in table['entries']:
        lines.append('    {1, kIcLogoPalette, "%s", %d, 0x%sull, 0x%sull, 0x%sull},  // %s' % (
            row['pc_file'], row['pc_bytes'], row['pc_fnv'], row['plate'], row['plate_dark'], row['id']))
    lines += ['};', '}', '']
    return chr(10).join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='action', required=True)
    b = sub.add_parser('build')
    b.add_argument('--iso1', required=True)
    b.add_argument('--iso2')
    b.add_argument('--pc', required=True)
    b.add_argument('--map', type=Path, required=True)
    b.add_argument('--out', type=Path, required=True)
    h = sub.add_parser('header')
    h.add_argument('table', type=Path)
    h.add_argument('out', type=Path)
    h.add_argument('--check', action='store_true', help='fail when OUT differs instead of writing it')
    args = parser.parse_args(argv)
    if args.action == 'build':
        table = build(args.iso1, args.iso2, args.pc, json.loads(args.map.read_text(encoding='utf-8')))
        args.out.write_text(json.dumps(table, indent=1) + '\n', encoding='utf-8')
        print('%d entries, %d not in table' % (len(table['entries']), len(table['not_in_table'])))
        return 0
    text = render_header(json.loads(args.table.read_text(encoding='utf-8')))
    if args.check:
        if not args.out.is_file() or args.out.read_text(encoding='utf-8') != text:
            print('%s is out of date' % args.out)
            return 1
        return 0
    args.out.write_text(text, encoding='utf-8', newline='\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
