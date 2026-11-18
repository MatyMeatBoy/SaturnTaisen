"""Package the Spanish language pack (data only) for a public release.

  python -X utf8 tools/es/empaquetar_idioma.py --version 0.2.1-alpha

Writes local/releases/SaturnTaisen-v<version>-es-language-pack.zip and its .sha256 (refuses to overwrite).
Contents: every reviewed batch (`*.out.jsonl`: {"id","es"}), the per-record overrides, the public part of the
style guide and a LEEME.txt. It never includes the English or Japanese source text (`*.in.jsonl`), the
reconstructed Japanese, the review notes, game files or discs. Inputs live under SAKURA_OWNER_ROOT/local.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _rutas import OWNER, WORK  # noqa: E402

LEEME = """SaturnTaisen - Spanish language pack (text data) - v{version}
=======================================================================

DATA-ONLY language pack: the Spanish translation of the game's dialogue, battle text and
menu-adjacent strings, produced by the project's translation pipeline (tools/es/ in the main
repo) from the English script, reviewed line by line against the Japanese. It contains no
Japanese or English original text, game code, audio, images or disc data.

Contents
  capituloN/loteNN.out.jsonl   dialogue batches, chapters 1-10 (ids TTTT-NNNN = table-record)
  capituloN/lote90.out.jsonl   battle text of scenario M## (ids M##-NNNN), N = scenario number
  capituloN/overrides.jsonl    per-record translations where identical English hides a different
                               speaker/register in the Japanese (they take priority over the batches)
  GUIA-ESTILO.md               translation conventions (register, tu/usted, glossary, unified decisions)

Format: one JSON object per line: {{"id": "TTTT-NNNN", "es": "text, \\n = in-game line break"}}.
Limit per record after wrapping: 30 columns x 4 lines (the builder wraps automatically).

Status (honest summary)
  - Script text: all 10 chapters and the battle scenarios M01-M26 are translated and were reviewed in
    two passes (completeness, pronouns/register, neutral Spanish) and cross-checked against the
    Japanese for speaker, tu/usted, gender, terms and jokes.
  - Menus/graphics (title, options, load/save, status, battle command bar) are NOT in this pack:
    they are redrawn by tools/es/menus_es.py and menus_disco2.py from your own disc.
  - Episode cards, the LOADING screen, the extra menu (OMALL.DAT) and video subtitles are still English.
  - Checked in the game: chapter 1, chapter 2 and spot checks (episode 7 text, disc 2 episode 8);
    chapters 3-6, 9 and 10 were verified on the built disc image only, not played. The text was
    verified in the HD text mode only for chapter 1.
  - There is no in-launcher language selector yet: the Spanish game is played from a disc image you
    build yourself with tools/es/construir_todo.py (needs Python and your own prepared English discs).
    This pack is the text input for that build.

You must own the game. No game files are distributed.
"""


def public_guide(text):
    """Everything before the internal review-lessons sections."""
    cut = re.search(r'^## Lecciones de revisión', text, re.M)
    return text[:cut.start()].rstrip() + '\n' if cut else text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    out = OWNER / 'local/releases' / f'SaturnTaisen-v{args.version}-es-language-pack.zip'
    if out.exists():
        raise SystemExit(f'refusing to overwrite {out}')
    out.parent.mkdir(parents=True, exist_ok=True)
    count = records = 0
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(WORK.glob('capitulo*/lotes/lote??.out.jsonl')) + sorted(WORK.glob('capitulo*/overrides.jsonl')):
            data = path.read_text(encoding='utf-8')
            for line in data.splitlines():
                if line.strip():
                    row = json.loads(line)
                    if set(row) != {'id', 'es'}:
                        raise SystemExit(f'unexpected keys in {path}: {sorted(row)}')
                    records += 1
            rel = path.relative_to(WORK)
            name = f'{rel.parts[0]}/{rel.name}' if rel.parts[1] == 'lotes' else rel.as_posix()
            z.writestr(name, data)
            count += 1
        z.writestr('GUIA-ESTILO.md', public_guide((WORK / 'GUIA-ESTILO.md').read_text(encoding='utf-8')))
        z.writestr('LEEME.txt', LEEME.format(version=args.version))
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    out.with_name(out.name + '.sha256').write_text(f'{digest}  {out.name}\n', encoding='utf-8')
    print(json.dumps(dict(output=str(out), files=count, records=records, sha256=digest, bytes=out.stat().st_size)))


if __name__ == '__main__':
    main()
