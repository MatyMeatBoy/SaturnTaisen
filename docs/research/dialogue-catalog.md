# Native English dialogue catalog

Run from the repository root with Python 3.11 or later.

```powershell
python tools/export_dialogue_catalog.py
python -m unittest discover -s tests -p test_dialogue_export.py
```

The exporter reads the prepared English ISOs in `local/prepared/disc1` and `local/prepared/disc2`. Use `--disc1` and `--disc2` to select other prepared images. Each export creates a new directory under the Git-ignored `local/work` tree. The default is `local/work/dialogue-catalog-worker`. Supply a fresh `--output` directory for subsequent runs.

- `dialogue.jsonl` is the UTF-8 machine-readable catalog, with one object per record.
- `dialogue.csv` carries the same fields in UTF-8. Native and display line breaks are embedded in quoted cells. Read with a CSV parser and import text columns as text when using a spreadsheet.
- `manifest.json` identifies the input images by SHA-256 and lists each table's ISO path, LBA, byte length, source SHA-256 and record count. It also lists rejected candidates and counts unsupported controls by byte. A missing candidate set or any rejection produces a nonzero exit status. Accepted tables still export when a candidate is rejected.

## Row identity and text

`record_key` combines `disc`, `iso_path`, `record_id` and the zero-based table `index`. Use it to associate translations with records from this source revision. Use `table_sha256` and the image hash in the manifest to validate that revision. An identical table or repeated record ID can appear in different contexts. The exporter retains every row in disc, path and native record order.

`relative_offset` is the offset stored in the entry, measured from the record area. `offset` and the exclusive `end_offset` are byte offsets from the beginning of the table. `prefix0` and `prefix1` preserve the unsigned values of the two big-endian words before the text. Their semantics remain unverified.

`text_bytes_hex` preserves the bytes of the string up to the first NUL. `text_cp1252` preserves their Windows-1252 decoding, including native CR line breaks and byte `85` decoded as an ellipsis. `display_text` converts CR and CRLF to LF for preview and editing. `unsupported_controls` maps hexadecimal byte values to occurrence counts and excludes the native CR separator. The decoded text keeps those bytes as characters for review.

## Format and observed coverage

The English format starts with two big-endian 32-bit offsets in two-byte units. They locate the record area and footer. Eight-byte entries begin immediately after the header, with a big-endian 32-bit ID and a big-endian 32-bit record-relative byte offset. The next entry, or the footer for the final entry, bounds the current record. The parser caps tables at 4 MiB and 65,535 entries and checks header alignment, record bounds, offset order and text termination. It rejects undefined Windows-1252 bytes. Both prepared Japanese discs use a different header and were rejected by these checks.

| Prepared image | Candidates | Accepted | Records | Rejected | Records containing tab |
| --- | ---: | ---: | ---: | ---: | ---: |
| English disc 1 | 56 | 56 | 29,725 | 0 | 2 |
| English disc 2 | 56 | 56 | 29,725 | 0 | 2 |
| Japanese disc 1 | 56 | 0 | 0 | 56 | — |
| Japanese disc 2 | 56 | 0 | 0 | 56 | — |

The 56 English table paths and their source hashes match across discs. The catalog has 59,450 rows across both disc contexts. In each English image, `0100TBL.BIN` contains 605 records. Coverage applies to files whose names end in `TBL.BIN` in the two prepared English images. Text in other resources, including menus and minigames, is outside this inventory.
