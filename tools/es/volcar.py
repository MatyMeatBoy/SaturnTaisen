"""Merge reviewed chapter-one batches into Spanish game tables and Codex's templates.

  python -X utf8 volcar_capitulo1.py            -> builds/es-cap1/files/SAKURA1/*TBL.BIN and SAKURA2/M01MES.BIN
  python -X utf8 volcar_capitulo1.py --plantillas  also fills target_es in local/work/spanish-translation
Every record whose English text has a reviewed translation is replaced; markers and unknown
records keep their English bytes. Fails on any text that does not fit or encode.
"""
import argparse
import json
import mmap
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _rutas import OWNER, ROOT, WORK  # noqa: E402
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'tools'))
import combate as es_mes  # noqa: E402
import tablas as es_tables  # noqa: E402
from audit_sdk import files  # noqa: E402
from export_dialogue_catalog import parse_table  # noqa: E402

TABLES = ('0100', '0101', '0102', '0103', '0108', '0109')


def quotes(text: str) -> str:
    """Straight double quotes become Spanish «»."""
    count = [0]

    def swap(_):
        count[0] += 1
        return '«' if count[0] % 2 else '»'
    return re.sub('"', swap, text) if text.count('"') % 2 == 0 else text


def load_memory():
    memory, kinds = {}, {}
    for source in sorted((WORK / 'capitulo1/lotes').glob('lote*.in.jsonl')):
        out = source.with_name(source.name.replace('.in.', '.out.'))
        es = {}
        for line in out.read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                es[row['id']] = quotes(row['es'])
        for line in source.read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            if row['id'] not in es:
                raise SystemExit(f"{row['id']} has no translation")
            memory[(row['tipo'] == 'combate', row['en'])] = es[row['id']]
            kinds[row['en']] = row['tipo']
    return memory, kinds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plantillas', action='store_true')
    args = parser.parse_args()
    memory, kinds = load_memory()
    target = WORK / 'builds/es-cap1/files'
    if target.exists():
        shutil.rmtree(target)
    image = OWNER / 'local/prepared/disc1/Track 01.iso'
    report, problems, filled = {}, [], {}
    with image.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        extents = {path: (lba, size) for path, lba, size in files(iso)}

        def read(name):
            lba, size = extents[name]
            return bytes(iso[lba * 2048:lba * 2048 + size])

        for table in TABLES:
            name = f'/SAKURA1/{table}TBL.BIN'
            original = read(name)
            texts = {}
            for record in parse_table(original):
                es = memory.get((False, record.display_text))
                if es is None:
                    continue
                lips = kinds.get(record.display_text) == 'LIPS'
                for issue in es_tables.check(es, keep_lines=lips):
                    problems.append(f'{table}-{record.index}: {issue}')
                texts[record.index] = '\n'.join(es_tables.wrap(es, lips))
                filled[f'1:{name}:{record.record_id}:{record.index}'] = texts[record.index]
            data = es_tables.build_table(original, texts)
            if len(data) > es_tables.SAFE_TABLE_BYTES:
                problems.append(f'{table}: {len(data)} bytes exceeds the safe {es_tables.SAFE_TABLE_BYTES}')
            out = target / 'SAKURA1' / f'{table}TBL.BIN'
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            report[name] = dict(records=len(parse_table(original)), spanish=len(texts), bytes=len(data), english_bytes=len(original))

        name = '/SAKURA2/M01MES.BIN'
        original = read(name)
        _, _, records = es_mes.parse(original)
        texts = {}
        for record in records:
            english = es_mes.decode(record['words'])
            es = memory.get((True, english))
            if es is None or not english.strip():
                continue
            for issue in es_tables.check(es):
                problems.append(f'M01-{record["index"]}: {issue}')
            texts[record['index']] = '\n'.join(es_tables.wrap(es))
        data = es_mes.build(original, texts)
        out = target / 'SAKURA2' / 'M01MES.BIN'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        report[name] = dict(records=len(records), spanish=len(texts), bytes=len(data), english_bytes=len(original))

    for problem in problems:
        print(problem)
    print(json.dumps(report, indent=1))
    if problems:
        raise SystemExit(1)

    if args.plantillas:
        folder = OWNER / 'local/work/spanish-translation/tables/disc1/SAKURA1'
        backup = WORK / 'builds/plantillas-codex-originales'
        for table in TABLES:
            path = folder / f'{table}TBL.jsonl'
            if not (backup / path.name).exists():
                backup.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup / path.name)
            rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
            for row in rows:
                es = filled.get(row['record_key'])
                if es is not None:
                    row['target_es'] = es.replace('\n', '\r')
                    row['status'] = 'translated'
            path.write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n' for r in rows), encoding='utf-8')
        print('plantillas actualizadas; copia original en', backup)


if __name__ == '__main__':
    main()
