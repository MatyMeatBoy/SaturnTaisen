"""Inventory and pairing of the tactical-mode resources of the PC edition (TS11): MAP, UNIT and ITEM.

Data only: names, sizes, hashes and statuses. No pixel is read, stored or written (the PC art is the owner's).
Sub-commands (each block is its own verifiable slice):

  python tools/tactical_pairing.py maps --pc ROOT --iso1 "local/prepared/disc1/Track 01.iso" \
      --iso2 "local/prepared/disc2/Track 01.iso" --out config/hd-tactical-map-pairs.json

  python tools/tactical_pairing.py units --pc ROOT --iso1 ... --iso2 ... --out config/hd-tactical-unit-inventory.json

ROOT is a folder holding the extracted PC `SAKURA1/...` and `SAKURA2/...` trees (SPR headers are parsed, never decoded).

maps: each Saturn `/SAKURA2/MAPnn.BIN` (13 on disc 1, 14 on disc 2) is paired with the PC `MAP/MAPnn/MAPnn.BIN` by
SHA-256 identity (the two editions ship the same terrain file), and the PC `MAPnn.TAB` text names the ground,
priority and animated SPR files of the map. Statuses: `paired` (identical BIN and a ground SPR present),
`paired-no-ground` (identical BIN, the TAB names no SPR that exists), `no-counterpart` (no PC BIN or different bytes).

units: inventory of the 27 Saturn `/SAKURA2/UNITnn.BIN` files (26 names; UNIT01 is on both discs) and the 291 PC `SAKURA2/UNIT/**.SPR`. The Saturn bank is an
offset table followed by data that no decoder in `tools/` reads, and the PC has per-character files, not per-stage
banks, so no content pairing is possible yet. Every item is recorded as `no-counterpart` with the reason; Saturn
files with identical bytes are grouped (`same_as`).

items: the 57 PC `SAKURA1/ITEM/*.SPR` pictures seen from the PC side. The Saturn `ITEMnn.BIN` pairs already exist
(`config/hd-item-map.json`, content signature from `match_hd_items.py`, and the eye review `config/hd-item-review.json`);
this view joins them: a PC picture is `paired` when at least one Saturn item is confirmed to it (review `confirmed`, or
tier `content` with no review row), `ambiguous` when it is only the best candidate of items the review marked `icon_only`
or `rejected`, and `no-counterpart` when no Saturn item ranks it first. The Saturn side is summarised the same way.
"""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

