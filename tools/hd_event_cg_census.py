"""Offline census of the PC EVENT and CG images against every decodable Saturn image (THD09).

PC side: every subimage of `SAKURA2/EVENT/**.SPR` (tactical event actors, used through EVENTANM.TAB) and
`SAKURA3/CG/**.SPR` (mini-game art). Saturn side (both discs, read-only):

  plates   full pictures from tools/decode_saturn_bg.py (BG, BBG, EVE, IC, KABE, TITLE, OMAKE, LOAD, WALL,
           the eight mini-game backgrounds) and the records of the seven `*_CG.BIN` ending banks;
  sprites  every VDP1-style image set found in any `SAKURA1/SAKURA2/SAKURA3` file (the EVS event banks, N/H/G/GK
           character banks, UNIT, WKL, FIX, SYSSPR): palette indices, so they are compared by silhouette.

Three comparisons, all content based (no file-name rule):

  plate      32x16 luminance signature plus edge signature of the whole PC subimage against every plate
             (the PC picture is twice the Saturn one; the best of top / bottom / whole alignment counts);
  component  masked normalised cross-correlation of a PC subimage (halved or not) slid over every plate
             (small cut-outs, photographs inside other pictures);
  sprite     intersection over union of the opaque silhouette against every sprite image of similar size.

A PC file is `paired` when one of its subimages passes the firm thresholds (score high, clear margin, enough
texture), `ambiguous` when something correlates but not firmly, `no-counterpart` otherwise, always with a
reason. The output holds names, sizes, hashes, classes and scores only: no pixels.

  python tools/hd_event_cg_census.py --build --pc ROOT --disc1 ISO1 --disc2 ISO2   # slow, local data
  python tools/hd_event_cg_census.py --check                                       # offline, repository only
  python tools/hd_event_cg_census.py --check --pc ROOT                             # also re-hash the PC files
"""
import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
OUTPUT = 'config/hd-event-cg-census.json'
FOLDERS = {'EVENT': 'SAKURA2/EVENT', 'CG': 'SAKURA3/CG'}
CONTROL_FOLDERS = ('SAKURA1/ENDING', 'SAKURA1/ICATCH', 'SAKURA1/TITLE')

SIG = (32, 16)
MIN_PLATE_SIDE = 96          # PC subimage side (px) to be considered a plate
PLATE_FIRM = 0.95            # luminance correlation of a firm plate pair
PLATE_EDGE = 0.60            # edge correlation required next to it
PLATE_MARGIN = 0.05          # lead over the runner-up plate
PLATE_AMBIGUOUS = 0.80
COMPONENT_FIRM = 0.93        # masked NCC of a firm component pair
COMPONENT_AMBIGUOUS = 0.85
COMPONENT_MARGIN = 0.03
COMPONENT_MIN_SIDE = 16      # side of the template after scaling
COMPONENT_MIN_PIXELS = 400   # opaque pixels of the template after scaling
MIN_WINDOW_VARIANCE = 25.0   # plate windows flatter than this (std 5) never score
COMPONENT_EDGE = 0.45        # edge correlation required next to a firm component pair
COMPONENT_MIN_STD = 12.0     # luminance spread (0-255) of the template
SPRITE_FIRM = 0.93
SPRITE_AMBIGUOUS = 0.85
SPRITE_MARGIN = 0.02
SPRITE_MIN_PIXELS = 150
SPRITE_MAX_FILL = 0.96       # a (near) full rectangle says nothing about shape
THRESHOLDS = {
    'plate': {'firm': PLATE_FIRM, 'edge': PLATE_EDGE, 'margin': PLATE_MARGIN, 'ambiguous': PLATE_AMBIGUOUS},
    'component': {'firm': COMPONENT_FIRM, 'margin': COMPONENT_MARGIN, 'ambiguous': COMPONENT_AMBIGUOUS,
                  'min_side': COMPONENT_MIN_SIDE, 'min_pixels': COMPONENT_MIN_PIXELS, 'min_std': COMPONENT_MIN_STD},
    'sprite': {'firm': SPRITE_FIRM, 'margin': SPRITE_MARGIN, 'ambiguous': SPRITE_AMBIGUOUS,
               'min_pixels': SPRITE_MIN_PIXELS, 'max_fill': SPRITE_MAX_FILL},
}
CLASSES = ('paired', 'ambiguous', 'no-counterpart')


