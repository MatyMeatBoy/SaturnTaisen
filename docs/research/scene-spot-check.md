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
| 32 | SAKURA1/BG/BG2053.SPR | 2:/SAKURA1/BG2053.BIN | yes, Chapter 9 |
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
| 10 | `1:/SAKURA1/BG1022.BIN` | 3 | not reached (no state) | OK |
| 20 | `1:/SAKURA1/BG1193.BIN` | 1 | DRAWN, hashes unchanged (below) | OK |
| 30 | `1:/SAKURA1/BG2039.BIN` | 1 | DRAWN, hashes unchanged (below) | OK |
| 40 | `1:/SAKURA1/BG2533.BIN` | 5 | not drawn on the reattr route (below) | OK (same scene, the PC picture is the cropped pan) |
| 50 | `2:/SAKURA1/BG1072.BIN` | 9 | not drawn on the reattr route (below) | OK (same room; the PC tint is lighter than the Saturn palette) |

Wrong pictures: 0, so no neighbour review was triggered.

### Numbers

- PC-versus-native captures for this audit: 2 of 5 (BG1193, BG2039); the other three are not reached or not drawn. [BG2533 has separate verified 1440p gameplay evidence](bg2533-pan.md).
- Error rate of what was drawn in game: 0 wrong of 2.
- Pair level: five catalog matches and zero mismatches in the selected examples.

### In-game half (2026-11-20, redone with the right preconditions)

