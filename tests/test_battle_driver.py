import pathlib, struct, sys, unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
import battle_driver as bd


def ram(units, pointer=(15, 63, 744, 744)):
    r = bytearray(0x60000)
    for i, (hp, mx, x, y) in enumerate(units):
        o = bd.TABLE + i * bd.STRIDE
        struct.pack_into('>2H', r, o + 8, hp, mx)
        struct.pack_into('>H', r, o + 0x4C, x)
        struct.pack_into('>H', r, o + 0x50, y)
    if isinstance(pointer, dict):
        pointer = (pointer['tx'], pointer['ty'], pointer['x'], pointer['y'])
    struct.pack_into('>4H', r, bd.POINTER, *pointer)
    return bytes(r)


# 5 allies (Sakura first), enemies from index 5
ALLIES = [(26, 120, 744, 720), (99, 120, 696, 744), (120, 120, 888, 720), (71, 120, 744, 744), (120, 120, 624, 732)]
FAR = [(80, 80, 840, 400), (30, 80, 432, 400)]
NEAR = [(80, 80, 768, 756), (15, 80, 792, 744)]


def intent(allies, enemies, pointer):
    r = ram(allies + enemies, pointer)
    return bd.decide(bd.parse_units(r), bd.parse_pointer(r))


class Decide(unittest.TestCase):
    def test_parse_skips_empty_tail(self):
        r = ram(ALLIES + FAR)
        self.assertEqual(len(bd.parse_units(r)), 7)
        self.assertEqual(bd.parse_units(r)[0].hp, 26)

    def test_active_unit_from_pointer(self):
        self.assertEqual(intent(ALLIES, FAR, dict(tx=0, ty=0, x=0, y=0)), ('wait',))

    def test_sakura_hurt_heals(self):
        self.assertEqual(intent(ALLIES, FAR, dict(tx=1, ty=1, x=744, y=720)), ('heal',))

    def test_sakura_healthy_never_attacks(self):
        al = [(120, 120, 744, 720)] + ALLIES[1:]
        self.assertEqual(intent(al, NEAR, dict(tx=1, ty=1, x=744, y=720))[0], 'flee')
        self.assertEqual(intent(al, FAR, dict(tx=1, ty=1, x=744, y=720))[0], 'end')

    def test_attack_weakest_in_range(self):
        self.assertEqual(intent(ALLIES, NEAR, dict(tx=1, ty=1, x=744, y=744)), ('attack', 6))

    def test_move_when_out_of_range(self):
        self.assertEqual(intent(ALLIES, FAR, dict(tx=1, ty=1, x=744, y=744)), ('move', 6))

    def test_acted_unit_is_not_active(self):
        r = bytearray(ram(ALLIES + FAR, (1, 1, 888, 720)))
        r[bd.TABLE + 2 * bd.STRIDE + 0x39] = 0x08
        self.assertEqual(bd.decide(bd.parse_units(bytes(r)), bd.parse_pointer(bytes(r))), ('wait',))

    def test_done_set_and_terrace_offset(self):
        r = ram(ALLIES + FAR, (1, 1, 888, 696))   # sprite one terrace above the record
        u, p = bd.parse_units(r), bd.parse_pointer(r)
        self.assertEqual(bd.decide(u, p)[0], 'move')
        self.assertEqual(bd.decide(u, p, done={2}), ('wait',))

    def test_victory_and_gameover(self):
        self.assertEqual(intent(ALLIES, [], dict(tx=1, ty=1, x=744, y=744)), ('victory',))
        dead = [(0, 120, 744, 720)] + ALLIES[1:]
        self.assertEqual(intent(dead, FAR, dict(tx=1, ty=1, x=744, y=744)), ('gameover',))

    def test_danger_and_aim(self):
        a, e = bd.split(bd.parse_units(ram(ALLIES + NEAR)), 5)
        self.assertTrue(bd.sakura_in_danger(a, e))
        p = dict(tx=0, ty=0, x=744, y=744)
        self.assertEqual(bd.aim(p, (744, 744), bd.DELTAS), None)
        d = bd.aim(p, (768, 732), bd.DELTAS)
        self.assertEqual(d, 'RIGHT')
        self.assertEqual(bd.aim(p, (744, 696), bd.DELTAS, banned={'UP'}) in (None, 'UP'), False)

    def test_presses_spacing(self):
        self.assertEqual(bd.presses(['RIGHT', 'A']), '8 RIGHT,38 A')

    def test_ic_detection(self):
        self.assertEqual(bd.ic_files(['/SAKURA2/N015.BIN', '/SAKURA2/IC0101.BIN']), ['/SAKURA2/IC0101.BIN'])


if __name__ == '__main__':
    unittest.main()