# ---------------------------------------------------------------- signatures and scores

def _zscore(values):
    values = np.asarray(values, dtype=np.float64).ravel()
    values = values - values.mean()
    norm = np.sqrt((values * values).sum())
    return values / norm if norm > 1e-9 else values * 0.0


def luma(image):
    """Float32 luminance (0-255) of an RGB(A) Pillow image."""
    return np.asarray(image.convert('L'), dtype=np.float32)


def edges(grey):
    """Gradient magnitude of a float luminance array (same shape, border replicated)."""
    padded = np.pad(grey, 1, mode='edge')
    gx = padded[1:-1, 2:] - padded[1:-1, :-2]
    gy = padded[2:, 1:-1] - padded[:-2, 1:-1]
    return np.hypot(gx, gy)


def signature(image):
    """(luminance, edge) z-scored 32x16 vectors of a Pillow image."""
    grey = image.convert('L')
    small = np.asarray(grey.resize(SIG, Image.BILINEAR), dtype=np.float64)
    wide = np.asarray(grey.resize((SIG[0] * 2, SIG[1] * 2), Image.BILINEAR), dtype=np.float64)
    edge = edges(wide.astype(np.float32))
    edge_small = edge.reshape(SIG[1], 2, SIG[0], 2).mean(axis=(1, 3))
    return _zscore(small), _zscore(edge_small)


def aligned_variants(image, plate_size):
    """The PC picture as the region a Saturn plate of `plate_size` covers.

    The PC art is about twice the Saturn size and often a few rows taller; when the aspect differs the
    picture is compared at its top, its bottom and whole.
    """
    pw, ph = plate_size
    width, height = image.size
    variants = [image]
    for scale in (2.0, 1.0):
        need = round(ph * width / pw)
        if height > need * 1.02 and abs(width / pw - scale) < 0.35:
            variants.append(image.crop((0, 0, width, need)))
            variants.append(image.crop((0, height - need, width, height)))
            break
    return variants


def plate_score(variants_signatures, plate_signature):
    """Best (luma, edge) correlation of the variants against one plate signature."""
    best = (-1.0, -1.0)
    for luma_sig, edge_sig in variants_signatures:
        score = (float(luma_sig @ plate_signature[0]), float(edge_sig @ plate_signature[1]))
        if score[0] > best[0]:
            best = score
    return best


def template_of(rgba, scale):
    """(grey float32, mask bool) of a PC subimage scaled by `scale`; None when unusable for NCC."""
    image = rgba.convert('RGBA')
    if scale != 1.0:
        size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
        image = image.resize(size, Image.BOX)
    arrays = np.asarray(image)
    mask = arrays[..., 3] > 127
    if mask.shape[0] < COMPONENT_MIN_SIDE or mask.shape[1] < COMPONENT_MIN_SIDE:
        return None
    if int(mask.sum()) < COMPONENT_MIN_PIXELS:
        return None
    grey = luma(image)
    if float(grey[mask].std()) < COMPONENT_MIN_STD:
        return None
    return grey, mask


