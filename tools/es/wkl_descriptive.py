"""Translate exact remaining descriptive graphics from the WKL name directory."""
from functools import lru_cache
from hashlib import sha256
import struct

from red_lz import compress, decompress_ex
from rotulos import read_indices, replace_text, write_indices
from wkl_pause import label_span

LABELS = {
    (0, 40, 16, '031addfd29b44e07383dd6a8c9586f9888b05f266051d74cd09b1540a8c40b80'): 'Soldado',
    (0, 40, 16, '1d7797233b0d22712778bcd90ab0fbe02cd040cbe77055c6fee75d0410359400'): 'Vapor',
    (0, 40, 16, '2420817f49d01bcff471a66d9592bf30ab393b1848d3b5cbe53348decf269021'): 'Avispones',
    (0, 40, 16, '3c3121368553319434d90722e62f0fce55dff6865c964e94eb11f074b7470604'): 'Peñasco',
    (0, 40, 16, '3f247c9749646f4a3d31ad8b60a46aa6bc2a5b8153fa79aa0b06b65523eebfba'): 'Demonio',
    (0, 40, 16, '4aef88275e188c20a4ba87d4e50a7fc27f806d36250453ec92b2853aa6af6265'): 'Carga',
    (0, 40, 16, '5c32aeb69cb8a668572f9e8898f3c10ed9953a24c53bf3b59288867d2f9f29a4'): 'Mariposa',
    (0, 40, 16, '6611af1260b53b464127497a3d12c6a68fe159d730ee0d8f243a3e076bfaca6f'): 'Caballero',
    (0, 40, 16, '78e92149dfe3ee10364a53653fd1a6e5aaafd594f0127d4ae7d7a82978635921'): 'Alcaudón',
    (0, 40, 16, '79a4793688ea498f2b8ec7cedf1afa206c0813b29e1224582ef72c881e3906dd'): 'Objetos',
    (0, 40, 16, '9b74a4bc43a6ddb775e2564f7ad2898e7a44893cd74c7b30fb017536a873d88d'): 'Tambor',
    (0, 40, 16, 'a0fabbb18c388eaea3599eb22b07325f8da915a042436c08d2bea66b7310f7b9'): 'Sombra',
    (0, 40, 16, 'aada3bd36622a64e3d145036337dc10a7e23b207d6de7361405c8c184a970efb'): 'Hielo',
    (0, 40, 16, 'aeda3131857a7359be99c51c586fac3c5a96ed6e523c86371971e1d32e08502b'): 'Cohete',
    (0, 40, 16, 'b483c952c4252a5fe50d7a8f143eece7ddcef3e637100189700b487ce498b822'): 'Torre\neléctrica',
    (0, 40, 16, 'df15ef68b03842057827fa766e041e4d13bdf28caf68d74f44c54701a6a94d89'): 'Jabalí',
    (0, 40, 16, 'e47d098ae735efea5c4193a43ef67f8675613cf84588e9e009f35397b4dab6bb'): 'Ciervo',
    (0, 40, 16, 'e75c08a0007fc3c6b955fe8f85fe366abfebee24d5057d56640e7b1d9614642c'): 'Samurái',
    (0, 40, 16, 'e8b0596d905cde6d728354d07c7447c47c8e700b1c0dc9e406ddd58cd0b1aee3'): 'Cañón',
    (0, 40, 16, 'ec85f6f6b49640247996a02755393f11a088029fdea2060d1104156b0a466010'): 'Lab.\ndemoníaco',
    (1, 56, 16, 'f2bfebc5bfa8c979a00dd880ba4dc5bf5bcb86c4bc061ee4c367e063861210f1'): 'Ninguno',
    (2, 88, 16, '1027e695dbb79824902e1af2dac406c2b94e6d73c685f7670e5ebc0b72955ba0'): 'Ballet del Fénix',
    (2, 88, 16, '13cff77d90a0c9c0d836c34f588ef9868e39b67fb1bd44ffc3ef6987fc18f9c3'): 'Ángel cibernético',
    (2, 88, 16, '1a22e6e723eee872e3eedef49703e03bbab68af973855e2cb96f09d2665b6da6'): 'Cañón mariposa',
    (2, 88, 16, '1e4f9e0c03ea341bb99dfe2d2b1f534d2cf754ed53b0b79bca8ae262ff1bbb7c'): 'Danza del rayo',
    (2, 88, 16, '31eddf9b846f28006b7d33da5ecb0be39477937944b83dd723f607d60c290ca6'): 'Golpe del ciervo\nde hielo',
    (2, 88, 16, '351e23031fd90b04f3ccaae8582bcc37b95c0e9e11847235810ca9d43db85b38'): 'Golpe de cuadrante',
    (2, 88, 16, '66ad804087701e89b3755ce2ec07aea62254c9810539bb533a55fb5dd35319af'): 'Electrochoque',
    (2, 88, 16, '6b4c7e5e4ef47f4ca073c9d5bcf3b9d598e267025a8870c34e43db36f0bea865'): 'Tajo sombrío',
    (2, 88, 16, '84a47ec9133edb1e17b3f2cbb7e00af54b26857d8bfec02b9fd3f6ae1eb8ad5d'): 'Hexagrama infernal',
    (2, 88, 16, '8d955b4cc9f2a216a9e4a3e8123cca371d3242e9031ff0ff481dafe7ef71562e'): 'Tajo recto',
    (2, 88, 16, '9038cda7093ba7704abe6189618e6573f1f5389c8d4151089237a89037046b90'): 'Jardín de Iris',
    (2, 88, 16, '9c14eefc0bc547efd91941d885d1c29c3780fc19c7bc8a6abd00d09515682091'): 'Gloria imperial',
    (2, 88, 16, 'cdfa98bcc91553ebdffd5da780a67074e6206f3e2f0d366cac23b89becec78fc'): 'Ninguno',
    (2, 88, 16, 'dcf0e17441b25b9472757cc4fa03007072df51cf7b63649994afdc66f36068b2'): 'Quebrantatierra',
    (2, 88, 16, 'e758b81b92caf298c9cfa17e38826a317c436f064d605930ba6df084d7c7fbb3'): 'Esplendor floral',
    (2, 88, 16, 'f53db8691fc3f3b04d055da3b3a55fc78300091a94d21fa5cb0fdd3e857107fd'): 'Número de la Bestia',
    (3, 48, 16, '01567991d0a5121538d32a687fb36df3bab366a14e8d6c6a4bb7d164cd8a353d'): 'Obstáculo',
    (3, 48, 16, '6ab7a9dd7920929d908d3fd5ddc4adbde4afd8de024c4692e1aadd760f95a198'): 'Rey demonio',
    (3, 48, 16, '79c9b59892db4ad569087a6021eb9f4a87509da0afa9672cfb434eec7ca64d16'): 'Acala de hielo',
    (3, 48, 16, 'a622b483164e91acd8adb4fbdac666e1d7edf0d162936c2bb038f29d383aa72f'): 'Acala de fuego',
    (3, 48, 16, 'ad682fe9fd1e6a1777e13f402ef498fdd521f6ce585cc33881c50620f5e85f74'): 'Acala del rayo',
    (3, 48, 16, 'af396aa40d5235a756721f5e26f22b36579d57d9a4a44e34670ed1c191bd7874'): 'Demonio',
    (3, 48, 16, 'fde74606cee98b9a400054f666a52511ab8356cae75fd1c548035dbbafa4fa67'): 'Retaguardia',
}
INK = {0: (40, 40, 80), 1: (208, 208, 208), 3: (56, 56, 72)}


