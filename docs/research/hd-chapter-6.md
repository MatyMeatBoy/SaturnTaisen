# HD chapter 6 coverage report (shard TH6)

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
