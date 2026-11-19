# BG2247 native pan in Chapter 8

An archived English Saturn disc 2 Continue checkpoint at frame 7000 contains all 23,140 bytes of `0805.BIN` in Low WRAM at `0x00204000`. The BG2247 file occupies FAD 127737. Its native color palette is at CRAM `0xe00` with fingerprint `524ED18124B313CB`, and the first unique 41,472-byte cell span is at VRAM `0x4a040`.

The muted 2,000-frame relay matches the corresponding archived guest hashes with zero interpreted blocks. The source-4 probe identifies VDP2 page `0x44000`. Twenty sampled 288 × 144 viewports at native (16, 8) match their exact decoded Saturn windows, including the moving section and the stop at offset 152. The 400-frame Zoom replay at 2560 × 1440 matches the same guest hashes and confirms exact native pixels at the four points below.

| Guest frame | Native vertical offset | Exact native pixels | PC 2× crop luminance correlation |
| --- | ---: | ---: | ---: |
| 7064 | 20 | 41,472 | 0.253 |
| 7160 | 68 | 41,472 | 0.451 |
| 7288 | 132 | 41,472 | 0.571 |
| 7352 | 152 | 41,472 | 0.553 |

The PC donor is `SAKURA1/BG/BG2247.SPR` subimage 0, 576 × 592. The crop comparison uses PC coordinates (0, 2y) with size 576 × 288, where y is the exact native offset. The upper dome, tower, sloped cornice and lower arch rails shift relative to one another across the four crops. The [independent affine-fit review](scroll-table.md#remaining-ten-offline-alignment-measurements-not-wired) also found a 0.392 worst-window correlation when fitting a shared crop. The asset depicts the same building from a different camera. The current crop renderer cannot preserve its native framing.

The coverage register attributes only the witnessed disc 2 appearance. Both discs contain the same file bytes. The BG2247 draw stays native. Raw captures, layer probes and comparison scripts are retained under `local/work/codex-bg2247/`.
