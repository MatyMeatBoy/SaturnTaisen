"""Play the Chapter 2 tactical battle without reading screenshots: run a segment, dump work RAM, decide the next input, repeat.

Development tool (needs the owner's discs, a development runtime without `release.marker` and tools/route_segment.py). Every step
is one `route_segment` run from the previous step's `finish.state` with `--dump`; the unit table (06057410, stride 0x60, HP +8, max
HP +0x0A, pixel x +0x4c, pixel y +0x50, flag +0x39 bit 0x08 = acted) and the map pointer (work RAM high 0x1f84: tile x, tile y, pixel
x, pixel y) are read back and the next input is chosen by `decide`. No picture is read. The decision functions are pure and tested in
tests/test_battle_driver.py.

    python tools/battle_driver.py --exe E --disc 1 --state S --backup B --out OUT [--max-steps 400] [--n-allies 5]

Policy: the active ally is the one whose pixel pair equals the pointer (the menu of the active unit opens by itself and the pointer
starts on it). Sakura (index 0, game over if she dies) never attacks: she heals with Def when hurt and otherwise only ends her turn.
The others try Atk when an enemy is within ATTACK_RANGE tiles (the RAM pointer jumping onto an enemy confirms the target) and
otherwise walk toward the weakest reachable enemy, then end the turn. Stops when the CD asks for an IC#### file (route_segment maps
the Play Disc commands to ISO names), when Sakura dies, or at --max-steps.
"""
import argparse, json, pathlib, re, struct, subprocess, sys

TABLE = 0x57410
STRIDE = 0x60
POINTER = 0x1F84
ATTACK_RANGE = 2          # tiles (isometric Manhattan); the pointer jump is the real check
TILE_DX, TILE_DY = 24, 12  # pixels per tile step along one iso axis
SAKURA = 0
ACTED = 0x08
MOVE_STEPS = 4             # tiles the pointer is walked from the unit (blue range is about this wide)
THREAT = 7                 # tiles; Sakura is "in danger" when an enemy is this close
HERE = pathlib.Path(__file__).resolve().parent


class Unit:
    def __init__(self, index, hp, maxhp, x, y, flag):
        self.index, self.hp, self.maxhp, self.x, self.y, self.flag = index, hp, maxhp, x, y, flag

    def __repr__(self):
        return 'U%d(%d/%d @%d,%d f%02x)' % (self.index, self.hp, self.maxhp, self.x, self.y, self.flag)


def parse_units(ram, count=16):
    """Unit records of the live table; records with max HP 0 are the empty tail."""
    out = []
    for i in range(count):
        o = TABLE + i * STRIDE
        hp, mx = struct.unpack_from('>2H', ram, o + 8)
        x, = struct.unpack_from('>H', ram, o + 0x4C)
        y, = struct.unpack_from('>H', ram, o + 0x50)
        if mx == 0:
            continue
        out.append(Unit(i, hp, mx, x, y, ram[o + 0x39]))
    return out


def parse_pointer(ram):
    tx, ty, px, py = struct.unpack_from('>4H', ram, POINTER)
    return dict(tx=tx, ty=ty, x=px, y=py)


def split(units, n_allies):
    """(allies, enemies): the table is compacted when a unit dies, so the first n_allies records are the allies."""
    live = [u for u in units if u.hp > 0]
    return [u for u in live if u.index < n_allies], [u for u in live if u.index >= n_allies]


