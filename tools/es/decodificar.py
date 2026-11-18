"""Decodifica a PNG los graficos de menu con texto de Sakura Taisen (Saturn).

Uso:  python tools/decodificar.py [--iso RUTA] [--salida DIR]

Lee los archivos de la ISO inglesa preparada, descomprime los flujos LZ
(red_lz) y dibuja cada grafico con la paleta que el juego usa en pantalla,
tomada de un savestate local (CRAM o tabla LUT de VDP1). Sin savestate
disponible usa escala de grises.

Tambien expone encode_*() para convertir un PNG editado de vuelta a bytes
(indices de paleta) y reinsertar.
"""
from __future__ import annotations

import argparse
import mmap
import os
import struct
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from red_lz import decompress_ex  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
OWNER = os.environ.get('SAKURA_OWNER_ROOT', ROOT)
WORK = os.path.join(OWNER, 'local', 'work')
ISO = os.path.join(OWNER, 'local', 'prepared', 'disc1', 'Track 01.iso')
ST = {
    'title': 'intro-enhanced/title-final.state',
    'program': 'sakura/continue-probe.state',
    'inter': 'sakura/intermission-down.state',
    'status': 'sakura/intermission-save.state',
    'options': 'sakura/exit-options.state',
    'optnav': 'sakura/options-nav.state',
    'load': 'sakura/select-continue-ref.state',
    'battle': 'sakura/chapter1-first-attack.state',
}


