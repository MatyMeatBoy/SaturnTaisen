# HD chapter 9 coverage (shard TH9)

Source: `config/hd-chapter-coverage.json` (chapter 9 entry, `unassigned`, `association`), cross-checked against `docs/research/chapter-sweep.md`, `config/hd-scene-bg-map.json`, `config/hd-scene-bg-review.json`, `config/hd-body-map.json`, `config/hd-item-map.json`, `config/film-fad-map.json` and `docs/PENDIENTES.md` (row TH9, status open). Names, hashes and counts only. This is a data report; it is not a replay, and it does not certify the chapter.

## 1. Initial catalog snapshot

Chapter 9 is on disc 2 (chapter-sweep row: CD-2, episode id `0900`). The coverage JSON attributes only these resources to it:

| Class | Count | Resources |
|---|---|---|
| Scene pictures | 1 | `2:/SAKURA1/TITLE9.BIN` (association: inferred, from episode numbering) |
| NC bodies | 0 | none attributed |
| Portraits | 6 | `0900FCE` (resident in RAM, evidence chapter-sweep), `0901FCE` to `0905FCE` (inferred) |
| FILM clips | 0 | none attributed |
| Tactical maps / units | 0 / 0 | none attributed |
| Menus/HUD | 0 | none attributed |

The empty lists are a gap in chapter evidence, not proof the chapter shows nothing. Chapters 7, 8 and 10 are equally thin (1 scene picture, 3 to 7 portraits); only chapter 1 has real attribution (4 pictures, 1 body, 1 film, 129 portraits, 1 tactical map).

Context pool (not attributed to any chapter): `unassigned` holds 1537 scene pictures, 293 bodies, 237 portraits, 53 FILM streams, 195 menus/HUD, 27 tactical maps, 27 tactical units. Chapter 9 must draw from it.

Association levels: observed (seen in runtime evidence), resident (in RAM, not shown drawn), inferred (numbering/atlas candidate), unknown. The initial snapshot had no `observed` chapter-9 entry. Later evidence is below.

## 2. Status per class

| Class | hd | paired-not-wired | unpaired | unknown | Example IDs |
|---|---|---|---|---|---|
| Scene pictures (attributed) | 0 | 0 | 0 | 1 | `TITLE9` |
| NC bodies (attributed) | 0 | 0 | 0 | 0 | no data |
| Portraits (attributed) | 0 | 0 | 0 | 6 | `0900FCE`, `0901FCE`, `0902FCE`, `0903FCE`, `0904FCE`, `0905FCE` |
| FILM (attributed) | 0 | 0 | 0 | 0 | no data |
| Tactical (attributed) | 0 | 0 | 0 | 0 | no data |
| Menus/HUD (attributed) | 0 | 0 | 0 | 0 | no data |

Pool reference (all chapters, unattributed), to show what chapter 9 could inherit:

| Class | hd | paired-not-wired | unpaired | unknown |
|---|---|---|---|---|
| Scene pictures | 917 | 474 | 104 | 42 |
| Bodies | 11 | 246 | 30 | 6 |
| Portraits | 181 | 0 | 0 | 56 |
| FILM | 44 | 7 | 2 | 0 |
| Menus/HUD | 0 | 76 | 84 | 35 |
| Tactical maps | 0 | 0 | 0 | 27 |
| Tactical units | 0 | 0 | 0 | 27 |

Pool examples: bodies hd `NC11`, paired-not-wired `NC10`, `NC12` to `NC16`, `NC21` to `NC26`; scene pictures `AI_CG`, `BG0000`, `BG1001` to `BG1004`; menus/HUD `ITEM01` to `ITEM06`; maps `MAP01` to `MAP06`; units `UNIT01` to `UNIT06`.

Catalog totals (for sizing): scene-bg map 519 content + 216 number pairs, 5 missing; body map 104 content + 40 candidate; item map 12 content + 68 candidate. These are not per chapter; no chapter field exists in them. In the unassigned pool the `TITLE8`, `TITLE9`, `TITLE10` entries are listed from disc 1 and `TITLE1` to `TITLE7` from disc 2, all `unknown`; the portraits `0801FCE` to `0807FCE` and `0900FCE` onward also appear there with disc 1 prefixes, status `unknown`. The portrait pool's 56 `unknown` entries have no per-ID chapter data.

## 3. Five highest-value next actions

