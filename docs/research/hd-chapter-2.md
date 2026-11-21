# HD chapter 2: coverage report (shard TH2)

## Continue route attribution

A muted strict-native replay on English disc 1 followed the established Episode 2 File 1 route through the tactical introduction and Kohran's movement grid. It matched all 28,491 guest hashes from the earlier continuous replay, SHA-256 `12cae74f096b5a5bff308994efce70ec40cef1525e9de663686e256903d136cf`, with zero interpreted blocks. The separate 9,501-frame Continue prefix also reproduced its reference exactly.

| Saturn file | CD play start FAD | Observation |
| --- | --- | --- |
| `SAKURA2/EVT02.BIN` | 221798 | Tactical module entry |
| `SAKURA2/MAP02.BIN` | 231973 | Terrain visible through movement and the selected Kohran grid |
| `SAKURA2/UNIT02.BIN` | 252153 | Only unit bank loaded in this route, followed by active unit selection and movement |
| `SAKURA2/EVE202.BIN` | 221148 | Opaque dialogue illustration, covered by prior HD evidence |
| `SAKURA2/EVE002.BIN` | 221023 | Airship illustration, covered by prior HD evidence |

The PC and Saturn copies of `MAP02.BIN` are byte-identical (336,640 bytes, SHA-256 `f2bc29c87209a2bb1ab28b0664e3be1140b2245632005e03f35d84e1b8015611`). PC `MAP02.TAB` identifies the 2048 × 2048 `MAP02_A.SPR` as ground. The native render probe separated the matching terrain from the grid and units on source 4, page `0x40000`, at scroll `(584, 704)`. The first 8,192 pattern-name bytes have FNV-1a `25FF56EB6965E424`. The PC crop shows the same terrain features with different textures. The exact transform and guarded HD ground draw remain open. Unit attribution records the active tactical bank, with identity-specific art still open.

`WKL02`, `FACE02` and `M02MES` were read during the same route. These reads alone do not establish the display of individual rows or portraits. The report and register do not extend the tactical sample to a full chapter exit test.

## Earlier inventory snapshot

The totals below are the baseline from before this attribution pass.

Source: `config/hd-chapter-coverage.json` (chapter 2 entry, `unassigned`, `association`), cross-checked with `config/hd-scene-bg-map.json`, `hd-scene-bg-review.json`, `hd-body-map.json`, `hd-item-map.json`, `film-fad-map.json` and `docs/PENDIENTES.md`. Names, hashes and counts only. The counts below reflect the coverage inventory. The [EVE202 tactical inset](eve202-tactical-inset.md) now has a verified scene replay. The full chapter-2 HD replay remains open.

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
2. **Wire the paired-not-wired scenes** (about 18 BG20xx per disc): generator/table for the compiled scene table; data in `config/hd-scene-bg-map.json` + `config/hd-scene-bg-review.json`, then SDK patch (next free number in `config/dependencies.json`).
3. **Attribute and wire NC bodies** (246 paired-not-wired disc-wide, 0 attributed to ch.2): trace which `NCxx` chapter 2 draws, then extend the draw list `BODY_DRAWS` in `tools/hd_chapter_coverage.py` and `config/hd-body-map.json` (candidates/undecoded: 40 candidate, 104 content).
4. **Resolve the 6 chapter-2 portraits** (`0201FCE`..`0206FCE`, all `unknown`): run `docs/research/portrait-animation-coverage.md` audit, then follow T106a-d for faces the matcher leaves native.
5. **Map chapter-2 FILM and tactical lists** (53 FADs unattributed; 54 tactical files unknown): record which `MOVIE###` plays in episode 2 in `config/film-fad-map.json`; list tactical map/unit files for S11 (TS11) from the replay.

## 4. Cannot be known without playing (owner's discs)

