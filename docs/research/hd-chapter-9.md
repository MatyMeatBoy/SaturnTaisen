# HD chapter 9 coverage (shard TH9)

Source: `config/hd-chapter-coverage.json` (chapter 9 entry, `unassigned`, `association`), cross-checked against `docs/research/chapter-sweep.md`, `config/hd-scene-bg-map.json`, `config/hd-scene-bg-review.json`, `config/hd-body-map.json`, `config/hd-item-map.json`, `config/film-fad-map.json` and `docs/PENDIENTES.md` (row TH9, status open). Names, hashes and counts only. This is a data report; it is not a replay, and it does not certify the chapter.

## 1. Scope

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

Association levels: observed (seen in runtime evidence), resident (in RAM, not shown drawn), inferred (numbering/atlas candidate), unknown. Chapter 9 has no `observed` entry at all.

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
