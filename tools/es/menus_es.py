"""Build Spanish menu graphics and their tile lists into builds/es-cap1/files.

  python -X utf8 menus_es.py [--preview]

Each menu: decompress the English text strip, clear the tiles we reuse, render the
Spanish words with the font that matches the English patch, recompress, and point
the game's per-item tile lists at the new tiles. Every patch first asserts that the
English bytes are exactly the expected ones, so a wrong offset fails loudly.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from decodificar import Disc, ISO  # noqa: E402
from fuente import fit  # noqa: E402
from red_lz import compress, decompress  # noqa: E402
from tiras import T, strip_from, strip_into  # noqa: E402
from wkl_attacks import traducir_ataques_wkl  # noqa: E402
from wkl_enemy_names import traducir_mosquete_wkl  # noqa: E402
from wkl_pause import traducir_pausa_tactica  # noqa: E402
from wkl_short_commands import traducir_comandos_aliados_wkl  # noqa: E402

from _rutas import WORK as _W, MENUS  # noqa: E402
WORK = str(_W)
OUT = os.path.join(WORK, 'builds', 'es-cap1', 'files')


class Files:
    """Lazily loaded, mutable copies of disc files to patch."""

    def __init__(self, disc: Disc):
        self.disc, self.data = disc, {}

    def __getitem__(self, name):
        if name not in self.data:
            self.data[name] = bytearray(self.disc.read(name))
        return self.data[name]

    def save(self):
        for name, data in self.data.items():
            path = os.path.join(OUT, *name.strip('/').split('/'))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(data)
            print('escrito', name, len(data))


def words16(values):
    return b''.join(struct.pack('>H', v) for v in values)


def expect(data, offset, blob, what):
    if bytes(data[offset:offset + len(blob)]) != blob:
        raise SystemExit(f'{what}: bytes inesperados en {offset:#x}: {bytes(data[offset:offset + len(blob)]).hex()}')


def put_stream(f: bytearray, offset: int, limit: int, raw: bytes, what: str):
    """Replace the LZ stream at offset. Only the bytes the original stream used, plus zero padding
    that already followed it, may be overwritten: data after a stream (palettes, tables) stays."""
    from red_lz import decompress_ex
    _, consumed = decompress_ex(bytes(f), offset)
    room = consumed
    while offset + room < offset + limit and f[offset + room] == 0:
        room += 1
    packed = compress(raw)
    if decompress(packed) != raw:
        raise SystemExit(f'{what}: la ida y vuelta LZ falla')
    if len(packed) > room:
        raise SystemExit(f'{what}: comprimido {len(packed)} > espacio {room} (original {consumed})')
    f[offset:offset + room] = packed + bytes(room - len(packed))
    return len(packed)


MIN_SQUEEZE = 0.85  # below this a word looks deformed: use the next (abbreviated) alternative


def choose(text, face, size, baseline, width, gamma):
    """text may be 'Word' or ['Word', 'Abbr.', ...]: first alternative that fits without heavy squeeze."""
    options = text if isinstance(text, list) else [text]
    last = None
    for option in options:
        for room in (width - 1, width):
            try:
                word, w, squeeze = fit(option, face, size, baseline, room, gamma=gamma)
            except ValueError:
                continue
            last = (option, word, w, squeeze)
            if squeeze >= MIN_SQUEEZE:
                return last
    if last is None:
        raise SystemExit(f'{options}: ninguna alternativa cabe en {width}px')
    return last


def draw_word(rows, first_tile: int, tiles: int, text, face: str, size: int, baseline: int, gamma=1.3, align='left'):
    """Clear tiles [first_tile, first_tile+tiles) and draw text (or the first fitting alternative) there."""
    x0, width = first_tile * T, tiles * T
    for y in range(T):
        for x in range(x0, x0 + width):
            rows[y][x] = 0
    chosen, word, w, squeeze = choose(text, face, size, baseline, width, gamma)
    if isinstance(text, list) and chosen != text[0]:
        print(f'    abreviado: {text[0]!r} -> {chosen!r}')
    left = x0 + (min(1, width - w) if align == 'left' else (width - w) // 2)
    for y in range(T):
        for x in range(w):
            if word[y][x]:
                rows[y][left + x] = word[y][x]
    return w, squeeze


def intermedio(files: Files, preview):
    """Intermission menu (Save / Status / Resume): strip ICATALL.DAT+0x2800, lists SAKURA+0x5f5c8."""
    ic, prog = files['/SAKURA1/ICATALL.DAT'], files['/SAKURA']
    english_lists = [1, 2, 13, 13, 13, 0, 3, 4, 5, 13, 13, 0, 6, 7, 8, 9, 10, 11]
    expect(prog, 0x5F5C8, words16(english_lists), 'listas del intermedio')
    raw = bytearray(decompress(bytes(ic[0x2800:0x3800])))
    rows = strip_from(raw, 0, 15)
    blank = 12  # 1-based tile 13 is the padding tile
    if any(rows[y][x] for y in range(T) for x in range(blank * T, blank * T + T)):
        raise SystemExit('el tile de relleno no está en blanco')
    face, size, base = 'CENTURY.TTF', 15, 13
    items = [('Guardar', 0, 4), ('Estado', 4, 3), ('Continuar', 7, 5)]
    for text, first, n in items:
        w, sq = draw_word(rows, first, n, text, face, size, base)
        print(f'  intermedio {text!r}: {w}px en {n} tiles, compresión horizontal {sq:.2f}')
    strip_into(raw, 0, rows)
    used = put_stream(ic, 0x2800, 0x1000, bytes(raw), 'tira del intermedio')
    lists = [1, 2, 3, 4, 13, 0, 5, 6, 7, 13, 13, 0, 8, 9, 10, 11, 12, 13]
    prog[0x5F5C8:0x5F5C8 + 36] = words16(lists)
    print(f'  intermedio: tira {used} bytes comprimidos, listas {lists}')
    preview.append(('intermedio', rows, 15))


def render_word(text, face, size, baseline, max_width, gamma=1.0, squeeze=1.0):
    from fuente import render
    word, w = render(text, face, size, baseline, squeeze=squeeze, gamma=gamma)
    while w > max_width and squeeze > 0.6:
        squeeze -= 0.02
        word, w = render(text, face, size, baseline, squeeze=squeeze, gamma=gamma)
    if w > max_width:
        raise SystemExit(f'{text!r}: {w}px no cabe en {max_width}px')
    return word, w, squeeze


def place_word(rows, word, w, pool):
    """Cut the word into 16px chunks, write each chunk to a free tile from pool. Returns tile list."""
    tiles = []
    for k in range(-(-w // T)):
        tile = pool.pop(0)
        x0 = tile * T
        for y in range(T):
            for x in range(T):
                sx = k * T + x
                rows[y][x0 + x] = word[y][sx] if sx < w else 0
        tiles.append(tile)
    return tiles


def free_tiles(rows, first, last):
    return [t for t in range(first, last) if not any(rows[y][x] for y in range(T) for x in range(t * T, t * T + T))]


def patch_parts(prog, offset, count, tiles, w, blank, what, unit=16, base=0):
    """Rewrite a list of `count` sprite parts (x, y=-8, 16, 16, char) centred like the English patch."""
    for k in range(count):
        rec = struct.unpack_from('>hhhhH', prog, offset + k * 10)
        if rec[1:4] != (-8, 16, 16):
            raise SystemExit(f'{what}: pieza {k} inesperada {rec} en {offset + k * 10:#x}')
    if len(tiles) > count:
        raise SystemExit(f'{what}: {len(tiles)} tiles > {count} piezas')
    x0 = -(w // 2)
    for k in range(count):
        tile = tiles[k] if k < len(tiles) else blank
        struct.pack_into('>hhhhH', prog, offset + k * 10, x0 + k * T, -8, 16, 16, base + tile * unit)


def titulo(files: Files, preview):
    """Title menu Program: strip LOGO.SH2+0xFF20 (65 tiles), part lists in LOGO.SH2 (loaded at 0x204000)."""
    logo = files['/SAKURA1/LOGO.SH2']
    end = 0x10808  # next stream
    raw = bytearray(decompress(bytes(logo[0xFF20:end])))
    rows = strip_from(raw, 0, len(raw) // 128)
    expect(logo, 0x6234, bytes.fromhex('0020a1e40020a0d60020a1940020a14e0020a1080020a086080508070708'), 'tabla del título')
    blank = 25
    for t in range(0, 25):  # English words live in 0-24; reuse them
        for y in range(T):
            rows[y][t * T:t * T + T] = [0] * T
    pool = list(range(0, 25))
    face, size, base = 'georgiab.ttf', 16, 12
    items = [('Nueva partida', 0x61E4, 8), ('Opciones', 0x60D6, 5), ('Continuar', 0x6194, 8), ('Día largo', 0x6108, 7)]
    for text, off, count in items:
        word, w, sq = render_word(text, face, size, base, count * T - 2, squeeze=0.82)
        tiles = place_word(rows, word, w, pool)
        patch_parts(logo, off, count, tiles, w, blank, f'título {text}')
        print(f'  título {text!r}: {w}px, {len(tiles)}/{count} piezas, tiles {tiles}, compresión {sq:.2f}')
    strip_into(raw, 0, rows)
    used = put_stream(logo, 0xFF20, end - 0xFF20, bytes(raw), 'tira del título')
    print(f'  título: tira {used} bytes comprimidos de {end - 0xFF20}')
    preview.append(('titulo', rows, len(raw) // 128))


def in_place(rows, words, face, size, base, gamma=1.3):
    """Redraw words inside the tiles their English words used: (first_tile, tiles, text, align)."""
    for first, n, text, *extra in words:
        opts = extra[0] if extra else {}
        w, sq = draw_word(rows, first, n, text, face, opts.get('size', size), base, gamma=gamma,
                          align=opts.get('align', 'left'))
        print(f'    {text!r}: {w}px en {n} tiles, compresión {sq:.2f}')


def inventario(files: Files, preview):
    """Localize the two 32px prompts and keep the final bracket tile."""
    import hashlib
    import fuente

    prog = files['/SAKURA']
    offset, limit = 0x59700, 0x59878
    native = decompress(bytes(prog[offset:limit]))
    if hashlib.sha256(native).hexdigest() != '20d1665dbd57c9e2c41f39a4aeeeb16c3fef36aed389093b951f69ce3773f4ed':
        raise SystemExit('Inventario: tira de botones inesperada')

    rows = strip_from(native, 0, 5)
    previous_levels = fuente.LEVELS
    try:
        fuente.LEVELS = [1, 6, 9]
        for first, label in ((0, 'Opc.'), (2, 'Volver')):
            draw_word(rows, first, 2, label, 'CENTURY.TTF', 12, 12, align='center')
    finally:
        fuente.LEVELS = previous_levels
    localized = bytearray(native)
    strip_into(localized, 0, rows)
    put_stream(prog, offset, limit, bytes(localized), 'Inventario')
    preview.append(('Inventario: Opc. / Volver', rows, 5))

    from rotulos import read_indices, write_indices

    footer_offset = 0x5940C
    panel = decompress(bytes(prog[footer_offset:offset]))
    if hashlib.sha256(panel).hexdigest() != '049da51c96042f41522061bdc23b32b438d13d5ce801587a86124c24efe47412':
        raise SystemExit('Inventario: panel inesperado')
    pixels = read_indices(panel, 0, 224, 128, 4)
    try:
        fuente.LEVELS = [1]
        ink, width, _ = fit('Objetos', 'CENTURY.TTF', 12, 10, 38, height=11)
    finally:
        fuente.LEVELS = previous_levels
    left = (38 - width) // 2
    for y, glyph_row in enumerate(ink, start=115):
        pixels[y][9:47] = [15] * 38
        pixels[y][9 + left:9 + left + width] = [3 if value else 15 for value in glyph_row]
    localized_panel = bytearray(panel)
    write_indices(localized_panel, 0, pixels, 4)
    put_stream(prog, footer_offset, offset, bytes(localized_panel), 'Inventario: Objetos')


def opciones(files: Files, preview):
    """Options and controller screens (SAKURA streams). Part tables untouched: same tiles per word."""
    prog = files['/SAKURA']
    face, size, base = 'CENTURY.TTF', 15, 13
    # Options texts: stream 0x5B320 (73 tiles), next stream 0x5C654
    raw = bytearray(decompress(bytes(prog[0x5B320:0x5C654])))
    rows = strip_from(raw, 0, len(raw) // 128)
    in_place(rows, [
        (0, 5, 'Vel. cursor'), (8, 3, 'Sonido'), (11, 3, ['Estéreo', 'Estér.']), (14, 3, 'Mono'),
        (17, 2, 'Voz'), (19, 2, 'Sí'), (21, 2, 'No'), (23, 3, ['Mandos', 'Mand.']), (26, 2, 'Fijar'),
        (28, 3, ['Aceptar', 'Acept.']), (31, 2, 'Salir'), (33, 2, 'OK'), (35, 3, ['Cancelar', 'Cancel.']),
        (38, 2, ['Mover', 'Mov.']), (40, 3, 'Atacar'), (43, 2, 'Def.'), (45, 2, ['Carga', 'Carg.']), (47, 2, 'Ver'),
        (49, 2, ['Hablar', 'Habl.']), (51, 4, 'Ninguno'), (55, 3, ['Original', 'Orig.']),
    ], face, size, base)
    strip_into(raw, 0, rows)
    used = put_stream(prog, 0x5B320, 0x5C654 - 0x5B320, bytes(raw), 'textos de opciones')
    print(f'  opciones: {used} bytes comprimidos de {0x5C654 - 0x5B320}')
    preview.append(('opciones', rows, len(raw) // 128))
    # Load / Options / Exit row: stream 0x59878 (15 tiles) drawn as one 12-tile row
    raw = bytearray(decompress(bytes(prog[0x59878:0x59C70])))
    rows = strip_from(raw, 0, len(raw) // 128)
    in_place(rows, [(0, 3, 'Cargar'), (3, 5, 'Opciones'), (8, 4, 'Salir')], face, size, base)
    strip_into(raw, 0, rows)
    used = put_stream(prog, 0x59878, 0x59C70 - 0x59878, bytes(raw), 'fila cargar/opciones/salir')
    print(f'  fila cargar/opciones/salir: {used} bytes comprimidos')
    preview.append(('cargar-opciones-salir', rows, len(raw) // 128))
    # Tab label «Options» painted in the options frame (4 bpp 288x144, stream 0x5AE38..0x5B320)
    from rotulos import load_palette, read_indices, replace_text, to_image, write_indices
    raw = bytearray(decompress(bytes(prog[0x5AE38:0x5B320])))
    fr = read_indices(raw, 0, 288, 144, 4)
    pal = load_palette(('options', 'cram', 0xA2C0), 4)
    replace_text(fr, pal, (11, 122, 56, 16), 'Opciones', 'CENTURY.TTF', 15, ink=5, bg=15, allowed=[15, 5])
    write_indices(raw, 0, fr, 4)
    used = put_stream(prog, 0x5AE38, 0x5B320 - 0x5AE38, bytes(raw), 'marco de opciones')
    print(f'  marco de opciones: {used} bytes comprimidos')


# Every WKL##.BIN stage file repeats the same battle command bar, but at a different absolute
# offset, computed from a per-file header (block 0, images 5-32 of the "battle menu" section).
# Algorithm from the English translation team's own tooling (WklBattleMenuExtractor in
# local/research/noahsteam-repo/SakuraTaisen/SakuraTaisen.cpp) — not guessed from a single file.
WKL_STAGES = ['WKL%02d' % n for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 21, 22)]


def battle_bar_sprites(data: bytes):
    """Returns the 28 (file_offset, width, height) battle-bar sprites of a WKL##.BIN file."""
    image_data_addr = struct.unpack_from('>I', data, 0xE8)[0]
    block_off, _ = struct.unpack_from('>II', data, image_data_addr)  # block 0 only: the command bar
    num_images = struct.unpack_from('>H', data, image_data_addr + block_off)[0]
    header_end = image_data_addr + block_off + 8
    misc_end = header_end + 16 * num_images + 8
    sprites = []
    for k in range(5, 33):  # 0-4 are other HUD bars; 5-32 are the 28 command-bar words/icons
        offset_from_header, offset_from_prev, w, h, _unknown = struct.unpack_from('>IIHHI', data, header_end + k * 16)
        sprites.append((misc_end + offset_from_header + offset_from_prev, w, h))
    return sprites