- Which scene pictures, bodies, portraits, FILM clips, tactical maps and menu/HUD items episode 2 actually draws (all attribution is inferred or absent).
- Whether the 6 portraits `0201`-`0206` appear individually, and which expressions.
- Whether the other paired scenes (BG20xx) render correctly in-game. The [EVE202 tactical inset](eve202-tactical-inset.md) has a verified HD substitution.
- Per-frame guest hash equality of a strict-native HD replay of the chapter-2 path (exit test).
- Alternate FILM cut use, and which tactical stages chapter 2 runs.
- Real-time text-in-picture issues (the reviews checked only Saturn-side/PC-side pictures).

## 5. Open questions

- Is BG20xx numbering really episode 2? No document asserts it; `TITLE2` is similarly only inferred.
- Why are chapter-2 bodies, FILM and menus/HUD empty in the JSON: no evidence yet, or truly none? Data cannot tell.
- `EVE202` draws `BBG202` on the verified disc-1 tactical path. The [runtime evidence](eve202-tactical-inset.md) covers two window sizes and the entry/exit cuts.
- Chapter-2 evidence: PENDIENTES T29 and T25 show episode 2 was played/booted (EVT02 at `00204000`; disc 1 dialogue and battle), but no row ties that to HD coverage; TH2 is still `open` (row TH2, T25 Spanish notes).
- Does the 0-count `bodies`/`film` for chapter 2 mean the coverage generator needs a chapter-2 observed-resources input like chapters 3-10 in `chapter-sweep.md`?


## Stage 02 tactical portraits

The English disc-1 strict Episode 2 route reads `FACE02.BIN` at
FAD 222327. The complete 76,148-byte file is resident at
`0x002B3800` in the intro, rocket dialogue and nearby snapshots.
Its SHA-256 is
`253500278286bc8a8d6e7c28bdee4d7ee199cc3b48f5b61c18ebab517ada49bb`.

The outer bank has 53 offset/length entries. The populated images
used here have an inner 16-byte offset/length header. Using
`tools/es/red_lz.py`, 41 entries decode to 3,264 bytes, a 64-byte
command header, a 40×48 indexed base, and two 40×16 strips.
The three exact active normal-sprite commands used 8-bit
indexed mode `0x00A0` and color field `0x0580`.
The base index bytes match their decoded bank slots exactly.

| Archived route | FACE02 slot | Command position | Base FNV-1a | PC KAOSLG.SPR subimage |
| --- | ---: | --- | --- | ---: |
| Intro, frame 3600 | 0 | (120,32) | `8D4FA9DE3B4F29EA` | 10 (Ogami) |
| Nearby, frame 600 | 30 | (16,160) | `2555200A223EBE85` | 208 (Kohran) |
| Rocket dialogue, frame 660 | 31 | (16,160) | `6F3107BD0DBE3782` | 209 (Kohran) |

Each archived RGB sample matches all 1,920 pixels of the decoded
base after applying the observed −4 color offset with clipping.
An independent muted 12-frame strict-native replay from the
unmodified rocket-dialogue snapshot matched all 69,120 pixels
inside the 240×288 portrait rectangle in two 2560×1440 native
captures, with zero interpreted blocks. The guest log SHA-256 is
`1a2f9c142b59500b9f2657963df5803f8b8fb706f6b436ea65d268c97c1fdf1d`.

The three corresponding PC faces rank first among the 164 decoded
KAOSLG.SPR bases and match the eye and mouth poses in a side-by-side
comparison. The PC archive SHA-256 is
`cf9a193477a8fa209cb9f5e9bbfd2ff7ed9bd2893e3e279c423147049097db20`.
The SPR indices are content matches. The bytes at the corresponding
offsets in FACE02.DAT alone do not give those SPR indices.

The initial attribution recorded native bank residency and three
observed PC base pairs. The tactical command layout and palette
are outside the existing narrative FCE compositor. Its six
chapter-2 FCE atlas associations remain inferred, and no observed
FCE identity or HD draw is claimed here. The individual tactical
strips, later phases and full chapter parity remain open.

