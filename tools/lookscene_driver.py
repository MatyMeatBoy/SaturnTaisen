"""Play the chapter-jump gaze ("look at") scenes without reading screenshots: run a segment, dump RAM, decide the next input, repeat.

Development tool (needs the owner's discs, a development runtime without `release.marker` and tools/route_segment.py from PR #566). The
RAM facts it relies on are measured in docs/research/look-scene-guide.md (bank-5 page 1, English disc 1):

* Low WRAM (offset from 0x00200000): cursor x at 0x22 and y at 0x24 (int16, relative to the screen centre, about -160..136 and -112..88),
  the script variables as BE16 words from 0x100 (var N at 0x100 + 2N; var00 is the id of the hotspot that was just looked at, 95 is the
  screen edge, var20 is the "edge hand" flag, var74 and var76 are the look counters of the two main hotspots).
* High WRAM 0x685B4 (BE32): the script cursor. The script file (bytecode) is resident in Low WRAM from 0x204000; the look loop waits on
  its `00 03` command (cursor 0x206B22/24 on bank-5 page 1) and every handler ends by returning there.
* Condition to leave the page: every hotspot the script registers with state 2 (`00 1b <id> 02 f6 <state>`) has to be looked at twice.
  The first look sets its counter to 1, the second to 2; when all counters are 2 the script falls through to the page finale.

The decision functions are pure and tested in tests/test_lookscene_driver.py.

    python tools/lookscene_driver.py play --route-segment tools/route_segment.py --exe E --state S --backup B --out OUT [--max-steps 40]
    python tools/lookscene_driver.py scan --route-segment tools/route_segment.py --exe E --state S --backup B --out OUT

`play` stops when the CD asks for a MAP/BBG/EVE/IC file (route_segment prints the ISO name of every Play Disc command), when the look page
is finished and the script moves on (reported as `left-page`), or at --max-steps. `scan` sweeps the cursor over a grid, looks, and prints
which hotspot id each position hits, to learn the boxes of a page that is not in BOXES yet.
"""
import argparse, json, pathlib, re, struct, subprocess, sys

CURSOR_X, CURSOR_Y = 0x22, 0x24          # Low WRAM, int16
VAR_BASE = 0x100                         # Low WRAM, BE16 per script variable
SCRIPT_LOW = 0x4000                      # script file offset inside Low WRAM
SCRIPT_CURSOR = 0x685B4                  # High WRAM, BE32 absolute address
SCRIPT_BASE = 0x204000
EDGE_ID = 95
MAIN_STATE = 2                           # hotspot state that makes it a goal
LOOKS_NEEDED = 2
PAGE_SPAN = 0x600                        # the dispatcher and the finale of bank-5 page 1 span 0x44A bytes after the wait command
VAR_HIT, VAR_EDGE = 0x00, 0x20
BIT = dict(RIGHT=0x8000, LEFT=0x4000, DOWN=0x2000, UP=0x1000, START=0x0800, A=0x0400, C=0x0200, B=0x0100)

# bank-5 page 1 (Sumire and Kanna): hit box (x0, x1, y0, y1) in cursor units and the counter variable of each main hotspot.
BOXES = {41: (-66, -60, -37, -28), 36: (12, 36, -74, -64)}
COUNTER = {41: 0x74, 36: 0x76}

# Cursor displacement after holding one direction for N frames from rest (measured on bank-5 page 1; identical for x and y).
DISP = [(0, 0), (4, 0), (8, 5), (14, 12), (16, 16), (22, 30), (30, 54), (36, 76), (44, 108), (52, 140)]


def u16(b, o):
    return struct.unpack_from('>H', b, o)[0]


def s16(b, o):
    return struct.unpack_from('>h', b, o)[0]


def parse_state(low, high):
    """Cursor, script cursor and the variables the page logic uses."""
    return dict(x=s16(low, CURSOR_X), y=s16(low, CURSOR_Y), script=struct.unpack_from('>I', high, SCRIPT_CURSOR)[0],
                hit=u16(low, VAR_BASE + 2 * VAR_HIT), edge=u16(low, VAR_BASE + 2 * VAR_EDGE),
                var=lambda n: u16(low, VAR_BASE + 2 * n))


