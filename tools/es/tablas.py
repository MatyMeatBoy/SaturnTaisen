"""Spanish dialogue tables for the English 32-bit TBL.BIN format.

Layout (verified against every English table by rebuild_identical):
  header: >II  record-area start and footer start, both in 2-byte units
  entries: >II record_id, byte offset relative to the record area
  record: >HH prefix0 prefix1, CP1252 text padded with spaces to even length, 00 00
  footer: copied unchanged (Japanese lip-sync vowel data, independent of text)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from export_dialogue_catalog import parse_table  # noqa: E402

MAX_COLS = 30
MAX_LINES = 4
SAFE_TABLE_BYTES = 93642  # largest English table the game is known to load (0400TBL)


def encode(text: str) -> bytes:
    raw = text.replace('\n', '\r').encode('cp1252')
    return raw + b' ' * (len(raw) % 2)


def build_table(original: bytes, texts: dict[int, str]) -> bytes:
    """texts maps record index -> display text (LF line breaks). Missing indexes keep the original."""
    start_words, footer_words = struct.unpack_from('>II', original)
    data_start, footer_start = 2 * start_words, 2 * footer_words
    records = parse_table(original)
    entries, body = [], bytearray()
    for record in records:
        prefix = original[record.offset:record.offset + 4]
        if record.index in texts:
            raw = encode(texts[record.index])
        else:
            raw = bytes.fromhex(record.text_bytes_hex)
        entries.append(struct.pack('>II', record.record_id, len(body)))
        body += prefix + raw + b'\0\0'
    head = 8 + 8 * len(records)
    if head != data_start:
        raise ValueError('unexpected header size')
    footer = original[footer_start:]
    out = struct.pack('>II', head // 2, (head + len(body)) // 2) + b''.join(entries) + body + footer
    return bytes(out)


def wrap(text: str, keep_lines: bool = False) -> list[str]:
    """Greedy wrap to MAX_COLS. keep_lines keeps explicit line structure (LIPS choices)."""
    if keep_lines:
        return [line.strip() for line in text.split('\n')]
    lines = []
    for paragraph in text.split('\n'):  # explicit breaks (choice menus) are kept
        lines += _wrap_paragraph(paragraph)
    return lines


def _wrap_paragraph(text: str) -> list[str]:
    words, lines, current = text.split(), [], ''
    for word in words:
        candidate = word if not current else current + ' ' + word
        if len(candidate) <= MAX_COLS:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def check(text: str, keep_lines: bool = False) -> list[str]:
    problems = []
    try:
        text.encode('cp1252')
    except UnicodeEncodeError as error:
        problems.append(f'character outside CP1252: {error.object[error.start]!r}')
    lines = wrap(text, keep_lines)
    if len(lines) > MAX_LINES:
        problems.append(f'{len(lines)} lines')
    for line in lines:
        if len(line) > MAX_COLS:
            problems.append(f'line over {MAX_COLS}: {line!r}')
    return problems


def rebuild_identical(original: bytes) -> bool:
    records = parse_table(original)
    texts = {r.index: r.display_text for r in records}
    return build_table(original, texts) == original
