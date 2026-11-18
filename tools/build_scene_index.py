"""Index ISO entries, verified FILM streams, and documented runtime observations."""
import argparse
from collections import Counter
import csv
import hashlib
import json
import mmap
from pathlib import Path, PurePosixPath
import re
import struct

if __package__:
    from .audit_sdk import files
    from .export_dialogue_catalog import PRIVATE_ROOT, WORKSPACE
    from .prepare_translation_workspace import read_rows, source_inventory
else:
    from audit_sdk import files
    from export_dialogue_catalog import PRIVATE_ROOT, WORKSPACE
    from prepare_translation_workspace import read_rows, source_inventory


TAGS = {"video": "vídeo", "dialogo": "diálogo", "eleccion": "elección",
        "mapa": "mapa", "combate": "combate", "menu": "menú"}
TRANSITION_NOTES = "docs/research/chapter1-wide-transitions.md"
BATTLE_NOTES = "docs/research/tactical-menu-independent-reference.md"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SWEEP_CASE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def hash_span(data, start, end):
    with memoryview(data) as view:
        return hashlib.sha256(view[start:end]).hexdigest()


def resource_id(disc, path, digest):
    return f"{disc}:{path}:{digest}"


def film_stream(data, start, end):
    """Validate Sega FILM/Cinepak headers and every indexed sample extent."""
    if start < 0 or end > len(data) or end - start < 80:
        return None
    if data[start:start + 4] != b"FILM" or data[start + 16:start + 20] != b"FDSC":
        return None
    header_size = struct.unpack_from(">I", data, start + 4)[0]
    fdsc_size, codec, height, width = struct.unpack_from(">I4sII", data, start + 20)
    table = start + 16 + fdsc_size
    if (codec != b"cvid" or not 1 <= width <= 4096 or not 1 <= height <= 4096
            or not 32 <= fdsc_size or not table + 16 <= start + header_size <= end
            or data[table:table + 4] != b"STAB"):
        return None
    size, time_base, count = struct.unpack_from(">III", data, table + 4)
    if not time_base or not count or size != 16 + 16 * count or table + size != start + header_size:
        return None
    max_end = 0
    for i in range(count):
        offset, length = struct.unpack_from(">II", data, table + 16 + 16 * i)
        if header_size + offset + length > end - start:
            return None
        max_end = max(max_end, offset + length)
    if not max_end:
        return None
    return {"format": "sega_film", "codec": "cvid", "width": width, "height": height,
            "samples": count, "byte_length": header_size + max_end}


def scan_disc(disc, iso, expected_sha):
    resources = []
    seen = set()
    with iso.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as image:
        digest = hash_span(image, 0, len(image))
        if digest != expected_sha:
            raise ValueError(f"disc {disc} SHA-256 differs from the source catalog")
        for path, lba, size in sorted(files(image)):
            start = lba * 2048
            end = start + size
            if end > len(image) or path in seen:
                raise ValueError(f"invalid or duplicate ISO file extent: {path}")
            seen.add(path)
            sha = hash_span(image, start, end)
            videos = []
            at = image.find(b"FILM", start, end)
            while at >= 0:
                film = film_stream(image, at, end)
                if film is None:
                    at = image.find(b"FILM", at + 4, end)
                    continue
                stop = at + film["byte_length"]
                videos.append({**film, "offset": at - start, "sha256": hash_span(image, at, stop)})
                at = image.find(b"FILM", stop, end)
            if videos:
                content = "sega_film" if len(videos) == 1 and videos[0]["offset"] == 0 else "sega_film_archive"
            elif image[start:min(end, start + 4)] == b"CPK ":
                content = "cri_cpk_header"
            else:
                content = "unknown"
            resources.append({
                "resource_id": resource_id(disc, path, sha), "disc": disc, "iso_path": path,
                "sha256": sha, "lba": lba, "byte_length": size, "format": content,
                "video_streams": videos,
            })
    return resources


def scene(scene_id, disc, tag, certainty, evidence, **attributes):
    return {
        "scene_id": scene_id, "disc": disc, "tag": tag, "certainty": certainty,
        "resource_id": None, "iso_path": None, "stream_offset": None,
        "dialogue_table": None, "associated_record_keys": [], "record_association": "unknown",
        "text_presence": "unknown", "wait_for_text": None, "runtime_layout": "unknown",
        "zoom_eligibility": "unknown", "fallback_layout": "native", "evidence": evidence,
        **attributes,
    }


