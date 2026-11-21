"""Find byte-exact Saturn event strip groups in a local tactical checkpoint."""

import argparse
from collections import defaultdict
import json
import mmap
from pathlib import Path
import re
import struct

from audit_native_characters import state_vectors
from audit_portrait_coverage import active_commands
from audit_sdk import files
from decode_saturn_units import UnitError, image_set


def coordinate(word):
    return ((word & 0x1fff) ^ 0x1000) - 0x1000


def event_banks(path, prefix):
    with path.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        return {
            Path(name).stem: iso[lba * 2048:lba * 2048 + size]
            for name, lba, size in files(iso)
            if re.fullmatch(r'/SAKURA2/EVS\d+\.BIN', name, re.IGNORECASE)
            and Path(name).stem.upper().startswith(prefix)
        }


def bank_sections(data):
    if len(data) < 8:
        raise ValueError('Truncated EVS table')
    table_size = struct.unpack_from('>I', data)[0]
    if not 8 <= table_size <= len(data) or table_size % 8:
        raise ValueError('Invalid EVS table size')
    sections = list(struct.iter_unpack('>II', data[:table_size]))
    cursor = table_size
    for offset, length in sections:
        if offset != cursor or offset + length > len(data):
            raise ValueError('Noncontiguous or truncated EVS section')
        cursor += length
    if cursor != len(data):
        raise ValueError('EVS table does not cover the whole file')
    return sections


def bank_image_sets(data):
    for slot, (offset, length) in enumerate(bank_sections(data)):
        try:
            records, base = image_set(data[offset:offset + length])
        except UnitError:
            continue
        yield slot, records, offset + base


def bank_inventory(banks):
    return {
        name: {
            'sections': len(bank_sections(data)),
            'image_sets': [
                {'slot': slot, 'data_offset': offset, 'images': len(records)}
                for slot, records, offset in bank_image_sets(data)
            ],
        }
        for name, data in sorted(banks.items())
    }


def exact_image_slot(data, group):
    observed = [(strip['offset'], strip['height']) for strip in group]
    for slot, records, start in bank_image_sets(data):
        if any(w != 8 or fmt != 4 for w, _, fmt, _, _, _ in records):
            continue
        if [(start + offset, h) for _, h, _, _, offset, _ in records] == observed:
            return slot
    return None


def contiguous_groups(strips):
    ordered = sorted(strips, key=lambda strip: strip['vram'])
    group = []
    for strip in ordered:
        if group:
            last = group[-1]
            length = 8 * last['height']
            if (last['vram'] + length != strip['vram'] or
                    last['offset'] + length != strip['offset']):
                yield group
                group = []
        group.append(strip)
    if group:
        yield group


