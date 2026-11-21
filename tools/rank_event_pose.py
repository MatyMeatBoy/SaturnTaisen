"""Rank local PC EVENT sprites against one verified Saturn strip group."""

import argparse
import json
from pathlib import Path

from PIL import Image

from audit_event_strips import event_banks, observed_groups
from decode_spred import decode


def native_mask(bank, strips):
    left = min(strip['x'] for strip in strips)
    top = min(strip['y'] for strip in strips)
    right = max(strip['x'] + 8 for strip in strips)
    bottom = max(strip['y'] + strip['height'] for strip in strips)
    mask = Image.new('L', (right - left, bottom - top))
    for strip in strips:
        offset, height = strip['offset'], strip['height']
        data = bank[offset:offset + 8 * height]
        image = Image.frombytes('L', (8, height), bytes(255 if v else 0 for v in data))
        mask.paste(image, (strip['x'] - left, strip['y'] - top))
    return mask


def normalized(mask):
    bounds = mask.getbbox()
    return mask.crop(bounds).resize((72, 96), Image.Resampling.NEAREST).tobytes() if bounds else b''


def occupied(mask):
    return {index for index, value in enumerate(normalized(mask)) if value}


def donor_mask(image):
    pixels = iter(image.tobytes())
    return Image.frombytes('L', image.size, bytes(
        255 if a and (r, g, b) != (0, 255, 255) else 0
        for r, g, b, a in zip(pixels, pixels, pixels, pixels)
    ))


def rank_pose(target, root, donors=None):
    reference = occupied(target)
    if not reference:
        raise ValueError('Empty Saturn silhouette')
    ranked, skipped = [], {}
    paths = sorted(root.glob('MAP*/EV*.SPR')) if donors is None else sorted(set(donors))
    for path in paths:
        name = path.relative_to(root).as_posix()
        try:
            images = decode(path.read_bytes())
        except (OSError, ValueError, IndexError) as error:
            skipped[name] = str(error)
            continue
        for ordinal, image in images:
            candidate = occupied(donor_mask(image))
            if not candidate:
                continue
            overlap = len(reference & candidate)
            union = len(reference) + len(candidate) - overlap
            ranked.append(dict(donor=name, image=ordinal, iou=overlap / union))
    ranked.sort(key=lambda row: (-row['iou'], row['donor'], row['image']))
    return ranked, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--bank', required=True)
    parser.add_argument('--slot', type=int, required=True)
    parser.add_argument('--event-root', type=Path, required=True)
    parser.add_argument('--donor', action='append', type=Path, help='Path relative to EVENT root')
    args = parser.parse_args()
    name = args.bank.upper()
    banks = event_banks(args.iso, name)
    groups = [group for group in observed_groups(args.state.read_bytes(), banks)
              if group['bank'] == name and group['image_slot'] == args.slot]
    if len(groups) != 1:
        parser.error(f'Expected one witnessed pose, found {len(groups)}')
    donors = [args.event_root / path for path in args.donor] if args.donor else None
    ranks, skipped = rank_pose(native_mask(banks[name], groups[0]['strips']), args.event_root, donors)
    if not ranks:
        parser.error('No decodable nonempty PC silhouettes in the selected scope')
    print(json.dumps(dict(witness=groups[0], candidates=ranks, skipped=skipped), indent=2))


if __name__ == '__main__':
    main()
