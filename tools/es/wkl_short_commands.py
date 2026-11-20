"""Localize short allied ability labels in the WKL compressed records."""
from functools import lru_cache
from hashlib import sha256
import struct

from red_lz import compress, decompress_ex
from rotulos import read_indices, replace_text, write_indices

# Maria's Podozhdi retains the name spoken in the Spanish battle tutorial.
LABELS = {
    'ee4b2dcb63be6bbc9137ca2b068fe85e016f0a7cf9c309b96bdc7b2b60e08251': 'Cubrir',
    '4f2964cd82782d41f06f65e5aa6a02b393f58b5e87a0d398abf07e48f9d48049': 'Carrera',
    'de02ef45d4ce84609d4c05334b4216ade1bbef917768ec94132273b0f4989e27': 'Muro ígneo',
    '6bf6b2175c8192aa8bfc63c3a49332d4757b4fbd3280206466b0db1f304339de': 'Ven aquí',
    'd06f3eef2e63c492a1fc484210c09758e065bbb65f8245d961d7db0812da1331': 'Terremoto',
    '143c46a20109c631054b8c5d637a636b3628bd6050379367fedf57fc3e638078': 'Puño K.',
}
WIDTH, HEIGHT = 56, 16
INK = {0: (40, 40, 80), 1: (208, 208, 208), 3: (56, 56, 72)}


@lru_cache(maxsize=128)
def _short_command(source: bytes) -> bytes | None:
    # Image 1 is the short ability. The separate image 2 holds the named attack.
    if len(source) < 80 or struct.unpack_from('>H', source)[0] != 4:
        return None
    width, height, _, _, _, relative, _, length = struct.unpack_from('>8H', source, 32)
    at = 80 + relative
    if (width, height, length) != (WIDTH, HEIGHT, WIDTH * HEIGHT // 2) or at + length > len(source):
        return None
    text = LABELS.get(sha256(source[at:at + length]).hexdigest())
    if text is None:
        return None
    rows = read_indices(source, at, width, height, 4)
    replace_text(rows, INK, (0, 0, width, height), text, 'georgiab.ttf', 11,
                 ink=1, bg=0, outline=3, allowed=(1, 3), squeeze=0.96)
    translated = bytearray(source)
    write_indices(translated, at, rows, 4)
    return compress(bytes(translated))


def traducir_comandos_aliados_wkl(wkl: bytearray) -> None:
    """Translate exact known textures, including their duplicate WKL records."""
    if len(wkl) < 0x104:
        raise ValueError('WKL: cabecera de comandos truncada')
    directory = struct.unpack_from('>I', wkl, 0x100)[0]
    if directory < 0x104 or directory + 512 > len(wkl):
        raise ValueError('WKL: directorio de comandos truncado')

    extents = set()
    for slot in range(64):
        relative, capacity = struct.unpack_from('>II', wkl, directory + 8 * slot)
        if capacity == 0:
            continue
        start = directory + relative
        end = start + capacity
        if relative < 512 or end > len(wkl):
            raise ValueError(f'WKL: bloque de comando {slot} inválido')
        extents.add((start, end))
    spans = sorted(extents)
    if any(end > next_start for (_, end), (next_start, _) in zip(spans, spans[1:])):
        raise ValueError('WKL: bloques de comando superpuestos')

    replacements = []
    for start, end in spans:
        decoded, _ = decompress_ex(wkl[start:end], limit=16384)
        if (encoded := _short_command(decoded)) is None:
            continue
        if len(encoded) > end - start:
            raise ValueError(f'WKL: comando necesita {len(encoded)} bytes, límite {end-start}')
        replacements.append((start, end, encoded))
    for start, end, encoded in replacements:
        wkl[start:end] = encoded.ljust(end - start, b'\0')
