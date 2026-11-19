"""Prepare local Enhanced Spanish episode centers from the installed Saturn discs."""

from collections import Counter
from pathlib import Path
import os
from tempfile import NamedTemporaryFile

from PIL import Image, ImageChops, ImageFilter

from decode_saturn_bg import Iso, decode


def fnv1a(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016X}"


def paint_episode_center(native, lettering, episode):
    """Remove English glyphs within the title area and composite the Spanish lettering."""
    native = native.convert("RGB")
    if native.size != (320, 224) or lettering.mode != "RGBA" or lettering.size != native.size:
        raise ValueError(f"Unexpected image geometry for Episode {episode}")

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
    base = base.convert("RGBA")
    base.alpha_composite(lettering)
    return base


def prepare_episode_centers(english_track, spanish_track, lettering_folder, destination):
    """Key local centers by the full Spanish TITLE bytes, which differ from English."""
    english, spanish = Iso(english_track), Iso(spanish_track)
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
            center = paint_episode_center(decode(en), lettering, episode)
        with NamedTemporaryFile(prefix=output.stem, suffix=".tmp", dir=destination, delete=False) as file:
            temporary = Path(file.name)
        try:
            center.save(temporary, format="PNG")
            os.replace(temporary, output)
        finally:
            temporary.unlink(missing_ok=True)
        outputs.append(output)
    return outputs