def tile_distance(a, b):
    """Isometric Manhattan distance in tiles between two pixel positions (steps of 24 x 12 pixels)."""
    return max(abs(a[0] - b[0]) // TILE_DX, abs(a[1] - b[1]) // TILE_DY)


def active_ally(allies, pointer, done=()):
    """The ally the pointer sits on (exact pixel pair first, then the closest within one tile and one terrace: the sprite is drawn
    offset by the terrace height). `done` holds the indices that already ended their turn this round (the +0x39 flag is cleared by End)."""
    ready = [u for u in allies if u.index not in done and not u.flag & ACTED]
    for u in ready:
        if (u.x, u.y) == (pointer['x'], pointer['y']):
            return u
    near = [u for u in ready if abs(u.x - pointer['x']) <= 24 and abs(u.y - pointer['y']) <= 24]
    near.sort(key=lambda u: (abs(u.x - pointer['x']) + abs(u.y - pointer['y']), u.index))
    return near[0] if near else None


def weakest(enemies, origin=None, reach=None):
    pool = enemies
    if origin is not None and reach is not None:
        pool = [e for e in enemies if tile_distance((origin.x, origin.y), (e.x, e.y)) <= reach]
    return min(pool, key=lambda e: (e.hp, e.index)) if pool else None


def nearest(enemies, unit):
    return min(enemies, key=lambda e: (tile_distance((unit.x, unit.y), (e.x, e.y)), e.hp, e.index)) if enemies else None


def sakura_in_danger(allies, enemies):
    s = next((u for u in allies if u.index == SAKURA), None)
    return bool(s and any(tile_distance((s.x, s.y), (e.x, e.y)) <= THREAT for e in enemies))


def decide(units, pointer, n_allies=5, done=()):
    """Next intent for the active unit: ('end', why) | ('heal',) | ('flee', enemy_index) | ('attack', enemy_index) | ('move', enemy_index) | ('wait',)."""
    allies, enemies = split(units, n_allies)
    if not enemies:
        return ('victory',)
    if not any(u.index == SAKURA for u in allies):
        return ('gameover',)
    me = active_ally(allies, pointer, done)
    if me is None:
        return ('wait',)
    if me.index == SAKURA:
        if any(tile_distance((me.x, me.y), (e.x, e.y)) <= THREAT for e in enemies):
            return ('flee', nearest(enemies, me).index)
        return ('heal',) if me.hp < me.maxhp else ('end', 'sakura-idle')
    target = weakest(enemies, me, ATTACK_RANGE)
    if target:
        return ('attack', target.index)
    return ('move', nearest(enemies, me).index)


def aim(pointer, target_xy, deltas, banned=()):
    """Direction that brings the pointer closest to target_xy under the measured per-direction pixel deltas, or None when on it."""
    here = (pointer['x'], pointer['y'])
    if here == tuple(target_xy):
        return None
    best, best_d = None, tile_distance(here, target_xy) * 10 + (abs(here[0] - target_xy[0]) + abs(here[1] - target_xy[1])) / 1000
    for name, (dx, dy) in deltas.items():
        if name in banned:
            continue
        p = (here[0] + dx, here[1] + dy)
        d = tile_distance(p, target_xy) * 10 + (abs(p[0] - target_xy[0]) + abs(p[1] - target_xy[1])) / 1000
        if d < best_d:
            best, best_d = name, d
    return best


DELTAS = dict(RIGHT=(24, -12), LEFT=(-24, 12), UP=(0, -24), DOWN=(0, 24))  # initial guess, re-learned from the pointer RAM


def presses(names, first=8, gap=30):
    """'frame BUTTON' list, one press every `gap` frames; the pseudo button WAIT only skips a slot."""
    return ','.join('%d %s' % (first + i * gap, n) for i, n in enumerate(names) if n != 'WAIT')


END = dict(fresh=['RIGHT'] * 4 + ['A'], acted=['RIGHT'] * 3 + ['A'], moved=['A', 'WAIT'] + ['RIGHT'] * 3 + ['A'])


class Driver:
    def __init__(self, exe, disc, root, state, backup, out, n_allies=5, hold=8):
        self.exe, self.disc, self.root, self.backup = exe, disc, root, backup
        self.state, self.out, self.n_allies, self.hold = state, out, n_allies, hold
        self.step_no, self.log, self.deltas = 0, [], dict(DELTAS)
        self.clock = 0
        self.movie = []
        out.mkdir(parents=True)

    def run(self, inputs, frames, label):
        self.step_no += 1
        d = self.out / ('s%03d' % self.step_no)
        cmd = [sys.executable, str(HERE / 'route_segment.py'), '--exe', str(self.exe), '--disc', str(self.disc), '--root', str(self.root),
               '--state', str(self.state), '--backup', str(self.backup), '--inputs', inputs, '--frames', str(frames), '--dump',
               '--hold', str(self.hold), '--out', str(d)]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, errors='replace')
        try:
            rep = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            raise RuntimeError('route_segment failed: ' + p.stdout[-400:])
        for item in [s for s in inputs.split(',') if s.strip()]:
            f, _, b = item.strip().partition(' ')
            self.movie.append('%d %s' % (self.clock + int(f), b))
        self.clock += frames - 1
        self.state = d / 'finish.state'
        ram = (d / 'ram-high.bin').read_bytes()
        for fname in ('ram-low.bin', 'ram-sound.bin'):
            (d / fname).unlink(missing_ok=True)
        units, ptr = parse_units(ram), parse_pointer(ram)
        files = rep['disc_files']
        self.log.append(dict(step=self.step_no, label=label, inputs=inputs, frames=frames, pointer=ptr,
                             units=[[u.index, u.hp, u.maxhp, u.x, u.y, u.flag] for u in units], disc_files=files,
                             state=str(self.state), state_sha256=rep['finish_state_sha256']))
        (self.out / 'driver-log.json').write_text(json.dumps(self.log, indent=1), encoding='utf-8')
        (self.out / 'driver.movie.txt').write_text('\n'.join(self.movie) + '\n', encoding='ascii')
        return units, ptr, files

    def learn(self, name, before, after):
        d = (after['x'] - before['x'], after['y'] - before['y'])
        if d != (0, 0) and abs(d[0]) <= 96 and abs(d[1]) <= 96:
            self.deltas[name] = d


def ic_files(files):
    return [f for f in files if re.search(r'/IC\d+', f, re.I)]


