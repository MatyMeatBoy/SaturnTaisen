# Translated-disc scripts for the Spanish edition

The private directory `local/work/spanish-translation` contains 56 UTF-8 tables in JSONL and CSV. `translation-manifest.json` indicates the path and record count of each table. The first script has 605 records in `tables/disc1/SAKURA1/0100TBL.jsonl`.

```powershell
python tools/prepare_translation_workspace.py
python -m unittest discover -s tests -p test_translation_workspace.py
```

The generator reads `local/work/dialogue-catalog-worker`. It also accepts `--catalog` for another validated catalog and `--output` to create a new directory under `local/work`. The generator requires a new destination to protect already-edited work.

## Editing

- Choose JSONL or CSV as the working copy. Both versions start with the same content and are edited separately.
- Write the Spanish text in `target_es` and update `status` according to progress. The initial state is `untranslated`. Keep `record_key` as the row identifier.
- Read `source_en` to preserve the CRs and the original characters decoded from Windows-1252. `source_en_display` shows the same text with LF line breaks for reading. In JSONL, CR and tabs appear as escapes. In CSV, line breaks go inside quoted cells. Open with a CSV reader and import the columns as text if using a spreadsheet.
- Review `prefix0`, `prefix1`, offsets, `text_bytes_hex`, and `unsupported_controls` when a line needs context. The two prefixes preserve native values and their semantics remain unverified. The pipeline prepares scripts and leaves Saturn reinsertion to the patch tool.

## Identity across discs

The catalog contains 59,450 physical records, 29,725 per disc. Sharing a translation requires the same ISO path, the same table SHA-256, and the same record sequence. The first disc identifies the 29,725 canonical rows for this edition. Each `alias_record_keys` field explicitly identifies the equivalent physical row on disc 2. Tables with different paths or hashes keep separate translations, even if they reuse IDs.

`source-manifest.json` keeps the original manifest with the disc and table hashes. `translation-manifest.json` also records the SHA-256 of the manifest and the source JSONL. The scripts remain in the private tree excluded from Git. Coverage corresponds to the native `*TBL.BIN` resources of the English catalog.
