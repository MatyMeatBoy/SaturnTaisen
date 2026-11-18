"""Build a Spanish copy of a prepared English Saturn ISO without touching the source.

All dialogue tables move to fixed 128 KiB slots appended after the data track, so a
table can grow without moving anything else and LBAs are identical in every build.
The original extents are left untouched (unreferenced). Both-endian LBA/size fields in
the directory record and the PVD volume size are updated. The source image is only read.
"""
import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

SECTOR = 2048


def both(value: int) -> bytes:
    return struct.pack('<I', value) + struct.pack('>I', value)


def directory_records(iso: bytearray):
    """Yield (path, record_offset, lba, size) for every file."""
    pvd = 16 * SECTOR
    if iso[pvd:pvd + 6] != b'\x01CD001':
        raise ValueError('not an ISO9660 image')
    root = pvd + 156
    seen = set()

    def walk(record_at, parent, depth):
        lba, size = struct.unpack_from('<I', iso, record_at + 2)[0], struct.unpack_from('<I', iso, record_at + 10)[0]
        if (lba, size) in seen or depth > 32:
            return
        seen.add((lba, size))
        at, end = lba * SECTOR, lba * SECTOR + size
        while at < end:
            length = iso[at]
            if not length:
                at = (at // SECTOR + 1) * SECTOR
                continue
            name = bytes(iso[at + 33:at + 33 + iso[at + 32]])
            if name not in (b'\0', b'\1'):
                name = name.decode('ascii').split(';')[0]
                path = f'{parent}/{name}'
                if iso[at + 25] & 2:
                    yield from walk(at, path, depth + 1)
                else:
                    yield path, at, *struct.unpack_from('<I', iso, at + 2), struct.unpack_from('<I', iso, at + 10)[0]
            at += length

    yield from walk(root, '', 0)


SLOT_SECTORS = 64  # 128 KiB per table; layout is fixed so savestates stay valid across rebuilds


def build(source: Path, output: Path, replacements: dict[str, bytes]) -> dict:
    """Every *TBL.BIN of the source moves to a fixed slot at the end, in sorted path order.
    Tables without a replacement keep their original bytes, so the layout never changes."""
    iso = bytearray(source.read_bytes())
    if len(iso) % SECTOR:
        raise ValueError('data track is not sector aligned')
    records = {path.upper(): (at, lba, size) for path, at, lba, size in directory_records(iso)}
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
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(iso)
    # Verify: every replaced file reads back exactly through the rewritten directory.
    check = {p.upper(): (lba, size) for p, _, lba, size in directory_records(iso)}
    for path, data in wanted.items():
        lba, size = check[path]
        if bytes(iso[lba * SECTOR:lba * SECTOR + size]) != data:
            raise ValueError('read-back mismatch: ' + path)
    return dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                output=str(output), output_sha256=hashlib.sha256(iso).hexdigest(), files=report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True, help='prepared English disc folder')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--files', type=Path, required=True, help='folder of replacement files named as in the ISO')
    args = parser.parse_args()
    if args.output_dir.resolve() == args.source_dir.resolve():
        raise SystemExit('output must differ from the source')
    replacements = {}
    for file in sorted(args.files.rglob('*')):
        if file.is_file():
            replacements['/' + file.relative_to(args.files).as_posix()] = file.read_bytes()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = build(args.source_dir / 'Track 01.iso', args.output_dir / 'Track 01.iso', replacements)
    for name in ('Track 02.wav', 'game.cue'):
        if (args.source_dir / name).exists() and not (args.output_dir / name).exists():
            shutil.copy2(args.source_dir / name, args.output_dir / name)
    (args.output_dir / 'es-build.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'files'} | {'files': len(report['files'])}, indent=2))


if __name__ == '__main__':
    main()
