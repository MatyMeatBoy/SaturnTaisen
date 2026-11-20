# Chapter 8 native opening picture evidence

A cold replay on prepared English Saturn disc 2 selects the Episode 8 Continue slot, then reads `0801.BIN` at FAD 108406. The muted strict-native run completes 12,000 frames with zero interpreted blocks. Its final guest hash `f4272e26bdde2c41` matches the archived cold route. This proof associates four native pictures with the chapter. It preserves their existing donor decisions and the separately verified BG2159 HD draw.

| Disc 2 file | FAD | Native display evidence |
| --- | --- | --- |
| `/SAKURA1/TITLE8.BIN` | 149253 | English cold frame 7000 and archived Spanish disc 2 frame 7000 each match the decoded source across all 71,680 pixels. |
| `/SAKURA1/BG1212.BIN` | 119984 | The archived Spanish cold frame 9000 and long replay frames 7750 through 9500 match all 41,472 pixels of the scene viewport. The English cold run independently reads the file. |
| `/SAKURA1/BG1050.BIN` | 117000 | The English cold trace reads this room plate. At frame 12000, 19,983 visible pixels match the plate at their exact positions and differ from BG4187. All 4,675 pixels in the unobstructed upper-left 85×55 region match. |
| `/SAKURA1/BG4187.BIN` | 132254 | The same scene displays 6,179 non-key pixels matching the seated group at their exact positions and differing from BG1050. |

For the two-layer room view, frame 11999 contains the exact BG1050 cells at VDP2 VRAM `0x34840` and palette at CRAM `0x200`. Its BG4187 cells and palette are at VRAM `0x4a040` and CRAM `0xe00`. The frame 12000 image contains Sakura's foreground sprite above both layers. The pixel counts cover the visible areas attributable to each source. [Patch 0215 verifies the BG4187 PC foreground](narrative-foreground-followup.md) with Sakura retained above it. The approved localized card still excludes the PC TITLE8 donor with baked-in lettering.

The scene evidence distinguishes disc reads, VRAM and CRAM residency, and display. The cold boot's black viewport shares the BG1341 image fingerprint before the chapter is selected and is outside the chapter scope. The existing `0801FCE.BIN` entry remains resident. Later chapter routes, tactical display and the complete HD exit test remain open.

The archived English checkpoint is under `local/work/later-chapter-audit/chapter-sweep/bank-8-battle-1-strict/`. Spanish evidence is under `local/work/guion-es/pruebas/es-all/d2-ep8-continue` and `d2-ep8-largo`. The muted English replay and the comparisons are retained under `local/work/codex-th8-attribution/`.

## HD room draw

The English disc 2 frame-11999 checkpoint supports a 180-field Enhanced
A/B on 0188 at 2560×1440. Installing the PC BG1050 background preserves
all guest hashes and final SRAM, with zero interpreted blocks. All four
sampled images change only inside the Zoom rectangle (272,29)–(2288,1037).
The 960,719 changed pixels per sample agree with the independent PC
decode within two RGB levels. The 1,052,226 inset pixels that differ
from the standalone native background remain exact. The private repro
is under `local/work/codex-th1/ch7-ch8-hd-plates/`.

## Verified festival scene draws on 0802

Six physical PC scene pictures render in Enhanced Zoom on the natural English
disc-2 Iris festival route. The checkpoints are from the 0802 play sequence
recorded in [Iris route evidence](nc3517-route-evidence.md).

| Physical PC donor | Saturn source FAD | Archived checkpoint under `nc3517-live/` | Changed pixels per sample |
| --- | ---: | --- | ---: |
| `BG1236.SPR` | 120467 | `iris-0802-monkey/terminal.state` | 2,010,472 |
| `BG1237.SPR` | 120490 | `iris-0802-festival-exit/terminal.state` | 1,257,512 |
| `BG2033.SPR` | 123593 | `iris-0802-deploy/f4320.state` | 2,031,150 |
| `BG2081.SPR` | 124708 | `iris-0802-stall-mid/terminal.state` | 1,625,295 |
| `BG2082.SPR` | 124731 | `iris-0802-stall-near/terminal.state` | 1,734,787 |
| `BG2083.SPR` | 124754 | `iris-0802-after-shoot/terminal.state` | 1,859,777 |

Each checkpoint was replayed with its own archived SRAM and neutral controller
for 56 fields at 2560×1440 with strict native and D3D11. The two arms used the
same cumulative 0213 runtime, SHA-256
`02AC1AAAB7D0CBDFEA8A3E1950D1583B7FEBF765AC5D0B67319678BC93C0E89C`,
and differed only by the presence of the named PC donor. All 336 guest hashes
and all six terminal SRAM pairs matched. Both arms reported zero interpreted
execution. Captures at fields 8, 16, 30 and 50 yielded 24 positive pairs.