1. **Attribute chapter 9 scene pictures** (closes the most: the 1537-item pool has 0 chapter 9 BG/EVE/CG entries). Run a cold-start chapter 9 sweep on disc 2 with the scene index, then rebuild: `tools/hd_chapter_coverage.py --index <scene-index> --portrait-audit <audit>` and update `CHAPTER_WITNESSES` in that tool (file+chapter+report) for each observed picture. Needs the owner's disc 2.
2. **Promote the 6 portraits `0900FCE` to `0905FCE`** from unknown to a real status: look them up in the portrait audit (`docs/research/portrait-animation-coverage.md`, `local/work/portrait-coverage-worker/portrait-coverage.json`), and record observed/resident evidence in `docs/research/chapter-sweep.md`. Closes 6.
3. **Find chapter 9 NC bodies**: capture which `NCxx` loads in chapter 9, then mark them in `config/hd-body-map.json` and `BODY_DRAWS` in `tools/hd_chapter_coverage.py`. 246 bodies are paired-not-wired, so wiring (T106a-d method) closes the largest block; the number in chapter 9 is no data.
4. **Map chapter 9 FILM clips**: check `config/film-fad-map.json` (`streams`, `unpaired_saturn`) for disc 2 streams hit in chapter 9; 7 are paired-not-wired and 2 unpaired in the whole pool, each alternate cut needs a decision. Tool: `tools/hd_chapter_coverage.py` plus the map.
5. **Tactical list for S11 and menus/HUD**: record whether chapter 9 has a stage (`MAP`/`UNIT` ids, 27 each, all `unknown`) and list HUD/ITEM resources (`config/hd-item-map.json`, 68 candidates vs 12 content). Feeds TS11. Closes up to the stage's map+units; count no data.

## 4. Cannot be known without playing (owner's discs)

- Which scene pictures (BG/EVE/CG) chapter 9 displays, and in what order.
- Which NC bodies and which portrait frames are drawn; whether a face falls back to native.
- Which FILM streams play and whether an alternate cut is reached.
- Whether chapter 9 contains a tactical stage, and which map/units.
- Menus/HUD used in the chapter.
- The per-frame guest-hash identity of the HD runtime against the build without HD over the chapter path (exit test of TH1-TH10).
- Whether the 0900 resident match in RAM means it was drawn.

## 5. Open questions

- Does `TITLE9` belong to chapter 9 (inferred only) and does disc 1 vs disc 2 copy matter (pool has `1:/SAKURA1/TITLE9.BIN`, chapter has `2:`)?
- Are `0901FCE` to `0905FCE` actually used in chapter 9, or only atlas members?
- Can the portrait `unknown` rate (56 of 237 in the pool) be reduced by data already in `local/`?
- Is the chapter 9 path in `docs/research/chapter-sweep.md` a Continue-screen entry only, or does it have a replayable input script for the strict-native hash check?
- No chapter field exists in `config/hd-scene-bg-map.json`, `hd-body-map.json` or `hd-item-map.json`; should chapter attribution live only in `config/hd-chapter-coverage.json`?



## Native route observations

The English disc-2 public Chapter 9 slot provides the cold
`0900` route and the BG2238 dream checkpoint. After the dream, the
route visits Ayame's Room and reaches the underground storage
briefing. The transition reads all five sectors of `0901.BIN` at
FAD 109322. The following 7,200-frame relay remains in the
briefing. Its trace has no `0902` read. The archived cold,
3,600-frame transition and 7,200-frame briefing runs report
zero interpreted blocks.

The native 288×144 window at (16,8) matches the following
stock images after RGB555 expansion. The named files also
appear as picture operands in the reached 0900 or 0901 scripts.

| Scene capture | Picture | Native RGB matches |
| --- | --- | ---: |
| Before the `0901` transition, frame 1200 | BG1072 | 29,284/41,472 |
| Salon route, frame 4800 | BG1076 | 41,472/41,472 |
| Storage approach, frame 3600 | BG1176 | 41,472/41,472 |
| Storage briefing relay, frame 5400 | BG2098 | 41,472/41,472 |
| Post-dream relay, frame 240 | BG2100 | 41,472/41,472 |

The public-slot cold replay at frame 12000 has the exact
active NC3018 240×144 body command, texture FNV-1a
`7D9E3EEA1B69ABC7`. All 18,885 opaque pixels match the native
capture at (64,8). The storage terminal state has NC81
208×144, texture FNV-1a `CAEE5C58F639F871`. All 11,561
opaque pixels match that capture at (64,8).

