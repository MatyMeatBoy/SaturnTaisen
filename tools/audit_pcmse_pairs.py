"""List offline PCMSE matches by Saturn dispatch ID and PC SE.TAB entry."""

import argparse
from hashlib import sha256
import json
import mmap
from pathlib import Path
import re
import struct
import wave

from audit_sdk import files


def pcmse_rows(data):
    if len(data) < 112 or struct.unpack_from('>I', data)[0] != 112:
        raise ValueError('Unexpected PCMSE bank directory')
    for index, (offset, count) in enumerate(struct.iter_unpack('>II', data[:112])):
        if not count:
            continue
        if offset < 112 or offset + count > len(data):
            raise ValueError(f'Invalid PCMSE entry {index}')
        yield index, offset, count


def read_bank(path):
    with path.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        for name, lba, size in files(iso):
            if name.upper() == '/SAKURA2/PCMSE.BIN':
                return iso[lba * 2048:lba * 2048 + size]
    raise ValueError(f'PCMSE bank absent in {path.name}')


def census(bank, pc):
    table = (pc / 'SAKURA2/SE.TAB').read_text(encoding='cp932')
    names = {}
    for identity, filename in re.findall(r'^\s*(\d+)\s+(\w+\.wav)\s+STATIC\b', table,
                                         flags=re.IGNORECASE | re.MULTILINE):
        identity = int(identity)
        if identity in names and names[identity] != filename.upper():
            raise ValueError(f'Ambiguous PC SE.TAB dispatch ID {identity}')
        names[identity] = filename.upper()
    result = []
    for index, offset, count in pcmse_rows(bank):
        identity = 41 + index
        if identity not in (*range(41, 52), 54) or identity not in names:
            raise ValueError(f'Unknown dispatch or missing PC entry for PCMSE row {index}')
        relative = Path('SAKURA2/SE') / names[identity]
        donor = pc / relative
        with wave.open(str(donor), 'rb') as source:
            audio = dict(rate=source.getframerate(), channels=source.getnchannels(),
                         bits=8 * source.getsampwidth(), frames=source.getnframes())
        result.append(dict(row=index, dispatch_id=identity, offset=offset, bytes=count,
                           saturn_sha256=sha256(bank[offset:offset + count]).hexdigest(),
                           pc=relative.as_posix(), pc_sha256=sha256(donor.read_bytes()).hexdigest(),
                           format=audio))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disc', type=Path, action='append', required=True)
    parser.add_argument('--pc-root', type=Path, required=True)
    args = parser.parse_args()
    try:
        banks = [read_bank(path) for path in args.disc]
        if any(bank != banks[0] for bank in banks[1:]):
            raise ValueError('PCMSE bank differs between discs')
        rows = census(banks[0], args.pc_root)
    except (OSError, ValueError, wave.Error) as error:
        parser.exit(1, f'{error}\n')
    print(json.dumps(dict(scope='dispatch-ID matches, not an audible verification', rows=rows), indent=2))


if __name__ == '__main__':
    main()
