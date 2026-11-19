# Stage21 ground from the PC edition

English disc 1 loads Stage21 during the second tactical sequence of episode 4. The disc's 237,312-byte MAP21.BIN matches the PC MAP21.BIN exactly. Its SHA-256 is `f01e20e18560ceb03cc27718373f0eedd6973cc8a0ff82d39b77eed43d032f91`. MAP21.TAB identifies MAP21_A as the ground, MAP21_B as priority scenery, and MAP21_Z as the all-map image.

The Enhanced compositor recognizes the Stage21 pattern-name signature `446FB372F79EDD04` at VDP2 source 4, page `0x40000`. MAP21_A.SPR is accepted at 1,105,672 bytes with FNV-1a `0006FEAF367A7203`. The asset has one 1118×910 image. The loader samples the same phase of each 2×2 source block as Stage01 to produce a 559×455 ground grid. The native world starts the PC drawing one row lower. Exact cyan and empty sample returns preserve the Saturn pixels behind the missing PC areas, including the rubble.

The chapter register places MAP21 in tactical maps, under episode 4.

The renderer uses the map scroll origin and covers only eligible source-4 pixels. It applies the source-4 color offset and preserves sprite, priority and shadow handling. Stage21 uses the baseline display fit and the ordinary menu and overlay path.

## Verification

- A fixed camera with a five-profile 2560×1440 comparison matched all 120 guest hashes. Enhanced with the ground asset absent or disabled matched in RGB, and the Original asset-present and asset-absent captures matched. The Stage01 extension asset was present during these controls.
- A D-pad replay at 2560×1440 matched all 180 guest hashes. Four captures sampled camera positions (104, 231) and (189, 231). Every changed RGB pixel equalled the expected PC sample after the native −4 color offset. The cyan-keyed area, UI and movement overlay remained intact.
- Stage01 regression matched 120 guest hashes and all four 2560×1440 RGB captures using the same Stage01 ground and extension assets.

The tested strict-native candidate used the isolated EVT21 extension described in [the chapter sweep](chapter-sweep.md#episode-4-second-tactical-overlay). Private receipts and build commands are in `local/work/codex-tw2-later-eve`. Other tactical layers, camera paths and package validation remain open.