At block close the project measured 65,712,717,705 logical bytes,
with hard links counted once and reparse points excluded, above the
20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.

### FACE02 PC runtime

Patch 0141 uses the top 80×96 crop of the three paired 80×160 PC sheets.
The English disc-1 tactical portrait command, captured byte fingerprint,
fixed position and composed 40×48 native RGB must all match. The composed
pixels must all be owned by VDP1, which keeps other fades, masks and
partially covered portraits native. The three bases are opaque on both
platforms. Kohran's two expressions are complete native base frames with
separate PC counterparts. The runtime decodes the exact PC archive
asynchronously when first matched, keeps only the three crops and draws the
unmodified donor colors at the existing nearest-neighbor integer viewport.
Original, an open menu and disabled HD portraits use the native draw.

The 24-frame muted strict A/B on the MAP04 stack used the same
`intro/native`, `sakura-nearby` and `rocket-dialogue` saves as above. At
pass 2 the async loader was pending and the frame was still identical.
At pass 18, each 2560×1440 capture matched all 69,120 donor RGB pixels inside
its portrait rectangle, with zero differences outside. This covered the
`stage02-hd-ground` layout. All 24 guest hashes matched for each run with
zero interpreted blocks.

| FACE02 slot | Rectangle at 1440p | SHA-256 of matching 24-frame guest logs |
|---|---|---|
| 0 | x1040, y240, 240×288 | `f0293d42d82ff8826d73aae7f097e0009e1b9b01fd6de5a16e68d0e767b7511b` |
| 30 | x416, y1008, 240×288 | `a721171e2d28885a53239a895f520a5ff2ff0d8308423a00335ebfd1f83d832b` |
| 31 | x416, y1008, 240×288 | `30ea4bed296df967110a88b4d2b939af781ce631c643a6094f9fff4d986a5dd5` |

Original, disabled HD portraits and the natural `round-two-kohran` slot 33
at the same position had equal full RGB captures and guest hashes. Slot 33
has native base FNV-1a `02EEF672B849CACB` and uses native rendering. The
900-frame opening suite matched every guest hash and all three 1440p
screenshots, with zero interpreted blocks. Opening hash-log SHA-256 is
`3e0d0f59d0344ea51c62fd2a3c15311d7f8929e2b59b01a66c65cc83474737dd`.
These three poses are the runtime coverage. Other commands and Chapter 2
narrative FCE rows retain their prior coverage status.

At this block close the project measured 63,457,660,640 logical bytes,
above the 20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.

## Traced attribution (TH2 pass 2)

Tool: `tools/chapter_loads.py` (every `Play Disc` command mapped to its ISO file, a state every 500 frames). Route: English disc 1, the 28,491-frame continuous Episode 2 File 1 movie (`local/work/t30-chapter2-followup/continuous-to-kohran`), strict native, zero interpreted blocks. Its frame hashes match the reference file byte for byte (SHA-256 `12cae74f096b5a5bff308994efce70ec40cef1525e9de663686e256903d136cf`); backup SHA-256 `4c22bf1e...`, movie `8b5539f3...`.

| Resource | Class | FAD | Frame (est.) | Checkpoint state SHA-256 (prefix) |
| --- | --- | ---: | ---: | --- |
| `SAKURA2/EVE202.BIN` | scene | 221148 | 7059 | `3b81dc4b` (state 7499) |
| `SAKURA2/EVE002.BIN` | scene | 221023 | 10724 | `85e1d10b` (state 10999) |
| `SAKURA2/MAP02.BIN` | map | 231973 | 6670 | `0780a726` (state 6999) |
| `SAKURA2/UNIT02.BIN` | unit | 252153 | 6865 | `0780a726` |
| `SAKURA2/FACE02.BIN` | portrait bank | 222327 | 6865 | `0780a726` |
| `SAKURA2/WKL02.BIN` | menu/HUD | 252927 | 6670 | `0780a726` |

