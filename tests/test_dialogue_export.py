import csv
import json
from pathlib import Path
import struct
import tempfile
import unittest

from tools.export_dialogue_catalog import CatalogRow, parse_table, write_catalog


def english_table(*records):
    data_start = 8 + 8 * len(records)
    entries = []
    data = bytearray()
    for record_id, prefix0, prefix1, raw in records:
        entries.append(struct.pack(">II", record_id, len(data)))
        data.extend(struct.pack(">HH", prefix0, prefix1) + raw + b"\0\0")
    if len(data) % 2:
        data.append(0)
    header = struct.pack(">II", data_start // 2, (data_start + len(data)) // 2)
    return header + b"".join(entries) + data + b"footer"


class DialogueExportTests(unittest.TestCase):
    def test_preserves_native_order_duplicate_ids_offsets_and_text(self):
        records = parse_table(english_table(
            (9, 3, 65535, b"One\rTwo\x85\t\x92"),
            (9, 0, 12, b""),
        ))
        first, second = records
        self.assertEqual((first.index, first.record_id, first.offset, first.relative_offset),
                         (0, 9, 24, 0))
        self.assertEqual((second.index, second.record_id, second.offset, second.relative_offset),
                         (1, 9, first.end_offset, first.end_offset - 24))
        self.assertEqual((first.prefix0, first.prefix1), (3, 65535))
        self.assertEqual(first.text_cp1252, "One\rTwo…\t’")
        self.assertEqual(first.display_text, "One\nTwo…\t’")
        self.assertEqual(first.text_bytes_hex, "4f6e650d54776f850992")
        self.assertEqual(first.unsupported_controls, {"09": 1})
        self.assertEqual(second.display_text, "")

    def test_rejects_malformed_extents_and_terminators(self):
        source = english_table((1, 0, 0, b"AB"), (2, 0, 0, b"CD"))
        variants = {
            "size": b"x" * (4 * 1024 * 1024 + 1),
            "short": b"short",
            "alignment": struct.pack(">I", 7) + source[4:],
            "footer outside table": source[:4] + struct.pack(">I", len(source)) + source[8:],
            "wrong width Japanese header": struct.pack(">HHHHHH", 4, 6, 123, 0, 0, 0) + b"\0" * 8,
            "repeated start": source[:20] + struct.pack(">I", 0) + source[24:],
            "out of range start": source[:20] + struct.pack(">I", 0xffffffff) + source[24:],
            "terminator outside record": source[:30] + b"AB" + source[32:],
            "undefined CP1252": source[:28] + b"\x81" + source[29:],
        }
        for label, data in variants.items():
            with self.subTest(label=label), self.assertRaises(ValueError):
                parse_table(data)

    def test_serializes_provenance_and_keeps_disc_context(self):
        record, = parse_table(english_table((9, 1, 2, b"Test\r\x85\t")))
        rows = [
            CatalogRow(disc, "/TESTTBL.BIN", "a" * 64, record)
            for disc in (1, 2)
        ]
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "new"
            write_catalog(output, rows, {"summary": "fixture"})
            entries = [json.loads(line) for line in (output / "dialogue.jsonl")
                       .read_text(encoding="utf-8").splitlines()]
            self.assertEqual([row["disc"] for row in entries], [1, 2])
            self.assertNotEqual(entries[0]["record_key"], entries[1]["record_key"])
            self.assertEqual(entries[0]["table_sha256"], "a" * 64)
            with (output / "dialogue.csv").open(encoding="utf-8", newline="") as csv_file:
                csv_rows = list(csv.DictReader(csv_file))
            self.assertEqual(csv_rows[0]["text_cp1252"], "Test\r…\t")
            self.assertEqual(json.loads(csv_rows[0]["unsupported_controls"]), {"09": 1})
            self.assertEqual(csv_rows[1]["record_key"], entries[1]["record_key"])
            self.assertEqual(json.loads((output / "manifest.json").read_text(encoding="utf-8")),
                             {"summary": "fixture"})
            with self.assertRaises(FileExistsError):
                write_catalog(output, [], {})


if __name__ == "__main__":
    unittest.main()
