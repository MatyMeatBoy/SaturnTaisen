"""One table for the tactical map grounds (TW6b): offline Saturn and PC ground keys and candidate geometry.

Data only: names, sizes, hashes, statuses. No pixel is read or stored.

The runtime keys a ground by the FNV-1a of the first 8,192 pattern-name bytes of VDP2 source 4 (page 0x40000), the
`mapSignature` of `port/tactical_ground.h`. That page is not a free number: the game expands the ground name table of the
MAPnn.BIN into VDP2 RAM, so the same signature can be computed from the BIN alone (no disc run needed):

  slot table   16 big-endian (offset, size) pairs at the start of the BIN (slot 0 is empty);
  slot 1       the cells of the first layer: its size / 32 is the character number where the ground cells start;
  slot 5       the ground name table, 128 x 128 big-endian 16-bit names;
  page word    0x00600000 + name + slot1_size / 32 for the 64 columns x 32 rows at the top left, 4 bytes each, big-endian.

Checked against the five signatures recorded from live runs (MAP01, MAP02, MAP04, MAP05, MAP06: all equal). MAP21 does not
follow the formula (its layout is its own) and keeps its recorded signature. Derived keys identify candidate
grounds. Camera registration, placement and foreground composition require a live replay.

Commands (see docs/research/tactical-ground-table.md):

  python tools/gen_tactical_ground_table.py --derive --pc <PC SAKURA2 root> --iso1 "local/prepared/disc1/Track 01.iso" \
      --iso2 "local/prepared/disc2/Track 01.iso" --inc local/work/tactical_ground_table.inc
  python tools/gen_tactical_ground_table.py --check    # offline: JSON against config/hd-tactical-map-pairs.json
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAIRS = ROOT / 'config/hd-tactical-map-pairs.json'
TABLE = ROOT / 'config/hd-tactical-ground-table.json'
SCHEMA = 1
PAGE = 0x40000
CHAR_BYTES = 32
NL = chr(10)
FNV_OFFSET, FNV_PRIME = 14695981039346656037, 1099511628211

# Entries written by hand in port/tactical_ground.h (patches 0102, 0138, 0139, 0140, 0153, 0097, 0214, 0240, 0242 and the MAP12/13/15 live-ground patches); the table keeps them as
# `hd` and the tests check the formula against them. MAP21's recorded signature is not derivable (see the module doc).
HAND = {
    'MAP01': ('1CAF3218B4B0F9F0', True),
    'MAP02': ('25FF56EB6965E424', True),
    'MAP04': ('451ACDDB5522070E', True),
    'MAP05': ('A18A5122F7C18729', True),
    'MAP06': ('B533F608A5E864D1', True),
    'MAP12': ('334C1BC64DDC4CEC', True),
    'MAP13': ('62C7F53B0136508A', True),
    'MAP14': ('6CA2B0FED140A513', True),
    'MAP15': ('4EF5A9A4BBA061C9', True),
    'MAP16': ('388594B7DBCB32C6', True),
    'MAP21': ('446FB372F79EDD04', False),
}
# Maps kept native after a live comparison (docs/research/tactical-pairing.md#live-map10-and-map19-ground-review).
NATIVE = {
    'MAP10': 'The PC facades and terrace need different offsets and the roof has a keyed span with another boundary; '
             'a single world sampler would misplace part of the foreground. Keep the native ground.',
    'MAP19': 'The PC lamps and rails sit differently from the Saturn drawing at the witnessed camera. Keep the native ground.',
}
# Tile grids the placement assembler of patch 0140/0153 draws (square tiles on the 2048 x 2048 plane).
PLANE = 2048


def fnv1a64(data):
    value = FNV_OFFSET
    for byte in data:
        value = ((value ^ byte) * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
    return value


def slot_table(data):
    if len(data) < 128:
        raise ValueError('MAP BIN shorter than its slot table')
    words = struct.unpack_from('>32I', data, 0)
    slots = [(words[i], words[i + 1]) for i in range(0, 32, 2)]
    for offset, size in slots:
        if offset > len(data) or size > len(data) - offset:
            raise ValueError('slot extent outside the file')
    return slots


def ground_signature(data):
    """FNV-1a of the first 8,192 bytes of the VDP2 source-4 name page the game builds from this BIN."""
    slots = slot_table(data)
    base_cells, base_size = slots[1][0], slots[1][1]
    names_at, names_size = slots[5]
    if names_size != 0x8000 or base_size % CHAR_BYTES:
        raise ValueError('not a ground name table')
    names = struct.unpack_from('>16384H', data, names_at)
    page = b''.join(struct.pack('>I', (0x00600000 + names[row * 128 + col] + base_size // CHAR_BYTES) & 0xFFFFFFFF)
                    for row in range(32) for col in range(64))
    return '%016X' % fnv1a64(page)


def spr_placements(data):
    """(count, max x, max y) of the SPRED placement chunk 13, or None."""
    word = lambda at: struct.unpack_from('>H', data, at)[0]
    dword = lambda at: struct.unpack_from('>I', data, at)[0]
    end = dword(16)
    for at in range(16, end, 16):
        offset, size, index = dword(at), dword(at + 4), dword(at + 8)
        if not offset and not size:
            break
        if index == 13:
            rows = [(word(p + 4), word(p + 6)) for p in range(offset + 16, offset + size, 16)]
            return word(offset), max(x for x, _ in rows), max(y for _, y in rows)
    return None


def stage_name(stem):
    return 'stage%s-hd-ground' % stem[3:]


def classify(pair, derived, plane=None):
    """Status and runtime geometry of one paired map. `plane` is the placement extent for tile grids."""
    stem = re.search(r'(MAP\d+)\.BIN$', pair['saturn'])[1]
    row = {'map': stem, 'saturn': [pair['saturn']], 'bin_sha256': pair['sha256'], 'signature': derived,
           'page': '0x%X' % PAGE, 'pc_ground': pair['pc_ground'], 'ground_size': pair['ground_size'],
           'ground_fnv': pair['ground_fnv'], 'ground_sha256': pair['ground_sha256'],
           'layout': pair['ground_layout'], 'images': pair['ground_image_sizes']}
    if stem in HAND:
        row.update(table='hand', status='hd', signature=HAND[stem][0], signature_derivable=HAND[stem][1],
                   derived_signature=derived)
        return row
    row['table'] = 'generated'
    if stem in NATIVE:
        row.update(status='native', reason=NATIVE[stem])
        return row
    if pair['ground_layout'] == 'single':
        width, height = pair['ground_image0_size']
        if width % 2 or height % 2:
            row.update(status='needs-assembler', reason='odd image size, no 2x world grid')
            return row
        row.update(status='candidate', world=[width // 2, height // 2], tile_px=0,
                   centre_layout=stage_name(stem))
        return row
    count, size = pair['ground_image_count'], pair['ground_image0_size']
    if len(pair['ground_image_sizes']) == 1 and size[0] == size[1] and count > 4 and plane == [PLANE, PLANE]:
        row.update(status='candidate', world=[PLANE // 2, PLANE // 2], tile_px=size[0],
                   centre_layout=stage_name(stem), plane=plane)
        return row
    row.update(status='needs-assembler',
               reason=('%d images of %s are not equal square tiles on the %d px plane: the placement assembler of patch 0140 '
                       'draws one tile size on a square plane, and these look like alternative images rather than tiles; '
                       'one image has to be chosen per scene before a sampler can use it' %
                       (count, ', '.join(pair['ground_image_sizes']), PLANE)))
    return row


def build(pairs, signatures, planes):
    """Merge Saturn rows that carry the same BIN (disc 1 and disc 2 MAP01) and classify every paired map."""
    by_hash = {}
    for pair in pairs['maps']:
        if pair.get('status') != 'paired':
            continue
        stem = re.search(r'(MAP\d+)\.BIN$', pair['saturn'])[1]
        if pair['sha256'] in by_hash:
            by_hash[pair['sha256']]['saturn'].append(pair['saturn'])
            continue
        by_hash[pair['sha256']] = classify(pair, signatures[stem], planes.get(stem))
    rows = sorted(by_hash.values(), key=lambda r: r['map'])
    seen = {}
    for row in rows:
        if row['signature'] in seen:
            raise ValueError('maps %s and %s share signature %s' % (seen[row['signature']], row['map'], row['signature']))
        seen[row['signature']] = row['map']
    counts = {}
    for row in rows:
        counts[row['status']] = counts.get(row['status'], 0) + 1
    return {'schema': SCHEMA,
            'scope': 'Tactical ground table: Saturn MAPnn.BIN to PC ground SPR and the runtime key. Data only.',
            'key': 'FNV-1a of the first 8192 name-page bytes of VDP2 source 4 at page 0x40000 (see tools/gen_tactical_ground_table.py)',
            'summary': counts, 'maps': rows}


def inc_text(table):
    lines = ['// Generated by tools/gen_tactical_ground_table.py from config/hd-tactical-ground-table.json. Do not edit.',
             '// path, bytes, asset FNV-1a, map signature, ground page, world width, world height, map end x, layout, tile size']
    for row in table['maps']:
        if row['table'] != 'generated' or row['status'] != 'candidate':
            continue
        lines.append('{"%s", %d, 0x%sull, 0x%sull, %s, %d, %d, %d, "%s", %d},' % (
            row['pc_ground'], row['ground_size'], row['ground_fnv'], row['signature'], row['page'],
            row['world'][0], row['world'][1], row['world'][0], row['centre_layout'], row['tile_px']))
    return '\n'.join(lines) + '\n'


def dump(path, text):
    path.write_text(text, encoding='utf-8', newline='\n')


def derive(args):
    sys.path.insert(0, str(ROOT / 'tools'))
    import tactical_pairing as tp
    pairs = json.loads(PAIRS.read_text(encoding='utf-8'))
    saturn = tp.read_saturn_maps([(1, args.iso1), (2, args.iso2)])
    signatures, planes = {}, {}
    for key, data in saturn.items():
        stem = re.search(r'(MAP\d+)\.BIN$', key)[1]
        try:
            signatures[stem] = ground_signature(data)
        except ValueError:
            signatures[stem] = None
    for pair in pairs['maps']:
        if pair.get('status') == 'paired' and pair['ground_layout'] == 'tiles':
            sprite = (args.pc / pair['pc_ground']).read_bytes()
            found = spr_placements(sprite)
            if found:
                tile = pair['ground_image0_size'][0]
                stem = re.search(r'(MAP\d+)\.BIN$', pair['saturn'])[1]
                planes[stem] = [found[1] + tile, found[2] + tile]
    missing = [k for k, v in signatures.items() if v is None]
    if missing:
        raise SystemExit('no derivable signature for %s' % missing)
    table = build(pairs, signatures, planes)
    dump(TABLE, json.dumps(table, indent=1, sort_keys=True) + '\n')
    if args.inc:
        dump(args.inc, inc_text(table))
    print(table['summary'])


def check(_):
    pairs = json.loads(PAIRS.read_text(encoding='utf-8'))
    table = json.loads(TABLE.read_text(encoding='utf-8'))
    problems = []
    by_saturn = {p['saturn']: p for p in pairs['maps'] if p.get('status') == 'paired'}
    listed = [s for row in table['maps'] for s in row['saturn']]
    if sorted(listed) != sorted(by_saturn):
        problems.append('table and pairs list different Saturn maps')
    for row in table['maps']:
        for saturn in row['saturn']:
            pair = by_saturn.get(saturn)
            if pair and (pair['sha256'] != row['bin_sha256'] or pair['ground_fnv'] != row['ground_fnv'] or
                         pair['ground_size'] != row['ground_size'] or pair['pc_ground'] != row['pc_ground']):
                problems.append('%s differs from the pairs file' % saturn)
    signatures = [row['signature'] for row in table['maps']]
    if len(set(signatures)) != len(signatures):
        problems.append('duplicate signatures')
    for problem in problems:
        print('FAIL', problem)
    if not problems:
        print('tactical ground table ok:', table['summary'])
    return 1 if problems else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--derive', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--pc', type=Path)
    parser.add_argument('--iso1')
    parser.add_argument('--iso2')
    parser.add_argument('--inc', type=Path, help='with --derive: export a preview of candidate entries')
    args = parser.parse_args(argv)
    if args.derive:
        if not (args.pc and args.iso1 and args.iso2):
            parser.error('--derive needs --pc, --iso1 and --iso2')
        derive(args)
        return 0
    return check(args)


if __name__ == '__main__':
    sys.exit(main())