def script_hotspots(low):
    """(wait_address, {id: state}) from the look page initialisation: `00 1b 80 00 00 ID 02 f6|f7 80 00 00 STATE` runs followed by the
    `00 03` wait command. Returns the LAST run in the script image, which is the page that is currently loaded."""
    s = bytes(low[SCRIPT_LOW:SCRIPT_LOW + 0x10000])
    runs = []
    for m in re.finditer(rb'\x00\x1b\x80\x00\x00(.)\x02[\xf6\xf7]\x80\x00\x00(.)', s, re.S):
        runs.append((m.start(), m.end(), m.group(1)[0], m.group(2)[0]))
    # group consecutive registrations (each is 14 bytes: 8 + 6)
    pages, cur = [], []
    for st, en, i, v in runs:
        if cur and st - cur[-1][1] > 4:
            pages.append(cur)
            cur = []
        cur.append((st, en, i, v))
    if cur:
        pages.append(cur)
    out = []
    for p in pages:
        w = s.find(b'\x00\x03', p[-1][1], p[-1][1] + 16)
        out.append((SCRIPT_BASE + w if w >= 0 else None, {i: v for _, _, i, v in p}))
    return out


def current_page(low, script_addr):
    """The registration run whose wait command is the closest one at or before the script cursor (None when the script is not in a page)."""
    best = None
    for wait, states in script_hotspots(low):
        if wait is not None and wait <= script_addr <= wait + PAGE_SPAN and (best is None or wait > best[0]):
            best = (wait, states)
    return best


def disp(h):
    """Pixels the cursor travels when a direction is held for h frames (linear interpolation of DISP, 4 px/frame beyond the table)."""
    if h <= 0:
        return 0
    for (h0, d0), (h1, d1) in zip(DISP, DISP[1:]):
        if h <= h1:
            return d0 + (d1 - d0) * (h - h0) / (h1 - h0)
    return DISP[-1][1] + 4 * (h - DISP[-1][0])


def hold_for(delta):
    """Frames to hold a direction to move |delta| pixels (0 when under 3 px)."""
    d = abs(delta)
    if d < 3:
        return 0
    h = 0
    while disp(h + 1) <= d:
        h += 1
    return h if abs(disp(h) - d) <= abs(disp(h + 1) - d) else h + 1


def centre(box):
    return (box[0] + box[1]) // 2, (box[2] + box[3]) // 2


def inside(pos, box):
    return box[0] <= pos[0] <= box[1] and box[2] <= pos[1] <= box[3]


def block_ends(low, wait):
    """Script addresses of the `op1e; op20 031d` pairs that close a handler inside the page: the script cursor rests there while the
    look loop waits for the next click (seen after Kanna's look on bank-5 page 1: 0x206C98)."""
    o = SCRIPT_LOW + wait - SCRIPT_BASE
    s = bytes(low[o:o + PAGE_SPAN])
    return {wait + m.start() for m in re.finditer(rb'\x00\x1e\x00\x20\x03\x1d', s)}


def waiting(script, wait, ends=()):
    return wait is not None and (wait <= script <= wait + 2 or script in ends)


def goals_of(states, counters):
    """Main hotspots still needing looks: [(id, looks_done)] in id order. `counters` maps id -> looks done."""
    return [(i, counters.get(i, 0)) for i, v in sorted(states.items()) if v == MAIN_STATE and counters.get(i, 0) < LOOKS_NEEDED]


def decide(low, high, boxes=BOXES, counter_vars=COUNTER):
    """Next intent: ('finish',) | ('advance',) | ('move', dx, dy, id) | ('look', id) | ('unknown', id) | ('no-page',).

    advance = press A about every 25 frames (closes dialogs, repeats the look when the cursor is on a hotspot)."""
    st = parse_state(low, high)
    page = current_page(low, st['script'])
    if page is None:
        return ('no-page',)
    wait, states = page
    counters = {i: st['var'](counter_vars[i]) for i in states if states[i] == MAIN_STATE and i in counter_vars}
    todo = goals_of(states, counters)
    for i, _ in todo:
        if i not in boxes or i not in counter_vars:
            return ('unknown', i)
    if not todo:
        return ('finish',)
    if not waiting(st['script'], wait, block_ends(low, wait)):
        return ('advance',)
    i = todo[0][0]
    if inside((st['x'], st['y']), boxes[i]):
        return ('look', i)
    cx, cy = centre(boxes[i])
    return ('move', cx - st['x'], cy - st['y'], i)


def movie_for(intent, frames=300, gap=25):
    """Input movie lines `frame HEXBITS 0` for one segment; returns (text, frames)."""
    ev = {}
    kind = intent[0]
    if kind == 'move':
        dx, dy = intent[1], intent[2]
        hx, hy = hold_for(dx), hold_for(dy)
        bx = (BIT['RIGHT'] if dx > 0 else BIT['LEFT']) if hx else 0
        by = (BIT['DOWN'] if dy > 0 else BIT['UP']) if hy else 0
        ev[5] = bx | by
        for end in sorted({5 + hx if hx else 0, 5 + hy if hy else 0} - {0}):
            ev[end] = (bx if hx and 5 + hx > end else 0) | (by if hy and 5 + hy > end else 0)
        frames = max(hx, hy) + 60
    else:
        for k in range(20, frames - 10, gap):
            ev[k] = BIT['A']
            ev[k + 4] = 0
    return ''.join('%d %04X 0\n' % (f, b) for f, b in sorted(ev.items())), frames