def scene_candidates(resources, dialogue_records):
    result = []
    for resource in resources:
        disc, path = resource["disc"], resource["iso_path"]
        identity = resource["resource_id"]
        common = {"resource_id": identity, "iso_path": path}
        records = dialogue_records.get((disc, path))
        if records:
            result.append(scene(
                f"table:{identity}", disc, "dialogo", "inferred", ["decoded native English table"],
                **common, dialogue_table=identity, associated_record_keys=[row["record_key"] for row in records],
                record_association="table_inventory",
            ))
        for stream in resource["video_streams"]:
            offset = stream["offset"]
            result.append(scene(
                f"film:{identity}:{offset}:{stream['sha256']}", disc, "video", "inferred",
                ["FILM/FDSC/STAB headers and sample extents checked"], **common, stream_offset=offset,
            ))
    return result


def runtime_observations(resources):
    by_name = {(row["disc"], row["iso_path"]): row["resource_id"] for row in resources}
    witnessed = (
        ("opening", "video", "opening", "unknown", TRANSITION_NOTES, "intro1799.state", None),
        ("title", "menu", "title", "unknown", TRANSITION_NOTES, "title-final.state", None),
        ("theater-map", "mapa", "row-gradient", "unknown", TRANSITION_NOTES, "map-room.state", None),
        ("dining-hall", "dialogo", "narrative", "present", TRANSITION_NOTES, "map-room.state frame 750", None),
        ("night-choices", "eleccion", "narrative", "present", TRANSITION_NOTES,
         "resume-chapter-6000.state frames 8 and 32", None),
        ("night-reply", "dialogo", "narrative", "present", TRANSITION_NOTES,
         "resume-chapter-6000.state frame 230", None),
        ("intermission-pause", "menu", "anchored-menu", "present", TRANSITION_NOTES,
         "intermission-down.state", "/SAKURA1/IC01.BIN"),
        ("loading", None, "anchored-menu", "present", TRANSITION_NOTES,
         "title-start/loading.state", "/SAKURA1/LOAD.BIN"),
        ("combat-action-menu", "combate", "unknown", "present", BATTLE_NOTES,
         "Beetle Saturn frames 14638, 15238, 15388", None),
    )
    result = []
    for name, tag, layout, text, report, sample, path in witnessed:
        if layout != "unknown":
            eligibility = "validated_for_observation"
        else:
            eligibility = "unknown"
        asset = by_name.get((1, path))
        result.append(scene(
            f"1:observation:{name}", 1, tag, "observed", [{"report": report, "sample": sample}],
            resource_id=asset, iso_path=path if asset else None,
            runtime_layout=layout, zoom_eligibility=eligibility, text_presence=text,
        ))
    return result


def sweep_evidence(entry, expected_tag):
    if not isinstance(entry, dict) or entry.get("tag") != expected_tag or expected_tag not in TAGS:
        raise ValueError(f"invalid chapter-sweep tag for {expected_tag}")
    evidence = entry.get("evidence")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("path"), str):
        raise ValueError("invalid chapter-sweep screenshot metadata")
    name, frame, sha = evidence["path"], evidence["frame"], evidence["sha256"]
    path = PurePosixPath(name)
    if (path.is_absolute() or name != path.as_posix() or ".." in path.parts
            or "\\" in name or ":" in name or path.suffix.lower() != ".png"
            or type(frame) is not int or frame < 0
            or not isinstance(sha, str) or not SHA256.fullmatch(sha)):
        raise ValueError("invalid chapter-sweep screenshot metadata")
    return {"path": name, "frame": frame, "sha256": sha}


def import_chapter_sweep(rows, resources, dialogue_records):
    if not isinstance(rows, list) or not rows:
        raise ValueError("chapter sweep observations must be a nonempty array")
    inventory = {(row["disc"], row["iso_path"]): row for row in resources}
    discs = {disc for disc, _ in inventory}
    result = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid chapter-sweep row")
        disc, case, episode, slot = (row["disc_on_continue"], row["case"],
                                     row["episode_on_continue"], row["slot"])
        if (type(disc) is not int or disc not in discs
                or not isinstance(case, str) or not SWEEP_CASE.fullmatch(case)
                or (disc, case) in seen or type(slot) is not int or slot not in (1, 2, 3)
                or not (episode == "Finale" or type(episode) is int and episode > 0)):
            raise ValueError("invalid or duplicate chapter-sweep selection")
        seen.add((disc, case))
        identifier = f"{disc}:observation:chapter-sweep:{case}"
        context = {"observed_episode": episode, "slot": slot}
        result.append(scene(
            f"{identifier}:selection", disc, "menu", "observed",
            [sweep_evidence(row["selection"], "menu")], **context,
        ))

        observed = row.get("observed_scene")
        if observed is None:
            continue
        if not isinstance(observed, dict) or observed.get("text_presence") != "present":
            raise ValueError(f"chapter-sweep dialogue lacks visible text evidence: {case}")
        evidence = sweep_evidence(observed, "dialogo")
        tables = []
        resident = {}
        reported = row.get("exact_resident_resources", [])
        if not isinstance(reported, list):
            raise ValueError(f"invalid chapter-sweep resource list: {case}")
        for item in reported:
            if not isinstance(item, dict) or not isinstance(item.get("iso_path"), str):
                raise ValueError(f"invalid chapter-sweep resource: {case}")
            path = item["iso_path"]
            resource = inventory.get((disc, path))
            if (resource is None or path in resident or item.get("disc", disc) != disc
                    or item["whole_file_equal"] is not True or item["sha256"] != resource["sha256"]
                    or item["bytes"] != resource["byte_length"] or item["equal_bytes"] != item["bytes"]
                    or item["lba"] != resource["lba"]):
                raise ValueError(f"unverified chapter-sweep resource at disc {disc}, path {path}")
            resident[path] = resource["resource_id"]
            if resource["format"] == "english_dialogue_table":
                tables.append((disc, path))
        if len(tables) > 1:
            raise ValueError(f"ambiguous chapter-sweep dialogue tables: {case}")
        linkage = {}
        if tables:
            key, = tables
            table_id = resident[key[1]]
            linkage = {"dialogue_table": table_id, "resource_id": table_id, "iso_path": key[1],
                       "record_association": "resident_table_inventory",
                       "associated_record_keys": [line["record_key"] for line in dialogue_records[key]]}
        result.append(scene(
            f"{identifier}:dialogue", disc, "dialogo", "observed", [evidence], **context,
            **linkage, text_presence="present", resident_resource_ids=list(resident.values()),
        ))
    return result


