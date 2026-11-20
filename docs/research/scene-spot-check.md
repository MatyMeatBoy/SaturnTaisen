# Scene spot check (1 in every 10)

Owner request (2026-11-19): shards connect pictures without checking each one, so the integration desk samples them. The list is every 10th distinct PC picture of the %d marked `hd` in `config/hd-chapter-coverage.json`, in sorted order (%d pictures). Verify each by drawing it in game (the picture over the Saturn scene, framing, no wrong picture) and report in a PR: OK, wrong picture (give the right one), or not reachable. Pictures already `verified_in_game` need no new work. Regenerate the list when the register changes a lot; the sample is meant to estimate the error rate, so a wrong match found here means checking its neighbours (same palette family, same shard worker).

| # | PC picture | Saturn picture (first seen) | Already seen in game |
|---|---|---|---|
| 1 | SAKURA1/BG/BG1001.SPR | 2:/SAKURA1/BG1001.BIN | no |
| 2 | SAKURA1/BG/BG1011.SPR | 2:/SAKURA1/BG1011.BIN | no |
| 3 | SAKURA1/BG/BG1021.SPR | 2:/SAKURA1/BG1021.BIN | no |
| 4 | SAKURA1/BG/BG1031.SPR | 1:/SAKURA1/BG1031.BIN | no |
| 5 | SAKURA1/BG/BG1041.SPR | 1:/SAKURA1/BG1041.BIN | no |
| 6 | SAKURA1/BG/BG1051.SPR | 1:/SAKURA1/BG1051.BIN | no |
| 7 | SAKURA1/BG/BG1061.SPR | 1:/SAKURA1/BG1061.BIN | no |
| 8 | SAKURA1/BG/BG1071.SPR | 1:/SAKURA1/BG1071.BIN | no |
| 9 | SAKURA1/BG/BG1081.SPR | 1:/SAKURA1/BG1081.BIN | no |
| 10 | SAKURA1/BG/BG1091.SPR | 1:/SAKURA1/BG1091.BIN | no |
| 11 | SAKURA1/BG/BG1101.SPR | 1:/SAKURA1/BG1101.BIN | no |
| 12 | SAKURA1/BG/BG1111.SPR | 1:/SAKURA1/BG1111.BIN | no |
| 13 | SAKURA1/BG/BG1123.SPR | 1:/SAKURA1/BG1123.BIN | no |
| 14 | SAKURA1/BG/BG1148.SPR | 1:/SAKURA1/BG1148.BIN | no |
| 15 | SAKURA1/BG/BG1167.SPR | 1:/SAKURA1/BG1167.BIN | no |
| 16 | SAKURA1/BG/BG1177.SPR | 1:/SAKURA1/BG1177.BIN | no |
| 17 | SAKURA1/BG/BG1194.SPR | 1:/SAKURA1/BG1194.BIN | no |
| 18 | SAKURA1/BG/BG1209.SPR | 2:/SAKURA1/BG1209.BIN | no |
| 19 | SAKURA1/BG/BG1225.SPR | 1:/SAKURA1/BG1225.BIN | no |
| 20 | SAKURA1/BG/BG1235.SPR | 1:/SAKURA1/BG1235.BIN | no |
| 21 | SAKURA1/BG/BG1245.SPR | 1:/SAKURA1/BG1245.BIN | no |
| 22 | SAKURA1/BG/BG1266.SPR | 1:/SAKURA1/BG1266.BIN | no |
| 23 | SAKURA1/BG/BG1291.SPR | 1:/SAKURA1/BG1291.BIN | no |
| 24 | SAKURA1/BG/BG1301.SPR | 1:/SAKURA1/BG1301.BIN | no |
| 25 | SAKURA1/BG/BG1315.SPR | 1:/SAKURA1/BG1315.BIN | no |
| 26 | SAKURA1/BG/BG1326.SPR | 1:/SAKURA1/BG1326.BIN | no |
| 27 | SAKURA1/BG/BG1342.SPR | 1:/SAKURA1/BG1342.BIN | no |
| 28 | SAKURA1/BG/BG1353.SPR | 1:/SAKURA1/BG1353.BIN | no |
| 29 | SAKURA1/BG/BG2015.SPR | 1:/SAKURA1/BG2015.BIN | no |
| 30 | SAKURA1/BG/BG2028.SPR | 1:/SAKURA1/BG2028.BIN | no |
| 31 | SAKURA1/BG/BG2041.SPR | 1:/SAKURA1/BG2041.BIN | no |
| 32 | SAKURA1/BG/BG2053.SPR | 1:/SAKURA1/BG2053.BIN | no |
| 33 | SAKURA1/BG/BG2064.SPR | 1:/SAKURA1/BG2064.BIN | no |
| 34 | SAKURA1/BG/BG2075.SPR | 1:/SAKURA1/BG2075.BIN | no |
| 35 | SAKURA1/BG/BG2086.SPR | 1:/SAKURA1/BG2086.BIN | no |
| 36 | SAKURA1/BG/BG2099.SPR | 1:/SAKURA1/BG2099.BIN | no |
| 37 | SAKURA1/BG/BG2120.SPR | 1:/SAKURA1/BG2120.BIN | no |
| 38 | SAKURA1/BG/BG2133.SPR | 1:/SAKURA1/BG2133.BIN | no |
| 39 | SAKURA1/BG/BG2145.SPR | 1:/SAKURA1/BG2145.BIN | no |
| 40 | SAKURA1/BG/BG2156.SPR | 1:/SAKURA1/BG2156.BIN | no |
| 41 | SAKURA1/BG/BG2166.SPR | 1:/SAKURA1/BG2166.BIN | no |
| 42 | SAKURA1/BG/BG2200.SPR | 1:/SAKURA1/BG2200.BIN | no |
| 43 | SAKURA1/BG/BG2212.SPR | 1:/SAKURA1/BG2212.BIN | no |
| 44 | SAKURA1/BG/BG2222.SPR | 1:/SAKURA1/BG2222.BIN | no |
| 45 | SAKURA1/BG/BG2235.SPR | 1:/SAKURA1/BG2235.BIN | no |
| 46 | SAKURA1/BG/BG2250.SPR | 2:/SAKURA1/BG2250.BIN | no |
| 47 | SAKURA1/BG/BG2272.SPR | 1:/SAKURA1/BG2272.BIN | no |
| 48 | SAKURA1/BG/BG2283.SPR | 1:/SAKURA1/BG2283.BIN | no |
| 49 | SAKURA1/BG/BG2294.SPR | 1:/SAKURA1/BG2294.BIN | no |
| 50 | SAKURA1/BG/BG2520.SPR | 1:/SAKURA1/BG2520.BIN | no |
| 51 | SAKURA1/BG/BG2530.SPR | 1:/SAKURA1/BG2530.BIN | no |
| 52 | SAKURA2/BG/BBG107.SPR | 2:/SAKURA2/BBG107.BIN | no |
| 53 | SAKURA2/BG/BBG211.SPR | 2:/SAKURA2/BBG211.BIN | no |
| 54 | SAKURA2/BG/BBG249.SPR | 2:/SAKURA2/BBG249.BIN | no |

