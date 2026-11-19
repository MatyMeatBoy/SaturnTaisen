"""Check that Spanish TITLE1..10.BIN cards keep what the runtime recognises them by (T107).

The 16:9 widening (patch0071) and the card detection use the FNV-1a 64 of the card's palette bytes. A repainted
card (portadas_es.py or the owner's painted art) is recognised, and widened, only if its size, palette and cell
table are those of the English card. Usage:

  python -X utf8 tools/es/verificar_portadas.py DIR   # DIR/SAKURA1/TITLEn.BIN (or DIR/TITLEn.BIN)

Reads the English cards from local/prepared/disc1/Track 01.iso. Exit status 1 on any difference.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import decode_saturn_bg as s  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CELLS_AT = 512 + 4480  # picture cells start; everything before is palette + u32 cell table


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    base = Path(sys.argv[1])
    iso = s.Iso(str(ROOT / 'local/prepared/disc1/Track 01.iso'))
    files = dict(iso.files('SAKURA1'))
    bad = 0
    for n in range(1, 11):
        english = iso.content(files['TITLE%d.BIN' % n])
        path = base / 'SAKURA1' / ('TITLE%d.BIN' % n)
        path = path if path.exists() else base / ('TITLE%d.BIN' % n)
        spanish = path.read_bytes()
        problems = []
        if len(spanish) != len(english):
            problems.append('size %d != %d' % (len(spanish), len(english)))
        elif spanish[:CELLS_AT] != english[:CELLS_AT]:
            problems.append('palette or cell table differ')
        elif s.palette_fingerprint(spanish) != s.palette_fingerprint(english):
            problems.append('fingerprint differs')
        print('TITLE%d %016X %s' % (n, s.palette_fingerprint(english), 'OK' if not problems else '; '.join(problems)))
        bad += bool(problems)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
