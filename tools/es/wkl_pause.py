"""Localize the verified native battle pause and confirmation sprites."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import struct

from rotulos import read_indices, replace_text, write_indices

# "No" already reads correctly in Spanish and keeps its original sprite.
LABELS = (
    (13, 0, 72, 'c0f3658732302e2bfd2701fde612e9f13890b811a77438536b5035f5a0d34c5a', 'Volver al título'),
    (13, 1, 72, '038e8564be31ddfb103859e3374723e3b60bb035afdb6330a30f399ceac118eb', 'Reiniciar'),
    (14, 1, 88, '4bdb064bc1d0a99cfd53007767c391f97c65b8fedf3a82f208d1d9e6004c6241', '¿Suspender partida?'),
    (14, 2, 88, '87560180acf4aca21b0abed5d62dfba001cae1eaaec24c8fbe126f3f701dc0e2', '¿Reiniciar combate?'),
    (14, 3, 40, 'd851e3e0282bd7091c2fbc2034de8ae6e8b99770a8891709dcdfa9ecd5a3ab2e', 'Sí'),
    (15, 1, 48, 'bd2e1dd6700b22d47e940eb403a24351d884dc48c7eb5a2c0bd05b8dd722e090', 'Reiniciar'),
    (15, 2, 48, '059959c0769a108adb3951428eced01939f9e9559c1ad7b980f637e8ef85e836', 'Opciones'),
)
INK = {0: (40, 40, 80), 1: (208, 208, 208), 3: (56, 56, 72)}
HEIGHT = 16


def label_span(wkl: bytes, block: int, image: int, expected_width: int) -> tuple[int, int]:
    if len(wkl) < 0xEC:
        raise ValueError('WKL: cabecera de menú truncada')
    directory = struct.unpack_from('>I', wkl, 0xE8)[0]
    if directory + 8 * (block + 1) > len(wkl):
        raise ValueError('WKL: directorio de menú truncado')
    relative, size = struct.unpack_from('>II', wkl, directory + 8 * block)
    begin, end = directory + relative, directory + relative + size
    if relative < 8 * (block + 1) or size < 16 or end > len(wkl):
        raise ValueError('WKL: bloque de menú inválido')
    count = struct.unpack_from('>H', wkl, begin)[0]
    if image >= count or begin + 16 * (count + 1) > end:
        raise ValueError('WKL: directorio de sprites de menú inválido')

    first, previous, width, height, _ = struct.unpack_from('>IIHHI', wkl, begin + 8 + 16 * image)
    start = begin + 16 * (count + 1) + first + previous
    stop = start + width * height // 2
    if (width, height) != (expected_width, HEIGHT) or stop > end:
        raise ValueError('WKL: dimensiones de rótulo inesperadas')
    return start, stop


@lru_cache(maxsize=len(LABELS))
def _translated_label(texture: bytes, width: int, text: str) -> bytes:
    rows = read_indices(texture, 0, width, HEIGHT, 4)
    replace_text(rows, INK, (0, 0, width, HEIGHT), text, 'georgiab.ttf', 11,
                 ink=1, bg=0, outline=3, allowed=(1, 3))
    out = bytearray(texture)
    write_indices(out, 0, rows, 4)
    return bytes(out)


def traducir_pausa_tactica(wkl: bytearray) -> None:
    """Translate the original WKL pause labels without moving any data."""
    edits = []
    for block, image, width, digest, label in LABELS:
        start, stop = label_span(wkl, block, image, width)
        texture = bytes(wkl[start:stop])
        if sha256(texture).hexdigest() != digest:
            raise ValueError(f'WKL: rótulo táctico {block}:{image} no reconocido')
        edits.append((start, stop, _translated_label(texture, width, label)))

    edits.sort()
    if any(stop > next_start for (_, stop, _), (next_start, _, _) in zip(edits, edits[1:])):
        raise ValueError('WKL: rótulos tácticos superpuestos')
    for start, stop, encoded in edits:
        wkl[start:stop] = encoded
