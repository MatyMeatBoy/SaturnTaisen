# MAP04 tiled ground from the PC edition

The second tactical battle in Chapter 3 reads `MAP04.BIN` at FAD 232311 on English Saturn disc 1. The 343,168-byte Saturn and PC copies match exactly, SHA-256 `cbf03a915ce77f009c49c874354940717639447662317353724aa8f2710e0eaf`. The PC map table names `MAP04_A.SPR` as ground and separately identifies the priority and animated underground files.

The ground donor is 1,839,340 bytes, FNV-1a `B9A138FDA90D0DEF`, SHA-256 `3c1fb662bec664056bbc28f1bdb90d732b98e4e6b23f53b0c1309bf3303bdb42`. Its SPRED placement table places 629 decoded 64 × 64 bitmaps at 632 distinct coordinates on a 2048 × 2048 plane. The loader samples even rows and columns into the 1024 × 1024 native-coordinate plane. It checks the file identity, placement extents, image ordinals, and unique cell positions. Unoccupied, alpha-zero and cyan positions retain native pixels.

Enhanced recognizes the first 8,192 pattern-name bytes of source 4 on VDP2 page `0x40000`, FNV-1a `451ACDDB5522070E`. The existing ground compositor applies the native per-line color offset and changes only eligible top-source-4 pixels inside the original integer-scaled 320 × 224 center. The priority and animated underground layers remain native.

## Verification

Five muted strict-native 180-frame runs use the retained Chapter 3 tactical checkpoint and ordinary camera inputs. The four Enhanced/Original comparisons use one local executable containing 94 separately recorded, byte-verified EVT04 variants from the registered disc overlay. Every run matches the portable interpreter reference and reports zero interpreted blocks. The guest hash log SHA-256 is `59d65bd6965fb992bd62c308d7b5b99720743bb5bb102ae5bd1b9017eb863c44`.

| Capture | Native camera origin | 1440p changed pixels matching the independent ground decode |
| --- | --- | ---: |
| 24 | (210, 781) | 790,812 |
| 74 | (285, 781) | 903,312 |
| 122 | (285, 700) | 1,116,000 |
| 168 | (285, 700) | 1,110,636 |

Every changed pixel matches the corresponding independently decoded PC sample with the native (−4, −4, −4) offset. The missing and same-length corrupted donor runs match the native control. The Original pair is pixel-identical. The stationary captures at 122 and 168 retain native animation. The layer probe identifies 14,395 visible changing native pixels within the animated source-3 region that are unchanged by the HD replacement at both captures. MAP02 and MAP06 passed strict-native regression comparisons, and MAP21 passed the same renderer comparison with portable execution. Each regression matched 60 guest hashes and 1440p RGB.

The local proof is in `local/work/codex-map04/`. Full chapter exit and package verification remain open.
