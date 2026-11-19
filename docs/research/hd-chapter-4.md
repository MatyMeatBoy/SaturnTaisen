# HD chapter 4 coverage report (shard TH4)

Source: `config/hd-chapter-coverage.json` (`chapters[3]`, `unassigned`, `association`), cross-checked with `config/hd-scene-bg-map.json`, `hd-scene-bg-review.json`, `hd-body-map.json`, `hd-item-map.json`, `film-fad-map.json`, `docs/research/chapter-sweep.md` and `docs/PENDIENTES.md` (rows T31, T32, T87, TH4). Names, hashes and counts only. Nothing here certifies the chapter; the exit test (strict-native replay with per-frame guest hashes identical to a build without HD) has not been run.

## 1. Scope: what the data attributes to chapter 4 (disc 1)

The generator attributes almost nothing to chapter 4. Every attributed entry has association `inferred` (episode file numbering), none `observed` or `resident`.

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
