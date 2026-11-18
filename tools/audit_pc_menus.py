"""Inventory owner PC menu/HUD resources (SAKURA1/SYSTEM) against Saturn disc files.

Matching names are candidates, never a claim of compatible layout, palette or composition.
No images, pixels or original artwork are written to this repository.
"""
import argparse
import hashlib
import json
import mmap
from pathlib import Path

from audit_pc_sprites import inspect
from audit_sdk import files

# Candidate correspondence between PC SAKURA1/SYSTEM/*.SPR resources and the Saturn files this
# project already edits for the Spanish menu patch (see docs/research/traduccion-espanol.md) or
# that are otherwise responsible for the same on-screen menu. A name match here is a lead to
# verify by inspecting both images, not a claim that geometry, palette or text position agree.
SYSTEM_CANDIDATES = {
    'TITLE': ['/SAKURA1/LOGO.SH2'],
    'SEGALOGO': ['/SAKURA1/LOGO.SH2'],
    'REDLOGO': ['/SAKURA1/LOGO.SH2'],
    'OPTION': ['/SAKURA'],
    'WINDOW': ['/SAKURA'],
    'NOWLOAD': ['/SAKURA1/LOAD.BIN'],
    'SISTEM': ['/SAKURA1/ICATALL.DAT'],
    'SIS_BG': ['/SAKURA1/ICATALL.DAT'],
    'SIS_BG2': ['/SAKURA1/ICATALL.DAT'],
    'SIS_BG3': ['/SAKURA1/ICATALL.DAT'],
    'SIS_ICON': ['/SAKURA1/ICATALL.DAT'],
    'OMKMOV_W': ['/SAKURA1/OMALL.DAT'],
    'OMKSND_W': ['/SAKURA1/OMALL.DAT'],
    'KARAOKE': ['/SAKURA1/OMALL.DAT'],
    'MINISAKU': ['/SAKURA1/OMALL.DAT'],
    'MSTAFF': ['/SAKURA1/OMALL.DAT'],
    'EXIT_W': ['/SAKURA'],
    'CAUTION': ['/SAKURA1/LOGO.SH2'],
    'TL_BG0': ['/SAKURA1/LOGO.SH2'],
    'TL_ROGO0': ['/SAKURA1/LOGO.SH2'],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pc-root', type=Path, required=True, help='extracted resource root containing SAKURA1')
    parser.add_argument('--disc', type=Path, action='append', required=True, help='prepared Saturn ISO, repeat for disc 2')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    wanted = {path.upper() for paths in SYSTEM_CANDIDATES.values() for path in paths}
    saturn_files = {}
    for number, iso in enumerate(args.disc, 1):
        with iso.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            for name, lba, length in files(data):
                if name.upper() not in wanted:
                    continue  # only hash the handful of candidate files; the ISO holds 1700+ entries
                if length > 64 * 1024 * 1024 or lba * 2048 + length > len(data):
                    raise ValueError(f'Invalid native resource extent for {name}')
                saturn_files.setdefault(name.upper(), []).append(dict(
                    disc=number, path=name, bytes=length,
                    sha256=hashlib.sha256(data[lba * 2048:lba * 2048 + length]).hexdigest(),
                ))

    system_dir = args.pc_root / 'SAKURA1' / 'SYSTEM'
    entries = []
    for file in sorted(system_dir.glob('*.SPR')):
        if file.stat().st_size > 64 * 1024 * 1024:
            raise ValueError('PC menu input exceeds budget')
        data = file.read_bytes()
        row = dict(id=file.stem, pc_path=file.relative_to(args.pc_root).as_posix(), bytes=len(data),
                   sha256=hashlib.sha256(data).hexdigest())
        try:
            row['images'] = inspect(data)
        except ValueError as error:
            row['error'] = str(error)
        candidates = SYSTEM_CANDIDATES.get(file.stem, [])
        row['saturn_candidates'] = [
            dict(saturn_path=path, found=[entry for entry in saturn_files.get(path.upper(), [])])
            for path in candidates
        ]
        entries.append(row)

    if not entries:
        raise ValueError('No menu SPR files found under SAKURA1/SYSTEM')

    report = dict(
        schema=1,
        scope='Saturn menu/HUD PC candidates for the HD mod; header inventory only; no import/mapping inferred',
        pc_files=len(entries),
        pc_image_entries=sum(len(row.get('images', [])) for row in entries),
        pc_header_errors=sum('error' in row for row in entries),
        named_without_candidate=sorted(row['id'] for row in entries if row['id'] not in SYSTEM_CANDIDATES),
        menus=entries,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"{report['pc_files']} PC menu files; {report['pc_image_entries']} nonempty images; "
          f"{len(entries) - len(report['named_without_candidate'])} with a candidate Saturn file")


if __name__ == '__main__':
    main()
