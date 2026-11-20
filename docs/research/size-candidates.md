# TP2a-size: the 19 `unsupported-size` entries against the free-box row style

The 19 entries are 12 distinct pictures (one or both discs): BG1257, BG1280, BG2093, BG2247, BG2290, BG2338 and the seven full-screen battle frames BBG238-BBG243 and BBG300. BG2077 and BG1283 (named in TP2a7) are no longer in the list: patches 0143 and 0145 already added them as calibrated rows.

## The row style

The style asked for exists since patch 0143: a `ScrollFit` row gives the PC box of a native offset with its own scale and crop (`rate_milli`, `origin`, `length`, `cross`, `cross_length`), guarded by the exact native-window matcher. This work measures every candidate against that style and wider (any scale on both axes, any position) and adds what passes.

Method (`tools/measure_size_candidates.py`, numbers only; `config/hd-size-candidates.json`): for each native window (stride 4 on the scroll axis; the whole picture for full-screen ones) the best PC box over a scale grid and every integer position, scored with the 32x16 grey signature of `tools/gen_scroll_pictures.py`, floor 0.90. The per-window best is a ceiling: if its minimum is below 0.90 no affine row can pass either.

| Picture | Native / PC | Ceiling min / mean | Result |
|---|---|---|---|
| BG2093 | 320x144 / 592x320 | 0.951 / 0.967 | passes; row added (patch 0154): rate 1.796, origin 23, 512x320 crop, all 33 offsets, min 0.9665 |
| BG2290 | 432x144 / 864x320 | 0.877 / 0.972 | only offsets 0, 4 and 8 are below the floor; needs a minimum-offset and an end clamp in the row (see below) |
| BG1257 | 456x144 / 1181x320 | 0.863 / 0.879 | fails at every offset: PC composition differs |
| BG1280 | 512x144 / 1241x320 | 0.796 / 0.852 | fails: PC composition differs |
| BG2247 | 288x296 / 576x592 | 0.376 / 0.549 | fails: different camera (native pan stays native, see bg2247-native-pan.md) |
| BG2338 | 320x160 / BG2238.SPR 592x320 | 0.943 (whole picture, box 28,0,584,320) | passes as a still, but it is a cross-number pair of the BG2238 still, not a scroll window |
| BBG238 | 320x224 / 640x480 | 0.987, box (74,33)-(615,425) | passes, static full frame |
| BBG239 | idem | 0.848 | fails |
| BBG240 | idem | 0.985, box (66,40)-(639,471) | passes |
| BBG241 | idem | 0.926, box (64,20)-(591,479) | passes |
| BBG242 | idem | 0.915, box (0,79)-(610,454) | passes |
| BBG243 | idem | 0.989, box (44,37)-(588,453) | passes |
| BBG300 | idem | 1.000, box (8,0)-(640,473) | passes |

BG2077 and BG1283 stay as they are (rows of patches 0143/0145).

## What the style does not cover

- The full-screen 320x224 frames have no proportional PC correspondence: the six that pass each need their own box (scale 1.7-2.0 and an offset up to 79 px, different per picture), so there is no common rule beyond "one measured box per picture". The table row type is a 288x144 scrolling window at (16,8); a full-frame row needs a new matcher (exact comparison of the 320x224 layer) and draw path in `frontend_sdl.cpp`. That is TP2b, not data. The measured boxes above are the data half. BBG239 has no box over 0.90 (best 0.848).
- BG2093 only draws where the native window matches exactly. The witnessed dream (per-line viewport origin under a variable blend) never matches, so disc-2 BG2093 in chapter 8 stays `unsupported-size`; the disc-1 entry becomes `wired-unverified`.
- BG2338 is not variant B and has no scroll window.

## Native witnesses

All 131 saved states under `local/work` (chapters 1-2 plus the probes) were searched for 64-byte tile blocks of each target (and of the rows already in the table). None of them contains any of these pictures, so none is witnessed natively: BG2093 is `wired-unverified`, not `hd`. Scenario scripts that request BG2093 are 0900 (chapter 9); BBG238-BBG300 are disc-2 battle frames. A witness needs a chapter 9 state or a replay of those scenes.
