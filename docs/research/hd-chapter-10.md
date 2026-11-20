# HD chapter 10 (Finale) coverage report (shard TH10)

The [Chapter 10 native evidence](th10-native-attribution.md) adds observed scene pictures and one resident portrait atlas to the chapter register. It records display, residency, and disc reads separately. The complete replay and HD exit test are open.

## Earlier catalog snapshot

Source data only: `config/hd-chapter-coverage.json` (entry `chapters[9]`, `unassigned`, `association`), cross-checked with `config/hd-scene-bg-map.json`, `config/hd-scene-bg-review.json`, `config/hd-body-map.json`, `config/hd-item-map.json`, `config/film-fad-map.json`, `docs/research/chapter-sweep.md` and `docs/PENDIENTES.md`. This is an offline data report. It certifies no replay and no chapter completion. Names, hashes and counts only.

## 1. Scope

Chapter 10 is on disc 2. The sweep saw it once: "Finale, File 1, CD-2", 12,000 frames, zero interpreted blocks, initial dialogue only (folder `bank-10-battle-1-strict`). "Finale, File 3" maps to portrait family `1004`. The chapter file uses the bank member name, not an observed scene list.

| Class | Count attributed to chapter 10 | Association |
| --- | --- | --- |
| Scene pictures (BG/EVE/CG/TITLE) | 1 | inferred (episode title number) |
| NC bodies | 0 | no data |
| Portraits | 4 | inferred (atlas membership) |
| FILM clips | 0 | no data |
| Tactical maps / units | 0 / 0 | no data |
| Menus/HUD | 0 | no data |

Nothing for chapter 10 is `observed` or `resident`. The 5 attributed items are candidates from numbering, not appearances.

## 2. Status per class

Chapter-10 attributed items (5 total):

| Class | hd | paired-not-wired | unpaired | unknown | Examples |
| --- | --- | --- | --- | --- | --- |
| Scene pictures | 0 | 0 | 0 | 1 | `TITLE10.BIN` |
| NC bodies | 0 | 0 | 0 | 0 | none |
| Portraits | 0 | 0 | 0 | 4 | `1001FCE.BIN`, `1002FCE.BIN`, `1003FCE.BIN`, `1004FCE.BIN` |
| FILM clips | 0 | 0 | 0 | 0 | none |
| Tactical | 0 | 0 | 0 | 0 | none |
| Menus/HUD | 0 | 0 | 0 | 0 | none |

Note: the same 5 names also appear under `unassigned` for disc 1 (`1:/SAKURA1/...`) with association `unknown` / status `unknown`. The chapter-10 copies are the disc-2 entries (`2:/SAKURA1/...`).

Context, whole disc 2 unassigned pool (items with no chapter; any may belong to chapter 10; status mix not split by disc in the data): scene pictures 774, portraits 39, FILM 22, bodies 147 entries on disc 2. For scale, whole-game unassigned status mix: scene pictures hd 917 / paired-not-wired 474 / unpaired 104 / unknown 42; bodies hd 11 / paired-not-wired 246 / unpaired 30 / unknown 6; portraits hd 181 / unknown 56; FILM hd 44 / paired-not-wired 7 / unpaired 2; menus-hud unpaired 84 / paired-not-wired 76 / unknown 35; tactical maps and units 27 each, all unknown. These are not chapter-10 counts.

Catalog totals (config summaries): `hd-scene-bg-map` content 519, number 216, missing 5; `hd-body-map` content 104, candidate 40; `hd-item-map` content 12, candidate 68. `film-fad-map`: 2 unpaired PC, 0 unpaired Saturn streams. Per-chapter counts from these catalogs: no data.

## 3. Five highest-value next actions

Ordered by number of items closed. Chapter-10 items are few because attribution is the gap, so action 1 dominates.

