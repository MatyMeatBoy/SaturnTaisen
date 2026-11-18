"""Rank decoded PC BG images against game screenshots (local use; assets stay under local/).

Usage: python tools/match_bg_screenshots.py SIGNATURES.json SHOTS_DIR [PREFIX ...]
PREFIX limits candidates to a shard, e.g. SAKURA1_BG10 SAKURA1_BG11 (see docs/research/bg-matching-shards.md).
SIGNATURES.json maps "SAKURA1_BG1119" to a 32x20 luminance list (see docs/research/bg-matching-progress.md).
Prints, per screenshot, the three best candidates (z-scored correlation). A margin under 0.05 is ambiguous;
always confirm visually (lighting variants such as BG1119/BG1120 share structure).
"""
import json
import sys
from pathlib import Path
from PIL import Image


def z(values):
    mean = sum(values) / len(values)
    std = (sum((x - mean) ** 2 for x in values) / len(values)) ** .5 or 1
    return [(x - mean) / std for x in values]


def main(signatures, shots, *prefixes):
    table = {name: z(values) for name, values in json.loads(Path(signatures).read_text()).items()
             if not prefixes or name.startswith(tuple(prefixes))}
    for path in sorted(Path(shots).glob('*.png')):
        image = Image.open(path).convert('L'); width, height = image.size
        region = image.crop((int(width * .05), int(height * .04), int(width * .95), int(height * .66))).resize((32, 20), Image.BOX)
        vector = z(list(region.tobytes()))
        ranked = sorted(((sum(a * b for a, b in zip(vector, other)) / len(vector), name) for name, other in table.items()), reverse=True)[:3]
        print(path.name, [(round(score, 2), name) for score, name in ranked])


if __name__ == '__main__':
    main(*sys.argv[1:])
