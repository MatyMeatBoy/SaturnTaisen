"""T100/S3 reference for the clip hook: CD play command -> start FAD -> PC clip, from config/film-fad-map.json.

The runtime hook (not written yet, see docs/research/clip-hook-design.md) must behave exactly like `lookup_play_command`.
Play commands are the 16-bit words the guest sends to the CD block, e.g. `1080 2EC7 0080 0026`; see parse_play for the
layout used (taken from the T53 trace only).

    python tools/film_clip_hook.py --emit-table   # rewrites docs/research/film-clip-table.txt (sorted FAD table)
"""
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAP = ROOT / 'config/film-fad-map.json'


def parse_play(words):
    """Start FAD of a CD `play` command, or None when the command is not a play with an FAD start.

    Layout seen in the T53 trace (`1080 2EC7 0080 0026`, `1082 7465 0080 0026`): word0 high byte 0x10 = play, the low 7 bits of
    word0's low byte are the FAD bits 22..16 when bit 7 of the command selects an FAD (0x80 set), word1 = FAD bits 15..0.
    Examples checked against the trace: 1080/2EC7 -> 0x002EC7, 1082/7465 -> 0x027465. This is the layout from the trace only;
    other play forms (track/index start, bit 7 clear) return None and are never mapped."""
    if len(words) < 2 or (words[0] >> 8) != 0x10 or not (words[0] & 0x80):
        return None
    return ((words[0] & 0x7F) << 16) | (words[1] & 0xFFFF)


def load_table(path=MAP):
    data = json.load(open(path, encoding='utf8'))
    table = {}
    for s in data['streams']:
        if 'movie' in s:
            table[(s['disc'], s['fad'])] = {'movie': s['movie'], 'alternate_cut': s['alternate_cut'], 'disc': s['disc'],
                               'duration': s['duration'], 'pc_duration': s['pc_duration']}
    return table


def lookup_fad(table, disc, fad):
    """Exact (disc, start FAD) match only (the same FAD exists on both discs for different films): a play that starts in the middle of a stream (resume) is deliberately not mapped here."""
    return table.get((disc, fad))


def lookup_play_command(table, disc, words):
    fad = parse_play(words)
    return None if fad is None else lookup_fad(table, disc, fad)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--emit-table', action='store_true'); a = ap.parse_args()
    t = load_table()
    if a.emit_table:
        out = ROOT / 'docs/research/film-clip-table.txt'
        out.write_text(''.join('0x%06X %-8s %s disc%d\n' % (f, e['movie'], 'ALT' if e['alternate_cut'] else 'ok ', d)
                               for (d, f), e in sorted(t.items(), key=lambda kv: (kv[0][1], kv[0][0]))), encoding='utf8')
    print(len(t), 'start FADs mapped,', sum(1 for e in t.values() if e['alternate_cut']), 'alternate cuts')


if __name__ == '__main__':
    sys.exit(main())
