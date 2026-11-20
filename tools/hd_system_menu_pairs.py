#!/usr/bin/env python3
"""THD21: pair the Saturn menu textures (VDP1 sprites of saved menu states) with the PC SYSTEM pictures by content.

Offline, read-only, data only (names, sizes, hashes, scores; no pixels are written anywhere).
  python tools/hd_system_menu_pairs.py --pc local/work/pc-cab/out-system --states NAME=STATE [...] --out config/hd-system-menu-pairs.json
Saturn side: every active VDP1 command of each Sakura v9 state is decoded with the CRAM bank it points at (index 0
transparent), unique by (texture FNV, palette FNV, size) like tools/menu_state_probe.py. PC side: every image of every
SAKURA1/SYSTEM/**/*.SPR (tools/decode_spred.py). Both go on mid-grey and are compared by a 32x32 luminance signature and a
32x32 gradient signature (as tools/match_hd_items.py); the score is the lower of the two correlations.
Tiers: `paired` (score >= 0.90, runner-up at least 0.05 lower, aspect within 30 %), `ambiguous` (best >= 0.75 but not firm),
`no-counterpart` (with a reason). A group is `connectable_by_table` when the pair is firm and the Saturn key (texture FNV +
palette FNV) is a single stable texture, like FONT_CSL (patch 0093) and the object cards (0090/0147).
"""
import argparse, hashlib, json, pathlib, struct, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from PIL import Image  # noqa: E402

SIG = (32, 32)
FIRM, FLOOR, MARGIN, ASPECT = 0.90, 0.75, 0.05, 0.30
BPP = {0: 4, 1: 4, 2: 8, 3: 8, 4: 8, 5: 16}

# Decisions and reasons no content measurement can change (docs/research/pc-asset-census.md, T110, menu-state-routes.md).
KEEP_NATIVE = {'R_HARI': 'keep native by decision (T110)', 'SHADE_WB': 'keep native by decision (T110)',
               'SHADE_WA': 'keep native by decision (T110)', 'OP_WIN': 'keep native by decision (T110)',
               'HARI': 'keep native by decision (T110), same family as R_HARI',
               'LIPSBARX': 'cursor strip of the shared window family; keep native with the frame',
               'LIPSBARY': 'cursor strip of the shared window family; keep native with the frame',
               'LIPSCUR': 'cursor of the shared window family; keep native with the frame'}
NO_NATIVE = {'SEGALOGO': 'PC boot logo; the Saturn cold boot of this disc never draws it',
             'REDLOGO': 'PC boot logo; the Saturn cold boot of this disc never draws it',
             'CAUTION': 'PC warning screen with baked Japanese text; no Saturn counterpart in the boot',
             'TL_BG0': 'PC title art; the Saturn title is VDP2 NBG3 plus logo sprites',
             'TL_ROGO0': 'PC title logo with baked Japanese lettering', 'TITLE': 'PC title with baked Japanese lettering',
             'NOWLOAD': 'Saturn LOADING screen is VDP2-only: no VDP1 texture to key',
             'KARAOKE': 'extra menu, not reachable without the unlocked backup', 'OMKMOV_W': 'extra menu, same',
             'OMKSND_W': 'extra menu, same', 'MINISAKU': 'extra menu, same', 'MSTAFF': 'extra menu, same',
             'JYOUKI': 'steam effect, not reached in a menu state'}

# PC images already wired by a shipped patch (docs/research/pc-menu-hud-inventory.md, TW5 table); a firm pair here
# is a confirmation of that patch, not new work.
INTEGRATED = {('SISTEM', 1): '0206', ('SISTEM', 4): '0206', ('SISTEM', 2): '0213', ('SISTEM', 5): '0213',
              ('SISTEM', 12): '0209', ('SISTEM', 11): '0205', ('SISTEM', 14): '0205', ('SISTEM', 8): '0150',
              ('SISTEM', 9): '0150', ('OPTION', 1): '0209', ('FONT_CSL', 0): '0093', ('FONT_CSL', 1): '0093'}


def integrated_patch(pc_file, index):
    return INTEGRATED.get((pathlib.PurePosixPath(pc_file).stem, index))


def fnv(data):
    h = 0xcbf29ce484222325
    for b in data:
        h = ((h ^ b) * 0x100000001b3) & 0xffffffffffffffff
    return '%016X' % h


def _centre(values):
    mean = sum(values) / len(values)
    c = [v - mean for v in values]
    norm = sum(v * v for v in c) ** 0.5
    return [v / norm for v in c] if norm else [0.0] * len(c)


