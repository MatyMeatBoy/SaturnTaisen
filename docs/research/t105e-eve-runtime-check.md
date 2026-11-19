# T105e runtime check, 2026-11-19 (patch 0090): FAILED to show the feature

Isolated build `local/build/rebuild-t105` (sources `local/deps/satrecomp-t105`). It was not finished: `port/frontend_sdl.cpp.obj`
(13:12) predated the patched source (13:16), so the first exe did not contain 0090. `ninja sakura.exe` rebuilt 13 objects
(vdp, state, vdp1, raster, cd, sh2, layers, hle_bios, machine, renderer, frontend and others) and relinked; the exe below is that one,
run from the private copy `local/build/sakura-t105run/t105.exe`.

Scenes: EVE0101 = `battle-entry-ref-3000.state` (the table's witness); EVE202 = `t30-chapter2-followup/cold-native/finish.state`
(the table's witness). Each run: strict native, hidden unthrottled window, `--pc-assets local/work/pc-cab/out-bg`,
presentation_mode=1, scene_view=1, pc_hd_backgrounds=0 (the T74 path only runs with that value), 1,200 frames, with and without
`SATRECOMP_NO_EVE_HD`, `SATRECOMP_BACKGROUND_STATS=1`.

| scene | frames | per-frame hashes with / without NO_EVE_HD | interpreted | `EVE picture:` lines | frame-1198 shot with / without |
| --- | --- | --- | --- | --- | --- |
| EVE0101 | 1200 / 1200 | identical | 0 / 0 | none | 6af81aac8606 / 6af81aac8606 |
| EVE202 | 1200 / 1200 | identical | 0 / 0 | none | 0dbb277cfb71 / 0dbb277cfb71 |

Result: guest parity holds (hashes identical, 0 interpreted), but the feature never fired: no `EVE picture:` line and no
difference in the window shot in either scene, so the PC picture was never drawn. Both scenes show the story inset with the
dialogue box. Not established which condition fails: the EVE code sits inside the branch that is entered only when
`uploadLayer` of the picture mix fails (the check listed as missing in the PR), the layer-5 palette fingerprint may differ from the
table's, or the layer is not static or has fewer than 12,000 visible pixels. Status stays "unverified in game"; the table rows
must not be treated as working. Local captures (not committed): `local/work/t105e-eve/*/shot.png`.

## Diagnosis and fix, 2026-11-19 (second pass, patch 0090 rewritten)

Temporary traces in `local/deps/satrecomp-t105` (removed again) found three separate reasons the first version never ran, in this order:

1. **The whole presentation block is gated on `floral`.** `if (texture && floral && ...)` is entered only when layer 5 matches a known
   floral backdrop. In an EVE scene layer 5 is the picture itself (41,472 pixels = the whole 288x144 inset), so `floral` stayed null and
   neither the T74 code nor the EVE code was ever reached (no trace line at the `uploadLayer` call at all). The `uploadLayer` condition was
   therefore not the cause: once the block was entered, `uploadLayer` returned 0 (the EVE branch is reached).
2. **`AnalyzePresentation` rejects the scene** (`scene=0,0,0,0`): it counts the picture in layers 1, 2 and 4 and gives up when layer 2 or 4
   has pixels outside the inset. New `AnalyzeEvePresentation` (inset almost all layer 5, box from layers 0 and 3) returns the witnessed
   `9,8,306,212`. The `zoomSafe` check for sprites outside the inset (EVE0101: 498 layer-0 and 311 layer-2 pixels on the left, 475 layer-2 on
   top) is skipped for EVE scenes: the zoom crops to the inset by design.
3. **EVE0101 has a constant colour offset (-4,-4,-4) on layer 5**, so the old `!offset` test left `visible=0`. The palette fingerprint
   matches (`D3C319A0279AEDB3`, slot EVE0101) and the layer is static (`0,0,100,100,no effects`). The PC picture now gets the same offset
   (`OffsetBackdropPixel`, re-uploaded only when it changes).

The EVE zoom layout does not depend on `SATRECOMP_NO_EVE_HD` (the flag only keeps the PC picture out), so the two captures differ only
inside the inset. EVE scenes get the zoom layout of any narrative scene only with `--pc-assets` and `pc_hd_backgrounds=0`; this reframing of
EVE scenes is a decision for the owner (the approved Zoom frame is unchanged for every scene that already used it).

Result with the patched exe (`local/build/sakura-t105run/t105.exe`, copy; strict native, hidden window, `--pc-assets local/work/pc-cab/out-bg`,
presentation_mode=1, scene_view=1, pc_hd_backgrounds=0, 1,200 frames, `SATRECOMP_BACKGROUND_STATS=1`):

| scene | per-frame hashes with / without NO_EVE_HD | interpreted | `EVE picture:` line | window shot, differing region |
| --- | --- | --- | --- | --- |
| EVE0101 (`battle-entry-ref-3000.state`) | 1200 identical | 0 / 0 | `EVE0101 SAKURA2/BG/BBG001.SPR usable=1` | x 48-912, y 50-482 (the 864x432 inset) |
| EVE202 (`t30-chapter2-followup/cold-native/finish.state`) | 1200 identical | 0 / 0 | `EVE202 SAKURA2/BG/BBG202.SPR usable=1` | x 48-912, y 56-488 (the 864x432 inset) |

Compared with PIL `ImageChops.difference(...).getbbox()` on the 960x720 window shots at frame 1198. Still to do: a side-by-side visual
review of both pictures against the Saturn originals, and a check that the other scenes keep their captures (only EVE palettes enter the
new path). Local captures (not committed): `local/work/t105e-eve2/*/shot.png`.