def write_csv(path, rows):
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False, separators=(",", ":"))
                             if isinstance(value, (list, dict)) else value for key, value in row.items()})


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def build(catalog, discs, output, observations_path=None):
    manifest_bytes = (catalog / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    inventory = source_inventory(manifest)
    records, jsonl_sha = read_rows(catalog / "dialogue.jsonl", inventory)
    source_discs = {row["disc"]: row["image_sha256"] for row in manifest["discs"]}
    if set(discs) != set(source_discs):
        raise ValueError("provided discs do not match the catalog inventory")
    resources = [resource for disc, iso in sorted(discs.items())
                 for resource in scan_disc(disc, iso, source_discs[disc])]
    by_path = {(r["disc"], r["iso_path"]): r for r in resources}
    for key, table in inventory.items():
        resource = by_path.get(key)
        if resource is None or resource["sha256"] != table["table_sha256"]:
            raise ValueError(f"catalog table differs from ISO: {key}")
        resource["format"] = "english_dialogue_table"
    candidates = scene_candidates(resources, records)
    observations = runtime_observations(resources)
    observation_manifest = None
    if observations_path is not None:
        data = observations_path.read_bytes()
        imported = import_chapter_sweep(json.loads(data.decode("utf-8")), resources, records)
        observations.extend(imported)
        observation_manifest = {
            "file": observations_path.name, "sha256": hashlib.sha256(data).hexdigest(),
            "count": len(imported), "tags": dict(Counter(row["tag"] for row in imported)),
        }
    scenes = candidates + observations

    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "resource-inventory.json", resources)
    write_csv(output / "resource-inventory.csv", resources)
    write_json(output / "scene-index.json", scenes)
    write_csv(output / "scene-index.csv", scenes)
    result = {
        "schema_version": 1, "tags": TAGS, "iso_sha256_by_disc": source_discs,
        "source_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "source_jsonl_sha256": jsonl_sha,
        "resources": dict(Counter(row["disc"] for row in resources)),
        "resource_candidates": dict(Counter(row["tag"] for row in candidates)),
        "runtime_observations": len(observations),
        "dialogue_records_linked": sum(len(row["associated_record_keys"]) for row in candidates),
    }
    if observation_manifest is not None:
        result["imported_observations"] = observation_manifest
    write_json(output / "manifest.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=PRIVATE_ROOT / "dialogue-catalog-worker")
    parser.add_argument("--output", type=Path, default=PRIVATE_ROOT / "scene-index")
    parser.add_argument("--observations", type=Path, help="optional chapter-sweep metadata JSON")
    for disc in (1, 2):
        parser.add_argument(f"--disc{disc}", type=Path,
                            default=WORKSPACE / "local/prepared" / f"disc{disc}" / "Track 01.iso")
    args = parser.parse_args()
    output = args.output.resolve()
    if PRIVATE_ROOT.resolve() not in output.parents or output.exists():
        parser.error("--output must be a new directory inside local/work")
    try:
        report = build(args.catalog, {1: args.disc1, 2: args.disc2}, output, args.observations)
    except (OSError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"Scene index failed: {error}\n")
    print(f"{sum(report['resources'].values())} ISO files; "
          f"{report['resource_candidates']}; {report['runtime_observations']} runtime observations")
    print(output)


if __name__ == "__main__":
    main()
