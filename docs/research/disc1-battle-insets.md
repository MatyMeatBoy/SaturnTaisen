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


## Controlled EVE plate replays

Patch 0190 adds EVE102, EVE105 and EVE207 to the exact source-5
288×144 inset path. The matcher requires the captured palette, the full
native pixel rectangle and the opaque RGB fingerprint. The visible
native RGB is the Saturn disc decode with the scene's signed −4
offset. The EVE105 crop follows the independent landmark registration
(462 inliers from 529 matches) and feathers six donor pixels along
its edges. The remaining pixels come from the Saturn frame.

| Disc-1 plate | CD FAD / sectors | Palette FNV-1a | Native RGB FNV-1a | PC donor crop (x, y, w, h) |
| --- | --- | --- | --- | --- |
| EVE102 | 221105 / 21 | `4308595E86AF5A10` | `22B9B9008C33A8D1` | (0,12,560,280) |
| EVE105 | 221126 / 22 | `87AEDEC945E0F9C3` | `36E30A75B96D379D` | (25,19,551,299) |
| EVE205 | 221168 / 19 | `C37A14C8F1D98E80` | `C8578462D33514F9` | (0,32,576,288) |
| EVE207 | 221187 / 22 | `3816EDE30024F930` | `02366C77791ABD9D` | (0,16,576,288) |

Each private QA seed changes only the active filename in a retained
English disc-1 EVT02 checkpoint. The real guest reader loads the plate
from the named CD extent. The pre-draw captures match in full RGB. The
donor-only and empty-folder pairs match all 2,932 guest fields and
final SRAM, with zero interpreted blocks. Same-length corrupt donors
preserve the Enhanced stock captures, and Original donor/empty pairs
match for all three added rows.

At 2560×1440, EVE102 and EVE207 change only the existing inset
(416,96)–(2144,960). Each of two sampled opaque frames matches
1,492,992 independently decoded donor pixels at the approved scale.
Their empty-folder captures match the 0188 runtime. The EVE205
regression matches 0188 with the donor present and with the folder
empty. EVE105 changes only (419,99)–(2135,957) inside the inset.
Each of four opaque EVE105 captures has 1,397,720 interior pixels within
two RGB levels per channel of the independent donor projection.

The tested build combines 0189, this patch and the independent IC08
table row (SHA-256
`b40e1081646c76ea343f5ab18e724783626cef59ee00ce1007cca5959624d87b`).
The controlled results certify the draw and fallback for those plate
identities. Their natural chapter occurrences remain open. Private
evidence is under `local/work/codex-tw5-next/refresh-audit/eve-0190/`
and `local/work/codex-th1/eve105-controlled/`.

## BBG203 partial PC coverage

A comparison against 46 decoded 2:1 candidates from the PC battle
background directory ranked BBG203.SPR image 0 first. The best
sampled 2:1 crop was (74,69)–(576,320), with luminance correlation
0.660. The next file scored 0.465. The existing landmark alignment
identifies the same artwork and its incomplete coverage. The pair
is recorded for the shared portion, with the render path pending.

On the prepared English disc 1, EVT03 contains the BBG203 filename
at offset 0x35C. The disc read to look for begins at FAD 220667.
The exact 33,792 tile bytes and 512 palette bytes were separately
searched in 319 retained local states around three Chapter 3 research
routes, with no match. The live inset must still be reached to check
its geometry and decide how to present the missing Saturn edges.

## BBG203 bounded registration

Patch 0320 adds the disc 1 MAP03 battle inset. The exact NBG3
footprint matches all 648 mapped cell names and all 41,472 visible
native pixels in the archived route. The donor is registered over
the native overlap and feathered before the uncovered right and lower
edges. The C++ compositor changes 100,215 pixels at 2x and writes
zero pixels outside the overlap.

The runtime prepares the texture asynchronously after the source-5
and exact final RGB checks. The native inset supplies pixels outside
the aligned area. Syntax and patch application passed. Linked HD
playback and package inclusion remain pending.
