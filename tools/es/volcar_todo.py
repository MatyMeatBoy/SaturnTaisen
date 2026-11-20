"""Merge every reviewed chapter batch into Spanish game tables for a whole disc.

  python -X utf8 volcar_todo.py --disc 1     -> local/work/guion-es/builds/es-all/disc1/files/SAKURA*/...
  python -X utf8 volcar_todo.py --disc 2

Translations are looked up per chapter (the first two digits of the table id, as in the batch ids),
keyed by the English display text, so identical English in different chapters can differ.
Battle tables (M##MES.BIN) use the `combate` batches of the same chapter number (M01 -> chapter 1).
Records whose English text has no translation (markers, empty, unknown) keep their English bytes and
are reported. Fails on any text that does not fit or encode. Nothing here is meant for Git data-wise:
inputs and outputs live under SAKURA_OWNER_ROOT/local.
"""
import argparse
import json
import mmap
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _rutas import OWNER, ROOT, WORK  # noqa: E402
sys.path.insert(0, str(ROOT / 'tools'))
import combate as es_mes  # noqa: E402
import tablas as es_tables  # noqa: E402
from audit_sdk import files  # noqa: E402
from export_dialogue_catalog import parse_table  # noqa: E402

MARKER = re.compile(r'^\d{4}TBL:\d+\s*$')
IRIS_ADDRESS = re.compile(r'\bMon[ \n]Frère\b')


def restore_localized_terms(text: str) -> str:
    text = IRIS_ADDRESS.sub('Onii-chan', text)
    for original, localized in (
        ('Madame Youki', 'Dama demonio'),
        ('Señor Fiesta', 'Chico Fiesta'),
        ('¡Yo qué más da!', '¡Yo estoy bien!'),
    ):
        text = text.replace(original, localized)
    return text


def quotes(text: str) -> str:
    """Straight double quotes become Spanish «»."""
    count = [0]

    def swap(_):
        count[0] += 1
        return '«' if count[0] % 2 else '»'
    return re.sub('"', swap, text) if text.count('"') % 2 == 0 else text


def load_memory():
    """memory[chapter][(is_battle, english)] -> spanish; kinds[chapter][english] -> tipo."""
    memory, kinds = defaultdict(dict), defaultdict(dict)
    for folder in sorted(WORK.glob('capitulo*/lotes')):
        chapter = int(folder.parent.name[len('capitulo'):])
        for source in sorted(folder.glob('lote??.in.jsonl')):
            out = source.with_name(source.name.replace('.in.', '.out.'))
            if not out.is_file():
                print(f'AVISO: {source.parent.parent.name}/{source.name} sin traducción; se omite')
                continue
            es = {}
            for line in out.read_text(encoding='utf-8').splitlines():
                if line.strip():
                    row = json.loads(line)
                    es[row['id']] = quotes(row['es'])
            for line in source.read_text(encoding='utf-8').splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                if row['id'] not in es:
                    raise SystemExit(f"{row['id']} has no translation")
                memory[chapter][(row['tipo'] == 'combate', row['en'])] = es[row['id']]
                kinds[chapter][row['en']] = row['tipo']
    return memory, kinds


def load_overrides():
    """capituloN/overrides.jsonl: {"id": "TTTT-iiii", "es": "..."} translates one record regardless of its
    English text (needed when identical English has different speakers/register in Japanese)."""
    overrides = {}
    for path in sorted(WORK.glob('capitulo*/overrides.jsonl')):
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                overrides[row['id']] = quotes(row['es'])
    return overrides


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disc', type=int, choices=(1, 2), required=True)
    args = parser.parse_args()
    memory, kinds = load_memory()
    overrides = load_overrides()
    target = WORK / f'builds/es-all/disc{args.disc}/files'
    if target.exists():
        shutil.rmtree(target)
    image = OWNER / f'local/prepared/disc{args.disc}/Track 01.iso'
    report, problems, untranslated = {}, [], defaultdict(list)
    with image.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        extents = {path: (lba, size) for path, lba, size in files(iso)}

        def read(name):
            lba, size = extents[name]
            return bytes(iso[lba * 2048:lba * 2048 + size])

        for name in sorted(extents):
            upper = name.upper()
            base = upper.rsplit('/', 1)[-1]
            table_match = re.fullmatch(r'(\d{2})\d{2}TBL\.BIN', base)
            battle_match = re.fullmatch(r'M(\d{2})MES\.BIN', base)
            if not (table_match or battle_match):
                continue
            chapter = int((table_match or battle_match).group(1))
            original = read(name)
            texts = {}
            if table_match:
                for record in parse_table(original):
                    english = record.display_text
                    if MARKER.match(english) or not english.strip():
                        continue
                    es = overrides.get(f"{base[:4]}-{record.index:04d}") or memory[chapter].get((False, english))
                    if es is None:
                        untranslated[name].append(record.index)
                        continue
                    es = restore_localized_terms(es)
                    lips = kinds[chapter].get(english) == 'LIPS'
                    for issue in es_tables.check(es, keep_lines=lips):
                        problems.append(f'{base}-{record.index}: {issue}')
                    texts[record.index] = '\n'.join(es_tables.wrap(es, lips))
                data = es_tables.build_table(original, texts)
                count = len(parse_table(original))
                if len(data) > es_tables.SAFE_TABLE_BYTES:
                    problems.append(f'{base}: {len(data)} bytes exceeds the safe {es_tables.SAFE_TABLE_BYTES}')
            else:
                _, _, records = es_mes.parse(original)
                for record in records:
                    english = es_mes.decode(record['words'])
                    if not english.strip():
                        continue
                    es = memory[chapter].get((True, english))
                    if es is None:
                        untranslated[name].append(record['index'])
                        continue
                    es = restore_localized_terms(es)
                    for issue in es_tables.check(es):
                        problems.append(f'{base}-{record["index"]}: {issue}')
                    texts[record['index']] = '\n'.join(es_tables.wrap(es))
                data = es_mes.build(original, texts)
                count = len(records)
            out = target / name.lstrip('/')
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            report[name] = dict(records=count, spanish=len(texts), bytes=len(data), english_bytes=len(original))

    for problem in problems:
        print(problem)
    for name, indexes in sorted(untranslated.items()):
        print(f'SIN TRADUCCION {name}: {len(indexes)} registros {indexes[:12]}')
    print(json.dumps(report, indent=1))
    if problems:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
