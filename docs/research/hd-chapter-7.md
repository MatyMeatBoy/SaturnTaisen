# HD chapter 7 coverage report (TH7)

The [Chapter 7 native evidence](th7-native-attribution.md) adds observed scene pictures and resident tactical files to the chapter register. It records display, residency, and disc reads separately. The complete replay and HD exit test are open.

## Earlier catalog snapshot

Source: `config/hd-chapter-coverage.json` (chapters[6], unassigned, association), cross-checked with `config/hd-scene-bg-map.json`, `hd-scene-bg-review.json`, `hd-body-map.json`, `hd-item-map.json`, `film-fad-map.json` and `docs/PENDIENTES.md`. Names, hashes and counts only. This is an offline data report; no replay was run, so nothing here certifies the chapter.

## 1. Scope (what the data attributes to chapter 7, disc 1)

| Class | Attributed to ch. 7 | Evidence |
| --- | --- | --- |
| Scene pictures | 1: `1:/SAKURA1/TITLE7.BIN` (inferred from title numbering) | no runtime trace |
| NC bodies | 0 | no data |
| Portraits | 3 atlases: `0700FCE.BIN` (resident in RAM), `0701FCE.BIN`, `0702FCE.BIN` (inferred) | `docs/research/chapter-sweep.md` row "7 / CD-1 / 0700" |
| FILM clips | 0 | no data |
| Tactical maps / units | 0 / 0 | no data |
| Menus / HUD | 0 | no data |

Chapter 7 is the thinnest chapter in the file apart from the ones that share the same pattern (chapters 2-10 each have 1-9 entries; only chapter 1 has bodies, film, a tactical map and 129 portraits). The only chapter-7 observation is the Continue-screen sweep (family `0700`, CD-1): the narrative script, dialogue table and portrait atlas of `0700` match in RAM. The sweep names no scene pictures, bodies, clips or tactical stages for chapter 7.

Chapters 6 and 7 are both on disc 1 (SHARDS.md), so disc-1 resources not placed in any chapter (below) can belong to chapter 7; the data does not say which.

## 2. Status per class

Chapter 7 own entries (all four non-portrait categories are empty):

| Class | hd | paired-not-wired | unpaired | unknown | Examples |
| --- | --- | --- | --- | --- | --- |
| Scene pictures | 0 | 0 | 0 | 1 | TITLE7 |
| NC bodies | 0 | 0 | 0 | 0 | none attributed |
| Portraits | 0 | 0 | 0 | 3 | 0700FCE, 0701FCE, 0702FCE |
| FILM | 0 | 0 | 0 | 0 | none attributed |
| Tactical | 0 | 0 | 0 | 0 | none attributed |
| Menus/HUD | 0 | 0 | 0 | 0 | none attributed |

Why the three portraits are `unknown`: the chapter file maps the portrait atlas to a status only through the portrait audit; the audit has no recipe entry for the `07xx` atlases in this data. Whether they are drawn or HD-replaced is no data.

Unassigned pool (global, not chapter 7 specific; the candidates for filling chapter 7):

| Class | Total | hd | paired-not-wired | unpaired | unknown | Examples |
| --- | --- | --- | --- | --- | --- | --- |
| Scene pictures | 1537 | 917 | 474 | 104 | 42 | hd: BG1001-BG1006; pnw: BG1011-BG1014; unpaired: BG0000, BG1130; unknown: BG2338, BG2518, AI_CG |
| NC bodies | 293 | 11 | 246 | 30 | 6 | hd: NC11, NC30, NC55, NC82, NC97; pnw: NC10, NC12-NC16; unpaired: NC3013, NC3047; unknown: NC3125, NC3126, NC4138 |
| Portraits | 237 | 181 | 0 | 0 | 56 | hd: 000c, 000e, 0011; unknown: 0801FCE-0806FCE |
| FILM | 53 | 44 | 7 | 2 | 0 | hd: SAKURA4+0, SAKURA4+113262592; pnw: SAKURA4+100188160, SAKURA4+59686912; unpaired: OPSAKURA.CPK+0 |
| Tactical maps | 27 | 0 | 0 | 0 | 27 | MAP01-MAP06 |
| Tactical units | 27 | 0 | 0 | 0 | 27 | UNIT01-UNIT06 |
| Menus/HUD | 195 | 0 | 76 | 84 | 35 | pnw: ITEM01, ITEM02, ITEM04; unpaired: ITEM03, ITEM09; unknown: LOAD, TMAP, WALL1 |

Notes: bodies and film counts include per-disc duplicate keys (e.g. NC11 appears twice). Scene-pictures hd/pnw come from `hd-scene-bg-map.json` (summary: content 519, number 216, missing 5; `hd-scene-bg-review.json` holds reviewed/rejected/cutout lists). Body map summary: content 104, candidate 40. Searching those catalogs for TITLE7, 0700, 0701 and 0702 finds no chapter-7 entry (the few text hits are SHA substrings, not names). The film map has no chapter field, so no clip can be tied to chapter 7 from `film-fad-map.json`.

## 3. Five highest-value next actions (by items closed)

