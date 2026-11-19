# HD chapter 2: coverage report (shard TH2)

Source: `config/hd-chapter-coverage.json` (chapter 2 entry, `unassigned`, `association`), cross-checked with `config/hd-scene-bg-map.json`, `hd-scene-bg-review.json`, `hd-body-map.json`, `hd-item-map.json`, `film-fad-map.json` and `docs/PENDIENTES.md`. Names, hashes and counts only. Nothing here is a replay result: no chapter-2 HD replay report exists yet (exit test of `docs/SHARDS.md` not met).

## 1. Scope

Chapter 2 is on disc 1. The JSON attributes very little to it; most chapter-2 content sits in `unassigned` (chapter unknown) because only observed/inferred evidence is attributed.

| Class | Attributed to ch.2 | Notes |
| --- | --- | --- |
| Scene pictures | 2 | `EVE202.BIN` (observed, evidence `saturn-bg-format.md`), `TITLE2.BIN` (inferred) |
| NC bodies | 0 | whole disc-1 body list is in `unassigned` (293 bodies, see below) |
| Portraits | 6 | `0201FCE` to `0206FCE`, all "inferred" (episode numbering) |
| FILM clips | 0 | 53 disc/FAD starts all unassigned |
| Tactical maps/units | 0 | 27 maps + 27 units, all unassigned, all `unknown` |
| Menus/HUD | 0 | 195 items unassigned |

Unattributed pool that may include chapter 2 (disc-wide, not chapter-specific): 1537 scene pictures (763 disc 1, 774 disc 2), 293 bodies, 237 portrait ids, 53 film streams, 195 menu/HUD. By file-number heuristic only (BG20xx, not documented as "chapter 2"): 97 distinct BG20xx per disc (194 entries both discs).

## 2. Status per class

Chapter-2-attributed items:

| Class | hd | paired-not-wired | unpaired | unknown |
| --- | --- | --- | --- | --- |
| Scene pictures (2) | 0 | 1: `EVE202` -> `SAKURA2/BG/BBG202.SPR` | 0 | 1: `TITLE2` |
| Bodies (0) | 0 | 0 | 0 | 0 |
| Portraits (6) | 0 | 0 | 0 | 6: `0201FCE`..`0206FCE` (status `unknown`; not the audited-hd path) |
| FILM (0) | no data | no data | no data | no data |
| Tactical (0) | no data | no data | no data | no data |
| Menus/HUD (0) | no data | no data | no data | no data |

Disc-wide pools in `unassigned` (chapter unknown; the status is real, the chapter is not):

| Class | hd | paired-not-wired | unpaired | unknown | Example IDs |
| --- | --- | --- | --- | --- | --- |
| Scene pictures (1537) | 917 | 474 | 104 | 42 | hd: `BG2004`, `BG2011`, `BG2012`, `BG2014`, `BG2016`; pnw: `BG2001`, `BG2002`, `BG2003`, `BG2005`, `BG2006`; unpaired: `BG2035`, `BG2044`, `BG2050`, `BG2059`, `BG2071`; unknown: `TITLE1`..`TITLE10` |
| Bodies (293) | 11 | 246 | 30 | 6 | hd: `NC11` (native face fallback, runtime evidence `saturn-bg-format.md`); pnw: `NC10`, `NC12`, `NC13`, `NC14`, `NC15` |
| Portraits (237) | 181 | 0 | 0 | 56 | ids `000c`, `000e`, `0011`, `0012`, `001f` (hd); the 6 chapter-2 ids above are in the unknown part |
| FILM (53) | 44 | 7 | 2 | 0 | `MOVIE000` (FAD 405, hd), `MOVIE001` (FAD 11975, hd); streams `OPSAKURA.CPK+0`, `SAKURA4+0`; alternate cuts stay native |
| Menus/HUD (195) | 0 | 76 | 84 | 35 | `ITEM01`..`ITEM05` (first entries) |
| Tactical maps/units (27+27) | 0 | 0 | 0 | 54 | `MAP01`..`MAP05`, `UNIT01`..`UNIT05` |

BG20xx heuristic subset (194 entries, 97 per disc): 74 hd, 18 paired-not-wired, 5 unpaired, per disc. Treat as a candidate list, not as chapter-2 proof. Per-picture mapping tiers (`hd-scene-bg-map.json`): 519 content, 216 number, 5 missing; all 203 SAKURA1 tier-number pairs were eyed on 2026-11-19 (`hd-scene-bg-review.json`), none confirmed in the runtime.

## 3. Five highest-value next actions

1. **Attribute chapter-2 scene pictures** (closes up to ~97 BG20xx entries per disc from unknown to chapter 2): run the chapter-2 strict-AOT replay (continue from episode 2 save, as in `chapter-sweep.md`), emit `observed-scene-resources.json`, rerun `python tools/hd_chapter_coverage.py --index local/work/scene-index-later --portrait-audit ...`; touch `CHAPTER_WITNESSES` in `tools/hd_chapter_coverage.py` only with documented witnesses. Needs the owner's discs.
2. **Wire the paired-not-wired scenes** (about 18 BG20xx per disc plus `EVE202`): generator/table for the compiled scene table; data in `config/hd-scene-bg-map.json` + `config/hd-scene-bg-review.json`, then SDK patch (next free number in `config/dependencies.json`).
3. **Attribute and wire NC bodies** (246 paired-not-wired disc-wide, 0 attributed to ch.2): trace which `NCxx` chapter 2 draws, then extend the draw list `BODY_DRAWS` in `tools/hd_chapter_coverage.py` and `config/hd-body-map.json` (candidates/undecoded: 40 candidate, 104 content).
4. **Resolve the 6 chapter-2 portraits** (`0201FCE`..`0206FCE`, all `unknown`): run `docs/research/portrait-animation-coverage.md` audit, then follow T106a-d for faces the matcher leaves native.
5. **Map chapter-2 FILM and tactical lists** (53 FADs unattributed; 54 tactical files unknown): record which `MOVIE###` plays in episode 2 in `config/film-fad-map.json`; list tactical map/unit files for S11 (TS11) from the replay.

## 4. Cannot be known without playing (owner's discs)

- Which scene pictures, bodies, portraits, FILM clips, tactical maps and menu/HUD items episode 2 actually draws (all attribution is inferred or absent).
- Whether the 6 portraits `0201`-`0206` appear individually, and which expressions.
- Whether paired scenes (`EVE202`, BG20xx) render correctly in-game; every pair is "not verified in the runtime".
- Per-frame guest hash equality of a strict-native HD replay of the chapter-2 path (exit test).
- Alternate FILM cut use, and which tactical stages chapter 2 runs.
- Real-time text-in-picture issues (the reviews checked only Saturn-side/PC-side pictures).

## 5. Open questions

- Is BG20xx numbering really episode 2? No document asserts it; `TITLE2` is similarly only inferred.
- Why are chapter-2 bodies, FILM and menus/HUD empty in the JSON: no evidence yet, or truly none? Data cannot tell.
- `EVE202` is `observed` for chapter 2 but `paired-not-wired`: is `BBG202` drawn at runtime or only resident?
- Chapter-2 evidence: PENDIENTES T29 and T25 show episode 2 was played/booted (EVT02 at `00204000`; disc 1 dialogue and battle), but no row ties that to HD coverage; TH2 is still `open` (row TH2, T25 Spanish notes).
- Does the 0-count `bodies`/`film` for chapter 2 mean the coverage generator needs a chapter-2 observed-resources input like chapters 3-10 in `chapter-sweep.md`?
