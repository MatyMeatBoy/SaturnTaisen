"""Extract unique English texts for a chapter into loteNN.in.jsonl translation batches,
from the project's own dialogue catalogue (local/work/dialogue-catalog-worker/dialogue.jsonl,
not committed). Reused for chapter 1; generalised here so later chapters (2-10) don't need
a new one-off script each time.

  python lotes.py --tables 0201 0202 0203 0204 0205 0206 --out capitulo2/lotes

Markers of the form `NNNNTBL:idx` are not texts to translate: the engine resolves them to
another record's text at runtime (see docs/research/traduccion-espanol.md).
"""
import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path

from _rutas import WORK  # noqa: E402

CATALOG = WORK.parents[1] / 'work' / 'dialogue-catalog-worker' / 'dialogue.jsonl'
MARKER = re.compile(r'^\d{4}TBL:\d+\s*$')
TIPO_RANGES = [(0x2000, 0x3000, 'evento'), (0x4000, 0x5000, 'LIPS'), (0x9000, 0xa000, 'objeto'),
               (0xc000, 0xd000, 'mapa'), (0xd000, 0xe000, 'especial')]
BATCH = 330


def tipo_of(record_id: int) -> str:
    for lo, hi, name in TIPO_RANGES:
        if lo <= record_id < hi:
            return name
    return 'otro'


def extract(tables: list[str]) -> list[dict]:
    seen: 'OrderedDict[str, dict]' = OrderedDict()
    with CATALOG.open(encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            table = row['iso_path'].split('/')[-1][:4]
            if table not in tables:
                continue
            text = row['display_text']
            if MARKER.match(text) or text in seen:
                continue
            seen[text] = dict(id=f"{table}-{row['index']:04d}", tipo=tipo_of(row['record_id']), en=text)
    return list(seen.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tables', nargs='+', required=True, help='four-digit table ids, e.g. 0201 0202')
    parser.add_argument('--out', type=Path, required=True, help='output dir for loteNN.in.jsonl, under local/')
    args = parser.parse_args()
    items = extract(args.tables)
    args.out.mkdir(parents=True, exist_ok=True)
    n = 0
    for n, start in enumerate(range(0, len(items), BATCH), 1):
        chunk = items[start:start + BATCH]
        path = args.out / f'lote{n:02d}.in.jsonl'
        with path.open('w', encoding='utf-8') as f:
            for item in chunk:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f'{path}: {len(chunk)} textos')
    print(f'total: {len(items)} textos únicos en {n} lotes')


if __name__ == '__main__':
    main()
