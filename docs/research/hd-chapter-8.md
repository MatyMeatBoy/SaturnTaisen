# HD chapter 8 coverage report (shard TH8)

Source: `config/hd-chapter-coverage.json` (chapters[7], `unassigned`, `association`), `docs/research/chapter-sweep.md`, `docs/SHARDS.md`, `docs/PENDIENTES.md` row TH8 (open). Names, hashes and counts only. This is a data report: no replay was run, nothing here certifies the chapter complete.

## 1. Scope

Chapter 8 is on disc 2 (CD-2). Observed evidence is limited to the Continue-screen sweep: the `0801` BIN/TBL/FCE family matches byte for byte in RAM from a saved state. Nothing else in the data is attributed to chapter 8 as `observed`.

| Class | Chapter 8 entries | Association |
| --- | --- | --- |
| Scene pictures (BG/EVE/CG) | 1 (`2:/SAKURA1/TITLE8.BIN`) | inferred (episode numbering) |
| NC bodies | 0 | none attributed |
| Portraits (FCE atlases) | 7 (`0801FCE` .. `0807FCE`) | `0801FCE` resident (RAM match), `0802`-`0807` inferred |
| FILM clips | 0 | none attributed |
| Tactical maps / units | 0 / 0 | none attributed |
| Menus/HUD | 0 | none attributed |

Disc-2 entries with no chapter attribution (the pool chapter 8 draws from, all `association: unknown`): 774 scene pictures, 147 bodies, 98 menus/HUD, 39 portrait entries, 22 FILM streams (counts of `2:`-prefixed keys in `unassigned`). Whole-game unassigned totals: scene pictures 1537, bodies 293, portraits 237, FILM 53, menus/HUD 195, tactical maps 27, tactical units 27.

## 2. Status per class (chapter 8 entries only)

| Class | hd | paired-not-wired | unpaired | unknown |
| --- | --- | --- | --- | --- |
| Scene pictures | 0 | 0 | 0 | 1 (`TITLE8.BIN`) |
| NC bodies | 0 | 0 | 0 | 0 |
| Portraits | 0 | 0 | 0 | 7 (`0801FCE`, `0802FCE`, `0803FCE`, `0804FCE`, `0805FCE`, `0806FCE`, `0807FCE`) |
| FILM clips | 0 | 0 | 0 | 0 |
| Tactical maps/units | 0 | 0 | 0 | 0 |
| Menus/HUD | 0 | 0 | 0 | 0 |

Context from the unassigned pool (not chapter 8 specific, whole game, both discs): scene pictures hd 917 / paired-not-wired 474 / unpaired 104 / unknown 42 (e.g. paired-not-wired `BG1011`, `BG1012`, `BG1013`); bodies hd 11 / paired-not-wired 246 / unpaired 30 / unknown 6 (hd e.g. `NC11`, `NC20`, `NC30`, `NC55`, `NC82`, `NC97`; paired-not-wired e.g. `NC10`, `NC12`, `NC13`); portraits hd 181 / unknown 56; FILM hd 44 / paired-not-wired 7 / unpaired 2; menus/HUD paired-not-wired 76 / unpaired 84 / unknown 35; tactical maps and units 27 each, all unknown.

Per-chapter portrait context: chapter 1 has 121 portraits hd; chapters 2-10 have none hd, all unknown (chapter 8: 7). The `hd` status of the 181 unassigned portraits is not tied to chapter 8; per-identity chapter membership: no data.

## 3. Five highest-value next actions

1. Attribute the 7 chapter 8 portrait atlases (`0801FCE`-`0807FCE`) to portrait identities: run the portrait audit and re-run the coverage tool so the status moves from unknown to hd/unpaired (closes up to 7). Touch: `tools/hd_chapter_coverage.py` with `--portrait-audit local/work/portrait-coverage-worker/portrait-coverage.json`, source `docs/research/portrait-animation-coverage.md`.
2. Add chapter witnesses for chapter 8 scene pictures/bodies from a cold replay of the `0801` route: observed BG/EVE/CG and NC files per frame range (closes the 774 + 147 disc-2 unattributed pool in part; real number no data). Touch: `CHAPTER_WITNESSES` in `tools/hd_chapter_coverage.py`, evidence in `docs/research/chapter-sweep.md`.
3. Resolve `TITLE8.BIN` (1 item): decide whether it is a title card with a PC counterpart; record pair or reason in `config/hd-scene-bg-review.json`, map in `config/hd-scene-bg-map.json`.
4. Attribute disc-2 FILM streams (22 unassigned; 0 in chapter 8) to chapter 8 by FAD and decide alternate cuts. Touch: `config/film-fad-map.json`.
5. List tactical maps/units used by chapter 8 for S11 (0 attributed now; whole game 27 maps, 27 units unknown). Touch: `config/hd-item-map.json` / tactical rows in `tools/hd_chapter_coverage.py`, shard TS11.

Counts closed per action are upper bounds from the data; none is verified.

## 4. Cannot be known without playing (owner's discs)

- Which scene pictures, bodies, portraits and clips chapter 8 actually draws, in order (the data has only one resident match and numbering inferences).
- Whether each `0802FCE`-`0807FCE` atlas is drawn in chapter 8 or only eligible.
- Whether a portrait that matches stays native on some frames (native face fallback), and the frame layouts needed (T106a-d style).
- Whether chapter 8 contains a FILM clip, a tactical stage, or alternate cuts.
- Per-frame guest-hash equality of an HD run versus a non-HD run along the chapter 8 path (the exit test); screenshots for the owner.

## 5. Open questions

- Does `TITLE8.BIN` belong to chapter 8 only, and has it a PC pair? (Data: unknown, inferred.)
- Are the 774 disc-2 scene pictures partly chapter 8? No data on the split.
- Do chapters 8-10 share atlases or scenes with earlier chapters? No data.
- The chapter-8 bodies and menus/HUD lists are empty: gap in evidence or truly none? No data.
- Which replay route (save state, inputs) reproduces the `0801` start for the strict-native exit test? Not stated in the files read.
