"""Audit local Saturn/PC portrait catalogs and snapshots without running the game."""
import argparse
from collections import Counter, defaultdict
from configparser import ConfigParser
import csv
from dataclasses import dataclass
from hashlib import sha256
import json
import mmap
from pathlib import Path
import re
import struct
import sys

from PIL import Image

if __package__:
    from .audit_sdk import files
    from .hd_matching import fnv64, load_image, prepare_variant, read_fce_images, workspace_file
else:
    from audit_sdk import files
    from hd_matching import fnv64, load_image, prepare_variant, read_fce_images, workspace_file


WORKSPACE = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = WORKSPACE / "local" / "work"
PARTS = {"base": (0, 48), "eyes": (48, 64), "mouth": (64, 80)}
YONEDA_IDS = set(range(0xE2, 0xE8))
STATE_HEADER = struct.pack("<II32sI", 0x53525354, 9, b"sakura", 0x4D414348)
STATE_VECTORS = (0x100000, 0x100000, 0x80000, 0x80000, 0x40000, 0x40000, 0x80000, 0x1000)
CHAPTER_ONE = re.compile(r"/01[0-9]{2}FCE\.BIN$", re.IGNORECASE)
STATE_FRAME = re.compile(r"(.+)-(\d+)\.state$", re.IGNORECASE)


@dataclass(frozen=True)
class Strip:
    y: int
    pixels: bytes


@dataclass(frozen=True)
class ObservedPortrait:
    base: bytes
    strips: tuple[Strip, ...]
    frame: bytes


def ranges(values):
    groups = []
    for value in sorted(set(values)):
        if groups and value == groups[-1][1] + 1:
            groups[-1][1] = value
        else:
            groups.append([value, value])
    return [f"{a:04x}-{b:04x}" if a != b else f"{a:04x}" for a, b in groups]


def alpha_coverage(image, raw, density):
    """Count alpha values under the nontransparent Saturn texels per part."""
    if len(raw) != 3200 or image.size != (40 * density, 80 * density):
        raise ValueError("atlas dimensions mismatch")
    mask = Image.frombytes("L", (40, 80), bytes(255 if byte else 0 for byte in raw))
    mask = mask.resize(image.size, Image.Resampling.NEAREST)
    alpha = image.getchannel("A")
    result = {}
    for key, (start, end) in PARTS.items():
        box = (0, start * density, image.width, end * density)
        values = alpha.crop(box).histogram(mask=mask.crop(box))
        result[key] = {"opaque": values[255], "partial": sum(values[1:255]), "missing": values[0]}
    return result


def patch_matches(atlas, frame):
    """Mirror the runtime's base-first, single-before-double byte matching."""
    if len(atlas) != 3200 or len(frame) != 1920:
        return ()
    base = atlas[:1920]
    if frame == base:
        return ((),)

    # Ignore origins whose unmodified prefix or suffix would already disagree.
    first = next(i for i, (a, b) in enumerate(zip(base, frame)) if a != b) // 40
    last = 47 - next(i for i, (a, b) in enumerate(zip(base[::-1], frame[::-1])) if a != b) // 40
    singles = []
    alternate = [[], []]
    for part in (1, 2):
        pixels = atlas[(32 + part * 16) * 40:(48 + part * 16) * 40]
        for y in range(33):
            start, end = y * 40, (y + 16) * 40
            segment = frame[start:end]
            backdrop = base[start:end]
            if segment == backdrop:
                continue
            literal = segment == pixels
            if not literal and any(actual != (paint or under)
                                   for actual, paint, under in zip(segment, pixels, backdrop)):
                continue
            match = (part, y, not literal)
            if y <= first and y + 16 > last:
                singles.append((match,))
            else:
                alternate[part - 1].append(match)
    if singles:
        return tuple(singles)

    doubles = []
    for eyes in alternate[0]:
        for mouth in alternate[1]:
            low, high = sorted((eyes[1], mouth[1]))
            if high - low < 16 or low > first or high + 16 <= last:
                continue
            if frame[(low + 16) * 40:high * 40] == base[(low + 16) * 40:high * 40]:
                doubles.append((eyes, mouth))
    return tuple(doubles)