All RGB changes were inside the existing Zoom viewport at (272, 29) to
(2288, 1037). For each changed pixel the control matched the independently
decoded Saturn picture after RGB555 quantization and nearest scaling. The
replacement matched the independently decoded PC picture after bilinear scaling
within two levels per channel. Interface and actor pixels outside the replaced
picture samples were exact. The BG1238 terminal checkpoint produced no positive
draw and is excluded. This batch verifies six scene pictures in the existing
runtime. The continuous chapter exit and package status remain open.

## Verified scene draws on the 0804 Iris route

Seven distinct physical PC backgrounds were verified in Enhanced Zoom on the
natural English disc-2 Iris route, after the festival sequence. The archived
checkpoint groups below are under `nc3517-live/`.

| Physical PC donor | Saturn source FAD | Checkpoint group | Local checkpoint field | Changed RGB pixels per positive capture |
| --- | ---: | --- | ---: | ---: |
| `BG1071.SPR` | 117483 | `iris-0804-night` | 3600 | 1,452,235 |
| `BG1125.SPR` | 118679 | `iris-0804-night` | 5960 | 1,440,871 |
| `BG1013.SPR` | 116149 | `iris-0804-night` | 7200 | 2,032,122 |
| `BG1019.SPR` | 116287 | `iris-0804-night` | 8360 | 1,355,344 |
| `BG2084.SPR` | 124777 | `iris-0804-planning` | 6680 | 1,294,945 |
| `BG2086.SPR` | 124823 | `iris-0804-planning` | 7679 | 1,358,437 |
| `BG1278.SPR` | 121054 | `iris-0804-warroom` | 8360 | 1,032,041 |

Fields 5960, 8360 in both groups, and 6680 were reproduced from their nearest
prior archived checkpoints with the original input suffix. All four relays
match the archived guest hashes. Every A/B test started at the listed field
and replayed 56 fields with the original input suffix on the same cumulative
0213 runtime, SHA-256
`02AC1AAAB7D0CBDFEA8A3E1950D1583B7FEBF765AC5D0B67319678BC93C0E89C`.
All 392 guest fields and the seven terminal SRAM pairs match. The 337
fields that overlap the archived input logs also match the archived guest
hashes. Both arms reported zero interpreted execution.

The only A/B asset difference was the named PC donor. Captures at offsets
8, 16, 30 and 50 used D3D11 at 2560×1440. All changed RGB samples were
within the existing Zoom viewport at (272, 29) to (2288, 1037). Each changed
control pixel matched the independently decoded Saturn picture, RGB555
quantized and nearest scaled. Each replacement matched the independently
decoded PC picture within two levels per channel after bilinear scaling.
BG2086 had a positive draw at offset 8 and all later samples matched the
control after the scene advanced. The other six donors were positive at
all four sampled offsets.

Local receipts and captures are under
`local/work/codex-witness-441-review/hud/chapter8-late-plates/`.
This scene test leaves the continuous chapter and package gates open.

## Verified scene draws on 0801 and early 0802

Five physical PC scene pictures render in Enhanced Zoom on the natural
English disc-2 Iris route before the festival stalls. The source groups
are under `nc3517-live/`.

| Physical PC donor | Saturn source FAD | Archived input group | Checkpoint field | Changed RGB pixels per capture |
| --- | ---: | --- | ---: | ---: |
| `BG1016.SPR` | 116218 | `iris-0801-clear-party` | 3890 | 2,031,394 |
| `BG1087.SPR` | 117851 | `iris-0801-room-enter` | 870 | 2,032,128 |
| `BG1112.SPR` | 118426 | `iris-0801-room-enter` | 1760 | 1,259,729 |
| `BG1276.SPR` | 121031 | `iris-0802-date` | 3570 | 2,014,907 |
| `BG1238.SPR` | 120513 | `iris-0802-date` | 6270 | 1,241,652 |

Three checkpoint relays run from the archived Yoneda, Iris room label
and Iris ask terminal states respectively. All 11,923 replay fields
match their archived guest hashes with zero interpreted blocks. These
relays produce the exact checkpoint fields rather than substituting
the groups' terminal saves.

Each A/B runs 56 fields on the original input suffix in D3D11 at
2560×1440 with the same strict runtime. Only the listed PC donor
differs between arms. All 280 A/B guest hashes match, as do terminal
SRAM pairs. Of these fields, 264 overlap the archived guest logs and
match exactly. The last 16 fields of BG1112 extend past the archive
with neutral input. The cumulative 0213 executable SHA-256 is
`02AC1AAAB7D0CBDFEA8A3E1950D1583B7FEBF765AC5D0B67319678BC93C0E89C`.

All captures at offsets 8, 16, 30 and 50 were positive. For every
changed pixel, the control matches the independently decoded Saturn
picture after RGB555 quantization and nearest scaling. Its PC
replacement matches the independently decoded bilinear sample within
two levels per channel. All changes stay within the established Zoom
rectangle (272, 29) to (2288, 1037). BG1090 did not produce visible A/B
changes at the tested checkpoint and remains pending. Receipts and
capture pairs are under
`local/work/codex-witness-441-review/hud/chapter8-early-plates/`.
The continuous chapter and package gates remain open.
