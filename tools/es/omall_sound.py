"""Localize the verified Saturn music gallery without modifying playback actions."""

import struct
from collections import Counter
from hashlib import sha256

from menus_es import put_stream
from omall_movie import SOURCE_SHA
from omall_movie_frame import FOOTER
from red_lz import decompress
from tiras import strip_from, strip_into

ROWS = (
    ("Title", "Título"),
    ("Blooming Maidens", "Doncellas en flor"),
    ("Excitement", "Emoción"),
    ("Silent Nihilist", "Nihilista silencioso"),
    ("Move Out!", "¡En marcha!"),
    ("Hive of Darkness", "Colmena de la Oscuridad"),
    ("A Fallen Angel", "Ángel caído"),
    ("Nighttime", "Noche"),
    ("Daytime", "Día"),
    ("Cheerful Theater", "Teatro alegre"),
    ("Strategy Meeting", "Reunión táctica"),
    ("Do Your Best!", "¡Ánimo!"),
    ("For the Capital", "Por la capital"),
    ("Final Battle", "Batalla final"),
    ("Sumire", "Sumire"),
    ("Kohran", "Kohran"),
    ("Iris", "Iris"),
    ("Sakura", "Sakura"),
    ("Kanna", "Kanna"),
    ("Maria", "Maria"),
    ("Ayame", "Ayame"),
    ("Battle 1", "Batalla 1"),
    ("Battle 2", "Batalla 2"),
    ("Victory", "Victoria"),
    ("Defeat", "Derrota"),
    ("Friendship", "Amistad"),
    ("Farewell", "Despedida"),
    ("Comedy", "Comedia"),
    ("New Years", "Año Nuevo"),
    ("Sadness", "Tristeza"),
    ("Anger", "Ira"),
    ("Joy", "Alegría"),
    ("Knights of Twilight", "Caballeros del ocaso"),
    ("Conspiracy", "Conspiración"),
    ("Blooming Maidens (Vocal)", "Doncellas en flor (vocal)"),
    ("EXIT", "SALIR"),
)
TILE_COUNT = 127
TABLE_END = 0x1B0
POINTERS = 0x256
FRAME_FOOTER = 0xAC80
TABLE_SHA = "643352823f7f0c4b64e2e87fefd5512c5669df8e1be07e1f558854e5a62c4bb1"
POINTERS_SHA = "15047abde58f38273745eb9d9cd8ecd5303b585264fae9a0e1f0066203102cae"
LAYOUT_SHA = "382cb5e6def70125b90a393083973ce4ac3668c6b46a7c0b032827562e8589c9"


def digest(blob):
    return sha256(blob).hexdigest()


def sound_glyphs(old_atlas, table):
    rows = strip_from(old_atlas, 0, TILE_COUNT)
    choices = {}
    cursor = 0
    starts = []
    for original, _ in ROWS:
        starts.append(cursor)
        word = []
        while tid := struct.unpack_from(">H", table, cursor)[0]:
            if not 1 <= tid <= TILE_COUNT:
                raise ValueError("OMALL: ficha musical fuera del atlas")
            word.extend(((tid - 1) * 16, (tid - 1) * 16 + 8))
            cursor += 2
        cursor += 2
        if len(word) != len(original) + len(original) % 2:
            raise ValueError(f"OMALL: rótulo musical inesperado para {original}")
        for char, x in zip(original.ljust(len(word)), word):
            glyph = tuple(tuple(row[x : x + 8]) for row in rows)
            if char != " " and any(map(any, glyph)):
                choices.setdefault(char, Counter())[glyph] += 1
    if cursor != len(table):
        raise ValueError("OMALL: longitud inesperada de la tabla de música")
    glyphs = {c: hits.most_common(1)[0][0] for c, hits in choices.items()}
    glyphs[" "] = ((0,) * 8,) * 16
    for accent, base, pixels in (
        ("Á", "A", ((3, 1), (4, 0))),
        ("á", "a", ((3, 2), (4, 1))),
        ("í", "i", ((3, 2), (4, 1))),
        ("ó", "o", ((3, 2), (4, 1))),
        ("é", "e", ((3, 2), (4, 1))),
        ("ñ", "n", ((1, 2), (2, 1), (3, 1), (4, 2), (5, 2), (6, 1))),
    ):
        g = [list(row) for row in glyphs[base]]
        if base == "i":
            g[:4] = [[0] * 8 for _ in range(4)]
        for x, y in pixels:
            g[y][x] = 1
        glyphs[accent] = tuple(map(tuple, g))
    glyphs["¡"] = tuple(row[::-1] for row in glyphs["!"][::-1])
    return rows, starts, glyphs


