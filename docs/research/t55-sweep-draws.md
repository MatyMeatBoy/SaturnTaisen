# T55 sweep: 17 strict-native cases and scene draws (2026-11-20)

Executable: `local/build/sakura-sweep/sakura-full.exe`, a private copy (with `art/`) of the PR #621 build `sakura-full.exe`, SHA-256 `96d48742606321825f94bf9a2b0c07ec915b091adb2c82cdf6bea0624df1b6ee` (231 patches up to 0245 plus the 1,411,614-block AOT). Disc 1 and disc 2 English images prepared locally. Nothing here is a game pixel: names, frames and hashes only; states, movies, backups and captures stay in `local/`.

## 1. The 40,000-frame sweep of the 17 cases (T55)

Each case is the backup RAM of `tools/chapter_jump.py` (`seeds.json` of the chapter sweep) with its `input.movie` (Continue sequence plus a confirm press every 120 frames from frame 9,250), run by `tools/chapter_loads.py --frames 40200 --interval 500 --keep-all` strict native (`SATRECOMP_STRICT_NATIVE=1`, `SATRECOMP_NO_CALLS/NO_FUNCTIONS=1`), headless and unthrottled. Every run exited 0 (no untranslated block), wrote 40,200 frame hashes and printed `interpreted 0 (0.00%)`. The run was repeated twice (once deleting unused states, once with `--keep-all`) and both `frames.hash` logs have the same SHA-256 (determinism). Over the frames they share, the logs are also identical to the 40,000-frame hash logs of the earlier 1,357,536-block sweep (`chapter-sweep/d-*`; only its last, buffered line is cut): the full-stack AOT does not change guest hashes.

| Case | Disc | Exit | Frames | Interpreted | frames.hash SHA-256 (first 16) | Same on rerun | Files loaded | Scene/battle files first loaded (BG, BBG, MAP) |
|---|---|---|---|---|---|---|---|---|
| bank-3-battle-1 | 1 | 0 | 40200 | 0 | db13555626df4821 | yes | 37 | BG1008, BG1022, BG1198, BG4114 |
| bank-3-battle-2 | 1 | 0 | 40200 | 0 | 7596d15144b16c47 | yes | 32 | MAP04 |
| bank-3-battle-3 | 1 | 0 | 40200 | 0 | de0665a73cfae715 | yes | 20 | MAP05 |
| bank-4-battle | 1 | 0 | 40200 | 0 | 913bfec6f11122a6 | yes | 44 | BBG204, MAP06, MAP21 |
| bank-5-battle | 1 | 0 | 40200 | 0 | e15098ec4e17540c | yes | 48 | BG1031, BG1051, BG1198, BG1243, BG2058, BG2132, BG2133, BG2156, BG2258, BG2533, BG3132, BG3133 |
| bank-6-battle | 1 | 0 | 40200 | 0 | 9039d641e536dcb7 | yes | 32 | BG1021, BG1025, BG1199, BG2156, BG4059, BG4119 |
| bank-7-battle | 1 | 0 | 40200 | 0 | 54b4ee4b9759f4f2 | yes | 41 | BG1178, BG1181, BG1266, BG1267, BG1268, BG2014, BG2019, BG2080, BG2126, BG2160, BG4017 |
| bank-8-battle-1 | 2 | 0 | 40200 | 0 | 3186aa792a263aa3 | yes | 31 | BG1050, BG1212, BG2159, BG4187 |
| bank-8-battle-2 | 2 | 0 | 40200 | 0 | 869771f5d456107c | yes | 30 | BBG208, MAP14 |
| bank-9-battle-1 | 2 | 0 | 40200 | 0 | b992c6643d5d5d7f | yes | 54 | BG1076, BG1278, BG2017, BG2018, BG2031, BG2091, BG2092, BG2093, BG2100, BG2156, BG2160, BG2236, BG2238, BG3091 |
| bank-9-battle-2 | 2 | 0 | 40200 | 0 | 69a08d12312ec244 | yes | 39 | BG1143, BG1160, BG1282, BG2021, BG2160, BG4055 |
| bank-10-battle-1 | 2 | 0 | 40200 | 0 | 71cc329f92c7458c | yes | 42 | BG1160, BG1213, BG1284, BG1285, BG1292, BG1293, BG2020, BG2023, BG2244, BG2245, BG2246, BG3020, BG4055 |
| bank-10-battle-2 | 2 | 0 | 40200 | 0 | f084c665b437486f | yes | 32 | BBG218, MAP19 |
| bank-10-final-battle | 2 | 0 | 40200 | 0 | 9a0976a7a287121d | yes | 32 | BBG218, MAP19 |
| public-7 | 1 | 0 | 40200 | 0 | b161e16a0cc23763 | yes | 41 | BG1178, BG1181, BG1266, BG1267, BG1268, BG2014, BG2019, BG2080, BG2126, BG2160, BG4017 |
| public-9 | 2 | 0 | 40200 | 0 | 3a174a61c73b2870 | yes | 54 | BG1076, BG1278, BG2017, BG2018, BG2031, BG2091, BG2092, BG2093, BG2100, BG2156, BG2160, BG2236, BG2238, BG3091 |
| public-finale | 2 | 0 | 40200 | 0 | f83b8016735687d7 | yes | 55 | BG1072, BG2025, BG2026, BG2046, BG2057, BG2111, BG2162, BG2163, BG2164, BG2165, BG2166, BG2167, BG2247, BG2248, BG2284, BG2285, BG2286, BG2287, BG2288, BG3026, BG3046, BG3163, BG3164, BG3165 |

