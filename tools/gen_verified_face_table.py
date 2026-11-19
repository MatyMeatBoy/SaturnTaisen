"""Generate exact NC20/NC30 face signatures using the owner's Saturn and PC files."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from decode_saturn_bg import Iso

CANDIDATES = ("NC20", "NC30")


def fnv64(data):
    result = 14695981039346656037
    for byte in data:
        result = ((result ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return result


def verified_rows(iso, pc_root, mapping):
    assets = mapping["assets"]
    extent = iso.find(assets["saturn_file"])
    if extent is None:
        raise ValueError(f"Missing {assets['saturn_file']}")
    saturn = iso.content(extent)
    pc = (pc_root / assets["pc_file"]).read_bytes()
    for name, data in (("saturn", saturn), ("pc", pc)):
        if hashlib.sha256(data).hexdigest() != assets[name + "_sha256"]:
            raise ValueError(f"Unexpected {name} asset identity: {assets[name + '_file']}")
    rows = defaultdict(set)
    for frame in mapping["frames"]:
        width, height = frame["saturn_size"]
        offsets = frame["saturn_offsets"] if "saturn_offsets" in frame else [frame["saturn_offset"]]
        for offset in offsets:
            data = saturn[offset:offset + width * height]
            if hashlib.sha256(data).hexdigest() != frame["saturn_sha256"]:
                raise ValueError(f"Sprite bytes disagree with the face map at offset {offset}")
            rows[fnv64(data), width, height].add(frame["pc_index"])
    if any(len(indices) != 1 for indices in rows.values()):
        raise ValueError("Ambiguous sprite signature in verified body face map")
    return fnv64(saturn), fnv64(pc), [(key, next(iter(rows[key]))) for key in sorted(rows)]


def render(iso, pc_root, config):
    lines = [
        "// SPDX-License-Identifier: GPL-3.0-only",
        "#pragma once", "#include <cstdint>", "#include <span>", "#include <string_view>",
        "namespace port {",
        "struct VerifiedBodyFace { uint64_t hash; unsigned width, height, pcIndex; };",
        "struct VerifiedBodyFaces {",
        "    uint64_t nativeAsset, pcAsset;",
        "    std::span<const VerifiedBodyFace> frames;",
        "};",
    ]
    cases = []
    for name in CANDIDATES:
        mapping = json.loads((config / f"hd-{name.lower()}-face-map.json").read_text(encoding="utf-8"))
        saturn_hash, pc_hash, rows = verified_rows(iso, pc_root, mapping)
        lines.append(f"inline constexpr VerifiedBodyFace k{name}[] = {{")
        for (hash_value, width, height), index in rows:
            lines.append(f"    {{0x{hash_value:016X}ull, {width}, {height}, {index}}},")
        lines.extend(("};", ""))
        cases.append(f'    if (name == "{name}.BIN") return '
                     f'{{0x{saturn_hash:016X}ull, 0x{pc_hash:016X}ull, k{name}}};')
    lines.extend(("inline VerifiedBodyFaces VerifiedFacesFor(std::string_view name) {",
                  *cases, "    return {};", "}", "}"))
    return "\n".join(lines)+"\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("track", type=Path)
    parser.add_argument("pc_assets", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1] / "config")
    args = parser.parse_args()
    args.output.write_text(render(Iso(args.track), args.pc_assets, args.config), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
