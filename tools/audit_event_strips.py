"""Find byte-exact Saturn event strip groups in a local tactical checkpoint."""

import argparse
from collections import defaultdict
import json
import mmap
from pathlib import Path
import re

from audit_native_characters import state_vectors
from audit_portrait_coverage import active_commands
from audit_sdk import files


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


def observed_groups(state, banks):
    vram = state_vectors(state)[3]
    local_x = local_y = 0
    linked = defaultdict(list)
    for control, _, mode, palette, source, size, x, y in active_commands(vram):
        kind = control & 15
        if kind == 10:
            local_x, local_y = coordinate(x), coordinate(y)
            continue
        # The witnessed EVS actor uses distorted 8-column, 8 bpp strips.
        if kind != 2 or control & 0x30 or mode != 0x90 or size >> 8 != 1:
            continue
        height = size & 255
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
                                          x=local_x + coordinate(x), y=local_y + coordinate(y)))

    results = []
    for (bank, palette), strips in sorted(linked.items()):
        for group in contiguous_groups(strips):
            xs = sorted(strip['x'] for strip in group)
            if len(xs) >= 3 and xs == list(range(xs[0], xs[0] + 8 * len(xs), 8)):
                results.append(dict(bank=bank, palette=palette, strips=group))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso', type=Path, required=True)
    parser.add_argument('--bank-prefix', default='EVS')
    parser.add_argument('states', type=Path, nargs='+')
    args = parser.parse_args()
    banks = event_banks(args.iso, args.bank_prefix.upper())
    if not banks:
        parser.error('No matching Saturn event banks')
    result = {str(path): observed_groups(path.read_bytes(), banks) for path in args.states}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