1. Place disc-1 resources into chapter 7 with a strict-native trace of the `0700` route (hundreds of unassigned scene pictures, bodies and clips are candidates; closes the "no data" for all classes). Touch: `docs/research/chapter-sweep.md` route list and `CHAPTER_WITNESSES` in `tools/hd_chapter_coverage.py`, then regenerate `config/hd-chapter-coverage.json`.
2. Record the file-load witnesses (BG/EVE/CG/NC names loaded after `0700`) as `observed` association. Touch: same tool, `CHAPTER_WITNESSES` entries `(disc, path): (chapter, report)`. Closes every scene picture and body found.
3. Resolve the 3 portrait atlases (`0700FCE`, `0701FCE`, `0702FCE`): add them to the portrait audit and check which portrait IDs they contain. Touch: `docs/research/portrait-animation-coverage.md` and the audit input `local/work/portrait-coverage-worker/portrait-coverage.json`. Closes 3 `unknown`.
4. Decide TITLE7: find its PC counterpart or record a reason it has none. Touch: `config/hd-scene-bg-map.json` (pair) or `config/hd-scene-bg-review.json` (rejected/note). Closes 1.
5. Identify the chapter-7 FILM streams and tactical stages (disc-1 SAKURA4 offsets, MAP/UNIT numbers) once a trace exists. Touch: `config/film-fad-map.json` (no chapter field, so chapter attribution must go in the coverage tool) and the S11 list (row TS11). Closes the empty film/tactical lines.

Actions 1-2 dominate: items 3-5 close 5 at most unless action 1 first exposes more.

## 4. Cannot be known without playing (owner's discs)

- Which scene pictures, bodies, portraits, clips and tactical maps chapter 7 actually draws, and in what order.
- Whether `0701FCE` and `0702FCE` are used at all in chapter 7 (episode-number inference only).
- Whether `TITLE7` is the chapter 7 title and when it is shown.
- Per-frame guest-hash equality of the HD runtime vs the build without HD on the chapter 7 path (the TH7 exit test).
- Which alternate film cuts chapter 7 triggers and the A/V offset of each.
- Face layouts for bodies that stay native (the T106 family, NC30/NC20 only so far).

## 5. Open questions

- Does chapter 7 begin at family `0700` and end before `0801` (disc 2)? Only the sweep row "7 / CD-1 / 0700" exists; no end marker is in the data.
- Do `0701`/`0702` belong to chapter 7, or are they the sub-episodes of chapter 6/7 on the same disc? Inferred from numbering only.
- Is a chapter 7 tactical map required? Only stage 01 is documented as the extended map (chapter 1).
- Can the global film streams be bound to chapters by FAD range, or must each come from a replay? `film-fad-map.json` formula: FAD = 150 + LBA + byte_offset / 2048; no chapter data.
- Who owns the `CHAPTER_WITNESSES` edits in `tools/hd_chapter_coverage.py` while TH0 is marked implemented? Check `docs/PENDIENTES.md` rows TH0 and TH7 before editing.


## Re-attribution with the EVT overlay build

Shard TH-reattribution repeated the traced attribution with the isolated AOT build of [the EVT overlay registry](evt-overlay-registry.md) (1,357,536 blocks, which unblocks `00204000`; exe SHA-256 `2818e414...`, copied to `local/build/sakura-reattr/`). Each chapter-jump case (`backup.bin` plus the archived `input.movie`, extended with a confirm press every 75 frames) ran cold, strict native, headless, 45,000 frames, with `tools/chapter_loads.py --exe <exe> --disc 1 --backup <backup.bin> --movie <extended.movie> --frames 45000 --interval 500 --out local/work/reattr/run-<case>`. States and movies stay in `local/work`.

| Case | Exit | Frames | Interpreted 0 | Backup | Movie | Hash log |
| --- | ---: | ---: | --- | --- | --- | --- |
| `bank-7-battle` | 0 | 45000 | yes | `f93949f0` | `5bfe6029` | `9c1a288e` |
| `public-7` | 0 | 45000 | yes | `efe16833` | `76bd1a24` | `dc2c96e0` |

The `0700` cold route (both `bank-7-battle` and `public-7`, identical reads) loads `TITLE7`, BG2019, BG1266, BG2014, NC3014, BG2126, NC3126, BG1267, BG1268, BG2160, BG1181, NC70, BG1178, BG4017 and BG2080. Eight of them were `unassigned` and are now chapter 7 (disc 1): BG1178, BG1181, BG2014, BG2160, BG4017, NC3014, NC3126, NC70. `LOAD.BIN` stays `unassigned` (read by chapters 5 to 10).

Association is `observed`: a disc read shows the game asked for the file, not that it drew. Not verified in game: any draw of the moved rows.

## Verified BG2160 on the Episode 7 route

The v0.2.27-alpha runtime replayed the Episode 7 continuation at
2560 × 1440. At relative field 330, BG2160 changed 2,028,420 pixels
when its verified PC archive was present. Every changed pixel matched
the native Saturn decode without the donor and the independent PC decode
within two channel levels with it. The changes stayed inside
(272,29)–(2288,1037). The same process reverified BG1181 at fields
600, 690, 780 and 870 and BG1178 at field 1200. The donor controls had
matching guest hashes across 5,100 fields, identical save memory and
zero interpreted blocks. BG2160 was already counted through its disc 2
witness, so this adds the Episode 7 appearance to the evidence.

## BG2014 behind NC3014

At the opening of the retained Episode 7 continuation, NC3014 covers
most of the background. Only 11,137 native image pixels are attributed
to BG2014, below the ordinary 12,000-pixel HD threshold. Patch 0263
accepts this exact disc, palette, cells and actor identity at 11,000
exposed pixels when source and top-layer ownership agree. It also
checks the donor size and full file fingerprint.

In the native-actor tests at 1440p, 239,408–241,941 changed pixels
matched the Saturn RGB before and the independent PC decode within
two channel levels after. With the HD actor active, 195,833 pixels
changed, including approximately 840 along the anti-aliased face
contour where it blends with the new background. The opaque actor
and protected areas matched. Missing and invalid donor controls and
both Original profiles matched. Each 200-field strict pair had the
same guest hashes and save memory with zero interpreted blocks.
This adds one unique verified PC file. Patch 0263 ships in
[v0.2.28-alpha](../releases/v0.2.28-alpha.md).