def active_commands(vram):
    """Walk the VDP1 list starting at zero with its single return register."""
    if len(vram) != 0x80000:
        raise ValueError("VDP1 VRAM size mismatch")
    at, return_at = 0, None
    for _ in range(0x4000):
        command = struct.unpack_from(">8H", vram, at)
        control, link = command[:2]
        if control & 0x8000:
            return
        if not (control & 0x4000) and (control & 15) <= 11:
            yield command
        target = at + 32
        jump = (control >> 12) & 3
        if jump in (1, 2):
            if jump == 2 and return_at is None:
                return_at = target
            target = (link << 3) & ~31
        elif jump == 3 and return_at is not None:
            target, return_at = return_at, None
        if target == at:
            break
        at = target & 0x7ffe0
    raise ValueError("unterminated VDP1 command list")


def observed_portrait(vram):
    """Reconstruct only the command layout the HD frontend currently recognizes."""
    def coordinate(word):
        return ((word & 0x1fff) ^ 0x1000) - 0x1000

    local_x, local_y = 0, 0
    base = None
    strips = []
    frame = None
    for cmd in active_commands(vram):
        kind = cmd[0] & 15
        if kind == 10:
            local_x, local_y = coordinate(cmd[6]), coordinate(cmd[7])
            continue
        if kind or cmd[0] & 0x8030 or cmd[2:4] != (0xA0, 0x4400):
            continue
        x, y = coordinate(cmd[6]) + local_x, coordinate(cmd[7]) + local_y
        is_base = cmd[5] == 0x530 and x == 16 and y == 160
        is_strip = cmd[5] == 0x510 and x == 16 and 160 <= y <= 192
        if not is_base and (base is None or not is_strip):
            continue
        at, size = cmd[4] * 8, (cmd[5] & 255) * 40
        pixels = bytes(vram[at:at + size])
        if len(pixels) < size:
            pixels += bytes(vram[:size - len(pixels)])
        if is_base:
            if base is not None:
                raise ValueError("multiple active portrait bases")
            base = pixels
            frame = bytearray(base)
        else:
            strips.append(Strip(y - 160, pixels))
            start = (y - 160) * 40
            for offset, value in enumerate(pixels, start):
                if value:
                    frame[offset] = value
    return None if base is None else ObservedPortrait(base, tuple(strips), bytes(frame))


def state_vectors(path):
    with path.open("rb") as source:
        if source.read(len(STATE_HEADER)) != STATE_HEADER:
            raise ValueError("expected Sakura v9 state")
        vram = palette = None
        for number, expected in enumerate(STATE_VECTORS):
            prefix = source.read(8)
            if len(prefix) != 8 or struct.unpack("<Q", prefix)[0] != expected:
                raise ValueError("invalid machine-state vector")
            if number in (3, 7):
                block = source.read(expected)
                if len(block) != expected:
                    raise ValueError("truncated machine-state vector")
                if number == 3:
                    vram = block
                else:
                    palette = block[0x800:0xa00]
            else:
                source.seek(expected, 1)
    return vram, palette


def compare_rgb(indices, palette, screenshot_rgb):
    """Compare opaque native pixels and test exact blends toward RGB555 white."""
    if len(palette) != 512 or len(screenshot_rgb) != 3 * len(indices):
        raise ValueError("invalid RGB comparison buffers")
    colors = [bytes(((word & 31) << 3, ((word >> 5) & 31) << 3, ((word >> 10) & 31) << 3))
              for word, in struct.iter_unpack(">H", palette)]
    pairs = Counter((colors[index], screenshot_rgb[3 * i:3 * i + 3])
                    for i, index in enumerate(indices) if index)
    mismatches = sum(count for (source, shown), count in pairs.items() if source != shown)
    white_steps = [
        step for step in range(1, 32) if mismatches and all(
            bytes((channel * (32 - step) + 248 * step) >> 5 for channel in source) == shown
            for source, shown in pairs
        )
    ]
    return {"opaque_pixels": sum(pairs.values()), "unblended_mismatches": mismatches,
            "white_blend_steps": white_steps}


def screenshot_comparison(path, portrait, palette):
    match = STATE_FRAME.fullmatch(path.name)
    if not match:
        return None
    name, frame_number = match.groups()
    image_path = path.with_name(f"{name}-{int(frame_number):06d}.png")
    if not image_path.is_file():
        return None
    image = load_image(image_path)
    if image.size != (320, 224):
        return {"name": image_path.name, "status": "screenshot is outside the native viewport size"}
    crop = image.crop((16, 160, 56, 208)).convert("RGB").tobytes()
    return {
        "name": image_path.name,
        "base": compare_rgb(portrait.base, palette, crop),
        "command_frame": compare_rgb(portrait.frame, palette, crop),
    }


