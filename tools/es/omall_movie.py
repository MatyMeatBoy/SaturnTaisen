"""Localize the verified Saturn movie gallery and its fixed-size resources."""
import hashlib
import struct
from collections import Counter
from menus_es import put_stream
from red_lz import decompress
from omall_movie_frame import movie_frame
from tiras import strip_from, strip_into

SOURCE_SHA = 'ace9f3f7f0f8833e26c187dc930833a0f535b012428c862328686b815b252295'
TABLE_SHA = '76e9f3b264f30102ec52d4e6412c790776eadc256731e209d8e444d3e4f7c571'
POINTERS_SHA = '0949a249471931ac6b88922d7777322871bcc667b14d58f2cbba443d7ecf7134'
ACTIONS_SHA = 'e16659e638eeae4305203a8b796dfb0fa7e1de2b428e9080cd0798890f3c5e06'
ROWS = (
    ('Load the Bullet Train!', '¡Al tren bala!'),
    ('Soaring Whale (D)', 'Ballena Voladora (Día)'),
    ('Soaring Whale (N)', 'Ballena Voladora (Noche)'),
    ('The Koubu', 'El Koubu'),
    ('EX', 'SA'),
    ('The Jinbu', 'El Jinbu'),
    ('Prologue', 'Prólogo'),
    ('Sakura vs Sumire', 'Sakura contra Sumire'),
    ('Move Out!', '¡En marcha!'),
    ('Five Intro', 'Los Cinco'),
    ('Stage Collapse', 'Derrumbe del escenario'),
    ('Meet Ayame', 'Encuentro con Ayame'),
    ("Maria's Past", 'El pasado de Maria'),
    ('Cannon Fire (N)', 'Cañonazo (Noche)'),
    ('Cannon Fire (D)', 'Cañonazo (Día)'),
    ("Iris' Dream", 'El sueño de Iris'),
    ('Iris is Saved', 'Rescate de Iris'),
    ("Miroku's Plot", 'El plan de Miroku'),
    ("Sakura's Power", 'El poder de Sakura'),
    ('Great Collapse', 'Gran derrumbe'),
    ('Retreat!', '¡Retirada!'),
    ('Date with Sakura', 'Cita con Sakura'),
    ('Meet Aya-me', 'Encuentro con Aya-me'),
    ('The Lost City', 'La ciudad perdida'),
    ('Mikasa, Launch!', '¡Despega, Mikasa!'),
    ('Kamikaze!', '¡Kamikaze!'),
    ('Victory!', '¡Victoria!'),
    ('Farewell', 'Despedida'),
    ('Ending Sakura', 'Final de Sakura'),
    ('Ending Sumire', 'Final de Sumire'),
    ('Ending Maria', 'Final de Maria'),
    ('Ending Kohran', 'Final de Kohran'),
    ('Ending Iris', 'Final de Iris'),
    ('Ending Kanna', 'Final de Kanna'),
    ('Opening 1', 'Intro 1'),
    ('Opening 2', 'Intro 2'),
    ("The Five's Goal", 'El plan de los Cinco'),
    *((f'EP {x}', f'Ep. {x}') for x in range(2, 10)),
    ('Final EP', 'Episodio final'),
    ('EXIT', 'SALIR'),
    ('??????', '??????'),
)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def lookup(old_raw, old_table, at):
    rows = strip_from(old_raw, 0, 144)
    entries = {}
    cursor = 0
    for original, translated in ROWS:
        ids = []
        start = cursor
        while (index := struct.unpack_from('>H', old_table, cursor)[0]):
            ids.append(index)
            cursor += 2
        cursor += 2
        entries[at+start] = (ids, original, translated)
    if cursor != len(old_table):
        raise ValueError("OMALL: tabla de películas inesperada")
    shapes = {}
    for ids, original, _ in entries.values():
        # The Koubu entry has a custom tile. Its letters are available in other entries.
        if original == 'The Koubu':
            continue
        text = original.ljust(2*len(ids))
        if len(text) != len(ids) * 2:
            raise ValueError(f"OMALL: texto de origen inesperado para {original}")
        for char, x in zip(text, (x for i in ids for x in ((i-1)*16,(i-1)*16+8))):
            glyph = tuple(tuple(row[x:x+8]) for row in rows)
            if char != " " and any(map(any, glyph)):
                shapes.setdefault(char, Counter())[glyph] += 1
    return entries, {c: variants.most_common(1)[0][0] for c,variants in shapes.items()}

