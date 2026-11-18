"""Validate a translated batch: python validar_lote.py loteNN

Reads loteNN.in.jsonl and loteNN.out.jsonl in capitulo1/lotes. Prints every problem;
exit status 0 only when every input id has exactly one valid Spanish text.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tablas import MAX_COLS, MAX_LINES, check, wrap  # noqa: E402

from _rutas import WORK  # noqa: E402
LOTES = WORK / 'capitulo1' / 'lotes'


def main(name: str) -> int:
    source = [json.loads(line) for line in (LOTES / f'{name}.in.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    out_path = LOTES / f'{name}.out.jsonl'
    done = {}
    problems = []
    if out_path.exists():
        for number, line in enumerate(out_path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                done.setdefault(row['id'], []).append(row['es'])
            except Exception as error:  # noqa: BLE001
                problems.append(f'line {number}: invalid JSON ({error})')
    for item in source:
        texts = done.get(item['id'])
        if not texts:
            problems.append(f"{item['id']}: missing")
            continue
        if len(texts) > 1:
            problems.append(f"{item['id']}: duplicated")
        text = texts[-1]
        lips = item['tipo'] == 'LIPS'
        if lips and len(text.split('\n')) != len(item['en'].split('\n')):
            problems.append(f"{item['id']}: LIPS needs {len(item['en'].split(chr(10)))} options, one per line")
        if not text.strip():
            problems.append(f"{item['id']}: empty")
        for issue in check(text, keep_lines=lips):
            problems.append(f"{item['id']}: {issue}  -> {' | '.join(wrap(text, lips))}")
    extra = set(done) - {item['id'] for item in source}
    problems += [f'{key}: not in this batch' for key in sorted(extra)]
    for problem in problems:
        print(problem)
    print(f'{name}: {len(source)} items, {sum(1 for i in source if i["id"] in done)} translated, {len(problems)} problems '
          f'(limit {MAX_LINES} lines x {MAX_COLS} chars after automatic wrapping)')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
