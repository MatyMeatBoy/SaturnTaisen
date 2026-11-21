"""Normalize a locally owned PC BGM WAV and report its loop marker, if present."""

import argparse
from pathlib import Path
import struct
import sys


def normalize(data):
    if len(data) < 12 or data[:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise ValueError('Expected a RIFF/WAVE file')
    end = struct.unpack_from('<I', data, 4)[0] + 8
    if end < 12 or len(data) - end not in (0, 8):
        raise ValueError('RIFF extent does not match the file')

    at = 12
    found_data = False
    while at + 8 <= end:
        kind, size = struct.unpack_from('<4sI', data, at)
        start = at + 8
        following = start + size + (size & 1)
        if following > end:
            raise ValueError('WAV chunk exceeds RIFF extent')
        if kind == b'data':
            found_data = True
            if len(data) != end:
                if following != end or data[start:start + 4] != b'loop':
                    raise ValueError('Expected an eight-byte loop prefix in the final data chunk')
                value = struct.unpack_from('<I', data, start + 4)[0]
                return data[:start] + data[start + 8:], value
        at = following
    if at != end or not found_data or len(data) != end:
        raise ValueError('Incomplete WAV chunks or missing data chunk')
    return data, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    try:
        data, loop = normalize(args.source.read_bytes())
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')
    print(f'loop_value={loop}', file=sys.stderr)
    sys.stdout.buffer.write(data)


if __name__ == '__main__':
    main()