def signatures(image):
    """(luminance, gradient) signatures of an RGBA picture composed on mid-grey."""
    rgba = image.convert('RGBA')
    grey = Image.new('RGB', rgba.size, (128, 128, 128))
    grey.paste(rgba, mask=rgba.split()[3])
    values = list(grey.convert('L').resize(SIG, Image.BILINEAR).tobytes())
    w, h = SIG
    grad = []
    for y in range(h):
        for x in range(w):
            gx = values[y * w + min(x + 1, w - 1)] - values[y * w + x]
            gy = values[min(y + 1, h - 1) * w + x] - values[y * w + x]
            grad.append((gx * gx + gy * gy) ** 0.5)
    return _centre(values), _centre(grad)


def corr(a, b):
    return sum(x * y for x, y in zip(a, b))


def score(a, b):
    return min(corr(a[0], b[0]), corr(a[1], b[1]))


def aspect_ok(sa, sb):
    ra, rb = sa[0] / sa[1], sb[0] / sb[1]
    return abs(ra - rb) / max(ra, rb) <= ASPECT


def pc_images(root):
    import decode_spred
    out = []
    for path in sorted(pathlib.Path(root).rglob('*.SPR')):
        if path.stem == 'KAO':  # portraits are a separate shard (THD01-THD20)
            continue
        raw = path.read_bytes()
        rel = path.relative_to(root).as_posix()
        try:
            images = decode_spred.decode(raw)
        except Exception as exc:  # a file the decoder refuses is listed, not hidden
            out.append({'file': rel, 'id': path.stem, 'error': str(exc)[:80]})
            continue
        for index, img in images:
            out.append({'file': rel, 'id': path.stem, 'index': index, 'size': list(img.size),
                        'sha256': hashlib.sha256(raw).hexdigest(), 'sig': signatures(img)})
    return out


