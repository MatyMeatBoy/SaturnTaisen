"""Read-only decoder for the Saturn tactical unit banks `SAKURA2/UNITnn.BIN` (TS11a).

Format (verified on all 27 banks of both discs; see docs/research/saturn-unit-bank-format.md):

  0x00  26 pairs of big-endian u32 (offset, size): 0xD0 bytes, so the first entry starts at 0xD0.
        Entries are contiguous; an entry with size 0 is empty (slots 1-11, 16, 17 in every bank seen).
  e0    a compressed image set: the game's LZ (tools/es/red_lz.py, SH-2 routine 0x0600A164) ending in its
        end marker; the whole stream is `size` bytes (the decoder reports the bytes consumed, size - 2).
  e12-e15, e23, e25
        palettes: big-endian RGB555 words (bit 15 set on opaque colours), 0x80 / 0x40 / 0x20 bytes.
  e18-e22, e24
        raw (not compressed) image sets.

An image set:

  0x00  u16 image count n, 14 zero bytes
  0x10  n records of 16 bytes: u16 width, u16 height, u16 format, u16 colour field, u32 offset, u32 size
  0x10 + 16 n  pixel data; `offset` is relative to the start of this area
  format 4: 8 bits per pixel, size = w*h (palette index 0 is clear); format 0: 4 bits per pixel, high nibble
  first, size = w*h/2, and the colour field holds a constant per set (0x5F0, 0x300, 0x3A0, 0x5E0).
  Pixels are linear, row by row (VDP1 sprite layout). The image sets of a bank end exactly where the
  records say, which is how every set is validated.

Which palette an image set uses is not stored in the bank (the 8-bit sets index a 256-colour table that the
game loads elsewhere), so images decode to palette indices; `palette_words()` returns the RGB555 words of an
entry for the local views that want colours. Silhouettes (`index != 0`) do not need a palette.

Usage:
  python tools/decode_saturn_units.py --inventory DISC1.iso DISC2.iso config/hd-saturn-unit-images.json
  python tools/decode_saturn_units.py "disc/Track 01.iso" SAKURA2/UNIT04.BIN            # list the entries
  python tools/decode_saturn_units.py "disc/Track 01.iso" SAKURA2/UNIT04.BIN OUTDIR      # one grey PNG per image
Never commit the output: it is the game's art.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'es'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import red_lz  # noqa: E402

SLOTS = 26
TABLE_BYTES = SLOTS * 8
FIRST_ENTRY = 0xD0
IMAGE_SLOTS = (0, 18, 19, 20, 21, 22, 24)
PALETTE_SLOTS = (12, 13, 14, 15, 23, 25)
COMPRESSED_SLOTS = (0,)
FORMAT_BPP = {0: 4, 4: 8}


class UnitError(ValueError):
    pass


def entries(data):
    """The 26 (offset, size) pairs; raises UnitError when the table is not contiguous inside the file."""
    if len(data) < TABLE_BYTES:
        raise UnitError('file shorter than the entry table')
    pairs = [struct.unpack_from('>II', data, 8 * i) for i in range(SLOTS)]
    if pairs[0][0] != FIRST_ENTRY:
        raise UnitError('first entry is not at 0xD0')
    cursor = FIRST_ENTRY
    for index, (offset, size) in enumerate(pairs):
        if offset != cursor or offset + size > len(data):
            raise UnitError('entry %d is not contiguous inside the file' % index)
        cursor += size
    return pairs


def entry_bytes(data, index):
    offset, size = entries(data)[index]
    return data[offset:offset + size]


def image_set(raw):
    """Parse an image set into (records, pixel_area_at). A record is (w, h, format, colour_field, offset, size).

    Validates every extent against `raw` and the size against the format."""
    if len(raw) < 16:
        raise UnitError('image set shorter than its header')
    count = struct.unpack_from('>H', raw, 0)[0]
    if raw[2:16] != bytes(14) or not 0 < count <= 1024 or 16 + 16 * count > len(raw):
        raise UnitError('bad image-set header')
    base = 16 + 16 * count
    records = []
    for n in range(count):
        record = struct.unpack_from('>HHHHII', raw, 16 + 16 * n)
        w, h, fmt, _, offset, size = record
        bpp = FORMAT_BPP.get(fmt)
        if bpp is None or size != (w * h * bpp + 7) // 8 or base + offset + size > len(raw):
            raise UnitError('image %d: invalid format, size or extent' % n)
        records.append(record)
    return records, base


def entry_image_set(data, index):
    """(records, raw_bytes_of_the_set) of an image slot, decompressing slot 0."""
    raw = entry_bytes(data, index)
    if not raw:
        raise UnitError('slot %d is empty' % index)
    if index in COMPRESSED_SLOTS:
        raw, used = red_lz.decompress_ex(raw)
    return image_set(raw)[0], raw


def image_indices(raw, record, base=None):
    """The palette indices of one image as a list of rows (4 bpp expanded to one index per pixel)."""
    w, h, fmt, _, offset, size = record
    if base is None:
        base = 16 + 16 * struct.unpack_from('>H', raw, 0)[0]
    pixels = raw[base + offset:base + offset + size]
    if FORMAT_BPP[fmt] == 8:
        flat = pixels
    else:
        flat = bytearray()
        for value in pixels:
            flat.append(value >> 4)
            flat.append(value & 15)
    return [bytes(flat[y * w:(y + 1) * w]) for y in range(h)]


def silhouette(rows):
    """Rows of 0/1 (1 where the palette index is not the clear index 0)."""
    return [[1 if v else 0 for v in row] for row in rows]


def palette_words(data, index):
    """RGB555 words of a palette slot."""
    raw = entry_bytes(data, index)
    return list(struct.unpack('>%dH' % (len(raw) // 2), raw[:len(raw) // 2 * 2]))


def all_images(data):
    """Yield (slot, n, record, rows) for every image of every image slot of a bank."""
    for slot in IMAGE_SLOTS:
        if not entries(data)[slot][1]:
            continue
        records, raw = entry_image_set(data, slot)
        base = 16 + 16 * len(records)
        for n, record in enumerate(records):
            yield slot, n, record, image_indices(raw, record, base)


def inventory(banks):
    """Data-only description of banks {name: bytes}: per bank the slots, and per distinct image set its images.

    Banks with identical bytes are listed once (`same_as`). Hashes are SHA-256 of the decoded bytes; no pixels."""
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    result, seen, sets = [], {}, {}
    for name, data in sorted(banks.items()):
        digest = sha(data)
        row = {'bank': name, 'size': len(data), 'sha256': digest}
        if digest in seen:
            row['same_as'] = seen[digest]
            result.append(row)
            continue
        seen[digest] = name
        slots = {}
        for slot, (offset, size) in enumerate(entries(data)):
            if not size:
                continue
            raw = data[offset:offset + size]
            item = {'offset': offset, 'size': size, 'sha256': sha(raw)}
            if slot in IMAGE_SLOTS:
                records, decoded = entry_image_set(data, slot)
                item['image_set'] = sha(decoded)
                item['images'] = len(records)
                if item['image_set'] not in sets:
                    sets[item['image_set']] = {
                        'first_seen': '%s slot %d' % (name, slot), 'decoded_size': len(decoded),
                        'compressed': slot in COMPRESSED_SLOTS,
                        'images': [{'w': r[0], 'h': r[1], 'format': r[2], 'colour_field': r[3], 'offset': r[4],
                                    'size': r[5], 'sha256': sha(decoded[16 + 16 * len(records) + r[4]:][:r[5]])}
                                   for r in records]}
            elif slot in PALETTE_SLOTS:
                item['colours'] = size // 2
            slots[str(slot)] = item
        row['slots'] = slots
        result.append(row)
    return {'schema': 1, 'scope': 'Saturn UNITnn.BIN image sets, names, sizes and hashes only (no pixels).',
            'summary': {'banks': len(result), 'distinct_banks': len(seen), 'distinct_image_sets': len(sets),
                        'distinct_images': len({i['sha256'] + '%dx%d' % (i['w'], i['h']) for v in sets.values() for i in v['images']})},
            'banks': result, 'image_sets': dict(sorted(sets.items()))}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == '--inventory':
        import decode_saturn_bg as saturn
        banks = {}
        for disc, path in ((1, argv[1]), (2, argv[2])):
            iso = saturn.Iso(path)
            for name, extent in iso.files('SAKURA2'):
                if name.startswith('UNIT') and name.endswith('.BIN'):
                    banks['%d:/SAKURA2/%s' % (disc, name)] = iso.content(extent)
        Path(argv[3]).write_text(json.dumps(inventory(banks), indent=1, sort_keys=True) + chr(10), encoding='utf-8', newline=chr(10))
        return 0
    if len(argv) not in (2, 3):
        print(__doc__)
        return 1
    import decode_saturn_bg as saturn
    iso = saturn.Iso(argv[0])
    folder, name = argv[1].strip('/').rsplit('/', 1)
    extent = dict(iso.files(folder)).get(name)
    if extent is None:
        print('file not found on the disc')
        return 1
    data = iso.content(extent)
    for slot, (offset, size) in enumerate(entries(data)):
        if size:
            print('slot %2d offset 0x%X size 0x%X' % (slot, offset, size))
    if len(argv) == 3:
        from PIL import Image
        out = Path(argv[2])
        out.mkdir(parents=True, exist_ok=True)
        for slot, n, record, rows in all_images(data):
            w, h = record[0], record[1]
            image = Image.new('L', (w, h))
            image.putdata([min(255, v * (16 if FORMAT_BPP[record[2]] == 4 else 1)) for row in rows for v in row])
            image.save(out / ('e%d_%03d.png' % (slot, n)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