The earlier runs drew nothing because the executable had no `art/` folder beside it ([headless-scene-draw.md](headless-scene-draw.md)). Redone with `tools/scene_draw_probe.py`: own copy `local/build/sakura-verify/sakura-verify.exe` (SHA-256 `2818e414...`, the isolated AOT build of #580) with `art/` beside it, `--pc-assets local/work/pc-cab/out-bg`, 2560x1440 Enhanced, `presentation_mode=1`, `scene_view=1`, `SATRECOMP_BACKGROUND_STATS=1`, strict native. Every sample runs twice (donor and no donor) from the same state; the per-frame guest hashes of the two runs are identical and both report 0 interpreted blocks. States replay with the cold-route movie `rb-full/input.movie` shifted to the state frame (the runtime does not index a movie by the saved frame), and the shifted run reproduces the original route hashes.

| # | Picture | State and route | Frame | Result |
|---|---|---|---|---|
| 20 | BG1193 | cold route, state at frame 252,000, SHA-256 `dbf9a25fd658...`; also `tp9/st/f253290.state` (`f9571001...`) | first draw 253,312; capture 253,357 | DRAWN, 1,198,577 pixels differ from the control |
| 30 | BG2039 | cold route, state at frame 138,000, SHA-256 `1c9021c787b2...`; also `tp9/st/f143070.state` (`c1b2dda1...`) | first draw 143,109; capture 143,154 | DRAWN, 2,019,152 pixels differ |
| 10 | BG1022 (chapter 3) | no state, `loads.json` or movie in `local/work` reaches it | none | not reached |
| 40 | BG2533 (chapter 5) | `reattr/run-bank-5-battle/state-11999.bin` (`38753899...`) with its movie, 700 frames (the load is at about frame 12,025) | 11,999-12,699 | NOT DRAWN: capture byte-identical to the control, no `scene picture:` line; a native scene was on screen. The PC picture is the cropped pan ([bg2533-pan.md](bg2533-pan.md)); this route does not show it |
| 50 | BG1072 (disc 2, chapter 9) | `reattr/run-public-finale/state-36499.bin` (`1faca6ae...`), disc 2, 700 frames (load at about frame 36,740) | 36,499-37,199 | NOT DRAWN: BG2111 and BG2251 were drawn instead, BG1072 was not |

For both drawn samples the changed pixels lie inside the Zoom picture rectangle (272,29)-(2288,1037); the dialogue box, the portrait and the lower frame are byte-identical to the control (read by eye on the BG2039 capture side by side: the photograph is the PC art, the box and the portrait are the native ones). Not checked: foreground sprites inside the picture rectangle (none were visible in these two captures), and a pixel-level comparison with the decoded PC subimage (done for BG2039 and BG1193 in the sections below).

Numbers now: in-game 2 of 5 drawn (BG1193, BG2039), 0 wrong; 2 reached but not drawn (BG2533, BG1072, cause not established), 1 not reached (BG1022). The register already marks BG1193 and BG2039 `verified_in_game`, so the deltas are attributed 0, integrated new 0, verified new 0.

### Not verified

For a follow-up on this route, reuse the separate [strict chapter 3 witness for BG1022](th3-native-attribution.md), the [verified BG2533 pan](bg2533-pan.md), and the [chapter 9 transition that captured the native BG1072 window](hd-chapter-9.md). The BG1072 capture supplies a starting point for a matched PC draw check.

## BG2034 on disc 1

The English Chapter 1 route reaches the drink scene from the retained field
59,098 checkpoint. Both 2,140-field 1440p Enhanced replays use the bundled
presentation art and the same 0176 runtime. The only difference is whether
the PC asset directory contains BG2034.SPR. All guest hashes match the
uninterrupted route, final SRAM matches between the cases, and both report
zero interpreted blocks.

The rendered scene changes only within (349,29)–(2288,1037) at replay
fields 1,980, 2,040 and 2,100. The other twelve full screenshots match,
including the early floral fade. The score checks the exposed right wall
at (1840,100)–(2220,350) against an independent decode of the 576×320 PC
subimage 0, resampled to the 2016×1008 picture. Mean absolute RGB error
is 0.137/0.129/0.127 with the donor and 46.951/45.679/40.204 without it
at each of those three fields. The comparison is confined to this
English disc 1 witness. Private samples and replay commands are under
`local/work/codex-th1/bg2034-live/`.

## BG2053 on disc 2

The Chapter 9 route enters Iris's room from the door-knock checkpoint.
Two 1,440-field English Enhanced replays at 2560×1440 load disc 2's
BG2053 at FAD 124053. They use the same executable, bundled presentation
art and recorded inputs. Only the donor replay has BG2053.SPR installed.
All guest hashes and final SRAM match, with zero interpreted blocks.

At fields 720 and 900 the changes are confined to the picture rectangle
(272,29)–(2288,1037). Iris, the bear and the bedding keep the Saturn
framing. Seven other sampled full frames match. In the patch of bedding
at (1750,480)–(2100,740), mean absolute RGB error against independently
decoded PC subimage 0 falls from 18.76 to 4.26 at both fields. This confirms
the existing scene replacement on disc 2. The private replay and receipts
are under `local/work/codex-th1/bg2053-live/`.

## BG1007, BG1046 and BG1058 on disc 1

Three independent English Chapter 1 Enhanced A/B replays at 2560×1440
use the same 0176 runtime, bundled floral art, and the exact saved-state
anchor for each scene. The PC directory contains only the named donor
in the enabled run and is empty in the control. The donors' full SHA-256
values match the scene catalog. Guest hashes and final SRAM match within
each pair, and all six runs report zero interpreted blocks. BG1007 and
BG1046 also match all 800 fields of their respective uninterrupted
Chapter 1 slices. For BG1058, the resumed continuation matches the cold
route through field 473 of 2,600 and then diverges while both A/B runs
remain identical to one another.

Each visible replacement changes only the picture rectangle
(272,29)–(2288,1037), with matching full-frame controls before the draw.
The BG1007 after-scene capture at field 740 also matches. The assay below
compares (1840,100)–(2220,350) to the independent 576×320 PC subimage 0
decode resampled bilinearly to 2016×1008. Each selected field gives the
same per-channel mean absolute RGB errors.

| Scene | Anchor field | Comparison fields | Donor RGB error | Missing donor RGB error |
| --- | ---: | --- | --- | --- |
| BG1007 | 77160 | 350, 450, 530 | 0.134/0.140/0.136 | 18.220/18.984/18.280 |
| BG1046 | 94380 | 260, 310, 380 | 0.117/0.123/0.119 | 10.071/10.699/10.405 |
| BG1058 | 103215 | 2140, 2220, 2280 | 0.090/0.080/0.076 | 12.477/11.604/9.791 |

Private commands and captures are under `local/work/codex-th1/ch1-scene-draws/`.

## BG1070 and BG2039 on disc 1

A natural 23,600-field continuation from Chapter 1 field 119,780
matches the uninterrupted guest hashes and provides exact checkpoints
at fields 142,710 and 143,000. The subsequent English disc 1 Enhanced
A/B replays run 650 and 470 fields respectively at 2560×1440. The PC
root either contains only the selected donor or is empty. The PC files
match the scene catalog's exact SHA-256, the guest hashes match both
within each pair and with the cold route, and both pairs retain the
same SRAM with zero interpreted blocks.

The changed samples remain inside (272,29)–(2288,1037) with seven
visible draws for each scene. The other seven BG1070 and five BG2039
samples match full RGB. An independent decode of each 576×320 PC
subimage 0 resampled to 2016×1008 verifies the crop
(1840,100)–(2220,350).

| Scene | Comparison fields | Donor RGB error | Missing donor RGB error |
| --- | --- | --- | --- |
| BG1070 | 240, 270, 330 | 0.119/0.117/0.128 | 54.706/55.175/52.173 |
| BG2039 | 145, 170, 220 | 0.098/0.081/0.078 | 10.042/7.724/7.118 |

This supplies the visible BG2039 proof missing in the earlier audit.
Private replays are under `local/work/codex-th1/ch1-scene-draws/`.

## BG1002 and BG1116 on disc 1

The English Chapter 1 replay has two 1440p A/B tests against the PC
donors selected in the scene catalog. One resumes at field 74,200
for 650 fields, the other at field 56,850 for 730. Guest hashes match
the uninterrupted run across both pairs and final backup RAM matches
within each pair. All four runs report zero interpreted blocks.

BG1002 changes in nine sampled captures and BG1116 in ten. The
preceding four and three captures respectively match in full RGB.
The changes are confined to the Zoom image rectangle
(272,29)–(2288,1037). The independent PC subimage 0 decoder matches
the reference crop at (1840,100)–(2220,350) after bilinear scaling.

| Scene | Comparison fields | Donor RGB error | Missing donor RGB error |
| --- | --- | --- | --- |
| BG1002 | 260, 310, 380 | 0.116/0.116/0.112 | 15.521/15.723/15.160 |
| BG1116 | 210, 260, 310 | 0.123/0.132/0.129 | 42.887/33.038/33.662 |

Private replay evidence is under `local/work/codex-th1/ch1-scene-draws/`.

## Late Chapter 1 backgrounds on disc 1

A muted, strict English disc 1 relay from the retained Chapter 1 field
143,150 checkpoint recorded four new checkpoints with the unchanged archived
input movie. Its first 961 guest hashes match the older uninterrupted run.
The rest of the comparison uses the new relay as its reference. The
renderer build includes patch 0187 and has SHA-256
`c216065dc774f1087cdd6aaf1aeee5fbe77a58ae474fc8ff7a668bb0fd82b805`.

Each 2560×1440 Enhanced replay has a donor-only PC folder and an empty-folder
control. All eight runs report zero interpreted blocks. Each pair matches
the relay on every guest field and has identical final backup RAM. Early
samples match in full RGB. When the donor draws, changes stay within the
Zoom picture at (272,29)–(2288,1037). At replay field 260, a 192×84 patch
clear of foreground sprites matches the independently decoded PC subimage
0 resized bilinearly to 2016×1008. The errors are mean absolute differences
in R, G and B.

| Scene | Relay checkpoint | Matching guest fields | Changed captures | With donor | Empty folder |
| --- | ---: | ---: | ---: | --- | --- |
| BG1030 | 228,420 | 620 | 6 | 0.058/0.068/0.047 | 30.070/28.119/27.665 |
| BG2535 | 232,800 | 620 | 6 | 0.087/0.076/0.083 | 51.403/45.726/42.637 |
| BG2173 | 239,080 | 620 | 6 | 0.081/0.079/0.057 | 7.117/5.810/3.398 |
| BG1193 | 253,100 | 660 | 5 | 0.113/0.115/0.124 | 33.032/33.172/33.970 |

BG1193 now has the live draw missing from the earlier offline audit.
Private replay commands, states, hashes and captures are under
`local/work/codex-th1/ch1-scene-draws/final-film-late/`.

## BG1143 and BG2004 on disc 1

A strict English Chapter 1 continuation from field 239,080 requested
23 sectors each at FAD 142078 and 146095. The disc directory identifies
`BG1143.BIN` and `BG2004.BIN` respectively. The replay did not request
the other files in either shared palette and cell group. This identifies
the exact disc-1 files behind the observed PC draws.

The two muted 2560×1440 Enhanced pairs use the 0188 renderer
(SHA-256 `fce7584605deda7351ae628f3568169436d890228aaaa5e135054ab11904ebf3`).
Each pair compares a PC folder containing only the named donor with an
empty control. All guest fields match the traced relay, backups match
within each pair, and all runs report zero interpreted blocks. Pixels
changed only within the Zoom rectangle (272,29)–(2288,1037).
The RGB errors are means for a foreground-free 192×84 tile against the
independently decoded donor resized to the Zoom picture.

| Scene | Relay anchor | Matching fields | Changed captures | With donor | Empty folder |
| --- | ---: | ---: | ---: | --- | --- |
| BG1143 | 253,100 | 560 | 1 of 5 | 0.151/0.146/0.156 | 46.162/45.101/43.838 |
| BG2004 | 255,900 | 630 | 4 of 6 | 0.006/0.008/0.007 | 6.658/7.592/9.092 |

BG1143 is visible at field 20 and the later samples match in full RGB.
BG2004 first changes at sampled field 170, after two matching samples.
Private replay commands, state anchors, CD trace, RGB captures and
comparison outputs are retained under
`local/work/codex-th1/ch1-scene-draws/aliases-0188/`.

## BG1171 on English disc 1

The natural Chapter 3 stage-wing continuation requests BG1171 at
FAD 142446 for 23 sectors. The archived native frames 8500 and 9000
show the same background. Resume the matching state and SRAM from
local/work/codex-th1/bg2290-live/after-stage-wing without controller input.

The exact runtime through patch 0188 matches 180 strict guest hashes
and SRAM with the donor present or absent. Both runs report zero
interpreted blocks. At frames 25, 75 and 150, all RGB differences
stay inside the existing image viewport (272,29) to (2288,1037).
The 1,330,988 changed pixels per capture match the independent bilinear
decode of BG1171.SPR subimage 0 within two levels per RGB channel.
Every changed pixel falls on unoccluded Saturn picture content before
replacement, so the native foreground remains exact.

Disc 2 and package inclusion remain open.

## BG1031 and BG1076 on English disc 1

The natural Chapter 3 continuation after the stage-wing pan requests BG1031
at FAD 139732 and BG1076 at FAD 140767, each for 23 sectors. Start from
wing-story/end.state with matching SRAM and use after-stage-wing/input.movie.
Both inputs are retained under local/work/codex-th1/bg2290-live.

The exact runtime through patch 0188 matches all 7,200 strict guest hashes
and SRAM with the two PC donors present or absent. Both comparisons report
zero interpreted blocks. Five 1440p captures show BG1031 between fields
1500 and 4500. Four show BG1076 between fields 5500 and 7000. RGB changes
stay inside the image viewport (272,29) to (2288,1037). Every changed pixel
falls on visible stock background before replacement and matches the
independent bilinear decode of the corresponding PC subimage within two
RGB levels. The Saturn foreground stays exact.

BG1031 also has a separate native Chapter 5 occurrence, and BG1076 has a
native English disc 2 Chapter 9 occurrence. Their HD draws on those
routes and package inclusion remain open.

## Isolated donor witnesses for Iris's room and the Chapter 9 opening

The English disc 1 Iris room checkpoint and the English disc 2 Chapter 9 opening checkpoint were replayed through patch 0217. Each case ran two 56-field strict-native profiles differing only in the availability of one PC file. All paired guest hashes and final SRAM matched. The runtime reported zero interpreted blocks.

| PC file | Natural checkpoint | Changed pixels per 2560 × 1440 capture |
| --- | --- | ---: |
| BG1101.SPR | Iris room, disc 1 | 1,250,234 |
| BG2018.SPR | Chapter 9 opening, disc 2 | 803,557–803,773 |

All eight comparisons changed only pixels in the (272,29)–(2288,1037) scene viewport. Every changed pixel came from the independently decoded native background and matched the bilinearly scaled PC decode within two RGB levels. The donor for the Chapter 9 opening has the shared native BG2017/BG2018 identity. The retained draw proves the PC file and the shared art. The full 12,000-field cold replay matched the archived guest hashes and SRAM. It read both aliases, finishing with BG2018 at FAD 123248, 23 sectors. The registry uses that canonical row for the shared draw and counts the physical PC donor once.

Private replay and pixel receipts are under `local/work/codex-th1/two-room-witnesses`. This evidence uses the existing runtime.