def read_native_discs(discs):
    complete = {}
    chapter = defaultdict(list)
    atlases = {}
    for disc, path in enumerate(discs, 1):
        with path.open("rb") as source, mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as iso:
            for name, lba, size in files(iso):
                if not name.endswith("FCE.BIN"):
                    continue
                start = lba * 2048
                if size > 1024 * 1024 or start + size > len(iso):
                    raise ValueError(f"invalid FCE extent: {name}")
                images = read_fce_images(iso[start:start + size])
                atlases[f"{disc}:{name}"] = [f"{identity:04x}" for identity in sorted(images)]
                for identity, raw in images.items():
                    if complete.setdefault(identity, raw) != raw:
                        raise ValueError(f"conflicting FCE identity: {identity:04x}")
                    if CHAPTER_ONE.search(name):
                        chapter[identity].append(f"{disc}:{name}")
    return complete, chapter, atlases


def verified_blob(path, expected_hash, exact_size=None):
    size = path.stat().st_size
    if size > 16 * 1024 * 1024 or exact_size is not None and size != exact_size:
        raise ValueError(f"invalid file size: {path.name}")
    data = path.read_bytes()
    if fnv64(data) != expected_hash:
        raise ValueError(f"hash mismatch: {path.name}")
    return data


def read_pack(folder, project):
    manifest = ConfigParser(interpolation=None)
    path = folder / "manifest.ini"
    if path.stat().st_size > 1024 * 1024:
        raise ValueError("pack manifest exceeds size limit")
    with path.open(encoding="utf-8") as source:
        manifest.read_file(source)
    root = manifest["pack"]
    count = root.getint("count")
    if root.getint("schema") != 1 or not 1 <= count <= 394:
        raise ValueError("invalid pack version or count")
    if (root.getint("source_bytes"), root.getint("source_hash"), root.getint("palette_hash")) != (
        project["source"]["bytes"], project["source"]["fnv64"], project["palette_hash"],
    ):
        raise ValueError("pack revision or palette differs from project")
    atlas = verified_blob(workspace_file(folder, root["native_file"]), root.getint("native_hash"), count * 3200)
    result = {}
    for index in range(count):
        entry = manifest[f"portrait-{index}"]
        identity, offset = entry.getint("native_id"), entry.getint("offset")
        if identity in result or not 1 <= identity <= 394 or offset != index * 3200:
            raise ValueError("pack contains a duplicate identity or invalid record offset")
        raw = atlas[offset:offset + 3200]
        if fnv64(raw) != entry.getint("raw_hash"):
            raise ValueError(f"pack native bytes failed hash check: {identity:04x}")
        result[identity] = (raw, tuple(
            (workspace_file(folder, entry[f"file{density}"]), entry.getint(f"hash{density}"))
            for density in (1, 2)
        ))
    return result


def portion_flags(bytes_, stride):
    return {name: any(bytes_[start * stride:end * stride]) for name, (start, end) in PARTS.items()}


def nearest_strip_rows(raw):
    results = {}
    for part in ("eyes", "mouth"):
        start, end = PARTS[part]
        strip = raw[start * 40:end * 40]
        distances = [sum(a != b for a, b in zip(strip, raw[y * 40:(y + 16) * 40]))
                     for y in range(33)]
        minimum = min(distances)
        results[part] = {"rows": [y for y, value in enumerate(distances) if value == minimum],
                         "different_index_pixels": minimum}
    return results


