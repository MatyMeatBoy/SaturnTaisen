"""T101/S4: which Saturn FILM streams may take the PC MP2 audio, derived from config/film-fad-map.json (no game data read).

Rule: a paired clip whose durations agree (alternate_cut false, |difference| <= 0.5 s) gets the PC audio; the 6 alternate cuts
keep the Saturn audio. Writes config/clip-audio-map.json: one entry per PC clip with every (disc, start FAD) that plays it.

    python tools/gen_clip_audio_map.py [--check]
"""
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / 'config/film-fad-map.json'
OUT = ROOT / 'config/clip-audio-map.json'


def build(src=SRC):
    with open(src, encoding='utf8') as f:
        streams = json.load(f)['streams']
    clips = {}
    for s in streams:
        if 'movie' not in s:
            continue
        c = clips.setdefault(s['movie'], {'movie': s['movie'], 'saturn_duration': s['duration'], 'pc_duration': s['pc_duration'],
                                          'duration_delta': round(s['pc_duration'] - s['duration'], 3),
                                          'audio': 'pc' if not s['alternate_cut'] else 'saturn', 'starts': []})
        c['starts'].append({'disc': s['disc'], 'fad': s['fad']})
    out = sorted(clips.values(), key=lambda c: c['movie'])
    for c in out:
        c['starts'].sort(key=lambda x: (x['disc'], x['fad']))
    return {'rule': 'audio=pc when the paired durations differ by <= 0.5 s; alternate cuts keep the Saturn audio',
            'clips': out}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); a = ap.parse_args()
    text = json.dumps(build(), indent=1) + '\n'
    if a.check:
        return 0 if OUT.read_text(encoding='utf8') == text else 1
    OUT.write_text(text, encoding='utf8')
    d = json.loads(text)['clips']
    print(len(d), 'clips,', sum(1 for c in d if c['audio'] == 'pc'), 'with PC audio')


if __name__ == '__main__':
    sys.exit(main())