class Driver:
    def __init__(self, route_segment, exe, root, state, backup, out, disc=1):
        self.rs, self.exe, self.root, self.backup, self.disc = route_segment, exe, root, backup, disc
        self.state, self.out, self.step_no, self.log, self.movie, self.clock = state, out, 0, [], [], 0
        out.mkdir(parents=True, exist_ok=True)

    def run(self, movie_text, frames, label):
        self.step_no += 1
        d = self.out / ('s%03d' % self.step_no)
        d.mkdir(parents=True, exist_ok=True)
        mv = d / 'in.movie'
        mv.write_text(movie_text, encoding='ascii')
        cmd = [sys.executable, str(self.rs), '--exe', str(self.exe), '--disc', str(self.disc), '--root', str(self.root), '--state', str(self.state),
               '--backup', str(self.backup), '--movie', str(mv), '--frames', str(frames), '--dump', '--out', str(d)]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, errors='replace')
        try:
            rep = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            raise RuntimeError('route_segment failed: ' + p.stdout[-400:])
        for line in movie_text.splitlines():
            f, b, _ = line.split()
            self.movie.append('%d %s 0' % (self.clock + int(f), b))
        self.clock += frames - 1
        self.state = d / 'finish.state'
        low, high = (d / 'ram-low.bin').read_bytes(), (d / 'ram-high.bin').read_bytes()
        (d / 'ram-sound.bin').unlink(missing_ok=True)
        self.log.append(dict(step=self.step_no, label=label, frames=frames, disc_files=rep['disc_files'], state=str(self.state),
                             state_sha256=rep['finish_state_sha256']))
        (self.out / 'driver-log.json').write_text(json.dumps(self.log, indent=1), encoding='utf-8')
        (self.out / 'driver.movie.txt').write_text('\n'.join(self.movie) + '\n', encoding='ascii')
        return low, high, rep['disc_files']


LOADS = re.compile(r'/(MAP|BBG|EVE|IC)\d', re.I)


def play(drv, max_steps):
    low, high, files = drv.run('', 60, 'start')
    seen_page = False
    while drv.step_no < max_steps:
        hit = [f for f in files if LOADS.search(f)]
        if hit:
            return 'loaded', hit
        intent = decide(low, high)
        if intent[0] == 'no-page':
            return ('left-page' if seen_page else 'no-page'), intent
        if intent[0] == 'unknown':
            return 'unknown-hotspot', intent
        seen_page = True
        text, frames = movie_for(intent)
        low, high, files = drv.run(text, frames, str(intent))
    return 'max-steps', None


def scan(drv, xs=(-52, -40, -28, -16, -4, 8, 20, 32, 44, 56, 68), ys=(-38, -30, -22, -14, -6, 2, 10, 18)):
    """Hit ids over a grid of cursor positions, each run from the same state (the cursor is placed with held directions)."""
    result = {}
    for dy in ys:
        for dx in xs:
            text, frames = movie_for(('move', dx, dy, 0))
            text += ''.join('%d %04X 0\n%d 0000 0\n' % (frames + 5, BIT['A'], frames + 9))
            keep = drv.state
            low, high, _ = drv.run(text, frames + 60, 'scan %d,%d' % (dx, dy))
            st = parse_state(low, high)
            result.setdefault(st['hit'], []).append((st['x'], st['y']))
            drv.state = keep
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('mode', choices=('play', 'scan'))
    ap.add_argument('--route-segment', type=pathlib.Path, default=pathlib.Path(__file__).with_name('route_segment.py'))
    ap.add_argument('--exe', type=pathlib.Path, required=True)
    ap.add_argument('--disc', type=int, default=1)
    ap.add_argument('--root', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1])
    ap.add_argument('--state', type=pathlib.Path, required=True)
    ap.add_argument('--backup', type=pathlib.Path, required=True)
    ap.add_argument('--out', type=pathlib.Path, required=True)
    ap.add_argument('--max-steps', type=int, default=40)
    a = ap.parse_args()
    drv = Driver(a.route_segment, a.exe, a.root, a.state, a.backup, a.out.resolve(), a.disc)
    if a.mode == 'scan':
        print(json.dumps({str(k): v for k, v in scan(drv).items()}))
        return 0
    why, info = play(drv, a.max_steps)
    print(json.dumps(dict(result=why, info=info, steps=drv.step_no)))
    return 0 if why in ('loaded', 'left-page') else 1


if __name__ == '__main__':
    sys.exit(main())
