# BG2290 and the Chapter 3 stage-wing scene

A retained English Saturn disc 1 Continue route reaches the stage wing from
the first-floor map after the dressing-room exchange with Iris. The saved
checkpoint contains the exact 27,182 bytes of `0301.BIN` at Low WRAM
`0x00204000`. Ordinary direction and button input then walks to the stage
wing and continues the scene. There are no guest-state edits. The script's
BG2290 command starts at file offset `0x694e`. The CD trace reads the
60,544-byte file at FAD 151959 in 30 sectors.

## Native pane and pan

The first unique 41,472-byte cell span is at VDP2 VRAM `0x4a080`. The
palette is at CRAM `0xe00`, FNV-1a `9215200C4EBC0C10`. The probe reads it
on source 4 at page `0x44000`. The native 432×144 picture scrolls through
the 288×144 window at (16,8). Samples at 4000 through 4250 remain at x=0.
The offsets refer to the picture actually shown. At sample 4300 the
serialized scroll register is already one pixel farther on.

| Replay frame | Native x | Exact native viewport pixels |
|---:|---:|---:|
| 4000–4250, every 50 frames | 0 | 41,472 |
| 4300 | 18 | 41,472 |
| 4350 | 43 | 41,472 |
| 4400 | 68 | 41,472 |
| 4450 | 93 | 41,472 |
| 4500 | 118 | 41,472 |
| 4550 | 143 | 41,472 |
| 4600 | 144 | 39,438 in the final composite |

At 4600 the source-4 probe still matches all 41,472 pixels of the last
native crop. The foreground covers part of that crop in the final frame.
The 1440p Enhanced comparison confirms exact 7× native RGB in the exposed
viewport at 4000, 4200, 4300, 4400, 4500 and 4550. The donor-present and
donor-absent 1440p captures also match at 4600.

The 864×320 donor aligns over much of the later pan. At the visible x=0
hold, the sampled best PC box `(0,0)-(518,304)` scores 0.8767, below the
0.90 signature floor. The x≥18 samples in this run score 0.9549 to 0.9880,
using independently selected boxes. The witnessed pan retains its
native draw because the tested crop fit misses the exposed opening.
The shared file's disc-2 appearance remains unwitnessed.

## Nearby stage pictures

The stage-wing shot starts on BG1031 (FAD 139732), matched pixel for pixel
on source 2 at sample 900. Its existing PC donor draws in Enhanced at
1440p. At frames 400, 900 and 1400 the changes stay in the
2016×1008 image viewport. All 1,338,605, 1,216,891 and 1,229,467 changed
pixels respectively match an independent bilinear decode of BG1031.SPR
subimage 0 to within one level per channel. BG1031 also has a separate
Chapter 5 native witness in the coverage register.

The later composites read BG2123 and BG3123 at FAD 148638 and 153698,
then BG2289 and BG3289 at FAD 151936 and 154135. At matching probes 1850
and 3750 their source-2 plates match all 41,472 pixels of their native
decodes. Their source-4 cut-outs match all 7,447 and 30,157 opaque
pixels respectively. The corresponding 1440p samples stay native
with the tested PC donors present. The existing pairing dispositions
remain in effect.

The 4,700-frame headless witness and both 1440p replays are muted and
strict-native. All report zero interpreted blocks. Their guest hash log
SHA-256 is `9540058425c4d14b8a9f3e2a6e0fe9655372b6f0f8cca15becfed8242748dc34`.
SRAM matches in the 1440p pair. This verifies a span of the stage-wing
event. The complete chapter exit and other branches are open.

The private inputs, RGB evidence and states are in
`local/work/codex-th1/bg2290-live/`.

## Enhanced donor fade

Patch 0188 verifies the calibrated donor on the same natural English disc 1
route at 2560 × 1440. The viewport remains at (272,29) to (2288,1037).
The native hold and pan stay pixel-identical through x=32. At x=33, the PC
art starts at 16/255 opacity and reaches full opacity at x=48. The original
foreground composite returns unchanged at frame 4600.

The hard switch at frame 4327 raised the transition from 7.837 to 16.510
mean absolute RGB levels per channel at native viewport size. The ramp
preserves the Saturn transition's 7.837 exactly. The first donor step
measures 8.033 versus Saturn's 7.871, and sampled early ramp steps span
7.620 to 8.205. Frames 4400 and 4550 match the full HD plate exactly.
All RGB changes stay in the viewport.

The baseline, hard-switch and ramp runs preserve all 4,700 archived guest
hashes and SRAM, with zero interpreted blocks. Disc 2 occurrence and
package inclusion remain open.

### v0.2.23-alpha replay

The English disc 1 route passes two 4,700-field strict replays
at 2560 × 1440 with the v0.2.23-alpha executable. Only BG2290
is supplied to the donor profile. The guest hashes match the
archived run and both profiles produce the same SRAM with zero
interpreted blocks.

Fields 4000, 4200 and 4300 are identical with and without the
donor. Fields 4400, 4500 and 4550 respectively change 1,769,297,
1,846,367 and 1,864,265 pixels inside (272,29)–(2288,1037).
At field 4600 the final foreground composite matches the native
control. This verifies the shipped panorama and its native return.

The prepared disc inventory gives BG2290 the same full-file SHA-256
on both discs. A scan of the four-digit script files for the
`0033 8000 08F2` background operand finds only 0301 at offset
0x694E on both discs. The disc 2 copy therefore stays a shared
resource with a separate live witness pending.