Result: 17/17 pass 40,200 frames with 0 untranslated and 0 interpreted blocks. No new block needs registering, so the EVT overlay registry is unchanged: the 1,411,614-block AOT covers every path the 17 cases reach. This closes the T55 sweep that earlier runs left at 6 + 6 cases; what stays open is the observation of the 19 inferred EVTs *in play* beyond these routes (a case only proves the loads it makes: chapter 3 battles load `MAP04/MAP05`, chapter 4 `MAP06/MAP21`, chapter 8 battle 2 `MAP14`, chapter 10 battles 2/final `MAP19`; the other EVT families were not reached by these backups).

## 2. Which `hd` scene pictures are really drawn

`tools/scene_draw_probe.py` (PR #604, in `main`) with a matched control: a donor root holding only the SPR under test and a control root without it, so both runs select the same floral backdrop; 2560x1440, 240-900 frames after the state, strict; the verdict needs the `scene picture:` trace, changed RGB pixels, the same strict guest hashes frame by frame in both runs, equal final SRAM and `interpreted 0`. Candidates came from (a) the retained states of the 17 cases at each BG/IC/EVE/BBG load, and (b) a discovery pass (full donor pack, 300 frames, trace only) over 465 states of `local/work/reattr`, `witness` (cold, jump, long and sweep routes) and `end2`; the 25 `hd` donors without a verified row that appeared were then probed with controls.

Promoted (verified in game, `verified_in_game: true`, 300 matched frames with identical guest hashes and SRAM, centre and foreground native layers intact in the 2560x1440 captures read by eye):

| Saturn picture | Chapter | State | State SHA-256 (first 16) | Pixels changed vs control |
|---|---|---|---|---|
| BG1062 | 9 | witness/long-public-9/seed-2/state-15999.bin | 0bb18c330c312e80 | 1280428 |
| BG1178 | 7 | reattr/run-bank-7-battle/state-21999.bin | 512f8401cae5f3a8 | 1988198 |
| BG1181 | 7 | witness/long-public-7/seed-2/state-8999.bin | ba9e51c7a81feeb3 | 1434912 |
| BG1195 | 8 | reattr/run-bank-8-battle-2/state-20499.bin | 5a1a3a196860e9d3 | 1867851 |
| BG1284 | 10 | reattr/run-bank-10-battle-1/state-6999.bin | 7ff6c626a56610c7 | 2028469 |
| BG1293 | 10 | witness/sweep-bank-10-battle-1/seed-1/state-1499.bin | 6830df124e300749 | 2029054 |
| BG2020 | 10 | reattr/run-bank-10-battle-1/state-8499.bin | 49bfcc37b1fbd27d | 1236123 |
| BG2097 | 9 | witness/long-public-9/seed-4/state-16999.bin | fa9f121380ac1398 | 1234196 |
| BG2110 | 9 | witness/long-public-9/seed-4/state-18999.bin | 0e31726dac51d867 | 1916581 |
| BG2160 | 9 | witness/long-public-9/seed-3/state-4999.bin | 2816334a3f4893d9 | 2028445 |
| BG2163 | 10 | reattr/run-public-finale/state-32499.bin | 341a721395ece9f4 | 1110728 |
| BG2164 | 10 | reattr/run-public-finale/state-33499.bin | 2905b8320630810b | 1341365 |
| BG2165 | 10 | witness/long-public-finale/seed-3/state-18999.bin | e8f9838e2cadcc59 | 1487559 |
| BG2166 | 10 | reattr/run-public-finale/state-30999.bin | 21b02aef30d82179 | 1764621 |
| BG2167 | 10 | witness/long-public-finale/seed-3/state-16999.bin | 4b0d3d1652750456 | 1712337 |
| BG2168 | 10 | reattr/run-public-finale/state-37999.bin | 84f8a73a7b1eb176 | 2009432 |
| BG2284 | 10 | witness/long-public-finale/seed-2/state-8999.bin | 45ffc1b68f0f9890 | 1803955 |

Also re-witnessed in the sweep states with matched controls (already verified before, no delta): BG1198, BG1008, BG1021, BG1031 (disc 1) and BG1143, BG2018 (for BG2017) (disc 2).

Not promoted:

| Donor | Result | Reason |
|---|---|---|
| BG1184 (disc 2) | DRAWN, rejected | The PC picture is framed differently from the Saturn picture (pool steps and wall shifted); same family as BG2247. Stays `hd` unverified. |
| BG1060 (disc 2) | DRAWN, rejected | The PC crop drops the left window column the Saturn picture shows. Stays unverified. |
| BG1072 (disc 2) | DRAWN, not promoted | This run sampled a fade-in and reports a brightness mismatch. The [separate settled Chapter 9 witness](hd-chapter-9.md#verified-bg1072-before-0901) remains recorded. |
| BG2236 first state | defect noted | In `reattr/run-bank-9-battle-1/state-13999.bin` (state SHA-256 prefix 503d7e0329777f95) the native frame blends a translucent figure over the picture; the donor run loses it. A settled capture changed 689,780 pixels from the control, but the figure loss keeps the donor out of this verified batch. Candidate for the blend guard in THD05. |
| BG1292, BG2091, BG2092, BG2111, BG2031 | trace only | Picture selected but no changed RGB pixels (the picture was under a fade or hidden by a foreground) |
| BG2533, BG2156, BG1051, BG2058, BG2258, BG2014, BG2023, BG2025, BG2026, BG2285, BG2286, BBG208, BBG218 | not drawn in the window | `unused in this replay window` from the states that precede their loads; BBG208/218 and the MAP floors load for battle (tactical path, not the Zoom scene path, so the scene probe cannot see them) |

IC, EVE, endings and MAP floors: none of the 17 cases loads an IC or EVE picture (they need intermission saves, see `docs/research/headless-scene-draw.md`), and the endings reached (`public-7/9/finale`) loaded only BG pictures in the window. MAP04/05/06/14/19/21 were loaded (see table) but the floor draw (patch 0188) was not captured here: the scene probe does not run the tactical path. These stay open under THD06/THD08.

## 3. Integration on the current register

The current file-based census adds 17 unique verified resources from
this sweep. The integrated count remains 585 of 1,095 and the verified
count rises from 151 to 168. The report uses the current scene register.
The older 1,167-file baseline and its totals are superseded by the
canonical resource census. The renderer and public package are unchanged.

### BG2236 on the public episode 9 route

A 5,000-field strict continuation from the public episode 9 checkpoint
at field 12,000 reached a second, settled BG2236 witness. The save at
field 16,499 has SHA-256
`9ebf5f957db33c9cfca0997e44ea061b000cc441991f744e2d9e5411421d50f0`.
At 2560 × 1440, v0.2.20-alpha selected the existing
`SAKURA1/BG/BG2236.SPR` and changed 2,021,423 pixels against the
missing-donor control. The runs matched all 72 guest hashes and ended
with zero interpreted blocks. This confirms reuse of the existing
file in the settled composition. The earlier translucent-figure
case remains open under THD05.
