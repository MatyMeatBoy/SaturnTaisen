"""T98/S1: map each Saturn FILM stream (by the start FAD of its CD play command) to its PC MOVIEnnn.MPG.

FAD = 150 + LBA + byte_offset / 2048. The Saturn streams come from local/work/scene-index/resource-inventory.json (both discs,
/SAKURA4 archive and the stand-alone .CPK films); the durations of both sides are measured with ffprobe (the Saturn bytes are read
from the disc ISOs, never written out of a temp folder). The pairing is the monotone alignment of the two duration sequences
(Saturn order against PC name order) with a penalty for a stream left unpaired; a pair whose durations differ by more than
0.5 s is flagged `alternate_cut` (a different edit of the same scene).

Writes config/film-fad-map.json: names, FADs and durations only, no game data.

    python tools/gen_film_fad_map.py --iso1 "local/prepared/disc1/Track 01.iso" --iso2 "local/prepared/disc2/Track 01.iso" \
        --pc-movies "<folder with MOVIE*.MPG>" --ffprobe ffprobe
"""
import argparse, hashlib, json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def duration(ffprobe, path):
    out = subprocess.run([ffprobe, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def align(saturn, pc, gap=10.0):
    """Monotone alignment minimising |duration difference| + gap per unpaired stream on either side."""
    n, m = len(saturn), len(pc)
    cost = [[0.0] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        cost[i][0] = i * gap; back[i][0] = 'S'
    for j in range(1, m + 1):
        cost[0][j] = j * gap; back[0][j] = 'P'
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            options = [(cost[i - 1][j - 1] + abs(saturn[i - 1] - pc[j - 1]), 'B'),
                       (cost[i - 1][j] + gap, 'S'), (cost[i][j - 1] + gap, 'P')]
            cost[i][j], back[i][j] = min(options)
    pairs, i, j = [], n, m
    while i > 0 or j > 0:
        step = back[i][j]
        if step == 'B':
            pairs.append((i - 1, j - 1)); i -= 1; j -= 1
        elif step == 'S':
            i -= 1
        else:
            j -= 1
    return pairs[::-1]


def find_pc_aliases(unpaired, paired, paths):
    sizes = {name: paths[name].stat().st_size for name in (*unpaired, *paired)}
    aliases = {}
    for name in unpaired:
        candidates = [target for target in paired if sizes[target] == sizes[name]]
        if not candidates:
            continue
        with paths[name].open('rb') as source:
            digest = hashlib.file_digest(source, 'sha256').hexdigest()
        for target in candidates:
            with paths[target].open('rb') as source:
                if hashlib.file_digest(source, 'sha256').hexdigest() == digest:
                    aliases[name] = {'canonical': target, 'sha256': digest}
                    break
    return aliases


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--iso1', required=True); ap.add_argument('--iso2', required=True)
    ap.add_argument('--pc-movies', required=True); ap.add_argument('--ffprobe', default='ffprobe')
    ap.add_argument('--inventory', default=str(ROOT / 'local/work/scene-index/resource-inventory.json'))
    ap.add_argument('--out', default=str(ROOT / 'config/film-fad-map.json'))
    a = ap.parse_args()
    inv = json.load(open(a.inventory, encoding='utf8'))
    inv = inv if isinstance(inv, list) else inv.get('resources', inv)
    isos = {1: open(a.iso1, 'rb'), 2: open(a.iso2, 'rb')}
    streams, seen = [], {}
    with tempfile.TemporaryDirectory() as tmp:
        for r in sorted(inv, key=lambda r: (r['disc'], r['lba'])):
            for index, v in enumerate(r.get('video_streams') or []):
                if v.get('format') != 'sega_film':
                    continue
                fad = 150 + r['lba'] + v.get('offset', 0) // 2048
                key = v.get('sha256', fad)
                if key in seen:
                    # The same film stored again (another disc or archive): own FAD, same clip as the first copy.
                    streams.append({'disc': r['disc'], 'file': r['iso_path'], 'index': index, 'fad': fad,
                                    'fad_hex': '0x%X' % fad, 'sectors': -(-v['byte_length'] // 2048), 'same_as_fad': seen[key]})
                    continue
                seen[key] = fad
                iso = isos[r['disc']]; iso.seek(r['lba'] * 2048 + v.get('offset', 0))
                p = pathlib.Path(tmp) / 'clip.cpk'; p.write_bytes(iso.read(v['byte_length']))
                streams.append({'disc': r['disc'], 'file': r['iso_path'], 'index': index, 'fad': fad,
                                'fad_hex': '0x%X' % fad, 'sectors': -(-v['byte_length'] // 2048), 'duration': duration(a.ffprobe, p)})
    pc_paths = {f.stem: f for f in sorted(pathlib.Path(a.pc_movies).glob('*.MPG'))}
    pc = [{'name': name, 'duration': duration(a.ffprobe, path)} for name, path in pc_paths.items()]
    stub = [s for s in streams if 'same_as_fad' not in s and s['duration'] is not None and s['duration'] < 0.5]
    real = [s for s in streams if s not in stub and 'same_as_fad' not in s]
    pcreal = [c for c in pc if c['name'] != 'REDLOGO']
    pairs = align([s['duration'] for s in real], [c['duration'] for c in pcreal])
    paired = set()
    for i, j in pairs:
        real[i]['movie'] = pcreal[j]['name']; real[i]['pc_duration'] = pcreal[j]['duration']
        real[i]['alternate_cut'] = abs(real[i]['duration'] - pcreal[j]['duration']) > 0.5
        paired.add(j)
    # Streams the monotone alignment left out (disc 2 stores FINAL before FLY, the PC numbers them the other way round):
    # pair each with the nearest unpaired PC clip within 4 s, closest first.
    free = [j for j in range(len(pcreal)) if j not in paired]
    loose = [s for s in real if 'movie' not in s]
    candidates = sorted(((abs(s['duration'] - pcreal[j]['duration']), id(s), j, s) for s in loose for j in free if abs(s['duration'] - pcreal[j]['duration']) <= 4.0), key=lambda c: c[0])
    for diff, _, j, s in candidates:
        if 'movie' in s or j in paired:
            continue
        s['movie'] = pcreal[j]['name']; s['pc_duration'] = pcreal[j]['duration']; s['alternate_cut'] = diff > 0.5; paired.add(j)
    by_fad = {s['fad']: s for s in streams}
    for s in streams:
        if 'same_as_fad' in s:
            first = by_fad[s['same_as_fad']]
            for k in ('duration', 'movie', 'pc_duration', 'alternate_cut'):
                if k in first:
                    s[k] = first[k]
    paired_names = [clip['name'] for j, clip in enumerate(pcreal) if j in paired]
    unpaired_names = [clip['name'] for j, clip in enumerate(pcreal) if j not in paired]
    aliases = find_pc_aliases(unpaired_names, paired_names, pc_paths)
    result = {'formula': 'FAD = 150 + LBA + byte_offset / 2048', 'streams': streams,
              'unpaired_pc': [name for name in unpaired_names if name not in aliases] + ['REDLOGO'],
              'pc_aliases': aliases,
              'unpaired_saturn': [s for s in real if 'movie' not in s]}
    pathlib.Path(a.out).write_text(json.dumps(result, indent=1) + '\n', encoding='utf8')
    print(len(streams), 'saturn streams,', sum(1 for s in streams if 'movie' in s), 'paired, unpaired pc:', result['unpaired_pc'])


if __name__ == '__main__':
    sys.exit(main())
