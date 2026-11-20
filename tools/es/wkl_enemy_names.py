"""Translate the witnessed common enemy unit labels in the tactical WKL banks."""
from functools import lru_cache
from hashlib import sha256
import struct

from red_lz import compress, decompress_ex
from rotulos import read_indices, replace_text, write_indices

LABELS = {
    'c55359234686e737b68d9f99d62c47d29f1534ca9c42bf589f4a24f9ce0e8674': 'Mosquete',
    'ff2ca705da0fa8e20c3059abf5fd32b97a2a2c83a985a77066e40519d3fc4829': 'Garra',
    '9d9485e953ef42004f01c944ba4f469ab88158e8bf6c647dc5183bac426c45e7': 'Tiro ácido',
}
PALETTE = {0: (40, 40, 80), 1: (208, 208, 208), 3: (56, 56, 72)}


def first_label(group: bytes) -> tuple[int, bytes] | None:
    if len(group) < 80 or struct.unpack_from('>H', group)[0] != 4:
        return None
    width, height, _, _, _, relative, _, size = struct.unpack_from('>8H', group, 16)
    start = 80 + relative
    if (width, height, size) != (40, 16, 320) or start + size > len(group):
        return None
    return start, group[start:start + size]


@lru_cache(maxsize=96)
def _translated_group(stock: bytes, start: int, texture: bytes, text: str) -> bytes:
    rows = read_indices(texture, 0, 40, 16, 4)
    replace_text(rows, PALETTE, (0, 0, 40, 16), text, 'georgiab.ttf', 10,
                 ink=1, bg=0, outline=3, allowed=(1, 3))
    out = bytearray(stock)
    write_indices(out, start, rows, 4)
    return compress(bytes(out))


def traducir_enemigos_wkl(wkl: bytearray) -> None:
    if len(wkl) < 0x104:
        raise ValueError('WKL: cabecera truncada')
    directory = struct.unpack_from('>I', wkl, 0x100)[0]
    if directory + 512 > len(wkl):
        raise ValueError('WKL: directorio de nombres truncado')

    replacements = []
    for group in range(7, 64):
        relative, size = struct.unpack_from('>II', wkl, directory + group * 8)
        if not size:
            continue
        start, end = directory + relative, directory + relative + size
        if relative < 512 or end > len(wkl):
            raise ValueError(f'WKL: grupo enemigo {group} fuera del banco')
        stock, _ = decompress_ex(wkl[start:end], limit=16384)
        label = first_label(stock)
        if label is None:
            continue
        offset, texture = label
        text = LABELS.get(sha256(texture).hexdigest())
        if text is None:
            continue
        encoded = _translated_group(stock, offset, texture, text)
        if len(encoded) > size:
            raise ValueError(f'WKL: el rótulo enemigo {group} excede su bloque')
        replacements.append((start, end, encoded))
    replacements.sort()
    if any(stop > next_start for (_, stop, _), (next_start, _, _) in zip(replacements, replacements[1:])):
        raise ValueError('WKL: grupos de nombre superpuestos')
    for start, stop, encoded in replacements:
        wkl[start:stop] = encoded.ljust(stop - start, b'\0')
