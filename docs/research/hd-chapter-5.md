# HD chapter 5 coverage (shard TH5)

Source data: `config/hd-chapter-coverage.json` (chapter 5, disc 1), `config/hd-scene-bg-map.json`, `config/hd-scene-bg-review.json`, `config/hd-body-map.json`, `config/hd-item-map.json`, `config/film-fad-map.json`, `docs/research/chapter-sweep.md`, `docs/PENDIENTES.md` (row TH5). Names and counts only; no game pixels, script text or disc contents. The initial inventory snapshot was offline. The native opening observations below use archived replays.

## 1. Initial catalog snapshot

Chapter 5 is attributed in the coverage JSON with only 5 resources, all disc 1, all status `unknown`. The only observed evidence is one strict replay (`bank-5-battle-strict`, Episode 5 File 1 CD-1, 12,000 frames, zero interpreted blocks, opening dialogue after Continue). The BIN/TBL/FCE family `0501` matched in RAM.

| Class | Attributed to ch.5 | Association |
| --- | --- | --- |
| Scene pictures (BG/EVE/CG) | 1 (the title card) | inferred |
| NC bodies | 0 | no data |
| Portraits (FCE atlases) | 4 | 1 resident, 3 inferred |
| FILM clips | 0 | no data |
| Tactical maps / units | 0 / 0 | no data |
| Menus / HUD | 0 | no data |

The empty classes mean chapter evidence is missing, not that chapter 5 shows none. The pool the chapter draws from is the `unassigned` section (disc inventory entries with no known chapter): scene pictures 1537, bodies 293, portraits 237, FILM 53, menus/HUD 195, tactical maps 27, tactical units 27.

## 2. Status

Chapter 5 (attributed items):

| Class | hd | paired-not-wired | unpaired | unknown | Examples |
| --- | --- | --- | --- | --- | --- |
| Scene pictures | 0 | 0 | 0 | 1 | `1:/SAKURA1/TITLE5.BIN` |
| Bodies | 0 | 0 | 0 | 0 | no data |
| Portraits | 0 | 0 | 0 | 4 | `0501FCE.BIN` (resident), `0502FCE.BIN`, `0503FCE.BIN`, `0504FCE.BIN` (inferred) |
| FILM | 0 | 0 | 0 | 0 | no data |
| Tactical | 0 | 0 | 0 | 0 | no data |
| Menus/HUD | 0 | 0 | 0 | 0 | no data |

Unassigned pool (the candidates for chapter 5, not yet placed):

| Class | hd | paired-not-wired | unpaired | unknown | Examples |
| --- | --- | --- | --- | --- | --- |
| Scene pictures (1537) | 917 | 474 | 104 | 42 | `AI_CG.BIN`, `BG0000.BIN`, `BG1001.BIN`, `BG1002.BIN` |
| Bodies (293) | 11 | 246 | 30 | 6 | `NC11.BIN` (hd), `NC10.BIN`, `NC12.BIN`, `NC13.BIN` (paired) |
| Portraits (237) | 181 | 0 | 0 | 56 | ids `000c`, `000e`, `0011`, `0012`, `001f` |
| FILM (53) | 44 | 7 | 2 | 0 | `/SAKURA4+0`, `/SAKURA4+100188160`, `OPSAKURA.CPK+0` |
| Menus/HUD (195) | 0 | 76 | 84 | 35 | `ITEM01.BIN` ... `ITEM06.BIN` |
| Tactical maps (27) | 0 | 0 | 0 | 27 | `MAP01.BIN`, `MAP02.BIN`, `MAP03.BIN` |
| Tactical units (27) | 0 | 0 | 0 | 27 | `UNIT01.BIN`, `UNIT02.BIN`, `UNIT03.BIN` |

Notes from other files: `config/hd-scene-bg-map.json` summary is content 519, number 216, missing 5 (whole catalog; tier `number` needs an eye check). Neither `hd-scene-bg-map.json` nor `hd-scene-bg-review.json` mentions `TITLE5` or `0501FCE`, so the title card has no BG pairing record; `TITLE1..10` widening is T87/patch0071 (all ten cards, not chapter specific). Both discs list `0501FCE` and `TITLE5` as `unknown` in the unassigned section. NC bodies in use: six have documented draws (NC11, NC20, NC30, NC55, NC82, NC97); which of them chapter 5 uses has no data.

## 3. Highest-value next actions (by items closed)

1. Place scene pictures for episode 5 (up to the 1537-entry pool; at minimum the 42 `unknown` and the 474 `paired-not-wired`): run the episode 5 route with the scene tagging and record `1:/SAKURA1/...` witnesses. Touch `tools/hd_chapter_coverage.py` (`CHAPTER_WITNESSES`, which today holds only chapter 1 entries) and regenerate `config/hd-chapter-coverage.json`. Use `observed-scene-resources.json` from `docs/research/chapter-sweep.md`.
2. Place NC bodies (pool 293; 246 paired-not-wired): trace with `SATRECOMP_BODY_TRACE=1` (patch0062) on the episode 5 replay, add witnesses as above; wiring beyond the six drawn bodies is T19/T106a2/T106b2 (`config/hd-body-map.json`, `config/hd-nc30-face-map.json`, `config/hd-nc20-face-map.json`).
3. Confirm portraits (4 attributed, 237 pool, 56 unknown): run `tools/` portrait audit (`docs/research/portrait-animation-coverage.md`) filtered to the `0501`..`0504` FCE family and mark which identities appear; promote `0501FCE` from resident to observed. File: `portrait-coverage.csv` input to `hd_chapter_coverage.py --portrait-audit`.
4. Map FILM clips for chapter 5 (pool 53: 7 paired-not-wired, 2 unpaired): find which FADs the chapter starts and add them to the chapter via `config/film-fad-map.json` (`streams`; 54 entries, alternate cuts keep Saturn picture/audio). Decision per alternate cut is required by SHARDS H1-H10 (c).
5. List tactical maps/units and menus/HUD for chapter 5 for S11 (27 + 27 unknown; 195 menus/HUD, 84 unpaired): identify the stage/battle in the episode 5 route, add them to `tactical-maps`/`tactical-units` in the coverage tool; item pairs are in `config/hd-item-map.json`.

