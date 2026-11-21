"""Find exact fixed-cell Saturn BG residency in archived Sakura v9 states."""

import argparse
from collections import defaultdict
import json
import mmap
from pathlib import Path

from audit_native_characters import state_vector_ranges
from decode_saturn_bg import HEADER, Iso, _fixed_cells


def scene_signatures(disc, paths):
    """Index palettes and the native cells following the first character."""
    signatures = defaultdict(dict)
    missing = []
    for path in sorted(set(paths)):
        extent = disc.find(path)
        raw = disc.content(extent) if extent is not None else b''
        layout = _fixed_cells(raw)
        if not layout:
            missing.append(path)
            continue
        _, _, palette_at = layout
        cells = raw[HEADER + 64:palette_at]
        if len(set(cells)) < 2:
            missing.append(path)
            continue
        signatures[raw[palette_at:palette_at + 512]][path] = cells
    return signatures, missing


def scan_states(signatures, states):
    matches = defaultdict(list)
    scanned = 0
    unreadable = 0
    for state in states:
        try:
            with state.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
                ranges = state_vector_ranges(data)
                scanned += 1
                vram_start, vram_end = ranges[6]
                cram_start, cram_end = ranges[7]
                for offset in range(cram_start, cram_end, 512):
                    possible = signatures.get(data[offset:offset + 512], {})
                    for path, cells in possible.items():
                        start = data.find(cells, vram_start + 64, vram_end)
                        if start >= 0:
                            matches[path].append({
                                'snapshot': str(state),
                                'vram': start - vram_start - 64,
                                'cram': offset - cram_start,
                            })
        except (OSError, ValueError):
            unreadable += 1
    return {'scanned': scanned, 'unreadable': unreadable, 'resident': dict(sorted(matches.items()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disc', type=Path, required=True, help='Saturn data-track ISO')
    parser.add_argument('--asset', action='append', required=True, help='case-sensitive path inside the ISO')
    parser.add_argument('--state-list', type=Path, required=True, help='one local snapshot path per line')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        disc = Iso(args.disc)
        with disc.file:
            signatures, missing = scene_signatures(disc, args.asset)
        state_list = args.state_list.read_text(encoding='utf-8-sig').splitlines()
        states = dict.fromkeys(Path(line.strip()).resolve() for line in state_list if line.strip())
        report = scan_states(signatures, states)
        report.update(scope='Exact palette and cell residency, excluding the first 64-byte character.',
                      unsupported_or_missing_assets=missing)
        args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"{report['scanned']} snapshots indexed, {len(report['resident'])} resident scene identities")


if __name__ == '__main__':
    main()
