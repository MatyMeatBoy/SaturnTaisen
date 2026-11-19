# Disc 1 battle insets

Seven disc 1 battle illustrations use the opaque 288 Ãƒâ€” 144 inset already used for BBG204. Each PC image was compared directly with its Saturn source. The aspect-preserving source crop below uses the PC file of the same number in `SAKURA2/BG`. Palette and visible RGB keys restrict the renderer to the opaque Saturn footprint. The RGB keys are derived with the same RGB555 channel expansion and four-level darkening verified on the BBG204 route. Other color effects fall back to the native image.

| Picture | Palette FNV-1a | Tile FNV-1a | PC crop (x, y, width, height) |
| --- | --- | --- | --- |
| BBG003 | `197A8477C531433B` | `323F84FDE0EF28D2` | `(60, 17, 404, 202)` |
| BBG008 | `41D01AD83398ED85` | `125A139EBA2367B1` | `(0, 24, 568, 284)` |
| BBG103 | `86E3822CB554B9F7` | `94D19B0410D94567` | `(0, 24, 560, 280)` |
| BBG104 | `ABD0D13E0D42EED3` | `D8359964CCFE48AE` | `(0, 32, 576, 288)` |
| BBG106 | `7151C1F654A70069` | `35099D234D727E44` | `(0, 20, 544, 272)` |
| BBG205 | `C37A14C8F1D98E80` | `6366E166FAD934A6` | `(0, 32, 576, 288)` |
| BBG235 | `2BC159FCB08D0238` | `54474E7D086C304B` | `(16, 8, 544, 272)` |

On disc 1, BBG002 and EVE002 occupy different disc extents with byte-identical files. They share the existing palette, frame and donor entry for EVE002. BBG205 and EVE205 are also byte-identical, and the existing scene path continues to use the same PC image. The catalog records the insets as connected. Individual appearances remain for TP9 spot checks.

BBG203 stays on the pending list. Landmark alignment shows that its same-number PC picture omits about 41 Saturn columns on the right and five rows at the bottom. The four square item cards use a separate geometry. BBG204 is covered by its own episode 4 replay.

BBG235 uses a 576 × 288 donor. Patch 0127 checks the declared crop against the decoded image after verifying the entire SPR file hash, so this shorter PC source can supply its valid 544 × 272 rectangle. A crop extending past the image remains native.

## Square item cards

BBG004 is referenced by EVT04 at offset 0x1588. On event stage 6, after loading the tile and palette data, the map helper at 0020E470 receives tile column 13, row 5 and 14 × 14 dimensions. The row stride is 128 bytes for the 64-column map, with a 2-byte cell name. This gives the fixed rectangle (104, 40, 112, 112) on the native 320 × 224 canvas. BBG004–BBG007 use identical 14 × 14 cell-map layouts and their matching PC file has one 224 × 224 image.

The shared inset renderer requires the exact palette, rectangle of top-layer ownership and every native RGB pixel before drawing. The target keeps the original integer scale. A card at a different position, a blend or an interrupted transition will use the Saturn frame. No individual square-card appearance has been verified in a replay. The BBG002 regression retains its 1440p 1728 × 864 inset, with 60 identical guest hashes across the main, missing-donor and Original cases.