def later_4bpp_overlaps(vram, commands, strips):
    last = max(strip['order'] for strip in strips)
    silhouette = set()
    for strip in strips:
        start, height = strip['vram'], strip['height']
        silhouette.update((strip['x'] + i % 8, strip['y'] + i // 8)
                          for i, value in enumerate(vram[start:start + 8 * height]) if value)

    overlaps = []
    for order, address, command, vertices in commands:
        if order <= last or command[0] & 0x3f != 2 or command[2] != 0x80:
            continue
        width, height = ((command[5] >> 8) & 63) * 8, command[5] & 255
        left, top = vertices[0]
        if not width or not height or not rectangular(vertices, width, height):
            continue
        covered = 0
        for x, y in silhouette:
            px, py = x - left, y - top
            if 0 <= px < width and 0 <= py < height:
                index = py * width + px
                packed = vram[(command[4] * 8 + index // 2) & 0x7ffff]
                covered += bool((packed & 15) if index & 1 else (packed >> 4))
        if covered:
            overlaps.append(dict(order=order, command_address=address, opaque_overlap=covered))
    return overlaps


def rectangular(vertices, width, height):
    left, top = vertices[0]
    right, bottom = left + width - 1, top + height - 1
    return vertices == [(left, top), (right, top), (right, bottom), (left, bottom)]


def framebuffer_witness(vram, buffers, palette, strips):
    # Compare the 16-bit, 512-pixel VDP1 layout observed in the MAP02 witness.
    # This does not identify the active display buffer or check VDP2 priority.
    samples = []
    for strip in strips:
        start, height = strip['vram'], strip['height']
        for index, texel in enumerate(vram[start:start + 8 * height]):
            x, y = strip['x'] + index % 8, strip['y'] + index // 8
            if texel and 0 <= x < 512 and 0 <= y < 256:
                address = 2 * (y * 512 + x)
                expected = (palette & 0xffc0) | (texel & 0x3f)  # CMDPMOD 0x90
                samples.append((address, expected))
    result = []
    for index, buffer in enumerate(buffers):
        matched = sum(struct.unpack_from('>H', buffer, address)[0] == expected
                      for address, expected in samples)
        result.append(dict(buffer=index, matching=matched, sampled=len(samples)))
    return result


def observed_groups(state, banks):
    vectors = state_vectors(state)
    vram = vectors[3]
    local_x = local_y = 0
    linked = defaultdict(list)
    commands = []
    for order, (command_address, command) in enumerate(active_commands(vram, with_address=True)):
        control, _, mode, palette, source, size, x, y = command
        kind = control & 15
        if kind == 10:
            local_x, local_y = coordinate(x), coordinate(y)
            continue
        if kind != 2:
            continue
        corners = struct.unpack_from('>8H', vram, command_address + 12)
        vertices = [(local_x + coordinate(cx), local_y + coordinate(cy))
                    for cx, cy in zip(corners[::2], corners[1::2])]
        commands.append((order, command_address, command, vertices))
        # The witnessed EVS actor uses distorted 8-column, 8 bpp strips.
        height = size & 255
        if control & 0x30 or mode != 0x90 or size >> 8 != 1 or not rectangular(vertices, 8, height):
            continue
        left, top = vertices[0]
        address = source * 8
        pixels = vram[address:address + height * 8]
        if len(pixels) != height * 8 or not any(pixels):
            continue
        candidates = [(name, offset) for name, data in banks.items()
                      if (offset := data.find(pixels)) >= 0]
        if len(candidates) != 1:
            continue
        bank, offset = candidates[0]
        if banks[bank].find(pixels, offset + 1) >= 0:
            continue
        linked[bank, palette].append(dict(vram=address, offset=offset, height=height,
                                          x=left, y=top, vertices=vertices,
                                          order=order, command_address=command_address))

    results = []
    for (bank, palette), strips in sorted(linked.items()):
        for group in contiguous_groups(strips):
            xs = sorted(strip['x'] for strip in group)
            if len(xs) >= 3 and xs == list(range(xs[0], xs[0] + 8 * len(xs), 8)):
                results.append(dict(bank=bank, palette=palette, strips=group,
                                    image_slot=exact_image_slot(banks[bank], group),
                                    later_4bpp_overlaps=later_4bpp_overlaps(vram, commands, group),
                                    framebuffer_512x256=framebuffer_witness(vram, vectors[4:6], palette, group)))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso', type=Path, required=True)
    parser.add_argument('--bank-prefix', default='EVS')
    parser.add_argument('--inventory', action='store_true', help='list native image sets without loading states')
    parser.add_argument('states', type=Path, nargs='*')
    args = parser.parse_args()
    banks = event_banks(args.iso, args.bank_prefix.upper())
    if not banks:
        parser.error('No matching Saturn event banks')
    if args.inventory:
        if args.states:
            parser.error('--inventory does not accept states')
        result = bank_inventory(banks)
    else:
        if not args.states:
            parser.error('Pass at least one tactical state or use --inventory')
        result = {str(path): observed_groups(path.read_bytes(), banks) for path in args.states}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