# Text labels of the 28 command-bar sprites (all 28 are words; "*" variants are the highlighted ones).
# English order: Mov, Mov*, Move, Atk, Atk*, Normal, Normal*, Special, Special*, Combo, Combo*, Def, Def*,
# Rest, Rest*, Defend, Defend*, Heal, Heal*, Info, Info*, Map, Advice, End, End*, Spcl, Spcl*, Cover.
BATTLE_BAR_ES = [
    'Mov', 'Mov', 'Mover', 'Atq', 'Atq', 'Normal', 'Normal', 'Espec.', 'Espec.', 'Combo', 'Combo',
    'Def', 'Def', 'Desc.', 'Desc.', 'Prot.', 'Prot.', 'Curar', 'Curar', 'Info', 'Info',
    'Mapa', 'Aviso', 'Fin', 'Fin', 'Esp.', 'Esp.', 'Cubrir',
]

# The English bar uses a condensed pixel font: strokes 1 px wide, 8 rows of capital/ascender (rows 4-11 of the
# 16 px sprite), x-height 6 rows, descenders 2 more rows, one empty column between letters, and a 1 px dark
# outline (palette index 3) shared between neighbours (4-connected, no corners). Only the "fill" of each letter is stored here
# (10 rows: row 0 = sprite row 4). The letters were read from the English sprites themselves (WKL02.BIN);
# P, F, u, q and "." do not occur there and are derived (R without leg, E without base, n turned 180 degrees,
# p mirrored, one pixel on the baseline).
_PIXEL_FONT = {
    'M': ('#...#', '#...#', '#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '.....', '.....'),
    'o': ('...', '...', '.#.', '#.#', '#.#', '#.#', '#.#', '.#.', '...', '...'),
    'v': ('...', '...', '#.#', '#.#', '#.#', '#.#', '#.#', '##.', '...', '...'),
    'A': ('.#.', '#.#', '#.#', '#.#', '###', '#.#', '#.#', '#.#', '...', '...'),
    't': ('...', '.#.', '###', '.#.', '.#.', '.#.', '.#.', '..#', '...', '...'),
    'k': ('#...', '#...', '#..#', '#.#.', '##..', '##..', '#.#.', '#..#', '....', '....'),
    'N': ('#..#', '#..#', '##.#', '#.##', '#.##', '#..#', '#..#', '#..#', '....', '....'),
    'r': ('...', '...', '##.', '#.#', '#..', '#..', '#..', '#..', '...', '...'),
    'm': ('.....', '.....', '##.#.', '#.#.#', '#.#.#', '#.#.#', '#.#.#', '#.#.#', '.....', '.....'),
    'a': ('...', '...', '.#.', '#.#', '.##', '#.#', '#.#', '.##', '...', '...'),
    'l': ('#', '#', '#', '#', '#', '#', '#', '#', '.', '.'),
    'S': ('.#.', '#.#', '#..', '.#.', '..#', '..#', '#.#', '.#.', '...', '...'),
    'p': ('...', '...', '##.', '#.#', '#.#', '#.#', '#.#', '##.', '#..', '#..'),
    'e': ('...', '...', '.#.', '#.#', '###', '#..', '#.#', '.#.', '...', '...'),
    'c': ('...', '...', '.#.', '#.#', '#..', '#..', '#.#', '.#.', '...', '...'),
    'i': ('#', '.', '#', '#', '#', '#', '#', '#', '.', '.'),
    'C': ('.#.', '#.#', '#..', '#..', '#..', '#..', '#.#', '.#.', '...', '...'),
    'b': ('#..', '#..', '##.', '#.#', '#.#', '#.#', '#.#', '##.', '...', '...'),
    'D': ('##.', '#.#', '#.#', '#.#', '#.#', '#.#', '#.#', '##.', '...', '...'),
    'R': ('##.', '#.#', '#.#', '#.#', '##.', '#.#', '#.#', '#.#', '...', '...'),
    's': ('....', '....', '.##.', '#..#', '.#..', '..#.', '#..#', '.##.', '....', '....'),
    'I': ('###', '.#.', '.#.', '.#.', '.#.', '.#.', '.#.', '###', '...', '...'),
    'n': ('...', '...', '##.', '#.#', '#.#', '#.#', '#.#', '#.#', '...', '...'),
    'f': ('..#', '.#.', '###', '.#.', '.#.', '.#.', '.#.', '.#.', '...', '...'),
    'E': ('###', '#..', '#..', '###', '#..', '#..', '#..', '###', '...', '...'),
    'd': ('..#', '..#', '.##', '#.#', '#.#', '#.#', '#.#', '.##', '...', '...'),
}
_PIXEL_FONT['P'] = _PIXEL_FONT['R'][:5] + ('#..',) * 3 + ('...',) * 2
_PIXEL_FONT['F'] = _PIXEL_FONT['E'][:7] + ('#..', '...', '...')
_PIXEL_FONT['u'] = ('...', '...') + tuple(r[::-1] for r in reversed(_PIXEL_FONT['n'][2:8])) + ('...', '...')
_PIXEL_FONT['q'] = tuple(r[::-1] for r in _PIXEL_FONT['p'])
_PIXEL_FONT['.'] = ('.',) * 7 + ('#',) + ('.',) * 2
_PIXEL_KERN = {('r', 'm'): 0}  # the English "rm" of "Normal" touches; every other pair has 1 empty column
# Sprites 9-10 ("Combo") sit one row higher than the rest of the bar in the original.
_BAR_RISE = {9: 1, 10: 1}


def pixel_word(text: str, w: int, h: int = 16, rise: int = 0):
    """Rows of a w x h sprite as chars ('.' empty, 'f' letter fill, 'o' outline) with the word in the bar's
    pixel font centred as the English sprites are. Raises SystemExit if it does not fit."""
    cols, x = [], 0
    for i, ch in enumerate(text):
        glyph = _PIXEL_FONT[ch]
        if i:
            x += _PIXEL_KERN.get((text[i - 1], ch), 1)
        cols.append((x, glyph))
        x += len(glyph[0])
    fill_w = x
    left = max(0, (w - fill_w - 2) // 2 + 1)
    if left + fill_w > w:
        raise SystemExit(f'combate: {text!r} no cabe en {w}px')
    fill = [[False] * w for _ in range(h)]
    for gx, glyph in cols:
        for gy, row in enumerate(glyph):
            for dx, c in enumerate(row):
                y = 4 - rise + gy
                if c == '#' and 0 <= y < h:
                    fill[y][left + gx + dx] = True
    out = [['.'] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if fill[y][x]:
                out[y][x] = 'f'
            elif ((y and fill[y - 1][x]) or (y < h - 1 and fill[y + 1][x])
                  or (x and fill[y][x - 1]) or (x < w - 1 and fill[y][x + 1])):
                out[y][x] = 'o'
    return [''.join(r) for r in out]


# Block 3, sprite 1 is the unit-information panel; the guest draws its
# title, bars, values and special-move name separately.
TACTICAL_STATUS_LABELS = (
    ((9, 34, 43, 15), 'Salud'),
    ((9, 50, 43, 14), 'Ánimo'),
    ((49, 72, 24, 15), 'Atq'),
    ((9, 88, 39, 15), 'Piloto'),
    ((9, 104, 39, 15), 'Armad.'),
    ((9, 120, 39, 15), 'Conf.'),
    ((9, 136, 39, 15), 'Poder'),
    ((9, 160, 39, 15), 'Especial'),
)


def traducir_estado_tactico(wkl: bytearray):
    """Translate only the confirmed English label boxes of a WKL status panel."""
    from rotulos import read_indices, replace_text, write_indices

    if len(wkl) < 0xEC:
        raise ValueError('WKL: cabecera truncada')
    directory = struct.unpack_from('>I', wkl, 0xE8)[0]
    if directory + 32 > len(wkl):
        raise ValueError('WKL: directorio gráfico truncado')
    offset, length = struct.unpack_from('>II', wkl, directory + 3 * 8)
    start, end = directory + offset, directory + offset + length
    if length < 40 or end > len(wkl):
        raise ValueError('WKL: bloque de estado inválido')
    count = struct.unpack_from('>H', wkl, start)[0]
    if count < 2 or 16 + count * 16 > length:
        raise ValueError('WKL: tabla de imágenes de estado inválida')
    relative, previous, width, height, _ = struct.unpack_from('>IIHHI', wkl, start + 24)
    panel = start + 16 + count * 16 + relative + previous
    size = width * height // 2
    if (width, height) != (152, 184) or panel + size > end or sha256(
        wkl[panel:panel + size]
    ).hexdigest() != '41c2da377699bd8e619c972918ea31788d9dfc0a87a0abb097d21f2dd36c4db8':
        raise ValueError('WKL: panel de estado inglés desconocido')

    rows = read_indices(wkl, panel, width, height, 4)
    # The verified panel uses white, muted outline and indigo ground.
    palette = {1: (208, 208, 208), 3: (56, 56, 72), 4: (40, 40, 80)}
    for box, text in TACTICAL_STATUS_LABELS:
        replace_text(rows, palette, box, text, 'georgiab.ttf', 11,
                     ink=1, bg=4, allowed=(1, 3, 4))
    write_indices(wkl, panel, rows, 4)


def combate(files: Files, preview):
    """Battle command bar, every stage (WKL01..WKL26.BIN): raw uncompressed 4bpp sprites, no LZ budget to
    respect. Every word is composed with the bar's own condensed pixel font (see _PIXEL_FONT) so it looks
    like the English one: letter fill keeps the original sprite's colour (1 normal, 12 highlighted),
    outline is index 3, background 0."""
    for stage in WKL_STAGES:
        wkl = files[f'/SAKURA2/{stage}.BIN']
        sprites = battle_bar_sprites(bytes(wkl))
        if len(sprites) != len(BATTLE_BAR_ES):
            raise SystemExit(f'combate {stage}: {len(sprites)} sprites, se esperaban {len(BATTLE_BAR_ES)}')
        for k, (text, (start, w, h)) in enumerate(zip(BATTLE_BAR_ES, sprites)):
            old = [((wkl[start + i // 2] >> 4) if i % 2 == 0 else (wkl[start + i // 2] & 15)) for i in range(w * h)]
            tones = {v for v in old if v not in (0, 3)}
            if len(tones) != 1:
                raise SystemExit(f'combate {stage}: sprite {k} con relleno {tones}')
            fill = tones.pop()
            rows = pixel_word(text, w, h, _BAR_RISE.get(k, 0))
            for y in range(h):
                for x in range(w):
                    v = {'.': 0, 'o': 3, 'f': fill}[rows[y][x]]
                    i_byte = start + (y * w + x) // 2
                    b = wkl[i_byte]
                    if x % 2 == 0:
                        wkl[i_byte] = (v << 4) | (b & 0x0F)
                    else:
                        wkl[i_byte] = (b & 0xF0) | v
        traducir_estado_tactico(wkl)
        traducir_ataques_wkl(wkl)
        traducir_comandos_aliados_wkl(wkl)
        traducir_mosquete_wkl(wkl)
        traducir_pausa_tactica(wkl)
        print(f'  combate {stage}: {len(sprites)} sprites, ficha de unidad, ataques y pausa traducidos')


def estado(files: Files, preview):
    """Status screen (ICATALL.DAT stream 0x13800, 48 tiles). Character names (tiles 0-16) stay as-is."""
    ic = files['/SAKURA1/ICATALL.DAT']
    face, size, base = 'CENTURY.TTF', 15, 13
    raw = bytearray(decompress(bytes(ic[0x13800:0x15000])))
    rows = strip_from(raw, 0, len(raw) // 128)
    in_place(rows, [
        (17, 2, 'Alto'), (20, 2, ['Ánimo', 'Mor.']), (22, 3, 'Normal'), (25, 2, ['Humor', 'Hum.']),
        (27, 3, ['Pésimo', 'Pés.']), (30, 2, ['Atq.', 'Atq']), (32, 2, 'Def'), (34, 2, 'Mov'),
    ], face, size, base)
    strip_into(raw, 0, rows)
    used = put_stream(ic, 0x13800, 0x15000 - 0x13800, bytes(raw), 'textos de estado')
    print(f'  estado: {used} bytes comprimidos de {0x15000 - 0x13800}')
    preview.append(('estado', rows, len(raw) // 128))


CARGA_ES = {
    'The Floral Assault Troop!': '¡Asalto floral imperial!',
    'Hive of Darkness': 'Colmena Oscura',
    'Unfit To Be Captain?': '¿Capitán indigno?',
    'Great Rampage!': '¡Gran estrago!',
    "A Maiden's Willpower!": '¡Voluntad de doncella!',
    "The Capital's Collapse": 'La caída de la capital',
    'The Limit of Life!': '¡Vida al límite!',
    'Days Of Peace': 'Días de paz',
    'The Ultimate Weapon': 'El arma definitiva',
    'Final Judgement': 'El juicio final',
    'Data to copy': 'Copiar', 'Copy to?': '¿Copiar adónde?', 'Data to load': 'Cargar',
    'Data to save': 'Guardar', 'Data to delete': 'Borrar', 'No Files': 'Vacío', 'Delete?': '¿Borrar?',
    'Yes': 'Sí', 'No': 'No', 'No Data': 'Vacío',
    'Please insert Disc 2': 'Inserta el disco 2', 'Please insert Disc 1': 'Inserta el disco 1',
    'Finale': 'Final', 'The End': 'Fin', "can't be read.": 'no es legible.',
    'To continue playing,': 'Para seguir jugando,', 'to continue playing.': 'para seguir jugando.',
    'Save Complete!': '¡Guardado!', 'Copy?': '¿Copiar?', 'Save?': '¿Guardar?', 'Load?': '¿Cargar?',
    'Delete Complete!': '¡Borrado!', 'Copy Complete!': '¡Copiado!',
}


# Character order of the 8x16 cells in the English load-screen font (SAKURA+0x5C654), read from the strip.
CARGA_CELDAS = (
    'Bapt9 pyGrs 1  1 2Peysid'
    'Plif! 10 AHi Bacilad C D'
    "inag Faiisalt 's LYe2 ap"
    " Oatau Tl  Wayrkl'd robe"
    ' co? e id.3 sa oRascse r'
    ' t we e!socass. ckJu4 co'
    "taSaten tilen'f toCallde"
    'dglolplt5 Con?o Thma  le'
    'ToeamiDaLiDempLoDig,g.em'
    'en6 eresveetnaManeUlUn? '
    'finsnu7 EnEpodofoma onop'
    'NoorFiFlow8 pipla?A po  '
)


def carga(files: Files, preview):
    """Load/save screen: 8x16 glyph PAIRS per 16x16 tile (stream SAKURA+0x5C654, 144 tiles) and
    zero-terminated 1-based tile lists at SAKURA+0x5A09E..0x5A34A, mostly reached through pointers.
    Glyphs come from the dialogue font (same typeface, full CP1252), remapped to this ink ramp."""
    import json
    prog = files['/SAKURA']
    base = 0x06004000
    knj = bytes(files.disc.read('/SAKURA1/0100KNJ.BIN'))
    cells = CARGA_CELDAS
    raw = bytearray(decompress(bytes(prog[0x5C654:0x5E190])))
    tiles_n = len(raw) // 128
    rows = strip_from(raw, 0, tiles_n)

    def knj_glyph(ch):
        g = ch.encode('cp1252')[0] - 1
        return [[(knj[g * 128 + y * 8 + x // 2] >> 4) if x % 2 == 0 else (knj[g * 128 + y * 8 + x // 2] & 15)
                 for x in range(8)] for y in range(T)]

    # Glyphs: the strip's own English cells when the character exists; accented letters = base cell
    # plus the accent of the dialogue font (aligned to the cell); ¿ ¡ = ? ! rotated 180 degrees;
    # anything else comes from the dialogue font through the learned ink map.
    import unicodedata
    from collections import Counter, defaultdict

    def cell(ch):
        c = cells.index(ch)
        return [[rows[y][c * 8 + x] for x in range(8)] for y in range(T)]

    def shifted(g, dx, dy):
        return [[g[y - dy][x - dx] if 0 <= y - dy < T and 0 <= x - dx < 8 else 0 for x in range(8)] for y in range(T)]

    def agree(ch, dx, dy):
        a, b = shifted(knj_glyph(ch), dx, dy), cell(ch)
        return sum(1 for y in range(T) for x in range(8) if a[y][x] and b[y][x]) -             sum(1 for y in range(T) for x in range(8) if bool(a[y][x]) != bool(b[y][x]))

    shared = [c for c in set(cells) if c not in ' ']
    DX, DY = max(((dx, dy) for dx in range(-3, 4) for dy in range(-4, 5)),
                 key=lambda d: sum(agree(c, *d) for c in shared))
    print(f'  carga: desfase fuente de diálogo -> celdas dx={DX} dy={DY}')
    offset = lambda ch: DX

    votes = defaultdict(Counter)
    for ch in set(cells) - {' '}:
        a, b = shifted(knj_glyph(ch), DX, DY), cell(ch)
        for y in range(T):
            for x in range(8):
                votes[a[y][x]][b[y][x]] += 1
    vmap = {k: v.most_common(1)[0][0] for k, v in votes.items()}

    def glyph(ch):
        if ch in cells and ch != ' ':
            return cell(ch)
        if ch in '¿¡':
            src = cell({'¿': '?', '¡': '!'}[ch])
            return [list(reversed(r)) for r in reversed(src)]
        g = shifted(knj_glyph(ch), DX, DY)
        return [[vmap.get(v, 0) for v in r] for r in g]
    # parse the English strings in place
    start, end = 0x5A09E, 0x5A34A
    strings, cur, at = [], [], start
    for i in range(start, end, 2):
        v = struct.unpack_from('>H', prog, i)[0]
        if v == 0:
            strings.append((at, cur))
            cur, at = [], i + 2
        else:
            cur.append(v)
    pointers = {}
    for i in range(0, len(prog) - 3, 2):
        v = struct.unpack_from('>I', prog, i)[0]
        if base + start <= v < base + end:
            pointers.setdefault(v - base, []).append(i)
    texts = []
    for off, lst in strings:
        en = ''.join(cells[2 * (t - 1):2 * (t - 1) + 2] for t in lst)
        es = CARGA_ES.get(en.strip(), None)
        if es is None and not en.startswith('Ep.') and en.strip():
            raise SystemExit(f'carga: sin traducción para {en!r}')
        if en.strip() == 'Ep. 10' and off not in pointers:
            es = ''
        texts.append((off, len(lst), en, es if es is not None else en.rstrip()))
    # tiles: unique glyph pairs of every final string. Buttons draw fixed English tile ids
    # (Copy=[90,4], Del=[102,41], Yes=[34,6], No=[133]); those ids keep their role with Spanish text.
    PINNED = {90: 'Co', 4: 'p.', 102: 'Bo', 41: 'r.', 34: 'Sí', 6: '  ', 133: 'No', 95: '  ', 144: '  '}
    slots = [None] * tiles_n
    for tid, pair in PINNED.items():
        slots[tid - 1] = pair
    for _, _, _, s in texts:
        s = s + (' ' if len(s) % 2 else '')
        for k in range(0, len(s), 2):
            if s[k:k + 2] not in slots:
                free = slots.index(None) if None in slots else None
                if free is None:
                    raise SystemExit(f'carga: más pares que {tiles_n} tiles')
                slots[free] = s[k:k + 2]
    pairs = [x if x is not None else '  ' for x in slots]
    GL = {ch: glyph(ch) for ch in set(''.join(pairs)) if ch != ' '}
    for t in range(tiles_n):
        for y in range(T):
            rows[y][t * T:t * T + T] = [0] * T
    for t, pair in enumerate(pairs):
        for half, ch in enumerate(pair):
            if ch == ' ':
                continue
            g = GL[ch]
            for y in range(T):
                for x in range(8):
                    rows[y][t * T + half * 8 + x] = g[y][x]
    print(f'  carga: {len(pairs)} pares de letras en {tiles_n} tiles')
    # strings: in place when they fit, otherwise relocated into freed space (only if pointed to)
    enc = lambda s: [pairs.index((s + (' ' if len(s) % 2 else ''))[k:k + 2]) + 1 for k in range(0, len(s) + len(s) % 2, 2)]
    area = bytearray(prog[start:end])
    used = bytearray(len(area))
    late = []
    for off, slot, en, es in texts:
        codes = enc(es) if es else []
        if not es:
            area[off - start:off - start + 2 * slot + 2] = bytes(2 * slot + 2)
            continue
        if len(codes) <= slot:
            data = words16(codes) + b'\0\0'
            area[off - start:off - start + 2 * slot + 2] = data + bytes(2 * slot + 2 - len(data))
            used[off - start:off - start + len(data)] = b'\1' * len(data)
        elif off in pointers:
            late.append((off, codes, es))
            area[off - start:off - start + 2 * slot + 2] = bytes(2 * slot + 2)
        else:
            raise SystemExit(f'carga: {es!r} no cabe en su hueco y no tiene puntero')
    for off, codes, es in late:
        need = 2 * len(codes) + 2
        spot = next((i for i in range(0, len(area) - need + 1, 2) if not any(used[i:i + need])), None)
        if spot is None:
            raise SystemExit(f'carga: sin espacio para reubicar {es!r}')
        area[spot:spot + need] = words16(codes) + b'\0\0'
        used[spot:spot + need] = b'\1' * need
        for p in pointers[off]:
            struct.pack_into('>I', prog, p, base + start + spot)
        print(f'  carga: {es!r} reubicada {off:#x} -> {start + spot:#x}')
    prog[start:end] = area
    strip_into(raw, 0, rows)
    size = put_stream(prog, 0x5C654, 0x5E190 - 0x5C654, bytes(raw), 'fuente de la carga')
    print(f'  carga: tira {size} bytes comprimidos de {0x5E190 - 0x5C654}')
    preview.append(('carga', rows, tiles_n))
    # Frame labels painted into the bitmap itself: «File 1/2/3» and «System RAM» (stream 0x5E190..0x5EB4C)
    from rotulos import load_palette, read_indices, replace_text, write_indices
    marco_start, marco_end = 0x5E190, 0x5EB4C
    raw = bytearray(decompress(bytes(prog[marco_start:marco_end])))
    fr = read_indices(raw, 0, 288, 184, 4)
    pal = load_palette(('load', 'cram', 0x2C0), 4)
    ink, bg, allowed = 5, 2, [2, 5]
    for n, y in ((1, 40), (2, 80), (3, 120)):
        replace_text(fr, pal, (196, y, 60, 16), f'Partida {n}', 'CENTURY.TTF', 15, ink=ink, bg=bg, allowed=allowed)
    replace_text(fr, pal, (2, 162, 108, 16), 'RAM del sistema', 'CENTURY.TTF', 15, ink=ink, bg=bg, allowed=allowed)
    write_indices(raw, 0, fr, 4)
    used = put_stream(prog, marco_start, marco_end - marco_start, bytes(raw), 'marco de carga')
    print(f'  marco de carga: {used} bytes comprimidos de {marco_end - marco_start}')


def titulo_rotulos(files: Files, preview, compare):
    """Painted labels on the title: frame header/banner (8 bpp) and Press Start (4 bpp)."""
    from rotulos import load_palette, read_indices, replace_text, to_image, write_indices
    logo = files['/SAKURA1/LOGO.SH2']
    # Program frame: 208x152, 8 bpp, stream 0x10808..0x11770
    raw = bytearray(decompress(bytes(logo[0x10808:0x11770])))
    rows = read_indices(raw, 0, 208, 152, 8)
    pal = load_palette(('program', 'cram', 0x500), 8)
    before = to_image([r[:] for r in rows], pal)
    from letras import compose, cut, mirror
    # «Programa»: the English «Program» plus its own «a» (letters of the English patch).
    head = (46, 9, 116, 16)
    bg_head = lambda v: v == 254
    program, a = cut(rows, head, 61, 149, bg_head), cut(rows, head, 114, 127, bg_head)
    compose(rows, head, [program, a], 1, 254)
    # Banner: «Revista Imperial de Combate» from the banner's own glyphs; d = mirrored b, s drawn alike.
    ban = (22, 129, 164, 7)
    bg_ban = lambda v: v == 12
    g = lambda x0, x1: cut(rows, ban, x0, x1, bg_ban)
    G = dict(I=g(37, 41), m=g(41, 53), p=g(53, 61), e=g(61, 66), r=g(66, 71), i=g(71, 75), a=g(75, 82),
             l=g(82, 86), C=g(89, 96), o=g(96, 102), b=g(114, 122), t=g(128, 133), R=g(135, 142), v=g(149, 155))
    G['d'] = mirror(G['b'])
    W, A, N = 255, 165, None
    G['s'] = [[N, N, N, N, N], [N, N, N, N, N], [A, W, W, W, A], [W, W, A, N, N], [A, W, W, W, A],
              [N, N, A, W, W], [A, W, W, W, A]]
    words = ['Revista', 'Imperial', 'de', 'Combate']
    glyphs, gaps = [], []
    for wi, word in enumerate(words):
        for ci, ch in enumerate(word):
            glyphs.append(G[ch])
            gaps.append(3 if ci == len(word) - 1 and wi < len(words) - 1 else 0)
    compose(rows, ban, glyphs, gaps, 12)
    compare.append(('marco del título', before, to_image(rows, pal)))
    write_indices(raw, 0, rows, 8)
    used = put_stream(logo, 0x10808, 0x11770 - 0x10808, bytes(raw), 'marco del título')
    print(f'  marco del título: {used} bytes comprimidos')
    # Press Start: 152x24, 4 bpp at +81760 of stream 0x25410..0x29940
    raw = bytearray(decompress(bytes(logo[0x25410:0x29940])))
    rows = read_indices(raw, 81760, 152, 24, 4)
    pal = load_palette(('title', 'cram', 0x60), 4)
    before = to_image([r[:] for r in rows], pal)
    # «Pulsa Start» from the English letters: P, u, s, a cut out; l from the B stem; «Start» kept whole.
    box = (0, 0, 152, 24)
    bg0 = lambda v: v == 0
    c = lambda x0, x1: cut(rows, box, x0, x1, bg0)
    P, u, s, a, start = c(3, 15), c(101, 113), c(40, 47), c(63, 76), c(48, 89)
    stem = c(90, 93)  # B stem: outline, ink, ink; close it with a mirrored outline column
    l = [r + [r[0]] for r in stem]
    compose(rows, box, [P, u, l, s, a, start], [0, 0, 0, 0, 6], 0)
    compare.append(('pulsa start', before, to_image(rows, pal)))
    write_indices(raw, 81760, rows, 4)
    used = put_stream(logo, 0x25410, 0x29940 - 0x25410, bytes(raw), 'logo del título')
    print(f'  logo del título: {used} bytes comprimidos')


def save_compare(compare):
    from PIL import Image, ImageDraw
    W = max(a.width + b.width + 10 for _, a, b in compare)
    H = sum(max(a.height, b.height) + 16 for _, a, b in compare)
    sheet = Image.new('RGB', (W, H), (40, 40, 40))
    dr = ImageDraw.Draw(sheet)
    y = 0
    for name, a, b in compare:
        dr.text((2, y), name, fill=(255, 255, 0))
        sheet.paste(a, (0, y + 14))
        sheet.paste(b, (a.width + 10, y + 14))
        y += max(a.height, b.height) + 16
    path = os.path.join(MENUS, 'tmp', 'menus_es_rotulos.png')
    sheet.save(path)
    print('comparación', os.path.abspath(path))


def save_preview(preview):
    from PIL import Image, ImageDraw
    S = 3
    ims = []
    for name, rows, n in preview:
        w = len(rows[0])
        im = Image.new('RGB', (w * S, T * S + 12), 'white')
        dr = ImageDraw.Draw(im)
        dr.text((2, 0), name, fill=(0, 0, 255))
        for y in range(T):
            for x in range(w):
                v = rows[y][x]
                if v:
                    g = int((v - 1) / 14 * 220)
                    dr.rectangle([x * S, y * S + 12, x * S + S - 1, y * S + 12 + S - 1], fill=(g, g, g))
        for t in range(n):
            dr.line([(t * T * S, 12), (t * T * S, 12 + T * S)], fill=(150, 200, 255))
        ims.append(im)
    W = max(i.width for i in ims)
    sheet = Image.new('RGB', (W, sum(i.height + 4 for i in ims)), (60, 60, 60))
    y = 0
    for i in ims:
        sheet.paste(i, (0, y))
        y += i.height + 4
    path = os.path.join(MENUS, 'tmp', 'menus_es_preview.png')
    sheet.save(path)
    print('vista previa', os.path.abspath(path))


def main():
    import fuente
    fuente.LEVELS = [1, 5, 9, 13]  # four ink steps: matches the look and keeps every stream within its space
    parser = argparse.ArgumentParser()
    parser.add_argument('--iso', default=ISO)
    args = parser.parse_args()
    files = Files(Disc(args.iso))
    preview = []
    intermedio(files, preview)
    titulo(files, preview)
    inventario(files, preview)
    opciones(files, preview)
    carga(files, preview)
    estado(files, preview)
    combate(files, preview)
    compare = []
    titulo_rotulos(files, preview, compare)
    files.save()
    save_preview(preview)
    save_compare(compare)


if __name__ == '__main__':
    main()
