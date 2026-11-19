"""Build config/hd-scene-bg-map.json: Saturn BG*.BIN <-> PC BG*.SPR by file number (T67/T74).

Evidence: the 12 pairs confirmed by eye in config/hd-scene-bg-pairs.json all share the file number, so
`BGnnnn.BIN` is paired with `BGnnnn.SPR`. Each pair is then scored on content (see match_bg_files.py):
  tier `content`   same-number PC picture is also the best content match, or scores <= 0.10
  tier `number`    same number only; content differs (other crop, lighting or palette variant): needs the
                   runtime or an eye check before it may be drawn
The runtime key is `cells_sha256`, the SHA-256 of the 41,472 picture bytes (0x50..0xA250) that the game
copies to VDP2 as 8x8 8 bpp cells. Data only: identifiers, hashes and scores, no pixels.

Usage: python tools/build_bg_map.py ISO PC_BG_DIR --cache DIR OUT.json
"""
import argparse, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn
import match_bg_files as match


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('iso', type=Path); p.add_argument('pc_bg', type=Path); p.add_argument('output', type=Path)
    p.add_argument('--cache', type=Path); p.add_argument('--folder', default='SAKURA1')
    a = p.parse_args()
    pc = match.pc_signatures(a.pc_bg, a.cache)
    by_name = {}
    for (name, index), value in pc.items():
        by_name.setdefault(name, []).append(((name, index), value))
    iso = saturn.Iso(a.iso)
    entries, unpaired = [], []
    for name, extent in iso.files(a.folder):
        if not (name.startswith('BG') and name.endswith('.BIN')):
            continue
        data = iso.content(extent); image = saturn.decode(data)
        if image is None:
            continue
        sig = match.signature(image)
        pc_name = name[:-4] + '.SPR'
        if pc_name not in by_name:
            unpaired.append(f'{a.folder}/{name}'); continue
        (key, (sha, top, bottom)) = by_name[pc_name][0]
        own = min(match.score(sig, top), match.score(sig, bottom))
        best = min((min(match.score(sig, t), match.score(sig, b)), k) for k, (_, t, b) in pc.items())
        tier = 'content' if best[1][0] == pc_name or own <= 0.10 else 'number'
        entries.append({
            'saturn_file': f'{a.folder}/{name}',
            'cells_sha256': hashlib.sha256(data[saturn.HEADER:saturn.PALETTE_AT]).hexdigest(),
            'pc_file': f'{a.folder}/BG/{pc_name}', 'pc_image_index': key[1], 'pc_sha256': sha,
            'content_score': round(own, 4), 'best_content_file': best[1][0], 'tier': tier})
    out = {'schema': 1,
           'scope': 'Saturn BG*.BIN to PC BG*.SPR by shared file number (verified by eye for the 12 pairs of hd-scene-bg-pairs.json), '
                    'with a content score per pair. cells_sha256 identifies the native picture at runtime. Data only, no pixels.',
           'pairs': entries, 'unpaired_saturn': unpaired}
    a.output.write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    tiers = {t: sum(e['tier'] == t for e in entries) for t in ('content', 'number')}
    dup = len(entries) - len({e['cells_sha256'] for e in entries})
    print(len(entries), 'pairs', tiers, 'unpaired', len(unpaired), 'duplicate cell hashes', dup)


if __name__ == '__main__':
    main()
