"""Localize the verified allied special-attack labels in Saturn WKL banks."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import struct

from red_lz import compress, decompress_ex
from rotulos import read_indices, replace_text, write_indices

# The sprite for each character's named special attack is image 2.
# Maria's Snegurochka is a proper name and keeps its native artwork.
ATTACKS = {
    0: ('ae4b1199575512918f9ec131f9161a409bc181da928915dc6ded6db4f65e0295', 'Acero tajante'),
    1: ('f8b6e713fcb66db41c46a1f036077c65b625d703545908b25c79147abfc4e14c', 'Divinidad floral'),
    2: ('bac47ebf335beac8cc4ee9f2f651b9e36f94a8ce8d1631a6d41f641bed86cc85', 'Vals de mariposa'),
    4: ('9d436fb1222b751ada7ba6fe076b36aab4b71747653b3a13a0728c266962ebfa', 'Marioneta de Iris'),
    5: ('45003032ef4b72f261cbe5e373bfd75f588b1709a06c55d03c0beb8194e411c9', 'Minirrobots'),
    6: ('169346f1c0097921fdda39f8b481997db634ac571a93ec54db01e214f0a83e33', 'Lluvia de bambú'),
}
ATTACK_DIGESTS = {digest: slot for slot, (digest, _) in ATTACKS.items()}
WIDTH = 88
HEIGHT = 16
INK = {0: (40, 40, 80), 1: (208, 208, 208), 3: (56, 56, 72)}


@lru_cache(maxsize=48)
def _translated_group(source: bytes, slot: int) -> bytes:
    if len(source) < 80 or struct.unpack_from('>H', source)[0] != 4:
        raise ValueError(f'WKL: grupo de ataque {slot} no reconocido')
    # Four 16-byte descriptors follow the 16-byte header.
    width, height, _, _, _, relative, _, size = struct.unpack_from('>8H', source, 48)
    at = 80 + relative
    expected, text = ATTACKS[slot]
    texture = source[at:at + size]
    if ((width, height, size) != (WIDTH, HEIGHT, WIDTH * HEIGHT // 2)
        or at + size > len(source) or sha256(texture).hexdigest() != expected):
        raise ValueError(f'WKL: textura de ataque {slot} no reconocida')

    rows = read_indices(texture, 0, WIDTH, HEIGHT, 4)
    replace_text(rows, INK, (0, 0, WIDTH, HEIGHT), text, 'georgiab.ttf', 11,
                 ink=1, bg=0, outline=3, allowed=(1, 3), squeeze=0.96)
    translated = bytearray(source)
    write_indices(translated, at, rows, 4)
    return compress(bytes(translated))


def traducir_ataques_wkl(wkl: bytearray) -> None:
    """Rewrite only the guarded PRS slots, preserving offsets and file size."""
    if len(wkl) < 0x104:
        raise ValueError('WKL: cabecera de ataques truncada')
    directory = struct.unpack_from('>I', wkl, 0x100)[0]
    if directory + 512 > len(wkl):
        raise ValueError('WKL: directorio de ataques truncado')

    replacements = []
    for slot in range(64):
        relative, capacity = struct.unpack_from('>II', wkl, directory + 8 * slot)
        if not capacity and slot not in ATTACKS:
            continue
        start = directory + relative
        end = start + capacity
        if relative < 512 or capacity == 0 or end > len(wkl):
            raise ValueError(f'WKL: bloque de ataque {slot} inválido')
        decoded, _ = decompress_ex(wkl[start:end], limit=16384)
        identity = slot
        if slot not in ATTACKS:
            # Alternate deployments can repeat a character in another slot.
            # Match only the same exact third sprite in a four-image record.
            if len(decoded) < 80 or struct.unpack_from('>H', decoded)[0] != 4:
                continue
            width, height, _, _, _, offset, _, size = struct.unpack_from('>8H', decoded, 48)
            at = 80 + offset
            if (width, height, size) != (WIDTH, HEIGHT, WIDTH * HEIGHT // 2) or at + size > len(decoded):
                continue
            identity = ATTACK_DIGESTS.get(sha256(decoded[at:at + size]).hexdigest())
            if identity is None:
                continue
        encoded = _translated_group(decoded, identity)
        if len(encoded) > capacity:
            raise ValueError(f'WKL: ataque {slot} necesita {len(encoded)} bytes, límite {capacity}')
        replacements.append((start, end, encoded))

    # A malformed directory must not cause conflicting or partial writes.
    replacements.sort()
    if any(end > following for (_, end, _), (following, _, _) in zip(replacements, replacements[1:])):
        raise ValueError('WKL: bloques de ataque superpuestos')
    for start, end, encoded in replacements:
        wkl[start:end] = encoded.ljust(end - start, b'\0')