# ---------------------------------------------------------------- ISO / datos
def iso_files(iso_path):
    from audit_sdk import files
    out = {}
    with open(iso_path, 'rb') as s, mmap.mmap(s.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        for p, lba, size in files(iso):
            if lba * 2048 + size <= len(iso):
                out[p.upper()] = (lba, size)
    return out


class Disc:
    def __init__(self, iso_path):
        self.path = iso_path
        self.index = iso_files(iso_path)
        self.cache = {}

    def read(self, name):
        name = name.upper()
        if name not in self.cache:
            lba, size = self.index[name]
            with open(self.path, 'rb') as f:
                f.seek(lba * 2048)
                self.cache[name] = f.read(size)
        return self.cache[name]

    def data(self, src):
        """src = ('lz', archivo, offset) o ('raw', archivo, offset, longitud)."""
        raw = self.read(src[1])
        if src[0] == 'lz':
            return decompress_ex(raw, src[2])[0]
        return raw[src[2]:src[2] + src[3]]


# ---------------------------------------------------------------- savestates
_states = {}


def state(key):
    path = os.path.join(WORK, ST[key])
    if path not in _states:
        if not os.path.exists(path):
            _states[path] = None
        else:
            d = open(path, 'rb').read()
            p = d.find(b'HCAM') + 4
            out = {}
            for n in ['ramHigh', 'ramLow', 'sound', 'vram1', 'fb0', 'fb1', 'vram2', 'cram']:
                L = struct.unpack_from('<Q', d, p)[0]
                out[n] = d[p + 8:p + 8 + L]
                p += 8 + L
            _states[path] = out
    return _states[path]


def rgb555(c):
    return ((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)


def palette(spec, n):
    """spec = (estado, 'cram', base) | (estado, 'lut', colr) | None."""
    if spec is None:
        return [(i * 255 // (n - 1),) * 3 for i in range(n)]
    s = state(spec[0])
    if s is None:
        return [(i * 255 // (n - 1),) * 3 for i in range(n)]
    if spec[1] == 'cram':
        c = s['cram']
        return [rgb555(struct.unpack_from('>H', c, ((spec[2] + i) * 2) % len(c))[0]) for i in range(n)]
    lut = s['vram1'][spec[2] * 8:spec[2] * 8 + 32]
    return [rgb555(struct.unpack_from('>H', lut, i * 2)[0]) for i in range(16)]


# ---------------------------------------------------------------- dibujo
def draw_linear(data, w, h, bpp, pal):
    im = Image.new('RGB', (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            if bpp == 4:
                i = (y * w + x) >> 1
                b = data[i] if i < len(data) else 0
                v = b >> 4 if not x & 1 else b & 15
            else:
                i = y * w + x
                v = data[i] if i < len(data) else 0
            px[x, y] = pal[v]
    return im


def draw_tiles(data, tw, th, bpp, pal, per_row=16):
    tb = tw * th * bpp // 8
    n = len(data) // tb
    rows = (n + per_row - 1) // per_row
    im = Image.new('RGB', (per_row * tw, rows * th), (0, 0, 0))
    for i in range(n):
        im.paste(draw_linear(data[i * tb:(i + 1) * tb], tw, th, bpp, pal), ((i % per_row) * tw, (i // per_row) * th))
    return im


def draw_vdp2_screen(data, w=40, h=28, map_off=0x200, cells_off=0x1380):
    """Archivos TITLE#.BIN / LOAD.BIN: paleta 256 (0x000), mapa 2 palabras
    40x28 (0x200), celdas 8x8 a 8bpp (0x1380)."""
    pal = [rgb555(struct.unpack_from('>H', data, i * 2)[0]) for i in range(256)]
    cells = data[cells_off:]
    im = Image.new('RGB', (w * 8, h * 8))
    px = im.load()
    for r in range(h):
        for c in range(w):
            w0, w1 = struct.unpack_from('>HH', data, map_off + (r * w + c) * 4)
            ch = (w1 & 0x7fff) // 2
            vf, hf = w0 >> 15 & 1, w0 >> 14 & 1
            for y in range(8):
                for x in range(8):
                    i = ch * 64 + y * 8 + x
                    v = cells[i] if i < len(cells) else 0
                    px[c * 8 + (7 - x if hf else x), r * 8 + (7 - y if vf else y)] = pal[v]
    return im


# ---------------------------------------------------------------- codificacion
def encode_linear(im, bpp, pal):
    """PNG (RGB) -> bytes de indices; cada color debe existir en la paleta."""
    im = im.convert('RGB')
    w, h = im.size
    lookup = {}
    for i, c in enumerate(pal):
        lookup.setdefault(c, i)
    px = im.load()
    vals = []
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if c not in lookup:
                # color mas cercano
                lookup[c] = min(range(len(pal)), key=lambda i: sum((a - b) ** 2 for a, b in zip(pal[i], c)))
            vals.append(lookup[c])
    if bpp == 8:
        return bytes(vals)
    return bytes((vals[i] << 4) | vals[i + 1] for i in range(0, len(vals), 2))


def encode_tiles(im, tw, th, bpp, pal, count, per_row=16):
    out = bytearray()
    for i in range(count):
        x, y = (i % per_row) * tw, (i // per_row) * th
        out += encode_linear(im.crop((x, y, x + tw, y + th)), bpp, pal)
    return bytes(out)


# ---------------------------------------------------------------- inventario
# (salida, fuente, tipo, parametros, paleta)
#   tipo 'lin': (offset, ancho, alto, bpp)   'tiles': (offset, n, tw, th, bpp)
#   tipo 'vdp2': ()  pantalla VDP2 completa
LZ, RAW = 'lz', 'raw'
WKL01_SPR = 0x339A8  # en WKLxx.BIN: copia del bloque de sprites de combate (VRAM1 0x4000)
# sprites de la barra de combate: (offset desde VRAM1 0x4000, ancho, alto)
BATTLE_BAR = [(a - 0x4000, w, 16) for a, w in [
    (0x5C80, 16), (0x5D00, 16), (0x5D80, 24), (0x5E40, 16), (0x5EC0, 16), (0x5F40, 24), (0x6000, 24),
    (0x60C0, 24), (0x6180, 24), (0x6240, 24), (0x6300, 24), (0x63C0, 16), (0x6440, 16), (0x64C0, 24),
    (0x6580, 24), (0x6640, 24), (0x6700, 24), (0x67C0, 24), (0x6880, 24), (0x6940, 16), (0x69C0, 24),
    (0x6A80, 24), (0x6B40, 24), (0x6C00, 16), (0x6C80, 24), (0x6D40, 24), (0x6E00, 16), (0x6E80, 16)]]
SPECS = [
    # Titulo: menu Program
    ('titulo_program_marco', (LZ, '/SAKURA1/LOGO.SH2', 0x10808), 'lin', (0, 208, 152, 8), ('program', 'cram', 0x500)),
    ('titulo_program_textos', (LZ, '/SAKURA1/LOGO.SH2', 0xFF20), 'tiles', (0, 65, 16, 16, 4), ('program', 'cram', 0x20)),
    ('titulo_program_textos_rojo', (LZ, '/SAKURA1/LOGO.SH2', 0xFF20), 'tiles', (0, 65, 16, 16, 4), ('program', 'cram', 0x40)),
    ('titulo_logo_marco', (LZ, '/SAKURA1/LOGO.SH2', 0x25410), 'lin', (0, 112, 136, 8), ('title', 'cram', 0x600)),
    ('titulo_logo_sakura', (LZ, '/SAKURA1/LOGO.SH2', 0x25410), 'lin', (41472, 152, 56, 8), ('title', 'cram', 0x600)),
    ('titulo_logo_emblema', (LZ, '/SAKURA1/LOGO.SH2', 0x25410), 'lin', (15232, 96, 96, 8), ('title', 'cram', 0x600)),
    ('titulo_logo_wars', (LZ, '/SAKURA1/LOGO.SH2', 0x25410), 'lin', (74048, 64, 80, 8), ('title', 'cram', 0x600)),
    ('titulo_copyright_sega', (LZ, '/SAKURA1/LOGO.SH2', 0x25410), 'lin', (79744, 168, 24, 4), ('title', 'cram', 0x60)),
    ('titulo_press_start', (LZ, '/SAKURA1/LOGO.SH2', 0x25410), 'lin', (81760, 152, 24, 4), ('title', 'cram', 0x60)),
    # Intermedio (Save / Status / Resume)
    ('intermedio_caja_a', (LZ, '/SAKURA1/ICATALL.DAT', 0x0), 'lin', (0, 112, 128, 8), ('inter', 'cram', 0x100)),
    ('intermedio_caja_b', (LZ, '/SAKURA1/ICATALL.DAT', 0x0), 'lin', (14336, 112, 128, 8), ('inter', 'cram', 0x100)),
    ('intermedio_textos', (LZ, '/SAKURA1/ICATALL.DAT', 0x2800), 'tiles', (0, 15, 16, 16, 4), ('inter', 'cram', 0x2F0)),
    # Status
    ('status_paneles', (LZ, '/SAKURA1/ICATALL.DAT', 0x8800), 'lin', (0, 144, 384, 8), ('status', 'cram', 0x600)),
    ('status_textos', (LZ, '/SAKURA1/ICATALL.DAT', 0x13800), 'tiles', (0, 48, 16, 16, 4), ('status', 'cram', 0x2D0)),
    ('status_retratos', (LZ, '/SAKURA1/ICATALL.DAT', 0x15000), 'tiles', (0, 25, 40, 48, 8), ('status', 'cram', 0x0)),
    # Opciones
    ('opciones_marco', (LZ, '/SAKURA', 0x5AE38), 'lin', (0, 288, 144, 4), ('options', 'cram', 0xA2C0)),
    ('opciones_marco_b', (LZ, '/SAKURA', 0x5940C), 'lin', (0, 224, 128, 4), ('optnav', 'cram', 0xA2C0)),
    ('opciones_textos', (LZ, '/SAKURA', 0x5B320), 'tiles', (0, 73, 16, 16, 4), ('options', 'cram', 0xA2D0)),
    ('opciones_textos_rojo', (LZ, '/SAKURA', 0x5B320), 'tiles', (0, 73, 16, 16, 4), ('options', 'cram', 0xA2F0)),
    ('opciones_flechas', (LZ, '/SAKURA', 0x59700), 'tiles', (0, 5, 16, 16, 4), ('options', 'cram', 0xA2F0)),
    ('opciones_exit', (LZ, '/SAKURA', 0x59878), 'tiles', (0, 15, 16, 16, 4), ('options', 'cram', 0xA2D0)),
    # Carga / guardado (copia en el programa principal: la que usa la version inglesa)
    ('carga_marco', (LZ, '/SAKURA', 0x5E190), 'lin', (0, 288, 184, 4), ('load', 'cram', 0x2C0)),
    ('carga_caja_176x24', (LZ, '/SAKURA', 0x5E190), 'lin', (26496, 176, 24, 4), ('load', 'cram', 0x2C0)),
    ('carga_caja_144x24', (LZ, '/SAKURA', 0x5E190), 'lin', (28608, 144, 24, 4), ('load', 'cram', 0x2C0)),
    ('carga_caja_yesno', (LZ, '/SAKURA', 0x5E190), 'lin', (33408, 144, 32, 4), ('load', 'cram', 0x2C0)),
    ('carga_textos', (LZ, '/SAKURA', 0x5C654), 'tiles', (0, 144, 16, 16, 4), ('load', 'cram', 0x2F0)),
    ('carga_textos_azul', (LZ, '/SAKURA', 0x5C654), 'tiles', (0, 144, 16, 16, 4), ('load', 'cram', 0x2E0)),
    ('carga_iconos', (LZ, '/SAKURA', 0x5EB4C), 'tiles', (0, 6, 40, 40, 8), ('load', 'cram', 0x600)),
    ('ldsvall_marco_jp', (LZ, '/SAKURA1/LDSVALL.DAT', 0x0), 'lin', (0, 288, 184, 4), ('load', 'cram', 0x2C0)),
    ('ldsvall_textos_jp', (LZ, '/SAKURA1/LDSVALL.DAT', 0x1000), 'tiles', (0, 134, 16, 16, 4), ('load', 'cram', 0x2F0)),
    # Omake (extras)
    ('omake_textos_1000', (LZ, '/SAKURA1/OMALL.DAT', 0x1000), 'tiles', (0, 127, 16, 16, 4), None),
    ('omake_textos_79000', (LZ, '/SAKURA1/OMALL.DAT', 0x79000), 'tiles', (0, 144, 16, 16, 4), None),
    # Combate (sin comprimir, LUT de VDP1)
    ('combate_barra_wkl01', (RAW, '/SAKURA2/WKL01.BIN', WKL01_SPR, 0x2F00), 'sprites', BATTLE_BAR, ('battle', 'lut', 0xFFEC)),
    ('combate_marco_wkl01', (RAW, '/SAKURA2/WKL01.BIN', WKL01_SPR, 0x600), 'lin', (0, 96, 32, 4), ('battle', 'lut', 0xFFEC)),
]
SCREENS = [('episodio_%02d' % i, '/SAKURA1/TITLE%d.BIN' % i) for i in range(1, 11)] + [('pantalla_loading', '/SAKURA1/LOAD.BIN')]


def render_spec(disc, spec):
    name, src, kind, par, pal = spec
    data = disc.data(src)
    if kind == 'lin':
        off, w, h, bpp = par
        return draw_linear(data[off:], w, h, bpp, palette(pal, 1 << bpp))
    if kind == 'sprites':
        pal16 = palette(pal, 16)
        ims = [draw_linear(data[o:], w, h, 4, pal16) for o, w, h in par]
        out = Image.new('RGB', (sum(i.size[0] + 2 for i in ims), max(i.size[1] for i in ims)), (0, 0, 0))
        x = 0
        for i in ims:
            out.paste(i, (x, 0))
            x += i.size[0] + 2
        return out
    off, n, tw, th, bpp = par
    tb = tw * th * bpp // 8
    return draw_tiles(data[off:off + n * tb], tw, th, bpp, palette(pal, 1 << bpp),
                      per_row=16 if tw <= 16 else 8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--iso', default=ISO)
    ap.add_argument('--salida', default=os.path.join(HERE, '..', 'decodificados'))
    a = ap.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    disc = Disc(a.iso)
    for spec in SPECS:
        im = render_spec(disc, spec)
        im.save(os.path.join(a.salida, spec[0] + '.png'))
        print('ok', spec[0], im.size)
    for name, f in SCREENS:
        im = draw_vdp2_screen(disc.read(f))
        im.save(os.path.join(a.salida, name + '.png'))
        print('ok', name, im.size)


if __name__ == '__main__':
    main()