def masked_ncc(plates_fft, plates_sq_fft, shape, grey, mask):
    """Best masked NCC of one template over a batch of plates.

    `plates_fft`/`plates_sq_fft` are rfft2 of the plates and of their squares (batch, H, W/2+1), computed at the
    plate size, so only positions where the template lies fully inside are valid (no wrap-around is used).
    Returns (scores, ys, xs) per plate.
    """
    height, width = shape
    th, tw = grey.shape
    if th > height or tw > width:
        return None
    m = mask.astype(np.float32)
    n = float(m.sum())
    mean = float((grey * m).sum() / n)
    t0 = (grey - mean) * m
    t_norm = float((t0 * t0).sum())
    if t_norm <= 1e-6:
        return None
    ft0 = np.conj(np.fft.rfft2(t0, s=shape))
    fm = np.conj(np.fft.rfft2(m, s=shape))
    num = np.fft.irfft2(plates_fft * ft0, s=shape)[:, :height - th + 1, :width - tw + 1]
    s1 = np.fft.irfft2(plates_fft * fm, s=shape)[:, :height - th + 1, :width - tw + 1]
    s2 = np.fft.irfft2(plates_sq_fft * fm, s=shape)[:, :height - th + 1, :width - tw + 1]
    var = np.maximum(s2 - s1 * s1 / n, n * MIN_WINDOW_VARIANCE)
    score = np.clip(num / np.sqrt(var * t_norm), -1.0, 1.0)
    flat = score.reshape(score.shape[0], -1)
    best = flat.argmax(axis=1)
    width_valid = score.shape[2]
    return (flat[np.arange(flat.shape[0]), best], best // width_valid, best % width_valid)


def edge_agreement(grey, mask, window):
    """Masked correlation of the gradient magnitudes of a template and the plate window it matched."""
    a, b = edges(grey)[mask], edges(window)[mask]
    return float(_zscore(a) @ _zscore(b)) if a.size > 8 else 0.0


def mask_bbox(mask):
    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        return None
    return int(ys.min()), int(ys.max()) + 1, int(xs.min()), int(xs.max()) + 1


def silhouette_iou(a, b):
    """Intersection over union of two equally sized boolean arrays."""
    union = int(np.logical_or(a, b).sum())
    return float(np.logical_and(a, b).sum()) / union if union else 0.0


class SpriteIndex:
    """Saturn sprite silhouettes bucketed by their bounding-box size."""

    def __init__(self):
        self.buckets = defaultdict(list)
        self.seen = set()

    def add(self, name, mask):
        box = mask_bbox(mask)
        if box is None:
            return
        y0, y1, x0, x1 = box
        crop = mask[y0:y1, x0:x1]
        if crop.size < 16 or int(crop.sum()) < SPRITE_MIN_PIXELS:
            return
        digest = hashlib.sha256(np.packbits(crop).tobytes() + repr(crop.shape).encode()).digest()[:12]
        if digest in self.seen:
            return
        self.seen.add(digest)
        self.buckets[crop.shape[::-1]].append((name, crop, int(crop.sum()) / crop.size))

    def best(self, mask, scales=(1.0, 0.5)):
        """[(iou, name, scale)] best two distinct names over the scales for a PC opaque mask."""
        box = mask_bbox(mask)
        if box is None:
            return []
        y0, y1, x0, x1 = box
        crop = mask[y0:y1, x0:x1]
        found = {}
        for scale in scales:
            width, height = max(1, round(crop.shape[1] * scale)), max(1, round(crop.shape[0] * scale))
            if width * height < 16:
                continue
            scaled = np.asarray(Image.fromarray(crop.astype(np.uint8) * 255).resize((width, height), Image.BOX)) > 127
            if int(scaled.sum()) < SPRITE_MIN_PIXELS:
                continue
            for dw in (-1, 0, 1):
                for dh in (-1, 0, 1):
                    for name, candidate, fill in self.buckets.get((width + dw, height + dh), ()):
                        aligned = scaled
                        if candidate.shape != scaled.shape:
                            aligned = np.asarray(Image.fromarray(scaled.astype(np.uint8) * 255).resize(
                                candidate.shape[::-1], Image.NEAREST)) > 127
                        iou = silhouette_iou(aligned, candidate)
                        if iou > found.get(name, (0, 0))[0]:
                            found[name] = (iou, scale, fill)
        ranked = sorted(((v[0], k, v[1], v[2]) for k, v in found.items()), reverse=True)
        return ranked[:2]


# ---------------------------------------------------------------- Saturn side

HEROINE_RECORDS = ((0x00000, 320, 120), (0x0A1A0, 320, 120), (0x14340, 112, 120), (0x17D48, 136, 80),
                   (0x1ACB0, 88, 80), (0x1CC28, 88, 104), (0x1F464, 320, 160), (0x2CB24, 320, 160),
                   (0x3A1E4, 320, 160), (0x478A4, 320, 160), (0x54F64, 64, 64), (0x562A4, 320, 160))
GENERAL_RECORDS = tuple((n * 76672, 320, 224) for n in range(4))
ENDING_BANKS = {'GE': (GENERAL_RECORDS, 0)}
ENDING_BANKS.update({code: (HEROINE_RECORDS, 1) for code in ('AI', 'KA', 'KO', 'MA', 'SA', 'SU')})


def decode_record(data, offset, width, height, skip_tiles):
    """One ending-bank record: 256 RGB555 words, an identity name table, then 8x8 8 bpp tiles."""
    cells = width * height // 64
    palette_at, tiles_at = offset, offset + 512 + cells * 4 + skip_tiles * 64
    if tiles_at + cells * 64 > len(data):
        return None
    pixels = np.frombuffer(data, np.uint8, cells * 64, tiles_at)
    index = pixels.reshape(height // 8, width // 8, 8, 8).transpose(0, 2, 1, 3).reshape(height, width)
    words = np.frombuffer(data, '>u2', 256, palette_at).astype(np.uint32)
    table = np.stack([(words & 31) * 255 // 31, ((words >> 5) & 31) * 255 // 31, ((words >> 10) & 31) * 255 // 31], 1)
    return Image.fromarray(table.astype(np.uint8)[index], 'RGB')


def ending_records(name, data):
    code = re.match(r'(AI|GE|KA|KO|MA|SA|SU)_CG\.BIN$', name)
    if not code:
        return []
    records, skip = ENDING_BANKS[code.group(1)]
    out = []
    for number, (offset, width, height) in enumerate(records):
        image = decode_record(data, offset, width, height, skip)
        if image is not None:
            out.append((f'{name}#{number}', image))
    return out


def image_sets(data):
    """Yield (offset, [(index, width, height, pixels uint8 array)]) for every plausible VDP1-style image set."""
    size = len(data)
    zeros = re.compile(rb'\x00{14}')
    for match in zeros.finditer(data):
        at = match.start() - 2
        if at < 0 or at % 2:
            continue
        count = (data[at] << 8) | data[at + 1]
        if not 1 <= count <= 400:
            continue
        end = at + 16 + 16 * count
        if end > size:
            continue
        records, ok = [], True
        for n in range(count):
            width, height, fmt, _colour, offset, length = struct.unpack_from('>HHHHII', data, at + 16 + 16 * n)
            if width == 0 and height == 0 and length == 0:
                continue
            if not (1 <= width <= 640 and 1 <= height <= 480 and fmt in (0, 4)
                    and length > 0 and (fmt == 4 or width * height % 2 == 0)
                    and length == (width * height if fmt == 4 else width * height // 2)
                    and end + offset + length <= size):
                ok = False
                break
            raw = np.frombuffer(data, np.uint8, length, end + offset)
            if fmt == 0:
                raw = np.stack([raw >> 4, raw & 15], 1).reshape(-1)
            records.append((n, width, height, raw.reshape(height, width)))
        if ok and records:
            yield at, records


def saturn_pool(isos):
    """(plates {name: [(image, key)]...}, SpriteIndex, counts) from the prepared Saturn discs."""
    import decode_saturn_bg as saturn
    plates, plate_names, sprites = {}, defaultdict(list), SpriteIndex()
    counts = Counter()
    for disc, iso_path in isos:
        iso = saturn.Iso(iso_path)
        for folder in ('SAKURA1', 'SAKURA2', 'SAKURA3'):
            for name, extent in iso.files(folder):
                if name.endswith(('.SND', '.DAT', '.ADP', '.WAV')) or extent[1] > 3_000_000:
                    continue
                data = iso.content(extent)
                label = f'{folder}/{name}'
                images = []
                if name.endswith('.BIN'):
                    image = saturn.decode(data)
                    if image is not None:
                        images.append((label, image))
                    images.extend((f'{folder}/{n}', i) for n, i in ending_records(name, data))
                for key, image in images:
                    digest = hashlib.sha256(image.tobytes() + repr(image.size).encode()).hexdigest()
                    if digest not in plates:
                        plates[digest] = image
                    plate_names[digest].append(f'd{disc}:{key}')
                for at, records in image_sets(data):
                    for number, _w, _h, pixels in records:
                        sprites.add(f'd{disc}:{label}@{at:#x}#{number}', pixels != 0)
    ordered = sorted(plates, key=lambda d: sorted(plate_names[d])[0])
    counts['plates'] = len(ordered)
    counts['plate_occurrences'] = sum(len(v) for v in plate_names.values())
    counts['sprite_masks'] = len(sprites.seen)
    return [(plate_names[d], plates[d]) for d in ordered], sprites, dict(counts)


# ---------------------------------------------------------------- PC side

def pc_files(pc_root, folders):
    out = []
    for folder in folders:
        out.extend(sorted(p for p in (pc_root / folder).rglob('*') if p.is_file() and p.suffix.lower() == '.spr'))
    return out


def decode_pc(path):
    import decode_spred
    raw = path.read_bytes()
    try:
        images = decode_spred.decode(raw)
    except (ValueError, IndexError, struct.error):
        return raw, None
    return raw, images




RANK = {name: number for number, name in enumerate(CLASSES)}


def classify_scores(best, runner, firm, ambiguous, margin):
    """`paired` needs a high score and a clear lead; `ambiguous` any score above the floor."""
    if best >= firm and best - runner >= margin:
        return 'paired'
    if best >= ambiguous:
        return 'ambiguous'
    return 'no-counterpart'


def best_candidate(candidates):
    """The strongest (method, class, score, runner_up, counterpart, extra) tuple: class first, then score."""
    return min(candidates, key=lambda c: (RANK[c[1]], -c[2]))


def file_class(images):
    """Class of a PC file from its subimage rows: the best class of any subimage."""
    classes = [row['class'] for row in images]
    for name in CLASSES:
        if name in classes:
            return name
    return 'no-counterpart'


def _plate_worker(args):
    """Masked NCC of templates over one batch of same-size plates (process pool worker)."""
    plate_arrays, templates = args
    batch = np.stack(plate_arrays).astype(np.float32)
    batch -= batch.mean(axis=(1, 2), keepdims=True)
    shape = batch.shape[1:]
    fft = np.fft.rfft2(batch)
    fft_sq = np.fft.rfft2(batch * batch)
    out = []
    for key, grey, mask in templates:
        found = masked_ncc(fft, fft_sq, shape, grey, mask)
        out.append((key, None if found is None else tuple(np.asarray(x) for x in found)))
    return out


def component_search(plates, templates, workers, progress):
    """{template key: [(score, plate index, y, x)]} for every template over every plate."""
    groups = defaultdict(list)
    for index, (_names, image) in enumerate(plates):
        groups[image.size].append(index)
    keys = sorted(templates)
    jobs = []
    with ProcessPoolExecutor(workers) as pool:
        for size, members in groups.items():
            for at in range(0, len(members), 48):
                chunk = members[at:at + 48]
                arrays = [luma(plates[i][1]) for i in chunk]
                for start in range(0, len(keys), 250):
                    part = [(k, *templates[k]) for k in keys[start:start + 250]
                            if templates[k][0].shape[0] <= size[1] and templates[k][0].shape[1] <= size[0]]
                    if part:
                        jobs.append((chunk, pool.submit(_plate_worker, (arrays, part))))
        found = defaultdict(list)
        for number, (chunk, future) in enumerate(jobs):
            for key, result in future.result():
                if result is None:
                    continue
                scores, ys, xs = result
                for slot, plate_index in enumerate(chunk):
                    found[key].append((float(scores[slot]), plate_index, int(ys[slot]), int(xs[slot])))
            if number % 100 == 0:
                progress(f'component jobs {number}/{len(jobs)}')
    return found


def image_row(number, image, plates, plate_signatures, found, sprites):
    """Classify one PC subimage. `found` maps (index, scale) to the component search results."""
    rgba = np.asarray(image.convert('RGBA'))
    opaque = rgba[..., 3] > 127
    fill = float(opaque.mean())
    row = {'index': number, 'size': list(image.size), 'pixels_sha256': hashlib.sha256(rgba.tobytes()).hexdigest()[:16],
           'opaque': round(fill, 3)}
    candidates = []
    if min(image.size) >= MIN_PLATE_SIDE and fill > 0.5:
        rgb = image.convert('RGB')
        by_size, scored = {}, []
        for index, (_names, plate) in enumerate(plates):
            if plate.size not in by_size:
                by_size[plate.size] = [signature(v) for v in aligned_variants(rgb, plate.size)]
            scored.append((plate_score(by_size[plate.size], plate_signatures[index]), index))
        scored.sort(key=lambda t: -t[0][0])
        (luma_score, edge_score), top = scored[0]
        runner = next((s[0][0] for s in scored[1:] if plates[s[1]][0][0] != plates[top][0][0]), 0.0)
        cls = classify_scores(luma_score, runner, PLATE_FIRM, PLATE_AMBIGUOUS, PLATE_MARGIN)
        if cls == 'paired' and edge_score < PLATE_EDGE:
            cls = 'ambiguous'
        candidates.append(('plate', cls, luma_score, runner, plates[top][0][0], {'edge': round(edge_score, 3)}))
    for scale in (0.5, 1.0):
        ranked = sorted(found.get((number, scale), ()), key=lambda t: -t[0])
        if not ranked:
            continue
        score, index, y, x = ranked[0]
        runner = next((s for s, i, _y, _x in ranked[1:] if plates[i][0][0] != plates[index][0][0]), 0.0)
        cls = classify_scores(score, runner, COMPONENT_FIRM, COMPONENT_AMBIGUOUS, COMPONENT_MARGIN)
        template = template_of(image, scale)
        edge = 0.0
        if template is not None and score >= COMPONENT_AMBIGUOUS:
            grey, mask = template
            edge = edge_agreement(grey, mask, luma(plates[index][1])[y:y + grey.shape[0], x:x + grey.shape[1]])
            if cls == 'paired' and edge < COMPONENT_EDGE:
                cls = 'ambiguous'
        candidates.append(('component', cls, score, runner, plates[index][0][0],
                           {'scale': scale, 'at': [x, y], 'edge': round(edge, 3)}))
    ranked_sprites = sprites.best(opaque) if fill > 0 else []
    if ranked_sprites:
        iou, other, scale, other_fill = ranked_sprites[0]
        runner = ranked_sprites[1][0] if len(ranked_sprites) > 1 else 0.0
        cls = classify_scores(iou, runner, SPRITE_FIRM, SPRITE_AMBIGUOUS, SPRITE_MARGIN)
        if other_fill >= SPRITE_MAX_FILL:
            cls = 'ambiguous' if iou >= SPRITE_AMBIGUOUS else 'no-counterpart'
        candidates.append(('sprite', cls, iou, runner, other, {'scale': scale}))
    if candidates:
        method, cls, score, runner, other, extra = best_candidate(candidates)
        row.update({'class': cls, 'method': method, 'score': round(score, 3), 'runner_up': round(runner, 3),
                    'counterpart': other, **extra, 'methods': {c[0]: round(c[2], 3) for c in candidates}})
    else:
        row.update({'class': 'no-counterpart', 'method': 'none'})
    return row


def build(pc_root, isos, workers=16, limit=None, progress=print):
    from scene_file_queue import event_references
    plates, sprites, pool = saturn_pool(isos)
    progress(f'Saturn pool: {pool}')
    plate_signatures = [signature(image) for _names, image in plates]
    paths = pc_files(pc_root, list(FOLDERS.values()) + list(CONTROL_FOLDERS))
    every = {p.relative_to(pc_root).as_posix() for p in paths}
    if limit:
        paths = paths[::max(1, len(paths) // limit)]
    decoded = {p.relative_to(pc_root).as_posix(): decode_pc(p) for p in paths}
    templates = {}
    for name, (_raw, images) in decoded.items():
        for number, image in images or ():
            for scale in (0.5, 1.0):
                template = template_of(image, scale)
                if template is not None:
                    templates[(name, number, scale)] = template
    progress(f'{len(templates)} component templates over {len(plates)} plates')
    found = component_search(plates, templates, workers, progress)
    per_file = defaultdict(dict)
    for (name, number, scale), values in found.items():
        per_file[name][(number, scale)] = values
    references = event_references((pc_root / 'SAKURA2/EVENTANM.TAB').read_text(encoding='cp932'), every)
    files = []
    for name, (raw, images) in sorted(decoded.items()):
        folder = next((k for k, v in FOLDERS.items() if name.startswith(v + '/')), 'control')
        entry = {'file': name, 'folder': folder, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        if images is None:
            entry.update(images=[], decoder='unsupported')
        else:
            entry['images'] = [image_row(n, im, plates, plate_signatures, per_file[name], sprites) for n, im in images]
        entry['class'] = file_class(entry['images']) if entry['images'] else 'no-counterpart'
        if name in references:
            entry['event_references'] = len(references[name])
        files.append(entry)
    return {'pool': pool, 'files': files}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--pc', type=Path)
    parser.add_argument('--disc1')
    parser.add_argument('--disc2')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    if not args.build:
        parser.error('only --build exists in this partial version (THD09 draft)')
    result = build(args.pc, [(1, args.disc1), (2, args.disc2)], limit=args.limit)
    (ROOT / OUTPUT).write_text(json.dumps({'schema': 1, 'thresholds': THRESHOLDS, **result}, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