Result: 1 row moved from `unassigned` to chapter 2 (`WKL02.BIN`, menus-hud, status unknown); the other five were already chapter 2. Four random-input continuations from the last state (24,000 frames each) only restarted stage 2 (same EVT02/MAP02/UNIT02 reloads) and added no scene, body, portrait or film. `LIPS_CG.BIN` is read during the stage but is a shared tactical file and is not attributed. The route draws no NC body, no `02xxFCE` atlas and no FILM clip, so `0201FCE`..`0206FCE` stay inferred. The unit files `N0xx/H0xx/K0xx` are not register categories.

Blocker: the chapter's story after the stage-2 victory needs a state or save at the end of the battle (or a full winning play). Without it NC bodies, BG scenes, `02xxFCE` and FILM clips cannot be attributed.

## Verified WKL02 command submenus

Patch 0244 uses the PC `SAKURA2/SYSTEM/SLGSYS02.SPR` images 2 and 4
for the two visible vertical command shells in the natural English MAP02
battle. The exact VDP1 texture bytes occur in the attributed
`SAKURA2/WKL02.BIN` at offsets `0x3A3C0` and `0x3AC80` respectively.
Their native sizes are 40 × 48 and 40 × 80. The PC images are twice that
size on each axis. The runtime pins the PC file, both native textures,
their native LUT, and the observed mixed sprite scanout at a −4 RGB
offset. Unsupported palettes and composition states use Saturn pixels.

At 2560 × 1440, seven profiles each repeated 72 strict guest fields
with identical final SRAM in the Cancel and Advice menu checkpoints.
Only Enhanced with the exact donor drew the new shells. Four sampled
fields per case change 17,451 pixels for Cancel and 40,788 pixels for
Advice. Every change matches the independently decoded PC pixel after
the native color offset, replaces a matching native texture pixel, and
stays in the exact command rectangle. The localized labels, selection
highlight, units, cursor, terrain and grid retain their sampled native
pixels. Original and the missing, corrupt and disabled donor controls
match their respective references.

The horizontal frame shapes and remaining WKL02 content stay native.
The two new PC subimages are tactical HUD components and outside the
measured SAKURA1 menu inventory. Package inclusion remains open. The
private states, A/B captures and exact receipt are in
`local/work/codex-th1/thd22-wkl02`.

### Horizontal WKL02 frame witnesses

Two more PC donors align at 2× with native horizontal frames
on the recorded MAP02 command routes.

| Native WKL02 offset | Native size | Texture FNV-1a | PC SLGSYS02 ordinal | Opaque mask IoU |
| --- | --- | --- | ---: | ---: |
| 0x39640 | 96 × 32 | 18FDBFE27D4349D5 | 0 | 0.9989 |
| 0x39C40 | 120 × 32 | 0D7B8C2AB0FB6C5E | 1 | 0.9817 |

The comparison uses the full 2× Saturn mask and removes the
PC cyan key. The two frames use CMDPMOD 0x0088 and the same FFEC LUT as the
verified vertical frames. The 96-pixel frame appears in 15 retained
states and the 120-pixel frame in three. Each active VDP1 list also
draws either Cancel or Advice, after the horizontal frame.
The 120-pixel cases include kohran-end-order, purple-end-menu
and round-two-kohran-end. The related captures and inputs are in
the local Chapter 2 follow-up archive.

The current item-card capture keeps one command frame and its
ownership mask. Registering the horizontal rows alone would
leave the later vertical frame as the selected replacement.
The 120-pixel frame also exceeds the current 112-pixel mask
stride. The next runtime change needs separately bounded masks
for both frames and must record coverage by later commands.
Verify a case of each width with its submenu visible,
preserving labels, highlight and cursor in all comparisons.
The two horizontal rows are paired candidates and remain native.
