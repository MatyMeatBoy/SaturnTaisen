# HD chapter 1 coverage report (TH1)

Source: `config/hd-chapter-coverage.json` (chapter 1, disc 1), cross-checked with `config/hd-scene-bg-map.json`, `hd-scene-bg-review.json`, `hd-body-map.json`, `hd-item-map.json`, `film-fad-map.json`, `docs/PENDIENTES.md`. The stage ground has [its own replay evidence](stage01-pc-ground.md). The chapter-wide exit test from `docs/SHARDS.md` remains open.

Key fact: the generator attributes very little to chapter 1 directly. Only 7 non-portrait entries are chapter-attributed; almost all disc resources sit in the `unassigned` section (chapter unknown). Counts below are attributed entries only, with unassigned totals for context.

## 1. Scope (attributed to chapter 1)

| Class | Attributed | Association | Unassigned pool (all chapters) |
|---|---|---|---|
| Scene pictures | 4 | 3 observed, 1 inferred | 1537 |
| NC bodies | 1 | observed | 293 |
| Portraits | 129 | all inferred (atlas membership: 0100/0101/0102/0103/0108/0109FCE, both discs) | 237 |
| FILM clips | 1 (`1:/SAKURA4+23695360`, MOVIE001, FAD 11975) | observed | 53 |
| Tactical maps | 1 (`1:/SAKURA2/MAP01.BIN`) | observed | 26 |
| Tactical units | 0 | no data | 27 |
| Menus/HUD | 0 | no data | 195 |

Portrait row has 129 entries: 123 portrait ids plus 6 atlas files that are listed as entries.

## 2. Status per class

| Class | hd | paired-not-wired | unpaired | unknown |
|---|---|---|---|---|
| Scene pictures (4) | 1: `BG1119` | 2: `IC01` (to ICATCH IC0100), `EVE0101` (to BBG001) | 0 | 1: `TITLE1` |
| NC bodies (1) | 1: `NC20` (native face fallback true) | 0 | 0 | 0 |
| Portraits (129) | 121: `0001`-`000f`, `017a`-`017c` | 0 | 2: `00a1`, `0169` | 6: the atlas files `0100FCE`, `0101FCE`, `0102FCE`, `0103FCE`, `0108FCE`, `0109FCE` |
| FILM (1) | 1: MOVIE001 (no alternate cut) | 0 | 0 | 0 |
| Tactical maps (1) | 1: `MAP01` ground only, with the approved right-side extension | 0 | 0 | 0 |
| Tactical units | no data | no data | no data | no data |
| Menus/HUD | no data | no data | no data | no data |

Unassigned pool by status (chapter unknown, may include chapter 1 items):
- Scene pictures: 917 hd, 474 paired-not-wired, 104 unpaired, 42 unknown.
- Bodies: 11 hd, 246 paired-not-wired, 30 unpaired, 6 unknown.
- FILM: 44 hd, 7 paired-not-wired, 2 unpaired.
- Menus/HUD: 76 paired-not-wired, 84 unpaired, 35 unknown.
- Portraits: 181 hd, 56 unknown. Tactical maps/units: 26 + 27 unknown.

Map totals (all chapters): scene BG map 519 content + 216 number + 5 missing; body map 104 content + 40 candidate; item map 12 content + 68 candidate. Scene review: 114 reviewed, 47 rejected, 118 cutouts.

Existing evidence for chapter 1 on the PENDIENTES side: T09 (portraits, 32 pending in the 201 checkpoint, reviewing `004f`, `0095`, `00a1`, `00ef`, `013b`, `013c`, `0169`), T42 (201/304 and 91/123 checkpoint), T106b/b2 (NC20 face map, 63 textures at 72 offsets pinned; runtime consumption open), TH1 (open), TS11 (open).

## 3. Five highest-value next actions

1. Attribute chapter 1 resources: the 1537 scene pictures, 293 bodies and 53 FILM streams in `unassigned` are not tied to any chapter, so every other count is blocked. Touch `tools/hd_chapter_coverage.py` inputs (scene index in `local/work/scene-index-later`; episode numbering EVE01xx/BG11xx), then regenerate `config/hd-chapter-coverage.json` with `--check`. Closes the most items, potentially hundreds.
2. Wire the 474 scene pictures and 246 bodies that are paired-not-wired, starting with chapter 1's `IC01` and `EVE0101`: `config/hd-scene-bg-map.json`, `config/hd-body-map.json` and the SDK patch stack (`config/dependencies.json`, next free patch number).
3. Consume the NC20 face map (T106b2): `config/hd-nc20-face-map.json` into a new SDK patch; closes the `native_face_fallback` for the only chapter 1 body. Same for NC30 (T106a2) if chapter 1 uses it (no data).
4. Close the 8 non-hd portrait entries: decide `00a1` and `0169` (unpaired, review under T09 and `config/hd-portrait-*` catalogs), and record the 6 atlas files as atlas entries rather than portraits in the generator. Files: `docs/research/portrait-animation-coverage.md`, T09 list.
5. Tactical list for S11 (`STAGE01`, units no data): add chapter 1 stage maps and units to the TS11 pairing; `config/hd-item-map.json` has 68 candidates unconfirmed. Also record a decision for `TITLE1` (unknown).

## 4. Cannot be known without playing (owner's discs)

- Which scene pictures, bodies, portraits and FILM clips chapter 1 actually draws, in order (the 121 hd portraits are only eligible by atlas membership).
- Whether `IC01`/`EVE0101` and the unassigned pairs draw correctly at runtime, and whether native faces are used for NC20.
- Whether alternate FILM cuts exist in chapter 1 beyond MOVIE001.
- Tactical stage count and units for chapter 1 and menu/HUD resources shown.
- Strict-native hash identity of the HD runtime across a full chapter 1 path.

## 5. Open questions

- Does the generator's chapter attribution rule (observed, resident, inferred, unknown) get extended to use episode file numbering for the 1537 unassigned scene pictures?
- Why do menus/HUD and tactical units have no chapter 1 entries (no data vs none shown)?
- Are `00a1` and `0169` genuinely without a PC counterpart or a matcher gap?
- Is `TITLE1` a chapter 1 resource or a title-screen item shared across chapters?
- Which replay path defines "chapter 1 complete" for the exit test (no data in the files read)?
