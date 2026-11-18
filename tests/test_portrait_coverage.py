import unittest
from struct import pack_into

from PIL import Image

from tools.audit_portrait_coverage import (
    alpha_coverage, compare_rgb, observed_portrait, patch_matches, ranges,
)


class PortraitCoverageTests(unittest.TestCase):
    def test_vdp1_uses_active_commands_and_composites_overlapping_strips_in_order(self):
        vram = bytearray(0x80000)
        base, eyes, mouth = 0x60000, 0x60800, 0x60c00
        vram[base:base + 1920] = b"\x01" * 1920
        vram[eyes:eyes + 640] = b"\x00\x02" * 320
        vram[mouth:mouth + 640] = b"\x03\x00" * 320
        pack_into(">8H", vram, 0x00, 0x100A, 0x80 // 8, 0, 0, 0, 0, 160, 112)
        pack_into(">8H", vram, 0x20, 0x0000, 0, 0xA0, 0x4400, base // 8, 0x530, 0, 0)
        pack_into(">8H", vram, 0x80, 0x0000, 0, 0xA0, 0x4400, base // 8, 0x530,
                  (-144) & 0xffff, 48)
        pack_into(">8H", vram, 0xa0, 0x0000, 0, 0xA0, 0x4400, eyes // 8, 0x510,
                  (-144) & 0xffff, 56)
        pack_into(">8H", vram, 0xc0, 0x0000, 0, 0xA0, 0x4400, mouth // 8, 0x510,
                  (-144) & 0xffff, 64)
        pack_into(">H", vram, 0xe0, 0x8000)

        portrait = observed_portrait(bytes(vram))
        self.assertEqual(portrait.base, b"\x01" * 1920)
        self.assertEqual([strip.y for strip in portrait.strips], [8, 16])
        self.assertEqual(portrait.frame[0:2], b"\x01\x01")
        self.assertEqual(portrait.frame[8 * 40:8 * 40 + 2], b"\x01\x02")
        self.assertEqual(portrait.frame[16 * 40:16 * 40 + 2], b"\x03\x02")
        self.assertEqual(portrait.frame[24 * 40:24 * 40 + 2], b"\x03\x01")

    def test_patch_matcher_detects_ambiguous_and_nonoverlap(self):
        base = b"\x01" * 1920
        eyes = b"\x00\x02" * 320
        mouth = b"\x03\x00" * 320
        atlas = base + eyes + mouth
        row = lambda color: bytes(color) * 20
        normal = base[:3 * 40] + row((1, 2)) * 16 + base[19 * 40:27 * 40]
        normal += row((3, 1)) * 16 + base[43 * 40:]
        self.assertEqual(patch_matches(atlas, normal), (((1, 3, True), (2, 27, True)),))
        overlap = base[:8 * 40] + row((1, 2)) * 8 + row((3, 2)) * 8
        overlap += row((3, 1)) * 8 + base[32 * 40:]
        self.assertEqual(patch_matches(atlas, overlap), ())
        single = base[:3 * 40] + row((1, 2)) * 16 + base[19 * 40:]
        self.assertEqual(len(patch_matches(base + eyes + eyes, single)), 2)

    def test_required_alpha_is_measured_per_part_at_requested_density(self):
        native = bytes([1]) * 3200
        image = Image.new("RGBA", (80, 160), (7, 8, 9, 255))
        image.putpixel((0, 100), (7, 8, 9, 0))
        image.putpixel((0, 140), (7, 8, 9, 128))
        self.assertEqual(alpha_coverage(image, native, 2),
                         {"base": {"opaque": 7680, "partial": 0, "missing": 0},
                          "eyes": {"opaque": 2559, "partial": 0, "missing": 1},
                          "mouth": {"opaque": 2559, "partial": 1, "missing": 0}})
        self.assertEqual(ranges({1, 2, 3, 5, 9, 10}), ["0001-0003", "0005", "0009-000a"])

    def test_rgb_comparison_ignores_transparent_pixels_and_detects_exact_white_blend(self):
        palette = bytes(2) + b"\x7f\x05" + bytes(508)
        native = (40, 192, 248)
        faded = tuple((channel * 27 + 248 * 5) >> 5 for channel in native)
        self.assertEqual(compare_rgb(b"\x00\x01", palette, b"\xfe\x01\x03" + bytes(faded)),
                         {"opaque_pixels": 1, "unblended_mismatches": 1, "white_blend_steps": [5]})


if __name__ == "__main__":
    unittest.main()
