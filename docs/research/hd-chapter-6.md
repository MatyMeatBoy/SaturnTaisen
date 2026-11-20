# HD chapter 6 coverage report (shard TH6)

The [Chapter 6 native evidence](th6-native-attribution.md) adds observed scene pictures to the chapter register. It records display, residency, and disc reads separately. The complete replay and HD exit test are open.

## Earlier catalog snapshot

Source data only: `config/hd-chapter-coverage.json` (chapter 6 entry and `unassigned`), the HD map configs, `docs/research/chapter-sweep.md`, `docs/SHARDS.md` and `docs/PENDIENTES.md`. Names, hashes and counts only. No replay was run for this report; nothing here certifies the chapter.

## 1. Scope

Chapter 6 is on disc 1 (`/SAKURA1`, family `0601`). The Continue-screen sweep observed episode 6 and shows that the `0601` BIN/TBL/FCE family matches RAM byte for byte (chapter-sweep.md). The chapter entry in the coverage JSON holds only 8 attributed resources.

| Class | Attributed to chapter 6 | Basis |
| --- | --- | --- |
| Scene pictures | 1 (`1:/SAKURA1/TITLE6.BIN`) | inferred from the file name |
| NC bodies | 0 | no data |
| Portraits | 7 FCE atlases (`0601FCE` to `0607FCE`) | `0601FCE` resident in RAM, the other 6 inferred from numbering |
| FILM clips | 0 | no data |
| Tactical maps and units | 0 | no data |
| Menus/HUD | 0 | no data |

Association levels: `observed` (seen in runtime evidence), `resident` (matches RAM, not shown drawn), `inferred` (numbering or atlas membership), `unknown`. Chapter 6 has 0 observed, 1 resident and 7 inferred entries.

Unattributed pool, which may include chapter 6 items but is not assignable from the data: 1537 scene pictures, 293 bodies, 237 portraits, 53 FILM streams, 195 menu/HUD files, 27 maps, 27 unit files. `2:/SAKURA1/TITLE6.BIN` (disc 2 copy) sits there with association `unknown`.

## 2. Status per class (chapter 6 entries)

| Class | hd | paired-not-wired | unpaired | unknown |
| --- | --- | --- | --- | --- |
| Scene pictures | 0 | 0 | 0 | 1: `TITLE6.BIN` |
| NC bodies | 0 | 0 | 0 | 0 |
| Portraits | 0 | 0 | 0 | 7: `0601FCE` ... `0607FCE` |
| FILM | 0 | 0 | 0 | 0 |
| Tactical | 0 | 0 | 0 | 0 |
| Menus/HUD | 0 | 0 | 0 | 0 |

The status is `unknown` because no pairing is recorded for these files in the input catalogs. It does not mean they have no HD version.

Context from the unassigned pool, which is the likely source of the other chapter 6 items once attributed (counts as `hd` / `paired-not-wired` / `unpaired` / `unknown`):

| Class | Pool | Counts | Example IDs |
| --- | --- | --- | --- |
| Scene pictures | 1537 | 917 / 474 / 104 / 42 | hd: BG1001, BG1002; paired: BG1011, BG1012; unpaired: BG0000, BG1130; unknown: AI_CG, BG2338 |
| Bodies | 293 | 11 / 246 / 30 / 6 | hd: NC11, NC30, NC55, NC82; paired: NC10, NC12; unpaired: NC3013, NC3047; unknown: NC3125, NC4138 |
| Portraits | 237 | 181 / 0 / 0 / 56 | hd: 000c, 000e, 0011; unknown: 0801FCE, 0802FCE |
| FILM | 53 | 44 / 7 / 2 / 0 | hd: `SAKURA4+0`, `SAKURA4+113262592`; paired: `SAKURA4+100188160`; unpaired: `OPSAKURA.CPK+0` (both discs) |
| Menus/HUD | 195 | 0 / 76 / 84 / 35 | paired: ITEM01, ITEM02; unpaired: ITEM03, ITEM09; unknown: LOAD, TMAP, WALL1 |
| Tactical maps | 27 | 0 / 0 / 0 / 27 | MAP01 to MAP04 |
| Tactical units | 27 | 0 / 0 / 0 / 27 | UNIT01 to UNIT04 |

