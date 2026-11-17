"""Import Saturn battery saves into a separate native backup image.

Container layouts: bucanero/saturn-save-tools (BUP/SAROO),
hitomi2500/ss-save-parser (SH-2 odd-byte memory images), and Saturn BUP blocks.
Save states are not battery saves and are deliberately rejected.
"""
import argparse
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import struct
import zlib

SIGNATURE = b'BackUpRam Format'
MAX_INPUT = 2 * 1024 * 1024


@dataclass(frozen=True)
class Save:
    name: bytes
    comment: bytes
    language: int
    date: int
    data: bytes


def _save(name, comment, language, date, data):
    name = name.split(b'\0', 1)[0]
    if not name or len(name) > 11 or any(c < 32 or c > 126 for c in name):
        raise ValueError('Invalid Saturn save filename')
    if language > 5:
        raise ValueError('Invalid Saturn save language')
    return Save(name, comment[:10].split(b'\0', 1)[0], language, date, data)


def decode_ssf_single(data, name):
    """SSF per-game hooks: comment, NUL, language, LE packed date.

    This container has no magic or stored filename: require explicit selection,
    and obtain the Saturn filename from the user's selected file's basename.
    """
    if not 16 < len(data) <= MAX_INPUT:
        raise ValueError('Invalid SSF single-save size')
    if data[10] != 0:
        raise ValueError('Invalid SSF single-save padding')
    value = struct.unpack_from('<I', data, 12)[0]
    stamp = datetime(1980 + ((value >> 23) & 511), (value >> 19) & 15,
                     (value >> 14) & 31, (value >> 9) & 31, (value >> 3) & 63)
    date = int((stamp - datetime(1980, 1, 1)).total_seconds() // 60)
    return [_save(name, data[:10], data[11], date, data[16:])]


def decode_saves(data):
    if len(data) > MAX_INPUT:
        raise ValueError('Save container is too large')
    if data.startswith(b'Vmem') or data.startswith(b'SSAVERAW'):
        if len(data) < 64:
            raise ValueError('Truncated single-save header')
        if data.startswith(b'Vmem'):
            comment, language = data[28:38], data[39]
            date, size = struct.unpack_from('>II', data, 40)
        else:
            size = struct.unpack_from('>I', data, 28)[0]
            comment, language = data[32:42], data[43]
            date = struct.unpack_from('>I', data, 44)[0]
            crc = struct.unpack_from('>I', data, 12)[0]
            if crc and crc != zlib.crc32(data[16:]):
                raise ValueError('SAROO save CRC mismatch')
        if size != len(data) - 64:
            raise ValueError('Single-save size mismatch')
        return [_save(data[16:27], comment, language, date, data[64:])]
    # SH-2 memory-bus dumps have a dummy byte before each useful byte.
    if len(data) in (65536, 1048576) and data[1:32:2] == SIGNATURE:
        data = data[1::2]
    geometry = {32768: 64, 524288: 512}
    block = geometry.get(len(data))
    if block is None or not data.startswith(SIGNATURE):
        raise ValueError('Unsupported or truncated Saturn battery-save container')
    payload, total = block - 4, len(data) // block
    owned, names, saves = set(), set(), []
    for first in range(2, total):
        if not data[first * block] & 0x80:
            continue
        chain = [first]

        def byte_at(at):
            index, offset = divmod(at, payload)
            if index >= len(chain):
                raise ValueError('Truncated backup allocation table')
            return data[chain[index] * block + 4 + offset]

        position = 30
        while True:
            next_block = (byte_at(position) << 8) | byte_at(position + 1)
            position += 2
            if not next_block:
                break
            if next_block < 2 or next_block >= total or next_block in chain:
                raise ValueError('Invalid or cyclic backup allocation chain')
            chain.append(next_block)
        if owned.intersection(chain):
            raise ValueError('Overlapping backup files')
        owned.update(chain)
        stream = b''.join(data[n * block + 4:(n + 1) * block] for n in chain)
        size = struct.unpack_from('>I', stream, 26)[0]
        if size > len(stream) - position:
            raise ValueError('Truncated backup file payload')
        save = _save(stream[:11], stream[12:22], stream[11],
                     struct.unpack_from('>I', stream, 22)[0], stream[position:position + size])
        if save.name in names:
            raise ValueError('Duplicate Saturn save filename')
        names.add(save.name)
        saves.append(save)
    return saves


def make_backup(saves):
    image = bytearray(32768)
    image[:64] = SIGNATURE * 4
    cursor, names = 2, set()
    for save in saves:
        save = _save(save.name, save.comment, save.language, save.date, save.data)
        if save.name in names:
            raise ValueError('Duplicate Saturn save filename')
        names.add(save.name)
        blocks = 1
        while blocks * 60 < 30 + blocks * 2 + len(save.data):
            blocks += 1
        if cursor + blocks > 512:
            raise ValueError('Imported saves do not fit internal backup RAM')
        stream = bytearray(blocks * 60)
        stream[:11] = save.name.ljust(11, b'\0')
        stream[11] = save.language
        stream[12:22] = save.comment.ljust(10, b'\0')
        struct.pack_into('>II', stream, 22, save.date, len(save.data))
        for i in range(1, blocks):
            struct.pack_into('>H', stream, 30 + (i - 1) * 2, cursor + i)
        start = 30 + blocks * 2
        stream[start:start + len(save.data)] = save.data
        for i in range(blocks):
            offset = (cursor + i) * 64
            if i == 0:
                image[offset] = 0x80
            image[offset + 4:offset + 64] = stream[i * 60:(i + 1) * 60]
        cursor += blocks
    return bytes(image)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--format', choices=('auto', 'ssf-single'), default='auto',
                        help='SSF per-game files have no signature; select this format explicitly')
    parser.add_argument('--output', type=Path, help='new backup image; existing files are never replaced')
    args = parser.parse_args()
    try:
        if args.source.stat().st_size > MAX_INPUT:
            raise ValueError('Save container is too large')
        source = args.source.read_bytes()
        saves = (decode_ssf_single(source, args.source.stem.encode('ascii'))
                 if args.format == 'ssf-single' else decode_saves(source))
        selected = [s for s in saves if s.name.startswith(b'SAKURA___')]
        if not selected:
            raise ValueError('No Sakura Wars 1 battery save found')
        if args.output:
            result = make_backup(selected)
            with args.output.open('xb') as output:
                output.write(result)
        print(json.dumps({'source': str(args.source.resolve()),
                          'sha256': hashlib.sha256(source).hexdigest(),
                          'saves': [{'name': s.name.decode('ascii'), 'bytes': len(s.data)} for s in selected],
                          'output': str(args.output.resolve()) if args.output else None}, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, f'Import rejected: {error}\n')


if __name__ == '__main__':
    main()
