"""Original synthetic images exercise matching and integer-density output."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
import hashlib
import configparser
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))


class HdMatchingTests(unittest.TestCase):
    def module(self):
        import hd_matching
        return hd_matching

    def picture(self):
        im=Image.new('RGBA',(40,80),(10,20,30,255))
        for y in range(12,70):
            for x in range(7,31):im.putpixel((x,y),(200,50+y,70+x,255))
        return im

    def test_exact_scaled_art_wins_and_duplicate_candidates_require_review(self):
        m=self.module();native=self.picture()
        correct=native.resize((80,160),Image.Resampling.NEAREST)
        wrong=Image.new('RGBA',(80,160),'white')
        ranked=m.rank_images(native,[(9,wrong),(7,correct)])
        self.assertEqual(ranked[0]['index'],7)
        self.assertEqual(ranked[0]['error'],0)
        self.assertTrue(m.safe_suggestion(ranked))
        ranked=m.rank_images(native,[(7,correct),(8,correct.copy())])
        self.assertFalse(m.safe_suggestion(ranked))

    def test_density_variants_preserve_mask_and_never_require_fractional_presentation(self):
        m=self.module();pc=self.picture().resize((80,160),Image.Resampling.NEAREST)
        mask=bytes([0 if x<5 else 1 for y in range(80) for x in range(40)])
        one=m.prepare_variant(pc,mask,1);two=m.prepare_variant(pc,mask,2)
        self.assertEqual(one.size,(40,80));self.assertEqual(two.size,(80,160))
        self.assertEqual(one.getpixel((0,30))[3],0)
        self.assertEqual(two.getpixel((8,60))[3],0)
        self.assertEqual(two.getpixel((10,60))[3],255)
        for viewport_scale in range(1,13):
            density=m.choose_density(viewport_scale)
            self.assertIn(density,(1,2));self.assertEqual(viewport_scale%density,0)
            self.assertEqual((40*density)*(viewport_scale//density),40*viewport_scale)
        self.assertEqual(m.choose_density(3),1);self.assertEqual(m.choose_density(4),2)

    def test_bad_native_layout_and_noninteger_adjustments_are_rejected(self):
        m=self.module()
        with self.assertRaises(ValueError):m.read_fce_images(bytes(159))
        with self.assertRaises(ValueError):m.read_fce_images(bytes(161))
        self.assertEqual(m.read_fce_images(bytes(160)),{}) # real empty chapter resources
        with self.assertRaises(ValueError):m.prepare_variant(self.picture(),bytes(3200),3)
        with self.assertRaises(ValueError):m.prepare_variant(self.picture(),bytes(3200),1,0.5,0)
        with self.assertRaises(ValueError):m.decode_state_palette(b'bad state',4)

    def test_generated_project_paths_cannot_escape_the_workspace(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaises(ValueError):m.workspace_file(root,'../outside.png')
            self.assertEqual(m.workspace_file(root,'images/one.png'),root/'images/one.png')

    def test_export_only_accepted_pairs_and_preserve_manifest_when_inputs_change(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);raw=bytes([1]*3200);(root/'native.bin').write_bytes(raw)
            source=b'original synthetic source';(root/'source.spr').write_bytes(source)
            self.picture().resize((80,160),Image.Resampling.NEAREST).save(root/'pc.png')
            row=dict(id='0001',raw='native.bin',raw_sha256=m.fingerprint(root/'native.bin'),
                     selected=0,status='pending',dx=0,dy=0)
            project=dict(schema=1,kind='sakura-narrative-portraits',output=str(root/'out'),palette_hash=42,
                         source=dict(path=str(root/'source.spr'),bytes=len(source),fnv64=m.fnv64(source),
                                     sha256=hashlib.sha256(source).hexdigest()),
                         candidates=[dict(index=0,path='pc.png',sha256=m.fingerprint(root/'pc.png'))],rows=[row])
            result=m.export_pack(project,root);self.assertEqual(result['portraits'],0)
            row['status']='accepted';result=m.export_pack(project,root)
            self.assertEqual(result['portraits'],1)
            manifest=Path(result['manifest']);before=manifest.read_bytes()
            ini=configparser.ConfigParser();ini.read(manifest,encoding='utf-8')
            self.assertEqual(ini.getint('pack','count'),1)
            for density in (1,2):
                with Image.open(root/'out'/ini['portrait-0'][f'file{density}']) as im:
                    self.assertEqual(im.size,(40*density,80*density))
            (root/'pc.png').write_bytes(b'changed')
            with self.assertRaises(ValueError):m.export_pack(project,root)
            self.assertEqual(manifest.read_bytes(),before)


if __name__=='__main__':unittest.main()