def audit_catalog(project_file, pack_folder, discs):
    project = json.loads(project_file.read_text(encoding="utf-8"))
    if project.get("schema") != 1 or project.get("kind") != "sakura-narrative-portraits":
        raise ValueError("unexpected matcher project schema")
    source_info = project["source"]
    source = Path(source_info["path"])
    source_verified = source.is_file()
    if source_verified:
        blob = verified_blob(source, source_info["fnv64"], source_info["bytes"])
        if sha256(blob).hexdigest() != source_info["sha256"]:
            raise ValueError("PC source archive SHA-256 differs from project")
    root = project_file.parent
    pc = {}
    for entry in project["candidates"]:
        index = entry["index"]
        if type(index) is not int or not 0 <= index < 394 or index in pc:
            raise ValueError("invalid or duplicate PC candidate index")
        path = workspace_file(root, entry["path"])
        pc[index] = candidate_image(path, entry["sha256"])
    native, chapter, atlases = read_native_discs(discs)
    pack = read_pack(pack_folder, project)
    base_ids = defaultdict(list)
    rows = []
    errors = []
    for entry in sorted(project["rows"], key=lambda item: int(item["id"], 16)):
        identity = int(entry["id"], 16)
        path = workspace_file(root, entry["raw"])
        if path.stat().st_size != 3200:
            raise ValueError(f"incomplete native atlas: {identity:04x}")
        raw = path.read_bytes()
        if native.get(identity) != raw or sha256(raw).hexdigest() != entry["raw_sha256"]:
            raise ValueError(f"native atlas differs from source: {identity:04x}")
        base_ids[raw[:1920]].append(identity)
        candidate = pc[entry["selected"]]
        variants = {}
        if identity in pack:
            runtime, paths = pack[identity]
            if runtime != raw:
                errors.append(f"pack native bytes differ from ISO: {identity:04x}")
            for density, (variant, hash_) in enumerate(paths, 1):
                try:
                    verified_blob(variant, hash_)
                    image = load_image(variant)
                    expected = prepare_variant(candidate, raw, density, entry["dx"], entry["dy"])
                    if image.size != expected.size or image.tobytes() != expected.tobytes():
                        raise ValueError("RGBA differs from matcher output")
                    variants[density] = alpha_coverage(image, raw, density)
                except (ValueError, OSError) as error:
                    errors.append(f"{identity:04x} density {density}: {error}")
        eligible = entry["status"] in ("auto", "accepted")
        if (identity in pack) != eligible:
            errors.append(f"pack presence differs from matcher status: {identity:04x}")

        native_parts = portion_flags(raw, 40)
        candidate_parts = portion_flags(candidate.getchannel("A").tobytes(), 160)
        region_ready = {
            name: native_parts[name] and len(variants) == 2
            and all(variant[name]["opaque"] > 0 for variant in variants.values())
            for name in PARTS
        }
        region_ready["simultaneous"] = all(region_ready.values())
        ranked = entry["candidates"]
        rows.append({
            "id": f"{identity:04x}",
            "chapter1_sources": chapter.get(identity, []),
            "yoneda_art": identity in YONEDA_IDS,
            "status": entry["status"],
            "selected_pc": entry["selected"],
            "expected_pc": identity - 1,
            "top_error": ranked[0]["error"],
            "top_margin": ranked[1]["error"] - ranked[0]["error"] if len(ranked) > 1 else None,
            "native": native_parts,
            "selected_pc_regions": candidate_parts,
            "validated_variants": variants,
            "prepared_regions": region_ready,
            "nearest_strip_rows": nearest_strip_rows(raw),
        })

    project_ids = {int(row["id"], 16) for row in rows}
    if len(project_ids) != len(rows) or project_ids != native.keys() or pack.keys() - project_ids:
        raise ValueError("project, native ISO and pack identities disagree")
    selected = Counter(row["selected_pc"] for row in rows)
    for row in rows:
        row["selected_pc_uses"] = selected[row["selected_pc"]]
        row["same_native_base"] = [
            f"{identity:04x}" for identity in base_ids[native[int(row["id"], 16)][:1920]]
            if identity != int(row["id"], 16)
        ]
    candidate_summary = {
        "count": len(pc),
        "index_gaps": sorted(set(range(max(pc, default=-1) + 1)) - pc.keys()),
        "source_archive_verified": source_verified,
        "regions": dict(Counter(part for image in pc.values()
                                for part, present in portion_flags(image.getchannel("A").tobytes(), 160).items()
                                if present)),
    }
    return rows, native, pack, project["palette_hash"], candidate_summary, errors, atlases


