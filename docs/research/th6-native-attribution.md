# Chapter 6 native attribution

The evidence uses the prepared English Saturn disc 1. The cold Continue route selects the saved Chapter 6 entry and completes 12,000 frames with zero interpreted blocks. Its script, portrait atlas, and dialogue files begin at FAD 130578, 130596 and 130728. CD play starts were joined to the corresponding ISO extents.

## Displayed resources

| Picture | CD start FAD | Native frame proof |
| --- | ---: | --- |
| TITLE6.BIN | 172346 | The fresh cold replay's frame 7000 matches all 71,680 pixels of the native title picture. |
| BG1199.BIN | 142906 | 39,153 pixels in each first-scene inset match only this picture. |
| BG4119.BIN | 155101 | 2,308 pixels in each first-scene inset match only this picture. |
| BG1025.BIN | 139594 | 37,683 pixels in the inset match only this picture at the archived continuation's frame 1750. |
| BG4059.BIN | 154618 | 3,779 pixels in that inset match only this picture. |

For BG1199 and BG4119, the 11 shared colors complete all 41,472 pixels at cold frames 8000, 9000, 10000 and 11000.

For BG1025 and BG4059, the remaining 10 pixels match both files. Together the two native pictures account for all 41,472 pixels of the 288Ã—144 inset. The same exact composition recurs at frames 2450, 3150 and 5950. The archived continuation state also contains the complete source tiles of BG1025 and BG4059 at VDP2 addresses 0x34840 and 0x4A040, with corresponding palettes at CRAM offsets 0x200 and 0xE00.

The continuation's earlier frame 350 matches the complete 288Ã—144 BG1021 picture. Its source FAD is 139502. This is another chapter appearance of an asset already attributed to Chapter 1. The Chapter 1 catalog row is retained.

## Other reads and residency

The cold trace also reads KABE50 at 159586. The archived frame-9000 state contains the complete tiles and palettes for KABE50, BG1199 and BG4119 in VDP2 memory. The continued replay reads NC97 at 165809. Its established Chapter 1 body row remains.

The cold film reads at FAD 405 and 166362 occur before the Chapter 6 script load. This route still needs a chapter-specific film and a tactical display witness. The displayed native resources establish attribution. HD draws, the continuous chapter exit test and package inclusion remain open.

Private receipts are under local/work/codex-th6-attribution.

## HD background draws

Two 180-field replay pairs in the 0188 runtime use the Chapter 6 cold
frame-9000 checkpoint and the final state of the 6,000-field Chapter 6
continuation. Both pairs use the same English disc 1, recorded checkpoints
and 2560×1440 Enhanced setup. Only the respective PC background is present
in its donor profile. The 360 paired guest hashes and final SRAM match,
with zero interpreted blocks.

The four RGB samples in each pair differ only inside the Zoom rectangle
(272,29)–(2288,1037). Each changed pixel matches the independently decoded
PC image within two RGB levels. The uniquely identified foreground pixels
match the Saturn control exactly.

| Background | Changed pixels in each sample | Saturn foreground | Preserved foreground pixels |
| --- | ---: | --- | ---: |
| BG1199 | 1,913,159 | BG4119 | 113,092 |
| BG1025 | 1,790,430 | BG4059 | 172,186 |

These witnesses cover the two retained occurrences on disc 1. The private
commands and captures are under `local/work/codex-th1/ch6-hd-plates/`.