def play(drv, max_steps, n_allies):
    units, ptr, files = drv.run('', 60, 'start')
    waits, done = 0, set()
    while drv.step_no < max_steps:
        ic = ic_files(files)
        if ic:
            return 'ic', ic
        allies_now = split(units, n_allies)[0]
        who = active_ally(allies_now, ptr, done)
        if who is None and done and active_ally(allies_now, ptr, ()) is not None:
            done = set()          # the pointer is back on a unit that already ended: a new round started
        intent = decide(units, ptr, n_allies, done)
        who = active_ally(allies_now, ptr, done)
        kind = intent[0]
        if kind in ('victory', 'gameover'):
            return kind, None
        waits = waits + 1 if kind == 'wait' else 0
        if who is not None and kind != 'wait':
            done.add(who.index)
        if kind == 'wait':
            if waits >= 4:
                raise RuntimeError('no active ally after %d waits (pointer %r): stop and inspect %s' % (waits, ptr, drv.state))
            units, ptr, files = drv.run('', 300, 'wait')
        elif kind == 'end':
            units, ptr, files = drv.run(presses(END['fresh']), 520, 'end ' + intent[1])
        elif kind == 'heal':
            # Def = 2 RIGHT, A; first submenu entry (Heal) A, confirm A; then End (3 RIGHT) with the cursor back on Move
            units, ptr, files = drv.run(presses(['RIGHT', 'RIGHT', 'A', 'A', 'A']), 900, 'heal')
            units, ptr, files = drv.run(presses(END['acted']), 520, 'end after heal')
        elif kind == 'attack':
            units, ptr, files = drv.run(presses(['RIGHT', 'A', 'A', 'A']), 120, 'atk range')
            tgt = next((u for u in units if u.index == intent[1]), None)
            on_enemy = [u for u in units if u.index >= n_allies and (u.x, u.y) == (ptr['x'], ptr['y'])]
            if on_enemy:
                units, ptr, files = drv.run(presses(['A', 'A']), 900, 'atk confirm')
                units, ptr, files = drv.run(presses(END['acted']), 520, 'end after atk')
            else:
                units, ptr, files = drv.run(presses(['B', 'B', 'B', 'LEFT'][:3]), 120, 'atk none, back')
                units, ptr, files = drv.run(presses(END['fresh']), 520, 'end (no target)')
        elif kind in ('move', 'flee'):
            me = active_ally(split(units, n_allies)[0], ptr)
            tgt = next(u for u in units if u.index == intent[1])
            if kind == 'flee':   # aim at the mirror image of the enemy through Sakura: away from it
                tgt = Unit(-1, 0, 0, 2 * me.x - tgt.x, 2 * me.y - tgt.y, 0)
            units, ptr, files = drv.run(presses(['A']), 90, 'move range')
            banned = set()
            for _ in range(MOVE_STEPS * 2):
                if tile_distance((ptr['x'], ptr['y']), (me.x, me.y)) >= MOVE_STEPS:
                    break
                d = aim(ptr, (tgt.x, tgt.y), drv.deltas, banned)
                if d is None:
                    break
                before = ptr
                units, ptr, files = drv.run(presses([d]), 70, 'aim ' + d)
                drv.learn(d, before, ptr)
                if ptr['x'] == before['x'] and ptr['y'] == before['y']:
                    banned.add(d)
                elif any((u.x, u.y) == (ptr['x'], ptr['y']) for u in units if u.index != me.index):
                    pass  # over another unit: keep walking, the final tile is checked below
            if any((u.x, u.y) == (ptr['x'], ptr['y']) for u in units if u.index != me.index):
                units, ptr, files = drv.run(presses(['B']), 90, 'move occupied, cancel')
            units, ptr, files = drv.run(presses(['A']), 1100, 'move confirm')
            moved = next((u for u in units if u.index == me.index), None)
            if moved and (moved.x, moved.y) != (me.x, me.y):
                units, ptr, files = drv.run(presses(END['moved']), 520, 'end after move')
            else:
                units, ptr, files = drv.run(presses(['B', 'B']), 120, 'move failed, cancel')
                units, ptr, files = drv.run(presses(END['fresh']), 520, 'end (move failed)')
    return 'max-steps', None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--exe', type=pathlib.Path, required=True)
    ap.add_argument('--disc', type=int, default=1)
    ap.add_argument('--root', type=pathlib.Path, default=HERE.parent)
    ap.add_argument('--state', type=pathlib.Path, required=True)
    ap.add_argument('--backup', type=pathlib.Path, required=True)
    ap.add_argument('--out', type=pathlib.Path, required=True)
    ap.add_argument('--max-steps', type=int, default=400)
    ap.add_argument('--n-allies', type=int, default=5)
    a = ap.parse_args()
    drv = Driver(a.exe.resolve(), a.disc, a.root.resolve(), a.state.resolve(), a.backup.resolve(), a.out.resolve(), a.n_allies)
    result, extra = play(drv, a.max_steps, a.n_allies)
    print(json.dumps(dict(result=result, ic=extra, steps=drv.step_no, last_state=str(drv.state))))


if __name__ == '__main__':
    main()