1. Attribute disc-2 resources to chapter 10 from a traced run. Closes potentially hundreds of the 774 + 147 + 39 + 22 disc-2 unassigned entries, only by observation. Touch: the strict-native replay of `bank-10-battle-1-strict` and further saves of chapter 10 (files 2-3 etc.), the scene index (`tools/build_scene_index.py`, see `docs/research/scene-tagging.md`), and the `CHAPTER_WITNESSES` table in `tools/hd_chapter_coverage.py` (exact-file witnesses with a documented report). Then regenerate `config/hd-chapter-coverage.json`.
2. Resolve `1001FCE`-`1004FCE` (4 items). They are `unknown`, though `hd-chapter-coverage` shows 181 portraits `hd` elsewhere. Touch: `docs/research/portrait-animation-coverage.md` audit (`tools/audit_portrait_coverage.py`) and the portrait recipe. Run the audit for these four and record why each is hd or native.
3. The [Episode 10 donor decision](episode-title-pc-pairings.md#pair-metadata) now covers `TITLE10.BIN` on both discs. The approved cards use the localized center and wide surround. The PC alternative has Japanese text baked into the image.
4. Chapter-10 FILM mapping (0 attributed; scope item c). Touch: `config/film-fad-map.json` (22 disc-2 FILM entries unassigned) plus chapter attribution of those FADs; record a decision for each alternate cut (`alternate_cut` field).
5. List chapter-10 tactical maps/units for S11 (0 attributed; 27 maps and 27 units are unknown everywhere). Touch: `tools/hd_chapter_coverage.py` category tables (`MAP\d+`, `UNIT\d+`) and S11 (row TS11 in `docs/PENDIENTES.md`).

## 4. Cannot be known without playing (needs the owner's discs)

- Which BG/EVE/CG pictures the Finale actually draws and in which order; whether `TITLE10` is the episode title shown.
- Which NC bodies and portraits the three Finale files use; whether each portrait appears as a native face.
- Which FILM clips play in the Finale and whether any alternate cut plays.
- Which tactical maps and units the Finale battles use, and their layout.
- Menus/HUD drawn during the chapter.
- Per-frame guest hash identity between HD and non-HD runs along the full chapter path (the exit test in `docs/SHARDS.md`); only the initial dialogue (12,000 frames) is recorded.
- Screenshots the owner can open: no data (none recorded for chapter 10).

## 5. Open questions

- Are Finale Files 2 and 3 played on disc 2 only, and is File 1's 12,000-frame run enough to witness anything beyond the dialogue? The sweep records only File 1 and File 3's portrait family.
- Does `1002FCE` / `1003FCE` belong to File 2? The sweep table lists only `1001` and `1004`; the others are atlas inferences.
- Why do the same 5 names exist both as disc-2 chapter-10 entries and disc-1 `unassigned` entries? Possibly the shared `/SAKURA1` content on both discs; unconfirmed.
- Is the empty bodies/film/menus-hud/tactical result a data gap or a real absence? The chapter-coverage doc says empty lists flag gaps in evidence.
- Does the bg-map contain `TITLE10` at all (519 content + 216 number + 5 missing pairs)? Not confirmed in this pass.


## Re-attribution with the EVT overlay build

Shard TH-reattribution repeated the traced attribution with the isolated AOT build of [the EVT overlay registry](evt-overlay-registry.md) (1,357,536 blocks, which unblocks `00204000`; exe SHA-256 `2818e414...`, copied to `local/build/sakura-reattr/`). Each chapter-jump case (`backup.bin` plus the archived `input.movie`, extended with a confirm press every 75 frames) ran cold, strict native, headless, 45,000 frames, with `tools/chapter_loads.py --exe <exe> --disc 2 --backup <backup.bin> --movie <extended.movie> --frames 45000 --interval 500 --out local/work/reattr/run-<case>`. States and movies stay in `local/work`.

| Case | Exit | Frames | Interpreted 0 | Backup | Movie | Hash log |
| --- | ---: | ---: | --- | --- | --- | --- |
| `bank-10-battle-1` | 0 | 45000 | yes | `5f288f8b` | `5bfe6029` | `9e7f1f5e` |
| `bank-10-battle-2` | 0 | 45000 | yes | `c5b90e8b` | `5bfe6029` | `04a2e43b` |
| `bank-10-final-battle` | 0 | 45000 | yes | `c7c2fde7` | `5bfe6029` | `ecdc1bb4` |
| `public-finale` | 4 | 41684 | no | `efe16833` | `e0cdea12` | `9e3ddbe5` |

Chapter 10 (disc 2) routes `1001` (`bank-10-battle-1`), tactical stage 19 (`bank-10-battle-2` and `bank-10-final-battle`, identical reads) and the ending (`public-finale`, `1004`, ends reading `ENDING.BIN`). Thirty-one `unassigned` rows are now chapter 10: BG1284, BG1292, BG1293, BG2020, BG2023, BG2025, BG2026, BG2046, BG2057, BG2111, BG2163-BG2168, BG2248, BG2284-BG2286, BG3020, BG3026, BG3046, BG3163-BG3165, NC3023, NC3025, BBG218, UNIT19, WKL19. `LIPS_CG` and `LOAD.BIN` stay `unassigned`.

Exit 4 on `public-finale`: the strict AOT stops at 41,684 frames with `untranslated master SH-2 block at 06080000` (an ending-side overlay at a different address, not `00204000`). The loads recorded before it (up to `ENDING.BIN`) are valid; the remaining ending frames need that overlay translated by the overlay-registry owner.

Association is `observed`: a disc read shows the game asked for the file, not that it drew. Not verified in game: any draw of the moved rows.
