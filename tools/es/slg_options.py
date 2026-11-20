"""Carry already translated options assets into the two tactical overlays."""
from __future__ import annotations

from hashlib import sha256

from red_lz import decompress_ex

# (disc-1 /SAKURA origin, SLG origin, reserved bytes, decoded length,
# original SLG window SHA-256, translated decoded SHA-256)
STREAMS = (
    (0x5AE38, 0x4A258, 1256, 49920,
     '713b41afe717c67e0c4566d0ac0b13bd0a10abf89c85f5926607dd1da6525321',
     '34898f099b696c0e5599e66a8229f674f70eed2da6af1742689ee857b1f21d68'),
    (0x5B320, 0x4A740, 4884, 9344,
     'fd05502eac19425cb7bb303c7b48b000ac41b69a1a8c94e86ddb1bb75b7184b8',
     '5939c54db8739790c0985a42679f72688ae955492eaa8ad92a9aba590ee3f57f'),
)


def traducir_opciones_slg(programa: bytes, slg: bytearray, disc: int) -> None:
    """Reuse the matching Spanish options PRS streams in an SLG overlay."""
    if disc not in (1, 2):
        raise ValueError(f'SLG: disco desconocido {disc}')
    displacement = 0x138 if disc == 2 else 0
    edits = []
    for main, position, budget, size, stock_hash, translated_hash in STREAMS:
        original = slg[position:position + budget]
        if len(original) != budget or sha256(original).hexdigest() != stock_hash:
            raise ValueError(f'SLG: recurso original desconocido en {position:#x}')
        _, original_size = decompress_ex(original, limit=size)
        start = main + displacement
        packed = programa[start:start + budget]
        translated, used = decompress_ex(packed, limit=size)
        if len(translated) != size or sha256(translated).hexdigest() != translated_hash:
            raise ValueError(f'SLG: opciones traducidas no reconocidas en {start:#x}')
        if used > original_size and any(original[original_size:used]):
            raise ValueError(f'SLG: opciones traducidas sobrepasan su espacio en {position:#x}')
        edits.append((position, max(used, original_size), packed[:used]))
    for position, length, packed in edits:
        slg[position:position + length] = packed.ljust(length, b'\0')
