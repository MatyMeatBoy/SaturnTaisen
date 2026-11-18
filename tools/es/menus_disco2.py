"""Spanish menus for disc 2, derived from the disc-1 menu patches.

  python -X utf8 tools/es/menus_disco2.py     (needs `menus_es.py` already run for disc 1)

Disc 2 carries its own `SAKURA` program (data shifted by 0x138 bytes) and `LOGO.SH2` (title), so the
disc-1 offsets do not apply. For each file the changed ranges between the English disc-1 original and the
Spanish disc-1 result (builds/es-cap1/files) are located in the disc-2 file by their original bytes (with
context) and the same bytes are written there; absolute pointers (0x0600_4000 + file offset) inside a patched
range are moved by the same 0x138. Files byte-identical on both discs (ICATALL.DAT, OMALL.DAT, TITLE1.BIN,
LOAD.BIN, WKL01.BIN) reuse the disc-1 Spanish version. The 13 disc-2-only battle-bar files
(WKL12-20, WKL23-26) are redrawn with `menus_es.combate`. Output: builds/es-all/disc2/menus.
Inputs and outputs stay under SAKURA_OWNER_ROOT/local.
"""
import mmap
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _rutas import OWNER, ROOT as REPO, WORK  # noqa: E402
sys.path.insert(0, str(REPO / 'tools'))
from audit_sdk import files  # noqa: E402

CTX = 24
SHIFT = 0x138   # shift of /SAKURA data on disc 2 (also of the absolute pointers into the program image)
IDENTICAL = ('/SAKURA1/ICATALL.DAT', '/SAKURA1/OMALL.DAT', '/SAKURA1/TITLE1.BIN', '/SAKURA1/LOAD.BIN')
DISC2_WKL = [12, 13, 14, 15, 16, 17, 18, 19, 20, 23, 24, 25, 26]


def disc_files(disc):
    image = OWNER / f'local/prepared/disc{disc}/Track 01.iso'
    out = {}
    with image.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        for path, lba, size in files(iso):
            out[path.upper()] = bytes(iso[lba * 2048:lba * 2048 + size])
    return out


def ranges(a, b, gap=32):
    assert len(a) == len(b)
    out, start, last = [], None, None
    for i in range(len(a)):
        if a[i] != b[i]:
            if start is None:
                start = last = i
            elif i - last > gap:
                out.append((start, last + 1))
                start = i
            last = i
    if start is not None:
        out.append((start, last + 1))
    return out


def inside(word, program):
    return 0x06004000 <= word < 0x06004000 + len(program)


def relocate_pointers(a, es, b, s, e, new):
    """Range holding absolute pointers: accepted only if disc 2's original equals disc 1's once the
    pointers into the program image are moved by SHIFT."""
    lo, hi = (s // 4) * 4 - 8, (e + 3) // 4 * 4 + 8
    target = lo + SHIFT
    for i in range(0, hi - lo, 4):
        wa = struct.unpack_from('>I', a, lo + i)[0]
        wb = struct.unpack_from('>I', b, target + i)[0]
        if (wa + SHIFT if inside(wa, a) else wa) != wb:
            return None
    for i in range(lo, hi, 4):
        wn = struct.unpack_from('>I', es, i)[0]
        if wn != struct.unpack_from('>I', a, i)[0]:
            struct.pack_into('>I', new, i + SHIFT, wn + SHIFT if inside(wn, a) else wn)
    return target


def relocate(name, original1, spanish1, original2):
    new = bytearray(original2)
    resolved = failed = 0
    for s, e in ranges(original1, spanish1):
        old, repl = original1[s:e], spanish1[s:e]
        found = None
        for ctx in (CTX, 8, 0):
            pattern = original1[max(0, s - ctx):s] + old + original1[e:e + ctx]
            hits, at = [], original2.find(pattern)
            while at != -1 and len(hits) < 3:
                hits.append(at)
                at = original2.find(pattern, at + 1)
            if len(hits) == 1:
                found = hits[0] + min(ctx, s)
                break
            if hits:
                break
        if found is None and name == '/SAKURA' and relocate_pointers(original1, spanish1, original2, s, e, new):
            resolved += 1
            continue
        if found is None or bytes(new[found:found + len(old)]) != old:
            failed += 1
            print(f'  UNRESOLVED {name} {hex(s)}-{hex(e)} ({e - s} bytes)')
            continue
        new[found:found + len(old)] = repl
        resolved += 1
    print(f'{name}: {resolved} ranges moved to disc 2, {failed} unresolved')
    return bytes(new), failed


def battle_bars(out_dir):
    import fuente
    import menus_es
    from decodificar import Disc
    fuente.LEVELS = [1, 5, 9, 13]
    menus_es.WKL_STAGES = ['WKL%02d' % n for n in DISC2_WKL]
    menus_es.OUT = str(out_dir)
    stage_files = menus_es.Files(Disc(str(OWNER / 'local/prepared/disc2/Track 01.iso')))
    menus_es.combate(stage_files, [])
    stage_files.save()


def main():
    english = {1: disc_files(1), 2: disc_files(2)}
    spanish_dir = WORK / 'builds/es-cap1/files'
    out_dir = WORK / 'builds/es-all/disc2/menus'
    failed = 0
    for name in ('/SAKURA', '/SAKURA1/LOGO.SH2'):
        rel = name.lstrip('/')
        spanish1 = (spanish_dir / rel).read_bytes()
        data, bad = relocate(name, english[1][name], spanish1, english[2][name])
        failed += bad
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    for name in IDENTICAL:
        rel = name.lstrip('/')
        source = spanish_dir / rel
        if not source.is_file():
            continue
        if english[1][name] != english[2][name]:
            raise SystemExit(f'{name} differs between discs; port it explicitly')
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    wkl1 = spanish_dir / 'SAKURA2/WKL01.BIN'
    if wkl1.is_file() and english[1]['/SAKURA2/WKL01.BIN'] == english[2]['/SAKURA2/WKL01.BIN']:
        (out_dir / 'SAKURA2').mkdir(parents=True, exist_ok=True)
        (out_dir / 'SAKURA2/WKL01.BIN').write_bytes(wkl1.read_bytes())
    battle_bars(out_dir)
    if failed:
        raise SystemExit(f'{failed} unresolved ranges')
    print('disc 2 menus ready:', out_dir)


if __name__ == '__main__':
    main()