| Portrait | Base FNV-1a | Observation |
| --- | --- | --- |
| 0001 | `74801C684C1AF22E` | Exact VDP1 command and all 1,920 RGB pixels in the Salon route. |
| 00e9 | `391F36B3243EFF54` | Exact VDP1 command and all 1,920 RGB pixels at the end of storage. |
| 00fa | `5E689D81D45781D9` | Exact active base in the dream relay state. |
| 00fb | `EDD256F4A12B8B76` | Exact active base in the dream relay state. |
| 0104 | `DA1433DE513C8A53` | Exact VDP1 command and all 1,920 RGB pixels at cold frame 12000. |

Those command payloads belong to the exact resident `0900FCE`
or `0901FCE` atlases, respectively. The complete 147,360-byte
`0901FCE.BIN` matches the storage checkpoint in WRAM, SHA-256
`bad07425e09a84a31c5b578fda68f9b685d2380328f3a0e5991faa33647bb522`.
The catalog keeps that atlas resident. The displayed member
00e9 has its own observation.

BG2017 and BG2018 have identical Saturn file bytes on this
disc. Their indistinguishable visible region provides no
file-specific attribution here. The two already attributed
Chapter 1 portrait occurrences and the separate BG2238 HD
draw remain intact. This is native attribution. It does not
add new HD draws, certify later routes or change a package. The later [NC81 underlay replay](nc81-nc90-1440p.md) verifies the HD body with the native face in the storage checkpoint. The [registered NC3018 face replay](nc3018-registered-faces.md) verifies the corrected face placement in the cold checkpoint.

At block close the project measured 61,293,478,622 logical bytes
with hard links counted once and reparse points excluded, above
the 20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.

## Verified Chapter 9 scene draws

Four English disc 2 scenes in the archived Chapter 9 continuation have
isolated-donor Enhanced witnesses at 2560 × 1440. The runtime includes
patch 0213. The variant with the selected PC image and the stock variant
share the same route checkpoint, settings and background pack. Only the
named donor differs.

| Saturn picture | Archived checkpoint | Changed RGB pixels per sampled field |
| --- | --- | ---: |
| BG1076 | Post-dream route terminal before the salon relay | 2,031,368 |
| BG1176 | Storage briefing continuation | 1,280,324–1,280,618 |
| BG2098 | Natural 0902 module relay terminal | 1,868,127 |
| BG2100 | Reveal relay field 239 | 1,673,860 |

The reveal checkpoint was regenerated from the public Chapter 9 slot's
archived relay, with all 240 guest hashes matching the saved history.
All four 56-field strict comparisons match their stock guest hashes and
final SRAM, with zero interpreted blocks. The four sampled fields per
scene are 8, 16, 30 and 50.

Each changed output pixel lies in the picture viewport
(272,29)–(2288,1037), belongs to the independently decoded stock Saturn
plate, and agrees with the independently decoded bilinearly scaled PC
art within two RGB levels. The rest of the frame retains stock RGB.
BG1076's disc 1 witness remains in the registry; its donor is counted once.

Local receipts and replay outputs remain under
`local/work/codex-witness-441-review/hud/chapter9-plates/`.
This verification covers these four appearances.

## Verified lower scene plates on the natural 0904 route

The English disc 2 Iris route provides archived snapshots of eight
distinct lower scene pictures. Strict Enhanced pairs at 2560 × 1440
used the runtime through patch 0213 and differed only in the named
physical PC image. The existing native foregrounds were present in
both arms.

| Saturn picture | Natural checkpoint | Changed RGB pixels per positive capture |
| --- | --- | ---: |
| BG1061 | Iris entrance | 1,880,192 |
| BG1066 | Quiet map junction | 2,031,745 |
| BG1075 | Library continuation terminal | 2,029,456 |
| BG1077 | Iris room route at field 540 | 1,328,177 |
| BG1100 | Iris door knock | 2,032,127 |
| BG1101 | Iris room at field 180 | 2,032,126 |
| BG1325 | Hall relay at field 600 | 1,175,001 |
| BG2036 | Library entry at field 600 | 1,241,716 |

The 56-field arms match stock guest hashes and final SRAM for every
checkpoint, with zero interpreted blocks. Sampling fields 8, 16, 30 and
50 gives 35 positive RGB comparisons across nine replay sites. BG1075
matches stock at field 50 after the positive interval. Every changed
pixel lies within the (272,29)–(2288,1037) viewport, belongs to the exact
native lower plate, and matches the independent bilinear PC decode within
two RGB levels. All pixels outside the visible plate remain stock exact.

