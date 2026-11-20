"""Prepare local Enhanced Spanish episode centers from the installed Saturn discs."""

from collections import Counter
from contextlib import ExitStack
from pathlib import Path
import os
import struct
from tempfile import NamedTemporaryFile

from PIL import Image, ImageChops, ImageFilter

from decode_saturn_bg import Iso, decode


CARD_SIZE = (320, 224)
TITLE_AREA = (12, 46, 308, 182)


def fnv1a(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016X}"


def _english_cleanup(native, episode):
    area = (15, 55, 310, 170)
    inside = Counter(native.crop(area).getdata())
    outside = Counter(native.getdata()) - inside
    type_colors = {color for color, count in inside.items()
                   if count >= 12 and outside[color] <= 0.02 * count}
    mask = Image.new("L", native.size)
    if episode == 7:
        mask.paste(255, (0, 60, 320, 170))
    else:
        pixels = native.load()
        for y in range(area[1], area[3]):
            for x in range(area[0], area[2]):
                if pixels[x, y] in type_colors:
                    mask.putpixel((x, y), 255)
    preserve = ImageChops.invert(mask.filter(ImageFilter.MaxFilter(5)))
    base = native.copy()
    for _ in range(60):
        base = Image.composite(native, base.filter(ImageFilter.GaussianBlur(3)), preserve)
    return base


def _in_title_area(bounds):
    return (bounds is not None and TITLE_AREA[0] <= bounds[0] < bounds[2] <= TITLE_AREA[2]
            and TITLE_AREA[1] <= bounds[1] < bounds[3] <= TITLE_AREA[3])


def _ink_mask(source, other, episode):
    mask = Image.new("L", CARD_SIZE)
    ink, pixels, reference = mask.load(), source.load(), other.load()
    left, top, right, bottom = TITLE_AREA
    for y in range(top, bottom):
        for x in range(left, right):
            r, g, b = rgb = pixels[x, y]
            if rgb == reference[x, y]:
                continue
            white = min(rgb) >= 246
            pink = episode in (1, 8) and r >= 222 and r - g >= 30 and r > b >= 147
            red = episode == 6 and rgb == (148, 0, 0)
            if white or pink or red:
                ink[x, y] = 255
    return mask.filter(ImageFilter.MaxFilter(13))


def _fill_overlap(base, overlap):
    bounds = overlap.getbbox()
    if bounds is None:
        return base
    source = base.copy()
    pixels, missing, output = source.load(), overlap.load(), base.load()
    left, top, right, bottom = bounds
    # Both masks are inset from the image edges. Start at the nearest known
    # pixel in each direction so no old glyph color is blended into the result.
    for y in range(top, bottom):
        for x in range(left, right):
            if not missing[x, y]:
                continue
            samples = []
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                xx, yy, distance = x + dx, y + dy, 1
                while missing[xx, yy]:
                    xx, yy, distance = xx + dx, yy + dy, distance + 1
                samples.append((pixels[xx, yy], 1 / (distance ** 2 * (dx * dx + dy * dy))))
            weights = sum(weight for _, weight in samples)
            output[x, y] = tuple(
                round(sum(pixel[channel] * weight for pixel, weight in samples) / weights)
                for channel in range(3)
            )
    for _ in range(10):
        base = Image.composite(base.filter(ImageFilter.BoxBlur(1)), base, overlap)
    return base


def _aligned_cleanup(english, japanese, episode):
    en_ink = _ink_mask(english, japanese, episode)
    ja_ink = _ink_mask(japanese, english, episode)
    donor = ImageChops.subtract(en_ink, ja_ink)
    overlap = ImageChops.darker(en_ink, ja_ink)
    return _fill_overlap(Image.composite(japanese, english, donor), overlap)


def paint_episode_center(native, lettering, episode, *, japanese=None):
    """Recover a local plate before compositing the approved Spanish lettering."""
    native = native.convert("RGB")
    if native.size != CARD_SIZE or lettering.mode != "RGBA" or lettering.size != CARD_SIZE:
        raise ValueError(f"Unexpected image geometry for Episode {episode}")
    if japanese is not None and japanese.size == CARD_SIZE:
        japanese = japanese.convert("RGB")
    else:
        japanese = None

    if episode == 7 and _in_title_area(native.getbbox()):
        base = Image.new("RGB", CARD_SIZE)
    elif japanese is not None and _in_title_area(ImageChops.difference(native, japanese).getbbox()):
        base = _aligned_cleanup(native, japanese, episode)
    else:
        base = _english_cleanup(native, episode)
    base = base.convert("RGBA")
    base.alpha_composite(lettering)
    return base


def prepared_japanese_track(english_track):
    candidate = english_track.parent.parent / "disc1-ja" / "Track 01.iso"
    return candidate if candidate.is_file() else None


def _optional_japanese_iso(english_track, japanese_track, stack):
    track = japanese_track if japanese_track is not None else prepared_japanese_track(english_track)
    if track is None:
        return None
    try:
        iso = Iso(track)
    except (OSError, ValueError, struct.error):
        return None
    stack.enter_context(iso.file)
    return iso


def _japanese_card(iso, name):
    if iso is None:
        return None
    try:
        extent = iso.find(name)
        return decode(iso.content(extent)) if extent is not None else None
    except (OSError, ValueError, IndexError, struct.error):
        return None


def prepare_episode_centers(english_track, spanish_track, lettering_folder, destination, *, japanese_track=None):
    """Key local centers by the full Spanish TITLE bytes, which differ from English."""
    with ExitStack() as stack:
        english = Iso(english_track)
        stack.enter_context(english.file)
        spanish = Iso(spanish_track)
        stack.enter_context(spanish.file)
        japanese = _optional_japanese_iso(english_track, japanese_track, stack)
        destination.mkdir(parents=True, exist_ok=True)
        outputs = []
        for episode in range(1, 11):
            name = f"SAKURA1/TITLE{episode}.BIN"
            en_extent, es_extent = english.find(name), spanish.find(name)
            if en_extent is None or es_extent is None:
                raise ValueError(f"Missing {name} in the prepared disc pair")
            en, es = english.content(en_extent), spanish.content(es_extent)
            if en == es or en[:512] != es[:512]:
                raise ValueError(f"Unexpected English and Spanish TITLE{episode} pairing")
            source = lettering_folder / f"EPISODE{episode:02}-es-lettering-v1.png"
            output = destination / f"EPISODE{episode:02}-{fnv1a(es)}-es.png"
            with Image.open(source) as lettering:
                center = paint_episode_center(decode(en), lettering, episode, japanese=_japanese_card(japanese, name))
            with NamedTemporaryFile(prefix=output.stem, suffix=".tmp", dir=destination, delete=False) as file:
                temporary = Path(file.name)
            try:
                center.save(temporary, format="PNG")
                os.replace(temporary, output)
            finally:
                temporary.unlink(missing_ok=True)
            outputs.append(output)
        return outputs
