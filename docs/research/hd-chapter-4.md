# HD chapter 4 coverage report (shard TH4)

Source: `config/hd-chapter-coverage.json` (`chapters[3]`, `unassigned`, `association`), cross-checked with `config/hd-scene-bg-map.json`, `hd-scene-bg-review.json`, `hd-body-map.json`, `hd-item-map.json`, `film-fad-map.json`, `docs/research/chapter-sweep.md` and `docs/PENDIENTES.md` (rows T31, T32, T87, TH4). Names, hashes and counts only. Nothing here certifies the chapter; the exit test (strict-native replay with per-frame guest hashes identical to a build without HD) has not been run.

## 1. Initial catalog snapshot for chapter 4 (disc 1)

This snapshot predates the BBG204 and MAP21 draws and the [first tactical map and work RAM evidence](#first-tactical-map-and-work-ram) below. Its entries were inferred from episode numbering.

| Class | Attributed to ch. 4 | Items |
|---|---|---|
| Scene pictures (BG/EVE/CG) | 1 | `TITLE4.BIN` |
| NC bodies | 0 | none |
| Portraits | 4 | `0400FCE`, `0401FCE`, `0402FCE`, `0403FCE` |
| FILM clips | 0 | none |
| Tactical maps / units | 0 / 0 | none |
| Menus/HUD | 0 | none |

Chapter 4 is not attributed any BG, EVE, NC body or clip even though the game plays them: the scene index has no ch. 4 observation. The only runtime evidence is the sweep route "Episode 4, File 1, CD-1" (6,678 complete frames, folder `bank-4-battle-strict`), which stops at the `/SAKURA2/EVT06.BIN` load (77,716 bytes at `00204000`); see T31 and T32.

Disc-1 pool that chapter 4 may draw from (all in `unassigned`, association `unknown`):

| Class | Disc-1 entries, unassigned |
|---|---|
| Scene pictures | 1537 |
| Bodies | 293 |
| Portraits | 237 |
| FILM | 53 (49 are `/SAKURA4+offset` streams; the rest are `OPSAKURA.CPK`) |
| Menus/HUD (ITEM, LOAD, WALL, WKL...) | 195 |
| Tactical maps / units | 27 / 27 |

## 2. Status per class

### Attributed to chapter 4

| Class | hd | paired-not-wired | unpaired | unknown |
|---|---|---|---|---|
| Scene pictures (1) | 0 | 0 | 0 | 1: `TITLE4.BIN` |
| Portraits (4) | 0 | 0 | 0 | 4: `0400FCE`..`0403FCE` |
| All other classes | 0 | 0 | 0 | 0 |

`TITLE4` appears in no catalog (`hd-scene-bg-map`, `hd-scene-bg-review`), so its status is `unknown`. The four portrait files are not in the portrait audit's atlas lists, so they are `unknown`. The Saturn title cards are 16:9-widened without art by patch0071 (T87); the PC `TITLE*.SPR` carry Japanese text and are not a pairing.

### Disc-1 pool (not chapter-attributed; upper bound for chapter 4)

| Class | hd | paired-not-wired | unpaired | unknown | Examples |
|---|---|---|---|---|---|
| Scene pictures (1537) | 917 | 474 | 104 | 42 | hd `BG1001`,`BG1002`,`BG1003`; pnw `BG1011`,`BG1012`,`BG1013`; unpaired `BG0000`,`BG1130`,`BG1131`; unknown `AI_CG`,`BG2338`,`BG2518`,`GE_CG` |
| Bodies (293) | 11 (5 distinct: `NC11`,`NC30`,`NC55`,`NC82`,`NC97`) | 246 | 30 | 6 | pnw `NC10`,`NC12`,`NC13`; unpaired `NC3013`,`NC3047`,`NC3057`; unknown `NC3125`,`NC3126`,`NC4138` |
| Portraits (237) | 181 | 0 | 0 | 56 | hd `000c`,`000e`,`0011`; unknown `0801FCE`..`0806FCE` |
| FILM (53) | 44 | 7 | 2 | 0 | hd `SAKURA4+0`,`+113262592`,`+132290560`; pnw `SAKURA4+100188160`,`+121135104`,`+178169856`; unpaired `OPSAKURA.CPK+0` (twice) |
| Menus/HUD (195) | 0 | 76 | 84 | 35 | pnw `ITEM01`,`ITEM02`,`ITEM04`; unpaired `ITEM03`,`ITEM09`,`ITEM12`; unknown `LOAD`,`TMAP`,`WALL1`,`WKL01` |
| Tactical maps (27) | 0 | 0 | 0 | 27 | `MAP01`..`MAP06` |
| Tactical units (27) | 0 | 0 | 0 | 27 | `UNIT01`..`UNIT06` |

Notes: bodies and FILM rows contain both discs' duplicates (e.g. `NC11` is counted twice; `film` 44 hd = the 44 distinct movies, MOVIE015 on both discs). Catalog summaries: scene map 519 content / 216 number / 5 missing; body map 104 content / 40 candidate; item map 12 content / 68 candidate; all counted over both discs and not split by chapter.

## 3. Five highest-value next actions

1. **Attribute chapter 4 resources by runtime evidence** (affects all 2,000+ pool items, closes the "no data" for every class). Run the Episode 4 route past the EVT06 boundary (T31/T32; `tests/` movie, folder `bank-4-battle-strict`), record the files loaded/drawn, and add exact witnesses to `CHAPTER_WITNESSES` in `tools/hd_chapter_coverage.py`; regenerate with `python tools/hd_chapter_coverage.py ... ` and `--check`.
2. **Wire the 246 `paired-not-wired` bodies** (largest single block): `config/hd-body-map.json` plus the NC draw table (`BODY_DRAWS` in `tools/hd_chapter_coverage.py`, documented in `docs/research/saturn-bg-format.md`); follow T106a-d.
3. **Wire the 474 `paired-not-wired` scene pictures** and resolve the 42 `unknown`: `config/hd-scene-bg-map.json` / `hd-scene-bg-review.json` (shared file, keep both sides on merge); wiring lives in the compiled scene table generator.
4. **Decide the 76 `paired-not-wired` and 84 `unpaired` menus/HUD** (ITEM files): `config/hd-item-map.json` (only 12 `content` matches vs 68 `candidate`); feeds S11 (TS11).
5. **Resolve ch. 4 stragglers**: the 56 `unknown` portraits (including `0400FCE`..`0403FCE`) via `docs/research/portrait-animation-coverage.md` audit; map the 7 `paired-not-wired` FILM cuts in `config/film-fad-map.json` (decision per alternate cut); classify `TITLE4` (no catalog entry) and the 27+27 tactical files (S11).

## 4. What cannot be known without playing (owner's discs)

- Which BG/EVE/CG pictures, NC bodies and portraits chapter 4 actually draws, and in what order.
- Which of the 31 disc-1 `/SAKURA4` streams play in chapter 4, and the conditions for alternate cuts.
- Whether `TITLE4` and `0400`..`0403FCE` are drawn and how the card fades over the VDP2 plane.
- Which tactical map(s) and unit sets the chapter's battle uses.
- Per-frame guest-hash identity of an HD run versus native across the whole chapter path (past EVT06; only the first 6,678 frames of the route are verified).
- Which faces the matcher leaves native in this chapter's bodies and their frame layouts.

## 5. Open questions

- Is the chapter 4 attribution to be inferred from `04xxFCE` numbering only, or must every class be placed by observed route evidence? Current data: no `observed` entries.
- Does the 12,000-frame boundary route (`episode4-aot-fix.json`) reach a point where residency can be read per resource? Intermediate and final segments are marked "still to be run" in `chapter-sweep.md`.
- Are the 11 `hd` body rows (5 distinct) reachable in chapter 4 at all? Evidence: no data.
- Counts in the catalog summaries are not split by chapter; per-chapter totals for the pool classes: no data.
- Which PC `TITLE4`/episode card source (if any) can pair with the Saturn card, given the PC cards are Japanese text (T87)?


## First tactical map and work RAM

English disc 1 starts the first tactical sequence with `EVT06.BIN`
and reads `MAP06.BIN` at FAD 232643. The archived Episode 4 File 1
route uses the seed from the chapter sweep and
`tests/chapter4-load.movie`. Stock captures at frames 10000, 12000
and 14000 independently align with PC MAP06_A.SPR. There are 66,
32 and 43 RANSAC inliers, respectively. All three fits give an
approximately 2× native-to-PC scale. Their PC offsets are
(880,304), (0,768) and (0,680). The capture at frame 8000 repeats
the previously witnessed BBG204 image. Its muted strict-native
replay completed 8000 frames with zero interpreted blocks, and
the 320×224 RGB picture matches the archived reference. Every guest
hash matches the first 8000 lines of the earlier EVT21-boundary
route. The new hash log SHA-256 is
`a68f2e612a81df64231877c283a9cfb438c1615946b29567b28a5b155365d413`.

The Saturn and PC copies of `MAP06.BIN` are byte-identical at 328,128
bytes, SHA-256
`70b44bd3d9e0a5fa3bf850cd55d51ce32db0be5d861fe9f3df91a3e8130b258a`.
The PC `MAP06.TAB` designates the 2048×2048 subimage 0 in MAP06_A.SPR
as ground. The register attributes this ground pair to chapter 4
with a [verified source-4 ground replacement](map06-pc-ground.md). The priority
layer and gameplay overlays still come from the native renderer.

The frame-14000 state has NBG2 scroll (0, 340), consistent with the
fitted PC origin (0, 680). Its first 8192 bytes at VDP2 page
`0x40000` have FNV-1a `B533F608A5E864D1`. The same extraction
reproduces the documented MAP21 signature on its saved state.


The initial battle reference state at frame 6678 and the saved
Stage21 entry match the complete work RAM payloads below. Their
starting offset is `0x1F800` in the low WRAM vector.

| File | Start FAD | Resident bytes | SHA-256 |
| --- | ---: | ---: | --- |
| WKL06.BIN | 254038 | 551,532 | `f9306a073a1c603658e7b6c132b6ef36e889086e990f2c8856e056db1c14af4b` |
| WKL21.BIN | 255679 | 537,572 | `60fed250c11dab1d28df048763315fc62b159a0cee502a73b473a63cef2734f3` |

These WKL records establish residency only. The CD trace requests
UNIT06 and UNIT21 at distinct start FADs 252313 and 252553. The files
share identical bytes, so a RAM match alone cannot distinguish
the unit loads or tell which sprites drew. Both unit rows remain
unassigned. MAP21 and BBG204 keep their earlier verified draw evidence.

Full chapter parity, new HD rendering and packaging remain open.


At block close the main workspace measured 61,180,516,152 logical bytes
with hard links counted once and reparse points excluded, above the
20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.


## Cold replay trace

Shard TH4 replayed the Chapter 4 jump again from a cold start with the CD
`Play Disc` trace of `tools/witness_sweep.py` (the same ISO 9660 mapping,
FAD = LBA + 150), but listing every file instead of only scenes. Input is
the archived `bank-4-battle` seed (`backup.bin` SHA-256
`ed2f71f1996faa34299cc39653fefc6d442787140ccfd16dfebd7feb3010a0cc`) and its
`input.movie` (`3a4344074c1adf5cce138588c30a6aa10f83fe31a6e7cc8eb54f1c390f8412b5`),
English disc 1, muted strict native, build SHA-256
`f2fcb44a037b1427cf9fc18f927747f826809461312b2a16e276d4cce93684a4`.
The run stopped at 18,373 guest frames with the known
`untranslated master SH-2 block at 00204000` (EVT21 entry, see
[the sweep](chapter-sweep.md)). The hash log of those frames has SHA-256
`2c176ed87f6e89ee164ea0135dda5dada054dc31152b6a175e0637f8e2d0d33e`.
Load frames are estimated from the flushed hash log (early or late by a few
dozen frames; the last ones fall at the stop), and the state is the first
checkpoint at or after estimate + 60. A load is a disc read: it shows that
the game asked for the file, not that the file was drawn.

| Frame (est.) | Checkpoint (frame, state SHA-256 prefix) | Files read |
| ---: | --- | --- |
| 6,670 | 7999, `16373ef61a5f` | `EVT06` 221950, `MAP06` 232643, `WKL06` 254038 |
| 6,865 | 7999, `16373ef61a5f` | `UNIT06` 252313, `FACE06` 222500, `M06MES` 231496, `FIX06` 223053 |
| 7,449 | 7999, `16373ef61a5f` | `BBG204` 220685 |
| 11,281 / 14,626 | 11999, `9e1186436b37`; 15999, `5f9fdfa4dfeb` | `N004`, `K004`, `IRIS.SE`, `PCMSE` (battle-side data, not register classes) |
| 15,927 | 15999, `5f9fdfa4dfeb` | `LIPS_CG` (also read by the Chapter 2 route, so it is left with the lower chapter) |
| stop (18,373) | no checkpoint (the run ends first) | `EVT21` 222176, `MAP21` 233572, `WKL21` 255679, `UNIT21` 252553, `FACE21` 222775, `M21MES` 231583 |

The route contains no BG, NC, portrait atlas or FILM read after the opening
logo and film (`SAKURA4` at FAD 405 and `OPSAKURA.CPK` at 166362, which every
cold start plays): the Chapter 4 save starts in the tactical module, so the
story scenes of the chapter are not reached from a battle save.

Attributed to Chapter 4 by this trace (rows moved from `unassigned`, association
`observed`): `UNIT06.BIN` (252313, read with `MAP06`) and `UNIT21.BIN` (252553,
read with `MAP21` and `WKL21`). Their status stays `unknown`: the disc read
identifies the unit bank the battle requested, not which sprites drew (the two
files are byte-identical, see above, so the earlier RAM match alone could not
decide). `MAP06`, `MAP21`, `WKL06`, `WKL21` and `BBG204` were already
attributed. Not verified in game: any draw of the two unit rows.

Still open for Chapter 4 (nobody has this witness yet): a save or jump into
the story part (`0400FCE`..`0403FCE`, `TITLE4`, backgrounds and bodies of
Chapter 4), FILM clips of the chapter, the battle that follows the
`00204000` stop, and the translated build that would let the route pass it.


## Re-attribution with the EVT overlay build

Shard TH-reattribution repeated the traced attribution with the isolated AOT build of [the EVT overlay registry](evt-overlay-registry.md) (1,357,536 blocks, which unblocks `00204000`; exe SHA-256 `2818e414...`, copied to `local/build/sakura-reattr/`). Each chapter-jump case (`backup.bin` plus the archived `input.movie`, extended with a confirm press every 75 frames) ran cold, strict native, headless, 45,000 frames, with `tools/chapter_loads.py --exe <exe> --disc 1 --backup <backup.bin> --movie <extended.movie> --frames 45000 --interval 500 --out local/work/reattr/run-<case>`. States and movies stay in `local/work`.

| Case | Exit | Frames | Interpreted 0 | Backup | Movie | Hash log |
| --- | ---: | ---: | --- | --- | --- | --- |
| `bank-4-battle` | 0 | 45000 | yes | `ed2f71f1` | `5bfe6029` | `9f81e42a` |

The route runs past the former `00204000` stop through the `EVT21` overlay (`EVT21`, `MAP21`, `WKL21`, `UNIT21`, all already attributed to chapter 4) and ends in a tactical module without story files. The only new register-class read is `SAKURA2/LIPS_CG.BIN` at frame 13,326, which the Chapter 2 route also reads, so it stays `unassigned`. No row moved.

Association is `observed`: a disc read shows the game asked for the file, not that it drew. Not verified in game: any draw of the moved rows.
