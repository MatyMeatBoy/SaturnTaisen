"""Battle message tables (SAKURA2/M##MES.BIN) of the English patch.

Layout (verified by rebuild_identical on every M##MES of disc 1):
  header: >HH record-area start, footer start (2-byte units)
  entries: >HH record id, record offset in 2-byte units from the record area
  record: >HH prefix0 prefix1, text as 16-bit codes (CP1252 byte value, 0x0A0D = line break), 0x0000
  footer: copied unchanged
Text uses the 8x12 CP1252 battle font (M##MES.FNT), which already holds Spanish letters.
"""
import struct


def parse(data: bytes):
    start, footer = (2 * v for v in struct.unpack_from('>HH', data))
    entries = list(struct.iter_unpack('>HH', data[4:start]))
    records = []
    for index, (record_id, offset) in enumerate(entries):
        begin = start + offset * 2
        end = start + entries[index + 1][1] * 2 if index + 1 < len(entries) else footer
        words = list(struct.unpack_from(f'>{(end - begin) // 2}H', data, begin))
        records.append(dict(index=index, record_id=record_id, words=words))
    return start, footer, records


def decode(words) -> str:
    out = []
    for value in words[2:]:
        if value == 0:
            break
        out.append('\n' if value == 0x0A0D else bytes([value]).decode('cp1252', 'replace') if value < 256 else f'<{value:04x}>')
    return ''.join(out)


def encode(text: str) -> list[int]:
    words = []
    for char in text:
        if char == '\n':
            words.append(0x0A0D)
        else:
            words.append(char.encode('cp1252')[0])
    return words


def build(original: bytes, texts: dict[int, str]) -> bytes:
    start, footer, records = parse(original)
    entries, body = [], []
    for record in records:
        words = record['words']
        if record['index'] in texts:
            text_end = words.index(0, 2) if 0 in words[2:] else len(words)
            words = words[:2] + encode(texts[record['index']]) + [0] + words[text_end + 1:]
        entries.append(struct.pack('>HH', record['record_id'], len(body)))
        body += words
    head = 4 + 4 * len(records)
    if head != start:
        raise ValueError('unexpected header size')
    out = struct.pack('>HH', head // 2, (head + 2 * len(body)) // 2) + b''.join(entries) + struct.pack(f'>{len(body)}H', *body)
    return out + original[footer:]


def rebuild_identical(original: bytes) -> bool:
    _, _, records = parse(original)
    texts = {r['index']: decode(r['words']) for r in records}
    return build(original, texts) == original