def build_data(old_atlas, movie_atlas, program, t):
    table = program[t : t + TABLE_END]
    if digest(table) != TABLE_SHA:
        raise ValueError("OMALL: tabla de música sin firma conocida")
    rows, starts, glyphs = sound_glyphs(old_atlas, table)
    movie_rows = strip_from(movie_atlas, 0, 144)
    for char, x in {"R": 992, "b": 1448, "P": 80, "L": 1488, "z": 576}.items():
        glyphs[char] = tuple(tuple(row[x : x + 8]) for row in movie_rows)
    slots = {}
    strings = bytearray()
    dst = {}
    for offset, (_, text) in zip(starts, ROWS):
        if len(text) > 26:
            raise ValueError(f"OMALL: el rótulo musical no cabe: {text}")
        dst[offset] = len(strings)
        text = text.ljust(len(text) + len(text) % 2)
        for i in range(0, len(text), 2):
            tile = slots.setdefault(text[i : i + 2], len(slots) + 1)
            strings.extend(struct.pack(">H", tile))
        strings.extend(b"\0\0")
    if len(strings) > POINTERS or len(slots) > TILE_COUNT:
        raise ValueError("OMALL: las pistas no caben en la tabla o el atlas")
    for pair, tile in slots.items():
        x = (tile - 1) * 16
        for y in range(16):
            rows[y][x : x + 16] = glyphs[pair[0]][y] + glyphs[pair[1]][y]
    atlas = bytearray(old_atlas)
    strip_into(atlas, 0, rows)
    addr = 0x06004000 + t
    pointers = [p - addr for p in struct.unpack_from(">37I", program, t + POINTERS)]
    if set(pointers) != set(starts):
        raise ValueError("OMALL: punteros de pistas inesperados")
    if digest(struct.pack(">37H", *pointers)) != POINTERS_SHA:
        raise ValueError("OMALL: orden inesperado de las pistas")
    if digest(program[t + 0x2EA : t + 0x36C]) != LAYOUT_SHA or any(
        program[t + TABLE_END : t + POINTERS]
    ):
        raise ValueError("OMALL: estructura de la lista de pistas inesperada")
    patched = bytearray(program)
    patched[t : t + POINTERS] = strings.ljust(POINTERS, b"\0")
    struct.pack_into(">37I", patched, t + POINTERS, *(addr + dst[p] for p in pointers))
    return bytes(patched), bytes(atlas)


def sound_frame(frame):
    font = dict(FOOTER)
    font.update(
        M=("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
        Ú=("00110", "10001", "10001", "10001", "10001", "10001", "01110"),
        I=("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    )
    label = "MÚSICA"
    width = 88
    data = bytearray(frame)
    base = FRAME_FOOTER
    for y in range(8, 17):
        for x in range(6, 80):
            at = base + y * width + x
            if data[at] in {1, 2, 3, 4, 5}:
                data[at] = 2
    x = (width - 6 * len(label) + 1) // 2
    coords = [
        (x + i * 6 + dx, 8 + dy)
        for i, char in enumerate(label)
        for dy, row in enumerate(font[char])
        for dx, ink in enumerate(row)
        if ink == "1"
    ]
    for ix, y in coords:
        data[base + (y + 1) * width + ix + 1] = 5
    for ix, y in coords:
        data[base + y * width + ix] = 1
    return bytes(data)


def traducir_musica(
    source: bytes, archive: bytes, program: bytes, disc: int
) -> tuple[bytes, bytes]:
    """Add the music labels to an OMALL prepared with the movie gallery."""
    if (
        disc not in (1, 2)
        or digest(source) != SOURCE_SHA
        or len(archive) != len(source)
    ):
        raise ValueError("OMALL: archivo o disco no reconocido")
    atlas = decompress(source[0x1000:])
    frame = decompress(archive)
    old_frame = decompress(source)
    end = FRAME_FOOTER + 88 * 24
    if (
        decompress(archive[0x1000:]) != atlas
        or frame[FRAME_FOOTER:end] != old_frame[FRAME_FOOTER:end]
    ):
        raise ValueError("OMALL: atlas o rótulo de música inesperado")
    start = 0x51BF6 if disc == 1 else 0x51D2E
    new_program, new_atlas = build_data(
        atlas, decompress(source[0x79000:]), program, start
    )
    data = bytearray(archive)
    put_stream(data, 0x1000, 0x2000, new_atlas, "Sound labels")
    put_stream(data, 0, 0x1000, sound_frame(frame), "Sound frame")
    return bytes(data), new_program