SCHEMA = 1
BITS = (4, 4, 8, 8, 8, 16, 24, 32)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def fnv1a64(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return '%016X' % value


def spr_images(data):
    """List (width, height, format) of every image of a SPRED file from its table. Never decodes pixels."""
    if len(data) < 32 or data[:10] != b'SEGA SPRED':
        raise ValueError('unknown SPRED signature')
    long_ = lambda at: struct.unpack_from('>I', data, at)[0]
    word = lambda at: struct.unpack_from('>H', data, at)[0]
    bitmaps = None
    at = 16
    while at + 16 <= len(data):
        offset, size, index = long_(at), long_(at + 4), long_(at + 8)
        if not offset or not size:
            break
        if offset > len(data) or size > len(data) - offset or index >= 14:
            raise ValueError('invalid chunk extent')
        if index == 2:
            bitmaps = (offset, size)
        at += 16
        if at >= offset:
            break
    if not bitmaps or bitmaps[1] < 16:
        raise ValueError('missing image table')
    count = word(bitmaps[0])
    if bitmaps[0] + 16 + count * 16 > len(data):
        raise ValueError('image table exceeds file')
    images = []
    for n in range(count):
        p = bitmaps[0] + 16 + n * 16
        w, h, fmt = word(p), word(p + 2), word(p + 4)
        if w and h and long_(p + 12):
            images.append((w, h, fmt))
    return images


def parse_tab(text):
    """Parse a MAPnn.TAB: lines 'Role:<tab>Kind:<tab>file'. Commented lines ('#') are ignored.

    Returns a list of (role, kind, file) with the file in lowercase, forward slashes and no leading '..\\'."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = re.match(r'^(\w+):\s*(\w+):\s*(\S+)\s*$', line)
        if match:
            rows.append((match[1], match[2], match[3].replace('\\', '/').lower()))
    return rows


def tab_ground(rows):
    """The ground file: role Ground, else the first UnderGround File that is a `_a` picture (MAP12 style)."""
    for role in ('Ground', 'UnderGround'):
        for r, kind, name in rows:
            if r == role and kind == 'File' and name.endswith('.spr'):
                return name, role
    return None, None


def find_ci(folder, relative):
    """Resolve `relative` (lowercase, may contain ../) against `folder` ignoring case; None when absent."""
    path = folder
    for part in relative.split('/'):
        if part == '..':
            path = path.parent
            continue
        if part == '.':
            continue
        match = next((c for c in path.iterdir() if c.name.lower() == part), None) if path.is_dir() else None
        if match is None:
            return None
        path = match
    return path


def pair_map(saturn_key, saturn_data, pc_root):
    """One row for a Saturn MAP BIN: `saturn_key` like '1:/SAKURA2/MAP01.BIN' and its bytes."""
    name = saturn_key.split('/')[-1]
    stem = name[:-4]
    row = {'saturn': saturn_key, 'size': len(saturn_data), 'sha256': sha256(saturn_data)}
    folder = Path(pc_root) / 'SAKURA2' / 'MAP' / stem
    pc_bin = find_ci(folder, stem.lower() + '.bin') if folder.is_dir() else None
    if pc_bin is None:
        row.update(status='no-counterpart', reason='no PC MAP folder or BIN of this name')
        return row
    raw = pc_bin.read_bytes()
    row['pc_bin'] = f'SAKURA2/MAP/{stem}/{pc_bin.name}'
    row['pc_bin_sha256'] = sha256(raw)
    row['identical'] = raw == saturn_data
    if not row['identical']:
        row.update(status='no-counterpart', reason='PC BIN bytes differ from the Saturn BIN')
        return row
    tab = find_ci(folder, stem.lower() + '.tab')
    rows = parse_tab(tab.read_text(encoding='latin1')) if tab else []
    ground, role = tab_ground(rows)
    row['tab_roles'] = sorted({f'{r}:{k}' for r, k, _ in rows})
    path = find_ci(folder, ground) if ground else None
    if path is None:
        row.update(status='paired-no-ground', reason='the TAB names no ground SPR that exists in the PC folder')
        return row
    raw = path.read_bytes()
    images = spr_images(raw)
    row.update(status='paired', ground_role=role, ground_layout='single' if len(images) == 1 else 'tiles',
               pc_ground=path.resolve().relative_to(Path(pc_root).resolve()).as_posix(),
               ground_size=len(raw), ground_sha256=sha256(raw), ground_fnv=fnv1a64(raw),
               ground_image_count=len(images), ground_image0_size=list(images[0][:2]) if images else None,
               ground_image_sizes=sorted({'%dx%d' % i[:2] for i in images}))
    other = path.parent.resolve() != folder.resolve()
    if other:
        row['ground_shared_with'] = path.parent.name
    return row


def runtime_status(coverage):
    """Map '1:/SAKURA2/MAPnn.BIN' -> coverage status for the maps the register already lists."""
    result = {}
    for chapter in coverage.get('chapters', []):
        for key, entry in chapter['resources'].get('tactical-maps', {}).items():
            result[key] = entry['status']
    for key, entry in coverage.get('unassigned', {}).get('tactical-maps', {}).items():
        result.setdefault(key, entry['status'])
    return result


def build_maps(saturn_maps, pc_root, coverage=None):
    rows = [pair_map(key, data, pc_root) for key, data in sorted(saturn_maps.items())]
    if coverage is not None:
        status = runtime_status(coverage)
        for row in rows:
            row['register'] = status.get(row['saturn'], 'unknown')
    counts = {}
    for row in rows:
        counts[row['status']] = counts.get(row['status'], 0) + 1
    paired = {row['pc_bin'] for row in rows if row['status'] == 'paired'}
    stems = sorted(p.name for p in (Path(pc_root) / 'SAKURA2' / 'MAP').iterdir() if p.is_dir()) \
        if (Path(pc_root) / 'SAKURA2' / 'MAP').is_dir() else []
    pc_only = [s for s in stems if f'SAKURA2/MAP/{s}/{s}.BIN' not in paired and
               not any(r['saturn'].endswith(f'/{s}.BIN') for r in rows)]
    return {'schema': SCHEMA, 'scope': 'Saturn /SAKURA2/MAPnn.BIN to the PC MAP folders by byte identity; data only.',
            'summary': counts, 'pc_maps_without_saturn_file': pc_only, 'maps': rows}


def read_saturn_maps(isos):
    import decode_saturn_bg as saturn
    out = {}
    for disc, path in isos:
        iso = saturn.Iso(path)
        for name, extent in iso.files('SAKURA2'):
            if re.fullmatch(r'MAP\d+\.BIN', name):
                out[f'{disc}:/SAKURA2/{name}'] = iso.content(extent)
    return out


def read_saturn_units(isos):
    import decode_saturn_bg as saturn
    out = {}
    for disc, path in isos:
        iso = saturn.Iso(path)
        for name, extent in iso.files('SAKURA2'):
            if re.fullmatch(r'UNIT\d+\.BIN', name):
                out[f'{disc}:/SAKURA2/{name}'] = iso.content(extent)
    return out


def saturn_unit_rows(saturn_units):
    rows, first = [], {}
    for key, data in sorted(saturn_units.items()):
        digest = sha256(data)
        row = {'saturn': key, 'size': len(data), 'sha256': digest,
               'first_word': struct.unpack_from('>I', data, 0)[0] if len(data) >= 4 else None,
               'status': 'no-counterpart',
               'reason': 'Saturn unit bank is an offset table plus compressed data with no decoder; the PC has per-character files'}
        if digest in first:
            row['same_as'] = first[digest]
        else:
            first[digest] = key
        rows.append(row)
    return rows


def pc_unit_rows(pc_root):
    root = Path(pc_root)
    rows = []
    for path in sorted((root / 'SAKURA2' / 'UNIT').rglob('*')):
        if not path.is_file() or path.suffix.lower() != '.spr':
            continue
        raw = path.read_bytes()
        relative = path.relative_to(root).as_posix()
        parts = relative.split('/')
        row = {'pc': relative, 'group': '/'.join(parts[2:-1]) or '(root)',
               'size': len(raw), 'sha256': sha256(raw), 'fnv': fnv1a64(raw)}
        try:
            images = spr_images(raw)
            row.update(images=len(images), image_sizes=sorted({'%dx%d' % i[:2] for i in images}))
        except ValueError as error:
            row.update(images=None, error=str(error))
        row.update(status='no-counterpart', reason='no decoded Saturn unit frames to compare with')
        rows.append(row)
    return rows


def build_units(saturn_units, pc_root):
    saturn_rows, pc_rows = saturn_unit_rows(saturn_units), pc_unit_rows(pc_root)
    groups = {}
    for row in pc_rows:
        groups[row['group']] = groups.get(row['group'], 0) + 1
    return {'schema': SCHEMA, 'scope': 'Saturn UNITnn.BIN and PC UNIT SPR inventory; no pairing established; data only.',
            'summary': {'saturn_files': len(saturn_rows),
                        'saturn_distinct': len({r['sha256'] for r in saturn_rows}),
                        'pc_files': len(pc_rows), 'pc_groups': dict(sorted(groups.items())),
                        'paired': 0, 'ambiguous': 0, 'no-counterpart': len(saturn_rows) + len(pc_rows)},
            'saturn_units': saturn_rows, 'pc_units': pc_rows}


def item_verdicts(item_map, review):
    """Saturn item file -> (pc_file, verdict) with verdict confirmed | icon_only | rejected | candidate."""
    reviewed = {p['saturn_file']: p for p in review['pairs']}
    result = {}
    for pair in item_map['pairs']:
        row = reviewed.get(pair['saturn_file'])
        if row:
            result[pair['saturn_file']] = (row['pc_file'], row['verdict'])
        elif pair['tier'] == 'content':
            result[pair['saturn_file']] = (pair['pc_file'], 'confirmed')
        else:
            result[pair['saturn_file']] = (pair['pc_file'], 'candidate')
    return result


def build_items(item_map, review, pc_root):
    verdicts = item_verdicts(item_map, review)
    by_pc = {}
    for saturn, (pc, verdict) in sorted(verdicts.items()):
        by_pc.setdefault(pc, []).append((saturn, verdict))
    rows = []
    for path in sorted((Path(pc_root) / 'SAKURA1' / 'ITEM').glob('*.SPR')):
        raw = path.read_bytes()
        relative = path.relative_to(pc_root).as_posix()
        images = spr_images(raw)
        refs = by_pc.get(relative, [])
        confirmed = [s for s, v in refs if v == 'confirmed']
        row = {'pc': relative, 'size': len(raw), 'sha256': sha256(raw), 'images': len(images),
               'image_sizes': sorted({'%dx%d' % i[:2] for i in images}),
               'saturn_confirmed': confirmed, 'saturn_other': [f'{s}:{v}' for s, v in refs if v != 'confirmed']}
        if confirmed:
            row['status'] = 'paired'
        elif refs:
            row.update(status='ambiguous', reason='only the best candidate of Saturn items the review did not confirm')
        else:
            row.update(status='no-counterpart', reason='no Saturn ITEM ranks this picture first')
        rows.append(row)
    saturn = [{'saturn': s, 'pc': pc, 'verdict': v} for s, (pc, v) in sorted(verdicts.items())]
    count = lambda items, key: {k: sum(1 for i in items if i[key] == k) for k in sorted({i[key] for i in items})}
    return {'schema': SCHEMA, 'scope': 'PC SAKURA1/ITEM pictures joined with the Saturn item pairs and review; data only.',
            'summary': {'pc': count(rows, 'status'), 'saturn': count(saturn, 'verdict')},
            'pc_items': rows, 'saturn_items': saturn}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    maps = sub.add_parser('maps')
    maps.add_argument('--pc', type=Path, required=True)
    maps.add_argument('--iso1', required=True)
    maps.add_argument('--iso2', required=True)
    maps.add_argument('--coverage', type=Path, default=Path(__file__).resolve().parent.parent / 'config/hd-chapter-coverage.json')
    maps.add_argument('--out', type=Path, required=True)
    units = sub.add_parser('units')
    units.add_argument('--pc', type=Path, required=True)
    units.add_argument('--iso1', required=True)
    units.add_argument('--iso2', required=True)
    units.add_argument('--out', type=Path, required=True)
    items = sub.add_parser('items')
    items.add_argument('--pc', type=Path, required=True)
    config_dir = Path(__file__).resolve().parent.parent / 'config'
    items.add_argument('--map', type=Path, default=config_dir / 'hd-item-map.json')
    items.add_argument('--review', type=Path, default=config_dir / 'hd-item-review.json')
    items.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    if args.command == 'maps':
        coverage = json.loads(args.coverage.read_text(encoding='utf-8')) if args.coverage.exists() else None
        result = build_maps(read_saturn_maps([(1, args.iso1), (2, args.iso2)]), args.pc, coverage)
        args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
        print(result['summary'], 'pc-only', result['pc_maps_without_saturn_file'])
    elif args.command == 'units':
        result = build_units(read_saturn_units([(1, args.iso1), (2, args.iso2)]), args.pc)
        args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
        print(result['summary'])
    elif args.command == 'items':
        result = build_items(json.loads(args.map.read_text(encoding='utf-8')),
                             json.loads(args.review.read_text(encoding='utf-8')), args.pc)
        args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + chr(10), encoding='utf-8', newline=chr(10))
        print(result['summary'])


if __name__ == '__main__':
    main()
