import csv
import json
from pathlib import Path
import tempfile
import unittest

from tools.export_dialogue_catalog import CatalogRow, parse_table, write_catalog
from tools.prepare_translation_workspace import prepare


class TranslationWorkspaceTests(unittest.TestCase):
    def fixture(self, root, conflicting_alias=False):
        primary, = parse_table(bytes.fromhex("000000080000000e000000090000000000030004")
                               + b"A\rB\x85\t\0\0\0")
        distinct, = parse_table(bytes.fromhex("000000080000000e000000090000000000030004")
                                + b"C\rD\x85\t\0\0\0")
        catalog = root / "catalog"
        rows = [
            CatalogRow(1, "/S/0100TBL.BIN", "a" * 64, primary),
            CatalogRow(1, "/S/0101TBL.BIN", "a" * 64, primary),
            CatalogRow(2, "/S/0100TBL.BIN", "a" * 64, distinct if conflicting_alias else primary),
            CatalogRow(2, "/S/0101TBL.BIN", "b" * 64, distinct),
        ]
        discs = []
        for disc in (1, 2):
            tables = [dict(iso_path=row.iso_path, table_sha256=row.table_sha256, record_count=1)
                      for row in rows if row.disc == disc]
            discs.append(dict(disc=disc, tables=tables, candidate_count=2, table_count=2,
                              record_count=2, rejects=[], image_sha256=str(disc) * 64))
        write_catalog(catalog, rows, dict(schema_version=1, source_encoding="Windows-1252",
                                         source_linebreak="CR", discs=discs))
        return catalog

    def test_aliases_only_identical_tables_at_the_same_iso_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            output = root / "output"
            result = prepare(source, output)
            self.assertEqual((result["source_records"], result["translation_records"],
                              result["aliased_records"]), (4, 3, 1))
            table = output / "tables/disc1/S/0100TBL.jsonl"
            row = json.loads(table.read_text(encoding="utf-8"))
            self.assertEqual(row["record_key"], "1:/S/0100TBL.BIN:9:0")
            self.assertEqual(row["alias_record_keys"], ["2:/S/0100TBL.BIN:9:0"])
            self.assertEqual(row["source_en"], "A\rB…\t")
            self.assertEqual(row["source_en_display"], "A\nB…\t")
            self.assertEqual(row["text_bytes_hex"], "410d428509")
            self.assertEqual((row["prefix0"], row["prefix1"]), (3, 4))
            self.assertEqual(row["unsupported_controls"], {"09": 1})
            self.assertEqual((row["target_es"], row["status"]), ("", "untranslated"))
            with table.with_suffix(".csv").open(encoding="utf-8", newline="") as stream:
                csv_row, = csv.DictReader(stream)
            self.assertEqual(csv_row["source_en"], row["source_en"])
            self.assertEqual(json.loads(csv_row["alias_record_keys"]), row["alias_record_keys"])
            self.assertTrue((output / "tables/disc2/S/0101TBL.jsonl").is_file())
            self.assertFalse((output / "tables/disc2/S/0100TBL.jsonl").exists())
            self.assertEqual((output / "source-manifest.json").read_bytes(),
                             (source / "manifest.json").read_bytes())
            with self.assertRaises(FileExistsError):
                prepare(source, output)

    def test_rejects_conflicting_rows_under_a_single_table_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root, conflicting_alias=True)
            output = root / "output"
            with self.assertRaisesRegex(ValueError, "same table hash"):
                prepare(source, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