BG2036, BG2037 and BG2038 have identical Saturn file bytes on disc 2 and
the same registered PC BG2036 donor. The library entry's first 600 guest
hashes reproduced the archived replay and the CD trace read BG2036 at
FAD 123662 before the snapshot. A later library continuation scene with
the same native bytes independently changed 1,322,804 pixels per capture
with the canonical donor. The registry counts the one physical donor once.

Local receipts and repro commands are under
`local/work/codex-witness-441-review/hud/iris-background-plates/`.
This work verifies the named appearances without an SDK or package change.


## Re-attribution with the EVT overlay build

Shard TH-reattribution repeated the traced attribution with the isolated AOT build of [the EVT overlay registry](evt-overlay-registry.md) (1,357,536 blocks, which unblocks `00204000`; exe SHA-256 `2818e414...`, copied to `local/build/sakura-reattr/`). Each chapter-jump case (`backup.bin` plus the archived `input.movie`, extended with a confirm press every 75 frames) ran cold, strict native, headless, 45,000 frames, with `tools/chapter_loads.py --exe <exe> --disc 2 --backup <backup.bin> --movie <extended.movie> --frames 45000 --interval 500 --out local/work/reattr/run-<case>`. States and movies stay in `local/work`.

| Case | Exit | Frames | Interpreted 0 | Backup | Movie | Hash log |
| --- | ---: | ---: | --- | --- | --- | --- |
| `bank-9-battle-1` | 0 | 45000 | yes | `40277a3d` | `5bfe6029` | `26f69583` |
| `bank-9-battle-2` | 0 | 45000 | yes | `2d348634` | `5bfe6029` | `616e0bdf` |
| `public-9` | 0 | 45000 | yes | `1b3457dc` | `76bd1a24` | `01fd0005` |

Chapter 9 (disc 2) routes `0900` (`bank-9-battle-1` and `public-9`, identical reads) and `0904` (`bank-9-battle-2`). Twenty-one `unassigned` rows are now chapter 9: BG1143, BG2017, BG2021, BG2031, BG2091, BG2092, BG2156, BG2160, BG2236, BG3091, NC12, NC20, NC21, NC3017, NC3021, NC3031, NC32, NC34, NC41, NC50, NC51. `LOAD.BIN` stays `unassigned`.

Association is `observed`: a disc read shows the game asked for the file, not that it drew. Not verified in game: any draw of the moved rows.

## BG2021 on the earned Iris route

After Shika, the natural Iris route reads the Saturn BG2021 from FAD 123317. The state saved at field 480 of the post-film segment runs for 32 strict fields from the same initial SRAM in two 1440p profiles. The donor-only profile loads BG2021.SPR. The matched control reports the texture missing and uses the same floral backdrop. The 32 guest hashes and final SRAM match. The 546,597 changed pixels lie within the scene rectangle (272,29) to (2288,1037), leaving the dialogue and floral border identical. The tested executable is from v0.2.16.1-alpha. Private receipts: `local/work/codex-th1/thd01-probe/bg2021-ep9-proof`.

## Iris warehouse backgrounds

The natural 0903 route after Shika reads BG2101 and BG2102 at FAD 125124 and 125147. From the revelation segment at field 2160 and its terminal state, separate donor-only Enhanced 1440p runs draw BG2101 and BG2102. The corresponding controls keep the same floral backdrop with the individual donor absent. Each 32-field strict pair has identical guest hashes and SRAM. BG2101 changes 1,003,073 pixels within (272,29) to (2288,1032). BG2102 changes 360,855 within (309,29) to (2288,944). The dialogue and outer border compare exactly. The receipts are in `local/work/codex-th1/thd01-probe/iris-BG2101-f2160` and `iris-BG2102-terminal`. BG2103 shares a donor mapping and requires separate native attribution.

## Iris 0903 street and warehouse alias

The natural 0903 resume reads BG1180 at FAD 119484 and BG1174 at FAD 119346. The states at fields 1920 and 2400 respectively draw the corresponding PC donor at 1440p. The 0903 ending relay also reads BG2103 at FAD 125170. Its native disc bytes have the same SHA-256 as BG2102, and the field-1680 state has their exact resident cells and palette. The matched donor/profile comparison uses the existing BG2102 SPR for that second native file occurrence.

All three comparisons have matching 32-field strict guest hashes and SRAM, with RGB changes confined to the scene. BG1174 changes 1,357,463 pixels, BG1180 changes 2,032,121, and the BG2103 occurrence changes 323,079. The BG2103 occurrence uses an already counted physical donor. Private receipts are under `local/work/codex-th1/thd01-probe` in `iris-BG1174-f2400`, `iris-BG1180-f1920` and `iris-BG2103-f1680`.
