"""Export native English Saturn dialogue tables from prepared MODE1/2048 ISOs."""
import argparse
from collections import Counter
import csv
from dataclasses import asdict, dataclass, fields
import hashlib
import json
import mmap
from pathlib import Path
import struct
import sys

if __package__:
    from .audit_sdk import files
else:
    from audit_sdk import files


WORKSPACE = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = WORKSPACE / "local" / "work"
MAX_TABLE_SIZE = 4 * 1024 * 1024
MAX_RECORDS = 65535
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Record:
    index: int
    record_id: int
    relative_offset: int
    offset: int
    end_offset: int
    prefix0: int
    prefix1: int
    text_bytes_hex: str
    text_cp1252: str
    display_text: str
    unsupported_controls: dict[str, int]


@dataclass(frozen=True)
class CatalogRow:
    disc: int
    iso_path: str
    table_sha256: str
    record: Record

    def serialize(self):
        record = self.record
        return {
            "record_key": f"{self.disc}:{self.iso_path}:{record.record_id}:{record.index}",
            "disc": self.disc,
            "iso_path": self.iso_path,
            "table_sha256": self.table_sha256,
            **asdict(record),
        }


def parse_table(data: bytes) -> list[Record]:
    """Read the English 32-bit format. Keep record offsets relative to the table."""
    if not 16 <= len(data) <= MAX_TABLE_SIZE:
        raise ValueError("table size is outside the supported range")
    start_words, footer_words = struct.unpack_from(">II", data)
    data_start, footer_start = 2 * start_words, 2 * footer_words
    if not 16 <= data_start <= footer_start <= len(data) or (data_start - 8) % 8:
        raise ValueError("invalid English 32-bit header extents or entry alignment")
    count = (data_start - 8) // 8
    if count > MAX_RECORDS:
        raise ValueError("record count exceeds the supported limit")

    entries = list(struct.iter_unpack(">II", memoryview(data)[8:data_start]))
    records = []
    for index, (record_id, relative_offset) in enumerate(entries):
        offset = data_start + relative_offset
        end_offset = footer_start
        if index + 1 < count:
            end_offset = data_start + entries[index + 1][1]
        if not data_start <= offset <= end_offset - 6 or end_offset > footer_start:
            raise ValueError(f"record {index} has invalid or nonmonotonic data offsets")
        prefix0, prefix1 = struct.unpack_from(">HH", data, offset)
        stop = data.find(b"\0", offset + 4, end_offset)
        if stop < 0:
            raise ValueError(f"record {index} has no in-range text terminator")
        raw = data[offset + 4:stop]
        try:
            original = raw.decode("cp1252")
        except UnicodeDecodeError as error:
            raise ValueError(f"record {index} has an undefined CP1252 byte") from error
        controls = Counter(
            f"{byte:02x}" for byte in raw if byte == 0x7f or byte < 0x20 and byte != 0x0d
        )
        records.append(Record(
            index=index,
            record_id=record_id,
            relative_offset=relative_offset,
            offset=offset,
            end_offset=end_offset,
            prefix0=prefix0,
            prefix1=prefix1,
            text_bytes_hex=raw.hex(),
            text_cp1252=original,
            display_text=original.replace("\r\n", "\n").replace("\r", "\n"),
            unsupported_controls=dict(sorted(controls.items())),
        ))
    return records


def scan_disc(disc: int, image: Path) -> tuple[list[CatalogRow], dict]:
    rows = []
    tables = []
    rejects = []
    controls = Counter()
    control_record_count = 0
    with image.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        image_sha256 = hashlib.sha256(iso).hexdigest()
        candidates = sorted(file for file in files(iso) if file[0].upper().endswith("TBL.BIN"))
        path_counts = Counter(path for path, _, _ in candidates)
        for path, lba, size in candidates:
            source = {"iso_path": path, "lba": lba, "size": size}
            offset = lba * 2048
            try:
                if path_counts[path] > 1:
                    raise ValueError("ambiguous duplicate ISO path")
                if offset + size > len(iso):
                    raise ValueError("file extent exceeds data track")
                if size > MAX_TABLE_SIZE:
                    raise ValueError("table size exceeds the supported limit")
                table_data = iso[offset:offset + size]
                source["table_sha256"] = hashlib.sha256(table_data).hexdigest()
                records = parse_table(table_data)
            except ValueError as error:
                rejects.append({**source, "reason": str(error)})
                continue
            tables.append({**source, "record_count": len(records)})
            rows.extend(CatalogRow(disc, path, source["table_sha256"], record) for record in records)
            for record in records:
                controls.update(record.unsupported_controls)
                control_record_count += bool(record.unsupported_controls)

    return rows, {
        "disc": disc,
        "image_name": image.name,
        "image_sha256": image_sha256,
        "candidate_count": len(candidates),
        "table_count": len(tables),
        "record_count": len(rows),
        "unsupported_control_record_count": control_record_count,
        "unsupported_controls": dict(sorted(controls.items())),
        "tables": tables,
        "rejects": rejects,
    }


def write_catalog(output: Path, rows: list[CatalogRow], manifest: dict):
    # Creating the directory exclusively protects prior exports and other artifacts.
    output.mkdir(parents=True, exist_ok=False)
    columns = ["record_key", "disc", "iso_path", "table_sha256"]
    columns.extend(field.name for field in fields(Record))
    with (output / "dialogue.jsonl").open("x", encoding="utf-8", newline="\n") as json_file, (
        output / "dialogue.csv"
    ).open("x", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        for entry in rows:
            row = entry.serialize()
            json_file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            row["unsupported_controls"] = json.dumps(row["unsupported_controls"], separators=(",", ":"))
            writer.writerow(row)
    with (output / "manifest.json").open("x", encoding="utf-8", newline="\n") as manifest_file:
        json.dump(manifest, manifest_file, indent=2, ensure_ascii=False)
        manifest_file.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for disc in (1, 2):
        parser.add_argument(
            f"--disc{disc}", type=Path,
            default=WORKSPACE / "local" / "prepared" / f"disc{disc}" / "Track 01.iso",
        )
    parser.add_argument(
        "--output", type=Path, default=PRIVATE_ROOT / "dialogue-catalog-worker",
        help="new directory inside local/work (defaults to local/work/dialogue-catalog-worker)",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if PRIVATE_ROOT.resolve() not in output.parents:
        parser.error("--output must be a new directory inside local/work")
    if output.exists():
        parser.error(f"output already exists: {output}")

    catalog = []
    manifests = []
    try:
        for disc, image in enumerate((args.disc1, args.disc2), start=1):
            rows, manifest = scan_disc(disc, image)
            catalog.extend(rows)
            manifests.append(manifest)
        write_catalog(output, catalog, {
            "schema_version": SCHEMA_VERSION,
            "source_encoding": "Windows-1252",
            "source_linebreak": "CR",
            "table_glob": "*TBL.BIN",
            "discs": manifests,
        })
    except (OSError, ValueError) as error:
        print(f"Dialogue export failed: {error}", file=sys.stderr)
        return 1

    complete = True
    for disc in manifests:
        rejected = len(disc["rejects"])
        print(f"Disc {disc['disc']}: {disc['table_count']}/{disc['candidate_count']} tables, "
              f"{disc['record_count']} records, {rejected} rejects, "
              f"{disc['unsupported_control_record_count']} records with unsupported controls")
        complete &= not rejected and disc["candidate_count"] > 0
    print(output)
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