## BG1021 on disc 1

Sample 3 passed. The picture is the lobby staircase from English disc 1, `/SAKURA1/BG1021.BIN`. The PC donor is image 0 of `SAKURA1/BG/BG1021.SPR`, 576×320, with SHA-256 `6b9a590ae32013fa2531ab401f634797117f270fba44d87740dcb1fd361460ad`. The native palette fingerprint is `4CABAADB62E5EFAB`. The [Chapter 1 cold route](hd-chapter-1.md#observations-from-the-full-cold-route) identifies the scene around frame 59,800, and the [Chapter 6 native replay](th6-native-attribution.md#displayed-resources) independently identifies the same picture at CD FAD 139502.

Five muted 2560×1440 replays per scene used Enhanced with donor present, Enhanced with backgrounds disabled, Enhanced with an empty PC root, and Original with donor present or absent. Each profile used the same native KABE art with independent settings and backup copies. The only PC asset provided in the donor case was BG1021. The immutable MAP06 renderer build had SHA-256 `a501baae23cbd80e2259965e11427a970bb57c1100aec0768d56a11790de0db`. All runs used strict native execution and had zero interpreted blocks.

| Appearance | Resume source and capture | Identical guest hashes | Changed pixels |
|---|---|---|---:|
| Chapter 1, Iris at the staircase | Cold-route state saved at 60,150, capture at local frame 45 | 60 frames, SHA-256 `b5fc4dce40c06085fc90610257beabb669c5948f5a62e8e477b9069fbf351dfe` | 1,193,543 |
| Chapter 6, staircase after the transition | Archived Continue state saved at 11,999, capture at local frame 350 | 365 frames, SHA-256 `23ee1c728d7cb8fa9ccc0578ce61216fadfde6bd7c670b0cd817d3cc5b6d3795` | 1,955,736 |

Both changes were confined to the inset at `(272,29)`, 2016×1008 pixels. All 2,032,128 pixels in the Chapter 6 inset matched the bilinearly resized PC image within two RGB levels per channel, with mean RGB errors of 0.116, 0.114 and 0.108. A 310×290 interior sample of Iris and her teddy bear in Chapter 1 matched the disabled capture pixel for pixel. The disabled and missing-donor Enhanced captures were identical, and each Original pair was identical. SRAM matched across all five replays in each scene. The Chapter 1 cold replay also matched the earlier earned route for all 60,500 guest frames.

Private states, profiles, captures and hash logs are under `local/work/codex-th1/tp9-bg1021/`. This result covers the two English disc 1 appearances. The disc 2 listing still has no render witness. Package inclusion was outside this check.

## Offline audit of five pictures from an earlier Chapter-attributed snapshot

One in ten of the connected scene pictures, checked by eye. Names, status and verdicts only; no pixels are committed.

### Selection rule (reproducible)

The archived attributed subset had 58 distinct disc-qualified scene rows. The audit sorted their names and selected positions 10, 20, 30, 40 and 50. These five explicit selected names are recorded below.

### Verdicts

Two levels were tried. "In game" means the runtime drew the PC picture and a capture of it was compared with the native Saturn capture of the same scene. "Pair" means the decoded Saturn picture (`tools/decode_saturn_bg.py`) was compared by eye, side by side, with the decoded PC picture the table maps it to (`tools/decode_spred.py`); this checks the pairing data, not the runtime draw.

| # | Picture | Chapter | In game | Pair (offline, contact sheet) |
|---|---|---|---|---|
| 10 | `1:/SAKURA1/BG1022.BIN` | 3 | no comparable capture in this audit | OK |
| 20 | `1:/SAKURA1/BG1193.BIN` | 1 | no comparable capture in this audit | OK |
| 30 | `1:/SAKURA1/BG2039.BIN` | 1 | no comparable capture in this audit | OK |
| 40 | `1:/SAKURA1/BG2533.BIN` | 5 | no comparable capture in this audit | OK (same scene, the PC picture is the cropped pan) |
| 50 | `2:/SAKURA1/BG1072.BIN` | 9 | no comparable capture in this audit | OK (same room; the PC tint is lighter than the Saturn palette) |

Wrong pictures: 0, so no neighbour review was triggered.

### Numbers

- PC-versus-native captures for this audit: 0 of 5. [BG2533 has separate verified 1440p gameplay evidence](bg2533-pan.md).
- Error rate of what was reached in game: undefined (nothing reached).
- Pair level: five catalog matches and zero mismatches in the selected examples.

### Why the in-game check failed

BG2039 (frames 143,040-143,100) and BG1193 (253,260-253,320) lie on the chapter 1 cold route, which the input movie `local/work/rb-full/input.movie` (297,107 frames) reaches from a cold start. Headless runs with a copy of an existing build at `local/build/sakura-tp9run/` and `--pc-assets local/work/pc-cab/out-bg` with `pc_hd_backgrounds=0` did not draw any PC scene picture: no `scene picture:` trace line appeared and a PC capture was pixel-identical to the native one, in a state saved at frame 143,070 and in the cold route at frame 8,850 (BG1209, which the coverage report records as drawn). The build of 2026-11-18 predates the PC scene draw; the later builds tried either crashed at startup (t118) or ran no recompiled blocks (t116, t120). The frame 143,070 capture also shows a bedroom, not a group photo, so the guest-frame bracket in `hd-chapter-1.md` is the callback frame, a separate displayed-frame witness requires additional replay. The attempted builds provided no positive HD draw control, so these runs provide no runtime verdict for these two backgrounds.

### Not verified

The earlier audit adds only these five offline comparisons. The remaining spot checks stay open.