## 4. Cannot be known without playing (needs the owner's discs)

- Which scene pictures, bodies, portraits and clips episode 5 actually draws, and in which order.
- Whether native-face fallbacks (NC11, NC20, NC30, NC55) occur in episode 5 and how they look.
- The tactical map(s) and units fought in the chapter, and which menus/HUD screens appear.
- Whether FILM alternate cuts are reached and where the episode 5 clips start.
- Per-frame guest hash equality of a continuous strict-native replay of the whole chapter path with HD on versus off (the exit test). The existing 12,000-frame replay stops at the opening dialogue.
- Screenshots the owner can open.

## 5. Open questions

- Is the chapter 5 disc always disc 1, and which tool outputs mark the end of chapter 5 (the sweep covers only the opening dialogue)?
- `TITLE5.BIN` is `unknown` in the coverage JSON although the title cards are handled by T87/patch0071: should the title cards get their own status?
- The unassigned pool lists the same files on both discs (`2:/SAKURA1/0501FCE.BIN`, `2:/SAKURA1/TITLE5.BIN`) as `unknown`; are these shared residents or disc 2 copies, and should they be merged?
- The meaning of `unpaired` for the 84 menus/HUD entries (rejected versus absent counterpart) is not split in the data.
- No tactical stage-to-chapter table exists in the inputs: no data for which `MAPnn` is chapter 5.
- Row TH5 in `docs/PENDIENTES.md` is still `open` with no owner; this report does not change it.

## BG2533 runtime witness

The extended Episode 5 replay reached the BG2533 horizontal pan. The coverage generator records it as observed and HD. The scene uses the verified PC crop in Enhanced Zoom. See [BG2533 pan](bg2533-pan.md) for capture positions and fallback proof.


## Native opening observations

The English disc-1 Episode 5 File 1 save opens narrative script
`0501`. The 14,000-frame BG2533 route and a 7,200-frame continuation
from its frame-12149 save both ran strict-native with zero interpreted
blocks. The guest hash logs have SHA-256
`ff2b8b31b9259e928f361846c405ebd0796e096a3abd4d78bb5324cd36f2d7c2`
and `e50a62a1ad1c7b7e4b26049cfd85dcd70b9817fd02d285f9e87b66a1e1c95fb7`.
The continuation uses ordinary controller confirmations and ends
during the narrative prologue. Its frame numbers below are local to
that replay. The cold witness, motion capture and chapter-sweep
runs share the same guest hashes at all overlapping frames.

The CD FAD establishes the exact file read. Decoding the named image
and comparing the 288×144 native picture gives independent display
evidence.

| Frame | Native asset | Read FAD | Exact visible evidence |
| --- | --- | ---: | --- |
| Cold 9000 | BG1198 | 142883 | All 14,212 pixels outside the opaque NC90 mask. |
| Continuation 1800 | BG1243 | 143797 | All 41,472 picture pixels. |
| Continuation 4200 | BG1031 | 139732 | 29,639 pixels, the area outside the opaque NC60 mask. |
| Continuation 4800 | BG2132 + BG3132 | 148839 + 153744 | 23,415 and 18,112 matches. The union is all 41,472 pixels with 55 matching both. |
| Continuation 5400 | BG2133 + BG3133 | 148862 + 153767 | 24,892 and 16,593 matches. The union is all 41,472 pixels with 13 matching both. |
| Continuation 7200 | BG2058 | 147337 | 3,202 exposed matches outside NC3058, spanning 166 RGB colors. |

The NC90 active body command uses the exact 288×144 indexed body.
At cold frame 9000, 25,843 of its opaque pixels match the stock image.
NC60 matches 11,273 opaque pixels at (120,8) in continuation frame 4200,
following its read at FAD 165138. NC3058 has an exact 288×144 body
command in the terminal state and all 27,544 opaque pixels match
the frame-7200 capture. These are native body observations. The
coverage register retains their existing HD integration status
and records no new HD body draw.

| State / image | Portrait | Base FNV-1a | Native RGB comparison |
| --- | --- | --- | --- |
| Cold 9000 | 00ff | `25BB69A16079F802` | All 1,920 pixels match after the exact 27/32 white blend. |
| Cold 12149 / 12150 | 0169 | `7CA30C1792ED4682` | All 1,920 match. The active row-16 strip repeats the base region. |
| Cold 13999 / 14000 | 010f | `47658F2AA81A82AB` | All 1,920 match. |
| Continuation terminal | 016a | `09C1A8436F3C1C63` | All 1,920 match. |

The VDP1 command payloads match their identities in the resident
`0501FCE.BIN`. The 0169 cameo keeps its native emblem and its
existing chapter-1 inference. BG1198 also keeps its earlier
chapter-3 observation. These multiple chapter occurrences leave
the global replacement totals unchanged. BG2533 keeps its
separate HD witness, and the BG3132/BG3133 layers keep their
existing exclusions. Later chapter phases, tactical attribution,
full chapter parity and packaging remain open.

At block close the main workspace measured 61,107,185,170 logical bytes
with hard links counted once and reparse points excluded, above the
20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.
