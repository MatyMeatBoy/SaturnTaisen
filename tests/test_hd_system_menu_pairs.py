import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))
from PIL import Image, ImageDraw  # noqa: E402
import hd_system_menu_pairs as m  # noqa: E402


def frame(w, h, bars):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(250, 250, 250, 255), width=max(1, w // 40))
    for i, b in enumerate(bars):
        d.rectangle([4 + i * w // 6, 6, 4 + i * w // 6 + b, h // 2], fill=(90, 90, 200, 255))
    return img


def sat(name, img):
    return {'texture_fnv': name, 'palette_fnv': 'P', 'size': list(img.size), 'sig': m.signatures(img), 'states': {'s'}, 'commands': 1,
            'opaque': 1}


def pc(file, index, img):
    return {'file': file, 'id': file[:-4], 'index': index, 'size': list(img.size), 'sha256': 'x', 'sig': m.signatures(img)}


class Pairs(unittest.TestCase):
    def test_firm_pair_at_2x_and_ambiguity(self):
        a = frame(144, 32, [3, 9, 5])
        b = Image.new('RGBA', (144, 32), (0, 0, 0, 0))
        ImageDraw.Draw(b).ellipse([20, 4, 120, 28], fill=(255, 255, 255, 255))
        pcs = [pc('A.SPR', 0, a.resize((288, 64))), pc('B.SPR', 0, b.resize((288, 64))), pc('C.SPR', 3, Image.new('RGBA', (10, 300), (9, 9, 9, 255)))]
        rows = m.pair([sat('t1', a)], pcs)
        self.assertEqual(rows[0]['tier'], 'paired')
        self.assertEqual(rows[0]['pc_file'], 'A.SPR')
        self.assertEqual(rows[0]['scale'], [2.0, 2.0])
        twin = m.pair([sat('t1', a)], [pc('A.SPR', 0, a.resize((288, 64))), pc('A2.SPR', 0, a.resize((288, 64)))])
        self.assertEqual(twin[0]['tier'], 'ambiguous')   # identical runner-up: no margin

    def test_no_counterpart_and_aspect_filter(self):
        a = frame(144, 32, [3, 9])
        rows = m.pair([sat('t', a)], [pc('T.SPR', 0, frame(64, 400, [3, 9]))])
        self.assertEqual(rows[0]['tier'], 'no-counterpart')
        self.assertIn('aspect', rows[0]['reason'])

    def test_integrated_and_keep_native_reasons(self):
        a = frame(112, 176, [4, 8])
        sig = [pc('SISTEM.SPR', 12, a.resize((224, 352))), pc('R_HARI.SPR', 0, Image.new('RGBA', (32, 44), (1, 2, 3, 255)))]
        doc = m.build(sig, [sat('t', a)])
        self.assertEqual(doc['groups']['SISTEM.SPR']['rows'][0]['already_integrated_by'], '0209')
        self.assertFalse(doc['groups']['SISTEM.SPR']['connectable_by_table'])
        hari = [r for r in doc['pc'] if r['file'] == 'R_HARI.SPR'][0]
        self.assertIn('keep native', hari['reason'])

    def test_fnv_known_value(self):
        self.assertEqual(m.fnv(b''), 'CBF29CE484222325')


if __name__ == '__main__':
    unittest.main()