def candidate_image(path, expected_sha256):
    image = load_image(path)
    if image.size != (80, 160) or sha256(path.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError(f"candidate atlas failed dimensions or hash check: {path.name}")
    return image


def snapshot_observations(paths, native, pack, palette_hash):
    base_ids = defaultdict(list)
    parts = defaultdict(list)
    for identity, atlas in native.items():
        base_ids[atlas[:1920]].append(identity)
        parts[atlas[1920:2560]].append((identity, 1))
        parts[atlas[2560:3200]].append((identity, 2))

    observations = []
    for path in paths:
        result = {"state": path.name}
        try:
            vram, palette = state_vectors(path)
            result["palette_matches"] = fnv64(palette) == palette_hash
            portrait = observed_portrait(vram)
        except (OSError, ValueError) as error:
            observations.append({**result, "status": str(error)})
            continue
        if portrait is None:
            observations.append({**result, "status": "no active portrait base"})
            continue

        bases = base_ids.get(portrait.base, [])
        matches = {}
        for identity, (atlas, _) in pack.items():
            match = patch_matches(atlas, portrait.frame)
            if match:
                matches[f"{identity:04x}"] = match
        result.update({
            "base_ids": [f"{identity:04x}" for identity in bases],
            "strips": [
                {"y": strip.y, "matches": [[f"{i:04x}", p] for i, p in parts.get(strip.pixels, [])]}
                for strip in portrait.strips
            ],
            "pack_matches": matches,
            "status": "one pack match" if len(matches) == 1 and len(next(iter(matches.values()))) == 1
                      else "ambiguous pack match" if matches else "no pack match",
        })
        try:
            comparison = screenshot_comparison(path, portrait, palette)
        except (ValueError, OSError) as error:
            comparison = {"status": str(error)}
        if comparison is not None:
            result["screenshot"] = comparison
        observations.append(result)
    return observations


def coverage_summary(rows):
    pending = [row for row in rows if row["status"] == "pending"]
    return {
        "identities": len(rows),
        "status_counts": dict(Counter(row["status"] for row in rows)),
        "validated_variants": sum(len(row["validated_variants"]) for row in rows),
        "native_regions": {part: sum(row["native"][part] for row in rows) for part in PARTS},
        "prepared_regions": {
            part: sum(row["prepared_regions"][part] for row in rows)
            for part in (*PARTS, "simultaneous")
        },
        "prepared_rows_with_alpha_holes": {
            part: sum(any(counts[part]["missing"] or counts[part]["partial"]
                          for counts in row["validated_variants"].values()) for row in rows)
            for part in PARTS
        },
        "pending_ranges": ranges(int(row["id"], 16) for row in pending),
        "pending_selected_expected_pc": sum(row["selected_pc"] == row["expected_pc"] for row in pending),
        "pending_selected_other_pc": [row["id"] for row in pending if row["selected_pc"] != row["expected_pc"]],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PRIVATE_ROOT / "hd-matcher-project/project.json")
    parser.add_argument("--pack", type=Path, default=PRIVATE_ROOT / "v012-prepared-hd/portraits")
    parser.add_argument("--disc", type=Path, action="append", help="prepared Saturn ISO, repeat per disc")
    parser.add_argument("--states", type=Path, help="directory to scan for saved local .state snapshots")
    parser.add_argument("--output", type=Path, default=PRIVATE_ROOT / "portrait-coverage-worker")
    args = parser.parse_args()
    defaults = [WORKSPACE / "local" / "prepared" / f"disc{i}" / "Track 01.iso" for i in (1, 2)]
    output = args.output.resolve()
    if PRIVATE_ROOT.resolve() not in output.parents or output.exists():
        parser.error("--output must be a new directory inside local/work")
    if args.states is not None and not args.states.is_dir():
        parser.error("--states must be an existing directory")
    try:
        rows, native, pack, palette, candidates, errors, atlases = audit_catalog(args.project, args.pack, args.disc or defaults)
        chapter = [row for row in rows if row["chapter1_sources"]]
        observations = snapshot_observations(sorted(args.states.glob("*.state")), native, pack, palette) if args.states else []
        data = {
            "schema_version": 1,
            "pc_candidates": candidates,
            "catalog": coverage_summary(rows),
            "chapter1": coverage_summary(chapter),
            "errors": errors,
            "fce_atlases": atlases,
            "rows": rows,
            "snapshots": observations,
        }
        output.mkdir(parents=True, exist_ok=False)
        (output / "portrait-coverage.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        columns = ["id", "chapter1", "yoneda_art", "status", "selected_pc", "expected_pc",
                   "selected_pc_uses", "top_error", "top_margin", "base", "eyes", "mouth", "simultaneous"]
        with (output / "portrait-coverage.csv").open("x", encoding="utf-8", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({**row, **row["prepared_regions"], "chapter1": bool(row["chapter1_sources"])})
    except (KeyError, OSError, ValueError) as error:
        print(f"Portrait coverage audit failed: {error}", file=sys.stderr)
        return 1

    for label, summary in (("Catalog", data["catalog"]), ("Chapter 1", data["chapter1"])):
        print(f"{label}: {summary['identities']} identities, {summary['validated_variants']} verified variants, "
              f"{summary['status_counts'].get('pending', 0)} pending")
    print(f"{len(errors)} validation errors, {len(observations)} snapshots inspected")
    print(output)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
