"""Translate the witnessed common Musket unit label in the tactical WKL bank."""
from functools import lru_cache
from hashlib import sha256
import struct

from red_lz import compress, decompress_ex
from rotulos import read_indices, replace_text, write_indices

STOCK = 'c55359234686e737b68d9f99d62c47d29f1534ca9c42bf589f4a24f9ce0e8674'
PALETTE = {0: (40, 40, 80), 1: (208, 208, 208), 3: (56, 56, 72)}


@lru_cache(maxsize=32)
def _mosquete(block: bytes) -> bytes:
    if len(block) < 80 or struct.unpack_from('>H', block)[0] != 4:
        raise ValueError('WKL: grupo Mosquete inesperado')
    width, height, _, _, _, relative, _, size = struct.unpack_from('>8H', block, 16)
    start = 80 + relative
    tex = block[start:start + size]
    if (width, height, size) != (40, 16, 320) or sha256(tex).hexdigest() != STOCK:
        raise ValueError('WKL: textura original Mosquete desconocida')
    rows = read_indices(tex, 0, width, height, 4)
    replace_text(rows, PALETTE, (0, 0, width, height), 'Mosquete', 'georgiab.ttf', 10,
                 ink=1, bg=0, outline=3, allowed=(1, 3))
    result = bytearray(block)
    write_indices(result, start, rows, 4)
    return compress(bytes(result))


def traducir_mosquete_wkl(wkl: bytearray) -> None:
    if len(wkl) < 0x104:
        raise ValueError('WKL: cabecera truncada')
    directory = struct.unpack_from('>I', wkl, 0x100)[0]
    if directory + 512 > len(wkl):
        raise ValueError('WKL: directorio de nombres truncado')
    relative, size = struct.unpack_from('>II', wkl, directory + 15 * 8)
    start = directory + relative
    if relative < 512 or not size or start + size > len(wkl):
        raise ValueError('WKL: grupo de Mosquete fuera del banco')
    stock, _ = decompress_ex(wkl[start:start + size], limit=16384)
    new = _mosquete(stock)
    if len(new) > size:
        raise ValueError('WKL: el rótulo Mosquete excede su grupo')
    wkl[start:start + size] = new.ljust(size, b'\0')