Related catalog totals: `hd-scene-bg-map` 519 content + 216 number-tier pairs + 5 missing; `hd-body-map` 104 firm + 40 candidates; `hd-item-map` 12 content + 68 candidates; `film-fad-map` 54 streams, 2 unpaired PC, 0 unpaired Saturn. Portrait `hd` entries in the pool are keyed by atlas index and carry no chapter.

## 3. Five next actions, ordered by items closed

1. Attribute scene pictures to chapter 6. The chapter holds 1 of 1537 pictures, so the largest gap is evidence. Replay the chapter 6 path with `SATRECOMP_BODY_TRACE`-style tracing, record the BG/EVE/CG files drawn, and extend the observed list. Files: `tools/hd_chapter_coverage.py` (`CHAPTER_WITNESSES`), `config/hd-chapter-coverage.json`, `docs/research/chapter-sweep.md`. Closes up to the full scene-picture list, count no data.
2. Resolve the 7 FCE atlases (`0601FCE`-`0607FCE`) to portrait indexes using the portrait audit (`portrait-animation-coverage.json`), then mark them hd or native. Files: `docs/research/portrait-animation-coverage.md`, `tools/hd_chapter_coverage.py`. Closes 7.
3. Observe the chapter 6 NC bodies and sort them. In the pool 246 are paired-not-wired and only 6 draw (NC11, NC20, NC30, NC55, NC82, NC97). Follow T106a2/T106b2/T106d. Files: `config/hd-body-map.json`, `config/hd-nc30-face-map.json`, `config/hd-nc20-face-map.json`, `docs/research/saturn-bg-format.md`. Count for chapter 6: no data.
4. Map the chapter 6 FILM clips (the entry has none attributed). 7 pool streams are paired-not-wired and 2 are unpaired; each alternate cut needs a decision. Files: `config/film-fad-map.json`, `tools/hd_chapter_coverage.py`. Count: no data.
5. List chapter 6 tactical maps/units for S11 (TS11, all 54 pool files unknown) and decide the `TITLE6` card (T107d/T107f). Files: `config/hd-chapter-coverage.json` tactical sections, `docs/PENDIENTES.md` rows TS11, T107f. Closes 2 for the card (disc 1 and disc 2 copies), tactical count no data.

## 4. Cannot be known without playing (owner's discs)

- Which BG/EVE/CG pictures, bodies, portraits and clips chapter 6 actually draws, and in which order.
- Whether a resident file (`0601FCE`) is drawn, and which portrait frames appear.
- Which maps and units the chapter 6 battles load.
- Per-frame guest-hash equality of a strict native replay of the chapter 6 path with HD against the build without HD, as required by the SHARDS exit test.
- Whether native fallbacks (NC11, NC30 faces) show in chapter 6 scenes, and how the `TITLE6` card fades in.
- Zoom suitability of any chapter 6 scene (chapter-sweep marks it unknown, fallback native).

## 5. Open questions

- Is chapter 6 evidence limited to `0601`, or do `0602`-`0607` belong to later scenes of the same chapter? The data only infers them from numbering.
- Do the disc 1 and disc 2 `TITLE6.BIN` copies need separate entries? The JSON lists them apart.
- Should the unassigned pool be split by chapter from the scene index (`local/work/scene-index-later`) before TH6 starts? That index is not in Git, so this report did not read it.
- The JSON has no menus/HUD attribution rule; which HUD files count as chapter 6?
- Count of chapter 6 scene pictures: no data. Count of chapter 6 FILM streams: no data.


## Traced attribution (TH6)