@lru_cache(maxsize=128)
def _localize_group(raw):
    count = struct.unpack_from('>H', raw)[0] if len(raw) >= 2 else 0
    if count != 4 or len(raw) < 80:
        return raw, ()
    result = bytearray(raw)
    changes = []
    for image in range(count):
        w, h, _, _, _, relative, _, n = struct.unpack_from('>8H', raw, (image + 1) * 16)
        start = 80 + relative
        if n != w * h // 2 or start + n > len(raw):
            raise ValueError('WKL: descriptor de rótulo inválido')
        stock = raw[start:start + n]
        text = LABELS.get((image, w, h, sha256(stock).hexdigest()))
        if text is None:
            continue
        rows = read_indices(stock, 0, w, h, 4)
        if '\n' in text:
            for y, line in enumerate(text.splitlines()):
                replace_text(rows, INK, (0, 8 * y, w, 8), line, 'arialbd.ttf', 7,
                             ink=1, bg=0, allowed=(0, 1, 3))
        else:
            replace_text(rows, INK, (0, 0, w, h), text, 'georgiab.ttf', 10,
                         ink=1, bg=0, outline=3, allowed=(1, 3))
        write_indices(result, start, rows, 4)
        changes.append((start, n, text))
    return bytes(result), tuple(changes)


