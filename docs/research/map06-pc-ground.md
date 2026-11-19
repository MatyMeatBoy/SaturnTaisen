# MAP06 ground from the PC edition

The first tactical battle in Episode 4 reads MAP06.BIN at FAD 232643 on English Saturn disc 1. The 328,128-byte Saturn and PC files match exactly, SHA-256 `70b44bd3d9e0a5fa3bf850cd55d51ce32db0be5d861fe9f3df91a3e8130b258a`. The PC table specifies MAP06_A.SPR as ground. Its only image is 2048×2048, 6,152,194 bytes, FNV-1a `08A5D85E913F97BAB`, SHA-256 `53361c5f205203eb0ac652f9cd01bbb0a987ad620694932b10eb08a43eeb0aac`.

Enhanced uses the existing source-4 ground compositor when the 8,192-byte pattern-name table at VDP2 page `0x40000` has fingerprint `B533F608A5E864D1`. Each native ground coordinate takes the corresponding even row and column of the PC image. The colour offset, priority layers, dialogue, units, and unsupported blend cases retain their native composition rules. The registered PC image is optional. The native source supplies cyan, empty, or out-of-bounds samples.

## Verification

Three English disc 1 state resumes use distinct MAP06 camera positions. At each one, 180 strict-native guest frame hashes match across the tested profiles. The first position has Original present/absent controls. At 1080p the same position also has a same-length corrupt donor control. Original is identical in RGB with and without the PC file. The corrupt donor yields the missing-donor RGB. Differences in Enhanced are confined to the existing 320×224 integer-scaled centre.

| Route checkpoint | Camera origins observed at 1440p | Exact changed logical RGB samples in four captures |
| --- | --- | --- |
| 10000 | (440,152), (429,157), (272,236), (272,236) | 51,080 / 49,897 / 46,964 / 46,991 |
| 12000 | (0,384) | 37,553 / 37,663 / 37,305 / 37,522 |
| 14000 | (0,340) | 43,565 / 43,476 / 43,472 / 43,650 |

Every changed sample equals the independent PC image decode at the corresponding VDP2 camera coordinate, after the native colour offset. At checkpoint 12000 the signed offset is −64 in each channel and clips to the RGB range. During the camera pan after checkpoint 10000, the window capture at frame 74 shows the rendered state recorded at 73. The additional adjacent-state capture independently confirms that origin.

The headless strict replay matches the first 14,000 guest hashes of the archived Continue-to-battle route, SHA-256 `4f025e825d0c5cb232f7f42364411a2159fbdac860595bdfc254f15e8be11fd8`. Windowed RGB and 60 guest hashes match the previous renderer on MAP02 in strict mode and MAP21 in interpreter mode. The isolated interpreter check covers only MAP21 presentation. It uses the same checkpoint on both binaries.

Evidence is under `local/work/codex-tw2-fullscreen-bbg/chapter4-map06/`. Full chapter exit and package verification remain open. At verification the project measured 62,467,200,457 logical bytes, above its 20 GB limit. The delivered development ZIP remains 6,315,009,692 bytes.
