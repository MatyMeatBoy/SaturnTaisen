"""Prepare private, provenance-linked translation worksheets from a dialogue export."""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re

if __package__:
    from .export_dialogue_catalog import PRIVATE_ROOT
else:
    from export_dialogue_catalog import PRIVATE_ROOT


SOURCE_FIELDS = (
    "record_key", "disc", "iso_path", "table_sha256", "record_id", "index",
    "relative_offset", "offset", "end_offset", "prefix0", "prefix1", "text_bytes_hex",
    "text_cp1252", "display_text", "unsupported_controls",
)
OUTPUT_FIELDS = (
    "record_key", "alias_record_keys", "disc", "iso_path", "record_id", "index",
    "source_en", "target_es", "status", "source_en_display", "table_sha256",
    "relative_offset", "offset", "end_offset", "prefix0", "prefix1", "text_bytes_hex",
    "unsupported_controls",
)
ISO_PATH = re.compile(r"(?:/[A-Z0-9_.-]+)*/[A-Z0-9_.-]*TBL\.BIN\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")


def source_inventory(manifest):
    if (manifest.get("schema_version"), manifest.get("source_encoding"),
            manifest.get("source_linebreak")) != (1, "Windows-1252", "CR"):
        raise ValueError("unsupported dialogue catalog format")
    result = {}
    discs = set()
    for source in manifest["discs"]:
        disc = source["disc"]
        if type(disc) is not int or disc < 1 or disc in discs:
            raise ValueError("invalid or duplicate source disc")
        discs.add(disc)
        tables = source["tables"]
        if (source["rejects"] or len(tables) != source["candidate_count"]
                or len(tables) != source["table_count"] or not tables
                or sum(table["record_count"] for table in tables) != source["record_count"]
                or not HASH.fullmatch(source["image_sha256"])):
            raise ValueError(f"incomplete dialogue export for disc {disc}")
        for table in tables:
            path = table["iso_path"]
            key = disc, path
            if (not ISO_PATH.fullmatch(path) or {".", ".."} & set(path.split("/"))
                    or key in result or not HASH.fullmatch(table["table_sha256"])
                    or not 1 <= table["record_count"] <= 65535):
                raise ValueError(f"invalid table inventory for disc {disc}")
            result[key] = table
    if not result:
        raise ValueError("empty table inventory")
    return result


def read_rows(source, inventory):
    records = defaultdict(list)
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            digest.update(line)
            row = json.loads(line.decode("utf-8"))
            if row.keys() != set(SOURCE_FIELDS):
                raise ValueError(f"unexpected source fields at JSONL row {number}")
            disc, path = row["disc"], row["iso_path"]
            table = inventory.get((disc, path))
            group = records[disc, path]
            index = len(group)
            record_id = row["record_id"]
            key = f"{disc}:{path}:{record_id}:{index}"
            if (table is None or row["table_sha256"] != table["table_sha256"]
                    or index >= table["record_count"] or row["index"] != index
                    or row["record_key"] != key or type(record_id) is not int
                    or not 0 <= record_id <= 0xffffffff
                    or bytes.fromhex(row["text_bytes_hex"]).decode("cp1252") != row["text_cp1252"]):
                raise ValueError(f"inconsistent source at JSONL row {number}")
            group.append(row)
    if any(len(records[key]) != table["record_count"] for key, table in inventory.items()):
        raise ValueError("source JSONL does not cover the full table inventory")
    return records, digest.hexdigest()


def build_groups(inventory, records):
    groups = {}
    for key, source in sorted(inventory.items()):
        disc, path = key
        group_key = path, source["table_sha256"]
        if group_key not in groups:
            groups[group_key] = [key]
            continue
        canonical = groups[group_key][0]
        if len(records[key]) != len(records[canonical]) or any(
            any(row[field] != first[field] for field in SOURCE_FIELDS if field not in ("disc", "record_key"))
            for row, first in zip(records[key], records[canonical])
        ):
            raise ValueError(f"source rows disagree for the same table hash at {path}, disc {disc}")
        groups[group_key].append(key)
    return groups


def write_table(output, relative, canonical, aliases):
    base = output / relative
    base.parent.mkdir(parents=True, exist_ok=True)
    jsonl = base.with_suffix(".jsonl")
    csv_path = base.with_suffix(".csv")
    with jsonl.open("x", encoding="utf-8", newline="\n") as json_file, (
        csv_path.open("x", encoding="utf-8", newline="")
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for index, row in enumerate(canonical):
            translated = {
                **row,
                "alias_record_keys": [group[index]["record_key"] for group in aliases],
                "source_en": row["text_cp1252"],
                "source_en_display": row["display_text"],
                "target_es": "",
                "status": "untranslated",
            }
            result = {field: translated[field] for field in OUTPUT_FIELDS}
            json_file.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
            for field in ("alias_record_keys", "unsupported_controls"):
                result[field] = json.dumps(result[field], separators=(",", ":"))
            writer.writerow(result)
    return jsonl.relative_to(output).as_posix(), csv_path.relative_to(output).as_posix()


def prepare(source, output):
    source_manifest = (source / "manifest.json").read_bytes()
    inventory = source_inventory(json.loads(source_manifest.decode("utf-8")))
    records, jsonl_sha = read_rows(source / "dialogue.jsonl", inventory)
    groups = build_groups(inventory, records)
    output.mkdir(parents=True, exist_ok=False)
    tables = []
    for (path, sha), keys in groups.items():
        disc = keys[0][0]
        relative = Path(f"tables/disc{disc}") / path.lstrip("/")
        jsonl, csv_path = write_table(output, relative, records[keys[0]], [records[key] for key in keys[1:]])
        tables.append({
            "iso_path": path,
            "table_sha256": sha,
            "disc": disc,
            "alias_discs": [key[0] for key in keys[1:]],
            "records": len(records[keys[0]]),
            "jsonl": jsonl,
            "csv": csv_path,
        })
    source_records = sum(len(group) for group in records.values())
    translation_records = sum(table["records"] for table in tables)
    result = {
        "schema_version": 1,
        "source_language": "en",
        "target_language": "es",
        "source_manifest_sha256": hashlib.sha256(source_manifest).hexdigest(),
        "source_jsonl_sha256": jsonl_sha,
        "source_tables": len(inventory),
        "translation_tables": len(tables),
        "source_records": source_records,
        "translation_records": translation_records,
        "aliased_records": source_records - translation_records,
        "tables": tables,
    }
    (output / "source-manifest.json").write_bytes(source_manifest)
    (output / "translation-manifest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=PRIVATE_ROOT / "dialogue-catalog-worker")
    parser.add_argument("--output", type=Path, default=PRIVATE_ROOT / "spanish-translation")
    args = parser.parse_args()
    output = args.output.resolve()
    if PRIVATE_ROOT.resolve() not in output.parents or output.exists():
        parser.error("--output must be a new directory inside local/work")
    try:
        manifest = prepare(args.catalog, output)
    except (OSError, KeyError, ValueError) as error:
        parser.exit(1, f"Translation workspace failed: {error}\n")
    print(f"{manifest['translation_tables']} tables, {manifest['translation_records']} source records, "
          f"{manifest['aliased_records']} aliases\n{output}")


if __name__ == "__main__":
    main()
