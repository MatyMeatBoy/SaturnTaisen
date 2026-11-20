# Additional narrative foreground cut-outs

Patch 0215 registers four distinct PC foreground pictures on the existing Chapter 3, 6 and 8 routes. All use the opaque NBG2 picture layer and a 288 × 144 fixed-cell source. The renderer obtains transparency from the original Saturn index zero. That keeps real black pixels inside BG3289 and preserves the cyan or magenta cut-out boundaries where applicable. PC subimage 0 uses its authored cyan key. Every visible replacement still requires the native palette, cell and file fingerprints, current source ownership, and agreement with the original RGB.

| Saturn foreground | Natural route | CD FAD | Sampled silhouette IoU | Changed pixels per active 1440p sample |
| --- | --- | ---: | ---: | ---: |
| BG3289 | English disc 1, Chapter 3 stage wing | 154135 | 0.978 | 1,347,527 |
| BG4059 | English disc 1, Chapter 6 continuation | 154618 | 0.981 | 151,928 |
| BG4119 | English disc 1, Chapter 6 cold opening | 155101 | 0.927 | 90,232 |
| BG4187 | English disc 2, Chapter 8 room | 132254 | 0.892 | 258,605 |

Each scene uses its natural retained checkpoint. The 3,750-field relay leading to BG3289 matches the archived Chapter 3 input replay. Six muted Direct3D 11 variants per scene match 80 strict guest fields and final SRAM with zero interpreted blocks. The valid donors draw 79 times per scene. Every changed pixel in the five 2560 × 1440 samples per scene matches the independently decoded and registered PC output exactly, inside the exact Saturn ownership mask. Two same-field layer probes also show 265 native pixels occluded by Chapter 6 sprites and 4,566 by Sakura in Chapter 8. Those pixels stay identical.

Original with and without a donor, and the Enhanced missing and changed-byte donor profiles, match their controls. Chapter 5 BG3132 and BG3133 reproduce all 336 strict hashes, final SRAM, and 14 RGB samples from patch0210. The pre-existing compact Save and Spanish Load checks reproduce all 168 guest fields, final SRAM, and 12 RGB samples on the exact stack through patch0213. This verifies the four listed appearances. Other discs and public package inclusion remain open. Private profiles, captures, route hashes and build commands remain under local/work/codex-tp3c/fg-followup.