Tool: `tools/chapter_loads.py` (every `Play Disc` command mapped to its ISO file; FAD = LBA + 150; a state every 500 frames). English disc 1, `bank-6-battle` seed (backup SHA-256 `6633cfb0...`), the archived 12,000-frame chapter-jump movie extended with the same confirm cadence (a press every 75 frames) to 45,000 frames (movie SHA-256 `f248fe86...`). Strict native, zero interpreted blocks, exe SHA-256 `f2fcb44a...`. The first 12,000 frame hashes are byte-identical to the archived `bank-6-battle-strict` log; the 45,000-frame hash log has SHA-256 `6421ca86...`. Command: `python tools/chapter_loads.py --exe local/build/sakura-th56/sakura-th56.exe --disc 1 --backup <bank-6-battle backup.bin> --movie <extended input.movie> --frames 45000 --interval 500 --out local/work/th56/long-6`. States stay in `local/work`; only names, frames and hashes are here.

Frames are estimates from the buffered hash log (early by up to a few dozen); the checkpoint is the first state at or after estimate + 60.

Confirm-cadence route (`long-6`):

| File | Class | FAD | Frame (est.) | Checkpoint | State SHA-256 (prefix) |
| --- | --- | ---: | ---: | ---: | --- |
| `SAKURA1/LOAD.BIN` | menu/HUD | 160869 | 6475 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/0601.BIN` | script/data | 130578 | 6670 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/0601TBL.BIN` | script/data | 130728 | 6670 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/0601KNJ.BIN` | script/data | 130712 | 6670 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/0601FCE.BIN` | portrait atlas | 130596 | 6670 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/KABE50.BIN` | other | 159586 | 6670 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/NCOBJ.BIN` | other | 165874 | 6865 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/TMAP0.BIN` | menu/HUD | 172679 | 6865 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/TMAP1H.BIN` | menu/HUD | 172714 | 6865 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/TMAP2CH.BIN` | menu/HUD | 172924 | 6865 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/TMAPSP.BIN` | menu/HUD | 172994 | 6865 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/VDP1.BIN` | other | 216654 | 6865 | 6999 | `1d86c9e4d71afd55` |
| `SAKURA1/TITLE6.BIN` | scene | 172346 | 7059 | 7499 | `a3a261523d5742ae` |
| `SAKURA1/VCEADV` | other | 216468 | 7059 | 7499 | `a3a261523d5742ae` |
| `SAKURA1/BG1199.BIN` | scene | 142906 | 7643 | 7999 | `e34dd62318d663e8` |
| `SAKURA1/BG4119.BIN` | scene | 155101 | 7643 | 7999 | `e34dd62318d663e8` |
| `SAKURA1/BG2156.BIN` | scene | 149345 | 12025 | 12499 | `93884953f3f769e9` |
| `SAKURA1/BG1021.BIN` | scene | 139502 | 12396 | 12499 | `93884953f3f769e9` |
| `SAKURA1/BG1025.BIN` | scene | 139594 | 13511 | 13999 | `44d7d0e210259d23` |
| `SAKURA1/BG4059.BIN` | scene | 154618 | 13511 | 13999 | `44d7d0e210259d23` |
| `SAKURA1/NC97.BIN` | body | 165809 | 13697 | 13999 | `44d7d0e210259d23` |

The confirm cadence stops loading anything after `NC97` (frame 13697): the dialogue waits. Random input continues the chapter. From the `long-6` state at frame 13999 (`--state ... --auto 1:0 --frames 15000`; frames below are local to this continuation):

| File | Class | FAD | Frame (est.) | Checkpoint | State SHA-256 (prefix) |
| --- | --- | ---: | ---: | ---: | --- |
| `SAKURA1/BG1047.BIN` | scene | 140100 | 1025 | 1499 | `5ea4b910f64391f2` |
| `SAKURA1/NC40.BIN` | body | 164276 | 1025 | 1499 | `5ea4b910f64391f2` |
| `SAKURA1/BG1008.BIN` | scene | 139203 | 3556 | 3999 | `c83b2e0cea1d6cec` |
| `SAKURA1/LOADBGR.DAT` | menu/HUD | 160945 | 4334 | - | - |
| `?` | other | 212 | 4334 | - | - |
| `SAKURA3/MINIMAIG.BIN` | other | 267957 | 4334 | - | - |

From the `long-6` state at frame 12499 (`--auto 2:0 --frames 9000`):

| File | Class | FAD | Frame (est.) | Checkpoint | State SHA-256 (prefix) |
| --- | --- | ---: | ---: | ---: | --- |
| `SAKURA1/BG1003.BIN` | scene | 139088 | 822 | 999 | `bbcf322bc9342900` |
| `SAKURA1/BG1047.BIN` | scene | 140100 | 1415 | 1499 | `b8d2ca3c307022bc` |
| `SAKURA1/NC40.BIN` | body | 164276 | 1415 | 1499 | `b8d2ca3c307022bc` |
| `SAKURA1/BG1008.BIN` | scene | 139203 | 2972 | - | - |
| `SAKURA1/LOADBGR.DAT` | menu/HUD | 160945 | 3166 | - | - |
| `?` | other | 212 | 3166 | - | - |
| `SAKURA3/MINIMAIG.BIN` | other | 267957 | 3166 | - | - |

Both continuations end with exit code 4 `strict AOT: untranslated master SH-2 block at 00204000` right after `LOADBGR.DAT` and `SAKURA3/MINIMAIG.BIN`: the route reaches a new executable boundary. The PC address is shared with battle overlays and does not identify the loaded module. No `EVT`, `MAP` or `UNIT` file was read before the stop.

Attributed to chapter 6 by this pass: scene pictures `BG1003` and `BG1047` and body `NC40` (disc-1 rows moved from `unassigned`, status `hd`, not verified in game) plus second-occurrence rows for `BG1008` (chapter 3 row kept), `BG1021` and `NC97` (chapter 1 rows kept). Already chapter 6 and re-confirmed: `TITLE6`, `BG1199`, `BG4119`, `BG1025`, `BG4059`, `BG2156`. 9 JSON entries changed. `0601FCE` is read at FAD 130596 (resident row kept). Chapter-neutral loads (`LOAD.BIN`, `TMAP*`, `KABE50`, `VDP1`, `NCOBJ`, `ADV*`, `VCEADV`, `LOADBGR.DAT`) are listed above but not attributed.

Not verified: any HD draw of the new rows; the FILM clips of the chapter (none read after the opening FADs 405 and 166362, which precede the script); `0602FCE`..`0607FCE` (not read); the tactical stage; the chapter exit test. The random-input continuations show the branch the autopilot chose, not the canonical path.

### Episode 6 execution boundary on the 678,135-variant candidate

A fresh strict cold replay completed 14,000 fields. The first 12,000 field hashes equal the archived opening. From state 13999 and random input `1:0`, the candidate (SHA-256 prefix `f62001ee`) completed 4,405 fields before stopping at `00204000`. The last identified disc read is `/SAKURA3/MINIMAIG.BIN` (FAD 267957).

A second strict run saved field 4404. Loading that boundary with `SATRECOMP_NO_BLOCKS=1` completed 180 fields and read `/SAKURA3/SDDRVS.BIN` and `/SAKURA3/MINIMAIG.SND` (FAD 270955 and 268304). There were no EVT, MAP or UNIT reads in that interval. The traces show entry into the minigame branch. The entry state holds all 475,592 bytes of `/SAKURA3/MINIMAIG.BIN` verbatim at `00204000` in Low WRAM. The first two interpreter checkpoints retain exact equality. Captures and logs stay in `local/work/codex-th6-current`.
The 600-field interpreter reference from field 4404 yielded 1,692 variants beyond the 678,135-variant seed. Every complete extent matches that file and the set includes the missing entry PC. The `MINIMAIG_EP6` registry entry regenerates the 679,827-variant candidate database from the local English disc. A candidate with patch 0244 and the new blocks (SHA-256 prefix `9e7c58b9`) completes all 600 fields in strict native mode. Its complete guest hash log and final SRAM match the interpreter reference byte for byte. The minigame completion, episode exit and package inclusion remain open.

### Interactive minigame and return

From the same entry checkpoint, `--auto 3:300` adds controller input. The first candidate stops after 301 complete fields at `00205EE6`. The 6,000-field interpreter replay returns to the adventure by the sampled field 5500. Its newly discovered 622 variants all match complete instruction spans of the pinned MINIMAIG file, including the missing PC. Canonical discovery now produces 680,449 variants from the 678,135-variant seed.

The combined patch 0244 candidate (SHA-256 prefix `f8e41c28`) completes the identical 6,000-field sequence in strict native mode with zero interpreted blocks. All guest field hashes and final SRAM match the interpreter. The serialized terminal states have the same length and differ at four bytes, offsets `0x4059E1–0x4059E4`. Those four bytes belong to the serialized SCSP DSP host pointer `m_WRAM` (eight-byte field starting at `0x4059DF`, confirmed by the compiler record layout). The loader restores the current process pointer after reading the serialized DSP. The rest of each state is byte-identical. Both states then completed another 1,800 strict fields under the same controller input (`--auto 4:0`), with identical guest hashes and final SRAM. The subsequent states also differ only within the host pointer. This proves one interactive minigame route and return. The complete episode and package inclusion remain open.

### Verified BG1047 draw

English disc 1 FAD 140100, saved continuation field 1499. The patch 0244 candidate `f8e41c28` replayed 56 strict fields in Direct3D 11 at 2560 × 1440. Both runs had identical guest hashes and final SRAM. The only PC asset added was the exact `SAKURA1/BG/BG1047.SPR`, which the runtime reported usable. Four samples (8, 16, 30, 50) each change 1,336,862 pixels inside the Zoom scene rectangle (272, 29) to (2288, 1037). The native foreground, dialogue, and outer framing are preserved. The captures and trace are under `local/work/codex-th6-current/bg1047-1440-art`. Release inclusion remains open.

### Verified BG1003 draw

English disc 1 reads BG1003 at FAD 139088 in the second continuation. The field 899 checkpoint precedes the fade to Ogami's map. The patch 0244 candidate `f8e41c28` replays 56 strict fields at 2560 × 1440 in Direct3D 11 with identical guest hashes and final SRAM. Adding only `SAKURA1/BG/BG1003.SPR` changes 2,030,954 pixels in each of four samples, all within the approved scene rectangle. The runtime reports that exact donor usable. A later checkpoint at field 999 covers the fade and map, with seven samples identical across donor and missing-donor runs. Captures and traces are under `local/work/codex-th6-current/bg1003-1440-early` and `bg1003-1440-long`. Package verification remains open.

### Verified NC40 body draw

The same English disc 1 field 1499 checkpoint shows NC40 over BG1047. At 2560 × 1440 in Direct3D 11 on the patch 0244 candidate `f8e41c28`, the A/B loads only `SAKURA1/NC/NC40.SPR` in the donor arm. Both arms replay 56 strict fields with identical guest hashes and final SRAM. Four sampled fields each change 687,423 pixels inside the body rectangle from (874, 29) to (1924, 1037). The background, framing and dialogue pixels remain exact outside that rectangle. This is a large body draw witness for this occurrence. The runtime retained native mouth strips in the observed group, so the witness does not certify complete face animation. Captures and logs are in `local/work/codex-th6-current/nc40-1440`.

### NC40 mouth frames on the episode 6 route

Patch 0245 adds the 24 × 16 native strips at file offsets 40336 and 41488, paired to PC atlas ordinals 42 and 45. Both exact identities appear in the runtime face trace. In the 56-field checkpoint replay, 17 of the 53 sampled fields change only within (1168, 421) to (1336, 533). The other 36 samples are exact. The changed pixels show ordinal 45. A separate 300-field strict A/B from the same checkpoint confirms ordinal 42 at fields 60, 100 and 290. All 682 independently projected flat opaque texels from that PC part match in each sample. The complete guest hashes and final SRAM match. At 24 sampled fields the RGB differences stay within the mouth and chin rectangle (1168, 421) to (1336, 535). This witness is under `local/work/codex-th6-current/nc40-mouth-extended-*`. The Original profiles with and without donor match, as do the Enhanced missing and truncated donor profiles. Final SRAM and all 56 strict guest hashes match across profiles. Both registered mouth draws are visually verified. Evidence is in `local/work/codex-th6-current/nc40-mouth-full-*` and `nc40-faces-candidate/captures-vfs`. Other expressions and package inclusion remain open.

### Verified BG1064 upstairs draw

From the post-minigame state the 4,500-field confirm route reaches the lobby and reads BG1008. A directional move and confirm opens the second floor. The 1,200-field strict continuation reads `BG1064.BIN` at FAD 140491 and `NC95.BIN` at FAD 165781. Both segments report zero interpreted blocks.

From the upstairs continuation field 599, the 680,541-variant candidate `2c129cae` replays 56 strict fields with matching guest hashes and SRAM in both arms. At 2560 × 1440 the exact `BG1064.SPR` donor changes 1,331,893 pixels in each of four samples, confined to (272,29)–(2288,1037). The test isolates the background donor and preserves the native actor and dialogue. Evidence is under `local/work/codex-th6-current/bg1064-upstairs-1440`. Package verification remains open.

### Verified NC95 upstairs body

A second 56-field strict A/B from the same upstairs checkpoint adds only the PC `SAKURA1/NC/NC95.SPR`. The candidate reports nine PC parts. Four 2560 × 1440 samples each change 673,461 pixels within the bounds (853,29)–(1840,1037). The donor and missing-donor arms have identical guest hashes and final SRAM. The witness records this episode 6 body draw and preserves the separate episode 1 occurrence. A longer 300-field strict A/B verifies the two displayed face parts using the existing runtime mapping. At all 15 samples, complete independent projections match 4,093 flat opaque texels of PC ordinal 1 (eyes) and 1,408 of ordinal 4 (mouth) at body-relative coordinates (32,73) and (96,121). All these texels differ from the missing-donor control. Guest hashes and final SRAM match. This window displays the same expressions in every sample. Other expressions and package inclusion remain open. Private evidence is under `local/work/codex-th6-current/nc95-upstairs-1440` and `nc95-upstairs-faces`.

### West staircase and file 0602

From the lobby, the west staircase opens a conversation with Sakura. The 2,100-field strict continuation reads BG1119 at FAD 141733 and NC11 at FAD 161723. From field 699, two independent 56-field A/B pairs at 2560 × 1440 add BG1119 or NC11 alone. For BG1119 all four samples change 1,318,524 pixels within the scene. For NC11 they change 753,192–765,736 pixels inside the body bounds (902,29)–(2054,1037). Guest hashes and final SRAM match in both pairs. The two resources already had verified witnesses in other episodes.

The next 2,400-field strict continuation reaches file 0602. At the first script load it reads its dialogue and portrait tables, BG1076 (FAD 140767) and BG4351 (155651). It then reads NC40 (164276), NC26 (162222), NC42 (164421) and NC24 (162187). These are disc-read observations. The new 0602 assets still need individual RGB verification. Checkpoints and captures stay under `local/work/codex-th6-current/west-second-floor*` and the two `*-west-floor-1440` directories.

### Verified NC26 body in 0602

From continuation field 1199, an isolated PC `NC26.SPR` A/B at 2560 × 1440 matches all 56 strict guest hashes and final SRAM. Field 8 is identical during the blend. At fields 16, 30 and 50, the donor changes 701,770–701,773 pixels inside the body rectangle (671,29)–(1695,1037). The renderer reports nine PC face parts resident. This proves the body draw in this route; individual expressions and package inclusion remain open. BG4351, NC24 and NC42 are attributed only by the disc trace. BG4351 keeps the existing native cut-out policy. Captures are under `local/work/codex-th6-current/NC26-0602-early`.

### Verified NC24 and NC42 in 0602

Two isolated PC-donor A/B pairs continue from field 1199 with the original confirm cadence. Each pair completes 1,200 strict fields with identical guest hashes and final SRAM. At 2560 × 1440 the NC42 donor changes 956,281–956,282 pixels in seven samples (fields 180–360), within (496,29)–(2274,1037). NC24 changes 815,202–815,204 pixels in 16 samples within (496,29)–(1784,1037). The remaining samples of each pair match. The separate disc 2 NC24 witness remains in the ledger. This verifies the two body draws in 0602. Individual facial expressions and packaging remain open.

### Kohran and the later 0602 dialogue

The next 2,400-field strict continuation reads NC60 at FAD 165138. From its field 599 checkpoint, an isolated `NC60.SPR` A/B passes 56 strict fields with identical guest hashes and SRAM. Four 2560 × 1440 samples change 593,300–621,521 pixels within the body bounds (1000,29)–(1996,1037). NC60 already has a separate verified body witness.

A subsequent 3,500-field strict exploration (`--auto 6:0`) reads NC50 at FAD 164735, NC60 at 165138, NC10 at 161671 and NC30 at 162269. It completes without interpreted blocks and does not reach the next file or combat. These later reads establish file residency. Captures and checkpoints stay under `local/work/codex-th6-current/NC60-0602-early`, `file0602-deeper` and `file0602-next`.

## Re-attribution with the EVT overlay build

Shard TH-reattribution repeated the traced attribution with the isolated AOT build of [the EVT overlay registry](evt-overlay-registry.md) (1,357,536 blocks, which unblocks `00204000`; exe SHA-256 `2818e414...`, copied to `local/build/sakura-reattr/`). Each chapter-jump case (`backup.bin` plus the archived `input.movie`, extended with a confirm press every 75 frames) ran cold, strict native, headless, 45,000 frames, with `tools/chapter_loads.py --exe <exe> --disc 1 --backup <backup.bin> --movie <extended.movie> --frames 45000 --interval 500 --out local/work/reattr/run-<case>`. States and movies stay in `local/work`.

| Case | Exit | Frames | Interpreted 0 | Backup | Movie | Hash log |
| --- | ---: | ---: | --- | --- | --- | --- |
| `bank-6-battle` | 0 | 45000 | yes | `6633cfb0` | `5bfe6029` | `e283cbd2` |

The route reproduces the TH6 list (TITLE6, BG1199, BG4119, BG2156, BG1021, BG1025, BG4059, NC97), all already attributed. No row moved.

Association is `observed`: a disc read shows the game asked for the file, not that it drew. Not verified in game: any draw of the moved rows.

### Strict Perfect result and return

A continuous 6,150-field replay starts at the natural MINIMAIG entry
state (SHA-256 prefix a6cdcb5e5baf15d6). It solves all nine names, earns
the Perfect result at 49.50 seconds, and returns to the adventure. Its
input SHA-256 is
`35d7aeae2c9ab09aa3af70c57eb96eaa9090925b0315375c6ee6610b5d0447b8`.

Recording this replay in the interpreter identifies 65 new instruction
extents. Every extent matches complete bytes of the pinned MINIMAIG.BIN
module, including an entry at 0x0021C682. An isolated strict link with
these extents completes all 6,150 fields with zero interpreted blocks,
identical guest hashes, and byte-identical final SRAM. The shared guest
hash log SHA-256 is
`7967dde4cfefd8501cd4b801bfba1fefb3f4b30d5e47f68b078aea2c4a34d108`.
The regenerated registry includes the new extents. Public packaging
remains open.

The Perfect route has no MINIMAIG.GCG read. In the pinned module, the
exit dispatch that reaches the GCG loader depends on a mode byte copied
from guest high WRAM 0x06003013. The naturally earned episode route
keeps that mode at zero. A separate natural mode that sets it remains
to be found before the Maigo illustration can be witnessed.

The Long Day launch, winning route, Rankings, and return add 138
observed instruction spans to the same MINIMAIG registry. The
isolated strict candidate completes 1,250 menu-entry fields,
5,400 winning fields, 450 Rankings fields and 660 return fields
from their natural checkpoints. The entry and win logs match
the interpreter and each test preserves final SRAM. The donor
and control match through Rankings and return. The [HD reward
witness](saturn-bg-format.md#maigo-reward-in-long-day) records
the rendering comparison.