@lru_cache(maxsize=128)
def _pack(raw):
    data = compress(raw)
    return data.ljust((len(data) + 3) & ~3, b'\0')


def traducir_rotulos_wkl(wkl: bytearray) -> None:
    if len(wkl) < 0x104:
        raise ValueError('WKL: cabecera truncada')
    base = struct.unpack_from('>I', wkl, 0x100)[0]
    if base + 512 > len(wkl):
        raise ValueError('WKL: directorio truncado')
    groups = []
    cursor = 512
    fits = True
    for slot in range(64):
        pos, size = struct.unpack_from('>II', wkl, base + 8 * slot)
        if pos != cursor or size % 4 or base + pos + size > len(wkl):
            raise ValueError(f'WKL: topología de grupo {slot} desconocida')
        cursor += size
        if not size:
            groups.append((pos, 0, b'', b'', False))
            continue
        original = bytes(wkl[base + pos:base + pos + size])
        raw, used = decompress_ex(original, limit=16384)
        if any(original[used:]):
            raise ValueError('WKL: relleno PRS inesperado')
        localized, changes = _localize_group(raw)
        packed = _pack(localized) if changes else b''
        fits &= len(packed) <= size
        groups.append((pos, size, packed, original[:(used + 3) & ~3], bool(changes)))
    if fits:
        for pos, size, packed, _, changed in groups:
            if changed:
                wkl[base + pos:base + pos + size] = packed.ljust(size, b'\0')
        return

    # The stock directory describes contiguous, aligned PRS blocks. Repack only
    # this original extent and retain every other WKL block and file offset.
    records = bytearray(512)
    payload = bytearray()
    for slot, (_, _, packed, before, changed) in enumerate(groups):
        data = packed if changed else before
        struct.pack_into('>II', records, slot * 8, 512 + len(payload), len(data))
        payload.extend(data)
    if 512 + len(payload) > cursor:
        raise ValueError('WKL: los rótulos no caben en el banco de nombres original')
    wkl[base:base + cursor] = (records + payload).ljust(cursor, b'\0')

TURN_LABELS = (
    (3, '2cb4114952d546ec428e9e3733926f7ff7954e6a00a0998d7dd077ce4c8ab018', 'Actuando'),
    (21, 'd650b24cac387345066619d8c26b4f381eb15052a747105d73e0e1fbf68dd93a', 'En turno'),
)


def traducir_turno_wkl(wkl: bytearray) -> None:
    """Localize the two fixed-layout WKL turn notice sprites."""
    edits = []
    for image, digest, text in TURN_LABELS:
        start, stop = label_span(wkl, 3, image, 40)
        source = bytes(wkl[start:stop])
        if sha256(source).hexdigest() != digest:
            raise ValueError(f'WKL: aviso de turno {image} no reconocido')
        rows = read_indices(source, 0, 40, 16, 4)
        replace_text(rows, INK, (0, 0, 40, 16), text, 'georgiab.ttf', 10,
                     ink=1, bg=0, outline=3, allowed=(1, 3))
        patched = bytearray(source)
        write_indices(patched, 0, rows, 4)
        edits.append((start, stop, patched))
    for start, stop, data in edits:
        wkl[start:stop] = data