def traducir_peliculas(archive: bytes, program: bytes, disc: int) -> tuple[bytes, bytes]:
    """Return the localized OMALL and program with their original lengths."""
    if disc not in (1, 2) or digest(archive) != SOURCE_SHA:
        raise ValueError("OMALL: archivo o disco no reconocido")
    t = 0x520A8 if disc == 1 else 0x521E0
    old_table = program[t:t+0x264]
    if digest(old_table) != TABLE_SHA:
        raise ValueError("OMALL: tabla de películas sin firma conocida")
    old_atlas = decompress(archive[0x79000:])
    if len(old_atlas) != 144 * 128:
        raise ValueError("OMALL: atlas de películas de tamaño inesperado")
    entries, glyphs = lookup(old_atlas, old_table, t)
    for accent, base, shape in (('á','a',((3,1),(4,0))), ('í','i',((3,1),(4,0))),
                                ('ó','o',((3,1),(4,0))), ('ñ','n',((1,1),(2,0),(3,0),(4,1),(5,1),(6,0)))):
        glyph = [list(row) for row in glyphs[base]]
        if accent == 'í':
            glyph[:4] = [[0]*8 for _ in range(4)]
        for x, y in shape:
            glyph[y+1][x] = 1
        glyphs[accent] = tuple(map(tuple, glyph))
    glyphs['¡'] = tuple(row[::-1] for row in glyphs['!'][::-1])
    if 'p' not in glyphs:
        raise ValueError('Missing source glyph p')
    blank_shapes = [(0,)*8 for _ in range(16)]
    glyphs[' '] = tuple(blank_shapes)
    f_rows = ('00000000','00000000','000e11d0','00d7d000','001e0000','f1111110',
              *('001e0000',)*7,'00000000','00000000','00000000')
    glyphs['f'] = tuple(tuple(int(pixel,16) for pixel in row) for row in f_rows)
    glyphs['.'] = tuple((0,0,0,1,1,0,0,0) if 11 <= y <= 12 else (0,)*8 for y in range(16))
    pairs = {'??': 138}
    blocks = bytearray()
    relocation = {}
    for offset,(ids,original,word) in entries.items():
        relocation[0x06004000+offset] = 0x06004000+t+len(blocks)
        text = word.ljust(len(word)+(len(word)%2))
        for i in range(0,len(text),2):
            pair = text[i:i+2]
            if pair not in pairs:
                slot = len(pairs)
                pairs[pair] = slot if slot < 138 else slot+1
            blocks.extend(struct.pack('>H',pairs[pair]))
        blocks.extend(b'\0\0')
    if len(blocks) > 0x2D0 or max(pairs.values()) > 144:
        raise ValueError("OMALL: las películas no caben en la tabla o el atlas")
    rows = [list(row) for row in strip_from(old_atlas,0,144)]
    for pair, index in pairs.items():
        if pair == '??':
            continue
        x = (index-1)*16
        for y in range(16):
            rows[y][x:x+16] = glyphs[pair[0]][y]+glyphs[pair[1]][y]
    raw = bytearray(old_atlas)
    strip_into(raw,0,rows)
    old_ptr = program[t+0x2d0:t+0x398]
    ptr = struct.unpack('>50I',old_ptr)
    if set(ptr) != set(relocation):
        raise ValueError("OMALL: punteros de la lista de películas inesperados")
    offsets = struct.pack('>50H', *(address - (0x06004000 + t) for address in ptr))
    if digest(offsets) != POINTERS_SHA or digest(program[t+0x398:t+0x3c6]) != ACTIONS_SHA:
        raise ValueError("OMALL: orden o acciones de la lista de películas inesperados")
    prog = bytearray(program)
    prog[t:t+0x2d0] = blocks.ljust(0x2d0,b'\0')
    prog[t+0x2d0:t+0x398] = struct.pack('>50I',*(relocation[i] for i in ptr))
    data = bytearray(archive)
    put_stream(data,0x79000,len(data)-0x79000,raw,'Movie labels')
    put_stream(data,0,0x1000,movie_frame(decompress(archive)),'Movie frame')
    return bytes(data), bytes(prog)
