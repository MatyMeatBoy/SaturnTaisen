# HD coverage: chapter 3 (TH3)

The [Chapter 3 native evidence](th3-native-attribution.md) adds observed scene pictures and tactical resources to the chapter register. It records display, residency, and disc reads separately. The complete replay and HD exit test are open.

## Earlier catalog snapshot

Source: `config/hd-chapter-coverage.json` (`chapters[2]`, `unassigned`, `association`), `docs/research/hd-chapter-coverage.md`, `docs/research/chapter-sweep.md`. Chapter 3 is on disc 1 and its Continue-screen anchor is episode `0301`. Names and counts only; no game pixels or script text.

## 1. Scope (what the data attributes to chapter 3)

| Class | Attributed to ch.3 | Notes |
|---|---|---|
| Scene pictures | 1 (`1:/SAKURA1/TITLE3.BIN`) | inferred from the title numbering, not observed |
| NC bodies | 0 | no data |
| Portraits | 9 (`0301FCE`..`0309FCE`) | 1 resident (`0301FCE`), 8 inferred |
| FILM clips | 0 | no data |
| Tactical maps / units | 0 / 0 | no data |
| Menus/HUD | 0 | no data |

The chapter row is almost empty because only the exact witnesses in `CHAPTER_WITNESSES` and the episode-numbering inference place anything in a chapter. The real inventory sits in `unassigned` (chapter unknown): 1537 scene pictures, 293 bodies, 237 portraits, 53 FILM entries, 195 menu/HUD files, 27 maps, 27 units. Chapter 3 share of those: no data.

## 2. Status per class (chapter 3 rows only)

| Class | hd | paired-not-wired | unpaired | unknown | Examples |
|---|---|---|---|---|---|
| Scene pictures | 0 | 0 | 0 | 1 | `TITLE3.BIN` |
| Bodies | 0 | 0 | 0 | 0 | none attributed |
| Portraits | 0 | 0 | 0 | 9 | `0301FCE`, `0302FCE`, `0303FCE`, `0309FCE` |
| FILM | 0 | 0 | 0 | 0 | none attributed |
| Tactical | 0 | 0 | 0 | 0 | none attributed |
| Menus/HUD | 0 | 0 | 0 | 0 | none attributed |

Portraits are "unknown" because the portrait recipe does not list the `03xx` atlas names as paired in this join (the unassigned portrait entries use short ids such as `000c` with a `pc_index`). Whether the 9 have HD pairs: no data in the chapter row.

Context, unassigned pool (status counts, not chapter 3 specific): scene pictures hd 917 / paired-not-wired 474 / unpaired 104 / unknown 42; bodies hd 11 / paired-not-wired 246 / unpaired 30 / unknown 6 (e.g. hd `NC11`; paired `NC10`, `NC12`..`NC16`, `NC21`..`NC26`); FILM hd 44 / paired-not-wired 7 / unpaired 2 (e.g. `SAKURA4+100188160`, `OPSAKURA.CPK+0`); menus/HUD paired 76 / unpaired 84 / unknown 35 (e.g. `ITEM01`..`ITEM06`); portraits hd 181 / unknown 56; maps 27 and units 27 all unknown (e.g. `MAP01`, `UNIT01`).

## 3. Five next actions (by items closed)

1. Attribute scene pictures to chapter 3 from a traced run: add chapter-3 witnesses to `CHAPTER_WITNESSES` in `tools/hd_chapter_coverage.py` (or extend the scene index under `local/work/scene-index-later`), then regenerate `config/hd-chapter-coverage.json`. Closes the attribution of up to ~1537 pool entries (chapter 3 share: no data); until done the ch.3 scene-picture count stays 1.
2. Same step for NC bodies (293 in pool): record which `NCxx` the chapter draws in `docs/research/saturn-bg-format.md` (the evidence file the tool reads), then regenerate. Also decide the 246 `paired-not-wired` bodies in `config/hd-body-map.json`.
3. Resolve the 9 portraits (`0301FCE`..`0309FCE`): run the portrait audit (`docs/research/portrait-animation-coverage.md`, `local/work/portrait-coverage-worker/portrait-coverage.json`) and check `config/hd-portrait-recipe.json` / `config/hd-portrait-reviewed.json` for each; 9 items.
4. FILM: attribute ch.3 clips in `config/film-fad-map.json` (53 pool entries; 7 paired-not-wired, 2 unpaired need a decision on alternate cuts); evidence from `docs/research/chapter-sweep.md`.
5. Tactical: list the ch.3 maps/units for S11 (27 + 27 unknown, TS11 row in `docs/PENDIENTES.md`); chapter 3 battles 1-3 exist per `docs/research/evt-overlay-registry.md` (12,000 and 40,000 frame sweeps pass), which gives the path to trace. Use `config/hd-item-map.json` / `config/hd-system-hud-review.json` for menus/HUD (195 pool).

Also: `config/hd-scene-bg-map.json`, `config/hd-scene-bg-review.json` and `docs/research/bg-matching-progress.md` hold the BG pair decisions; they were not found to carry per-chapter keys (no data) so chapter 3 filtering needs the traced list from action 1.

## 4. Cannot be known without playing (owner's discs)

- Which scene pictures (BG/EVE/CG) chapter 3 actually draws, and in which order.
- Which NC bodies and portrait frames appear, and whether the matcher leaves a face native.
- Which FILM streams play in chapter 3 and whether an alternate cut is reached.
- The tactical map and unit files of the three chapter-3 battles.
- Per-frame guest-hash equality of the HD runtime vs the non-HD build on the chapter path (the exit test); a saved state does not certify it.
- Visual quality of every substitution and of the wide framing.

## 5. Open questions

- Is the `0301` entry (Continue anchor) the only chapter-3 file witness, and should the other `030x` episode numbers be accepted as chapter 3 or only inferred?
- Is `TITLE3.BIN` the chapter-3 title card? Only inferred from numbering.
- Why do disc-2 `TITLE*` copies appear in `unassigned` as unknown while disc-1 ones are inferred per chapter?
- Does the portrait join use short ids (`000c`) or `03xxFCE` names for HD status? The two namespaces are not linked in the chapter row.
- Chapter 3 translation progress (3 of 7 batches, per `docs/research/traduccion-espanol.md`) is unrelated to HD but shares the chapter exit test timing.

Nothing here is tested in a replay; status is catalog-level only.
