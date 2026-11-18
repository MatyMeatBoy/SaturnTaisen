"""Build a Spanish copy of a prepared English Saturn ISO without touching the source.

All dialogue tables move to fixed 128 KiB slots appended after the data track, so a
table can grow without moving anything else and LBAs are identical in every build.
The original extents are left untouched (unreferenced). Both-endian LBA/size fields in
the directory record and the PVD volume size are updated. The source image is only read.
"""
import argparse
import hashlib
import json
import mmap
import re
import shutil
import struct
from pathlib import Path

from _rutas import atomic_output, distinct_output, private_path, write_bytes

SECTOR = 2048


def both(value: int) -> bytes:
    return struct.pack('<I', value) + struct.pack('>I', value)


def directory_records(iso):
    """Yield (path, record_offset, lba, size) for every bounded file extent."""
    pvd = 16 * SECTOR
    if len(iso) < pvd + SECTOR or iso[pvd:pvd + 7] != b'\x01CD001\x01':
        raise ValueError('not an ISO9660 image')
    seen = set()

    def both_at(offset):
        little, big = struct.unpack_from('<I', iso, offset)[0], struct.unpack_from('>I', iso, offset + 4)[0]
        if little != big:
            raise ValueError(f'inconsistent both-endian field at {offset}')
        return little

    def extent(record_at):
        lba, size = both_at(record_at + 2), both_at(record_at + 10)
        if lba * SECTOR + size > len(iso):
            raise ValueError(f'extent falls outside the ISO at {record_at}')
        return lba, size

    def walk(record_at, parent, depth):
        lba, size = extent(record_at)
        if (lba, size) in seen or depth > 32:
            raise ValueError(f'repeated or deeply nested directory: {parent}')
        seen.add((lba, size))
        at, end = lba * SECTOR, lba * SECTOR + size
        while at < end:
            length = iso[at]
            sector_end = (at // SECTOR + 1) * SECTOR
            if not length:
                at = sector_end
                continue
            if length < 34 or at + length > min(end, sector_end):
                raise ValueError(f'invalid directory record at {at}')
            name_length = iso[at + 32]
            if not 0 < name_length <= length - 33:
                raise ValueError(f'invalid directory name at {at}')
            name = bytes(iso[at + 33:at + 33 + name_length])
            if name not in (b'\0', b'\1'):
                name = name.decode('ascii').split(';')[0]
                if not name or name in ('.', '..') or '/' in name or '\\' in name:
                    raise ValueError(f'invalid ISO path component: {name!r}')
                path = f'{parent}/{name}'
                if iso[at + 25] & 2:
                    yield from walk(at, path, depth + 1)
                else:
                    yield path, at, *extent(at)
            at += length

    yield from walk(pvd + 156, '', 0)


SLOT_SECTORS = 64  # 128 KiB per table; layout is fixed so savestates stay valid across rebuilds


def build(source: Path, output: Path, replacements: dict[str, bytes]) -> dict:
    """Every *TBL.BIN of the source moves to a fixed slot at the end, in sorted path order.
    Tables without a replacement keep their original bytes, so the layout never changes."""
    distinct_output(output, source)
    iso = bytearray(source.read_bytes())
    source_sha256 = hashlib.sha256(iso).hexdigest()
    if len(iso) % SECTOR:
        raise ValueError('data track is not sector aligned')
    records = {}
    for path, at, lba, size in directory_records(iso):
        key = path.upper()
        if key in records:
            raise ValueError(f'duplicate ISO path: {path}')
        records[key] = (at, lba, size)
    unknown = set(p.upper() for p in replacements) - set(records)
    if unknown:
        raise ValueError(f'not in the image: {sorted(unknown)}')
    tables = sorted(p for p in records if p.endswith(('TBL.BIN', 'MES.BIN')))
    first = len(iso) // SECTOR
    iso += bytes(len(tables) * SLOT_SECTORS * SECTOR)
    wanted = {p.upper(): d for p, d in replacements.items()}
    report = []
    for slot, path in enumerate(tables):
        at, lba, size = records[path]
        data = wanted.get(path, bytes(iso[lba * SECTOR:lba * SECTOR + size]))
        if len(data) > SLOT_SECTORS * SECTOR:
            raise ValueError(f'{path} needs {len(data)} bytes, slot holds {SLOT_SECTORS * SECTOR}')
        new_lba, mode = first + slot * SLOT_SECTORS, 'replaced' if path in wanted else 'moved'
        iso[new_lba * SECTOR:new_lba * SECTOR + len(data)] = data
        iso[at + 2:at + 10] = both(new_lba)
        iso[at + 10:at + 18] = both(len(data))
        report.append(dict(path=path, old_lba=lba, old_size=size, lba=new_lba, size=len(data), mode=mode,
                           sha256=hashlib.sha256(data).hexdigest()))
    # Other replaced files (menus, program) must keep their size and are written in place.
    for path, data in sorted(wanted.items()):
        if path in tables:
            continue
        at, lba, size = records[path]
        if len(data) != size:
            raise ValueError(f'{path}: in-place replacement must keep {size} bytes, got {len(data)}')
        iso[lba * SECTOR:lba * SECTOR + size] = data
        report.append(dict(path=path, lba=lba, size=size, mode='in-place', sha256=hashlib.sha256(data).hexdigest()))
    iso[16 * SECTOR + 80:16 * SECTOR + 88] = both(len(iso) // SECTOR)
    # Read back directory entries and replacements from the staged image before publishing.
    with atomic_output(output) as temporary:
        temporary.write_bytes(iso)
        with temporary.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as staged:
            check = {p.upper(): (lba, size) for p, _, lba, size in directory_records(staged)}
            for path, data in wanted.items():
                lba, size = check[path]
                if staged[lba * SECTOR:lba * SECTOR + size] != data:
                    raise ValueError('read-back mismatch: ' + path)
    return dict(source=str(source), source_sha256=source_sha256,
                output=str(output), output_sha256=hashlib.sha256(iso).hexdigest(), files=report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True, help='prepared English disc folder')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--files', type=Path, required=True, help='folder of replacement files named as in the ISO')
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    try:
        output_dir = private_path(args.output_dir)
        distinct_output(output_dir, source_dir)
        track_names = ('Track 01.iso', 'Track 02.wav', 'game.cue')
        originals = tuple(source_dir / name for name in track_names)
        outputs = tuple(output_dir / name for name in (*track_names, 'es-build.json'))
        for output in outputs:
            distinct_output(output, *originals)
        cue = originals[2].read_bytes()
        references = re.findall(rb'(?im)^\s*FILE\s+"([^"]+)"\s+\w+\s*$', cue)
        if references != [b'Track 01.iso', b'Track 02.wav'] or not originals[1].is_file():
            raise ValueError('the prepared CUE must reference the two local track filenames')
        replacements = {}
        for file in sorted(args.files.rglob('*')):
            if file.is_file():
                replacements['/' + file.relative_to(args.files).as_posix()] = file.read_bytes()
        report = build(originals[0], outputs[0], replacements)
        # Audio is immutable across revisions. Copy a fresh track only when absent.
        if not outputs[1].is_file():
            with atomic_output(outputs[1]) as output:
                shutil.copyfile(originals[1], output)
        write_bytes(outputs[2], cue)
        write_bytes(outputs[3], json.dumps(report, indent=2).encode('utf-8'))
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    print(json.dumps({k: v for k, v in report.items() if k != 'files'} | {'files': len(report['files'])}, indent=2))


if __name__ == '__main__':
    main()