def saturn_textures(states):
    from menu_state_probe import load
    from audit_portrait_coverage import active_commands
    seen = {}
    for name, path in states:
        vectors, _ = load(path)
        vram, cram = vectors[3], vectors[7]
        for c in active_commands(vram):
            if c[0] & 15 not in (0, 1, 2, 4, 5, 6):
                continue
            bpp = BPP.get((c[2] >> 3) & 7, 4)
            if bpp == 16:
                continue
            w, h = ((c[5] >> 8) & 0x3f) * 8, c[5] & 255
            if not w or not h:
                continue
            raw = vram[c[4] * 8:c[4] * 8 + w * h * bpp // 8]
            base = (c[3] & 0x7ff) * 2
            pal = cram[base:base + (512 if bpp == 8 else 32)]
            key = (fnv(raw), fnv(pal), w, h)
            if key in seen:
                seen[key]['states'].add(name)
                seen[key]['commands'] += 1
                continue
            rgb = []
            for i in range(len(pal) // 2):
                v = struct.unpack_from('>H', pal, i * 2)[0]
                rgb.append(((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, ((v >> 10) & 31) * 255 // 31))
            img = Image.new('RGBA', (w, h))
            px = img.load()
            for i in range(w * h):
                v = raw[i] if bpp == 8 else (raw[i // 2] >> (4 if i % 2 == 0 else 0)) & 15
                px[i % w, i // w] = (0, 0, 0, 0) if v == 0 else rgb[v % len(rgb)] + (255,)
            seen[key] = {'texture_fnv': key[0], 'palette_fnv': key[1], 'size': [w, h], 'sig': signatures(img),
                         'states': {name}, 'commands': 1, 'opaque': 1 if img.getchannel('A').getbbox() else 0}
    return list(seen.values())


def _strip(s):
    return {'texture_fnv': s['texture_fnv'], 'palette_fnv': s['palette_fnv'], 'size': s['size'],
            'states': sorted(s['states']), 'commands': s['commands']}


def pair(saturn, pcs):
    """Rank every PC image for every Saturn texture; pure function over signatures (unit-tested)."""
    rows = []
    usable = [p for p in pcs if 'sig' in p]
    for s in saturn:
        if s.get('opaque', 1) == 0:
            rows.append({**_strip(s), 'tier': 'no-counterpart', 'reason': 'fully transparent texture'})
            continue
        ranked = sorted(((score(s['sig'], p['sig']), p) for p in usable if aspect_ok(s['size'], p['size'])),
                        key=lambda t: -t[0])
        if not ranked:
            rows.append({**_strip(s), 'tier': 'no-counterpart', 'reason': 'no PC image of a compatible aspect'})
            continue
        best = ranked[0]
        second = ranked[1][0] if len(ranked) > 1 else -1.0
        row = {**_strip(s), 'pc_file': best[1]['file'], 'pc_index': best[1]['index'], 'pc_size': best[1]['size'],
               'pc_sha256': best[1]['sha256'],
               'scale': [round(best[1]['size'][0] / s['size'][0], 3), round(best[1]['size'][1] / s['size'][1], 3)], 'score': round(best[0], 3), 'runner_up_score': round(second, 3),
               'runner_up': '%s#%d' % (ranked[1][1]['file'], ranked[1][1]['index']) if len(ranked) > 1 else None}
        if best[0] >= FIRM and best[0] - second >= MARGIN:
            row['tier'] = 'paired'
        elif best[0] >= FLOOR:
            row['tier'] = 'ambiguous'
        else:
            row['tier'] = 'no-counterpart'
            row['reason'] = 'best score below %.2f (new PC art, baked Japanese text or a tile of a composite)' % FLOOR
        rows.append(row)
    return rows


def classify_pc(pcs, rows):
    paired = {(r['pc_file'], r['pc_index']) for r in rows if r['tier'] == 'paired'}
    amb = {(r['pc_file'], r['pc_index']) for r in rows if r['tier'] == 'ambiguous'}
    out = []
    for p in pcs:
        if 'sig' not in p:
            out.append({'file': p['file'], 'tier': 'undecodable', 'reason': p['error']})
            continue
        key = (p['file'], p['index'])
        row = {'file': p['file'], 'index': p['index'], 'size': p['size'], 'sha256': p['sha256']}
        if integrated_patch(*key):
            row['integrated_by'] = integrated_patch(*key)
        if key in paired:
            row['tier'] = 'paired'
        elif key in amb:
            row['tier'] = 'ambiguous'
        else:
            row['tier'] = 'no-counterpart'
            row['reason'] = KEEP_NATIVE.get(p['id']) or NO_NATIVE.get(p['id']) or \
                'no Saturn texture of the reached menu states matches (new PC art, baked Japanese text, or screen not reached)'
        out.append(row)
    return out


def groups(rows):
    """Per PC file: the firm pairs; connectable when each Saturn key is one texture with one palette fingerprint."""
    g = {}
    for r in rows:
        if r['tier'] == 'paired':
            g.setdefault(r['pc_file'], []).append({'texture_fnv': r['texture_fnv'], 'palette_fnv': r['palette_fnv'],
                                                   'size': r['size'], 'pc_index': r['pc_index'], 'score': r['score']})
    out = {}
    for f, v in sorted(g.items()):
        for row in v:
            row['already_integrated_by'] = integrated_patch(f, row['pc_index'])
        new = [row for row in v if not row['already_integrated_by']]
        out[f] = {'rows': v, 'connectable_by_table': bool(new), 'new_rows': len(new)}
    return out


def tally(xs):
    return {t: sum(1 for x in xs if x['tier'] == t) for t in ('paired', 'ambiguous', 'no-counterpart', 'undecodable')}


def build(pcs, sat):
    rows = pair(sat, pcs)
    pcrows = classify_pc(pcs, rows)
    return {'schema': 1,
            'scope': 'THD21 Saturn menu textures (VDP1, saved menu states) to PC SYSTEM images by content; data only, no pixels.',
            'thresholds': {'firm': FIRM, 'margin': MARGIN, 'floor': FLOOR, 'aspect': ASPECT},
            'summary': {'saturn_textures': len(rows), 'saturn': tally(rows), 'pc_images': len(pcrows), 'pc': tally(pcrows)},
            'saturn': sorted(rows, key=lambda r: (r['tier'], -r.get('score', 0), r['texture_fnv'])),
            'pc': pcrows, 'groups': groups(rows)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pc', type=pathlib.Path, required=True)
    ap.add_argument('--states', nargs='+', required=True, help='NAME=PATH')
    ap.add_argument('--out', type=pathlib.Path, required=True)
    a = ap.parse_args()
    doc = build(pc_images(a.pc), saturn_textures([s.split('=', 1) for s in a.states]))
    a.out.write_text(json.dumps(doc, indent=1) + '\n', encoding='utf-8')
    print(doc['summary'])


if __name__ == '__main__':
    main()
