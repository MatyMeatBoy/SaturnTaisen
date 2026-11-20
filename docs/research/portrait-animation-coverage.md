# HD portrait and animation coverage

The audit compares the Saturn and PC atlases against the prepared HD pack. It can also reconstruct the portrait described by local states' VDP1 commands and compare it against native 320 × 224 captures. It reads inputs in place and writes reports to a new directory under `local/work`.

```powershell
python tools/audit_portrait_coverage.py --states local/work/sakura
python -m unittest discover -s tests -p test_portrait_coverage.py
```

Use `--output` with a different directory to repeat the run. Other inputs can be specified with `--project`, `--pack`, and `--disc` repeated per disc. `portrait-coverage.csv` is used to filter identities by chapter, state, or region. `portrait-coverage.json` adds the source FCEs, scores, alpha measurements, and comparisons against states and captures.

## Catalog coverage

The auditor compared the project's 304 40 × 80 Saturn atlases against the FCEs on both discs and verified the 394 80 × 160 PC atlases via SHA-256, with continuous indices from 0 to 393. It also verified the original KAO file. In the pack, it validated the binary catalog and the FNV hashes of the 382 PNG variants. When comparing their RGBA pixels against those regenerated at 1x and 2x density, the 382 variants matched. None has a pixel with partial or zero alpha where Saturn requires opacity.

Chapter 1 covers the union of identities found across the six FCEs `0100`, `0101`, `0102`, `0103`, `0108`, and `0109` on both discs.

| Scope | Saturn | HD base | HD eyes | HD mouth | Both HD strips available | PNGs verified | Pending |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Catalog | 304 | 191 | 191 | 191 | 191 | 382 | 113 |
| Chapter 1 | 123 | 81 | 81 | 81 | 81 | 162 | 42 |

Each valid atlas has 48 base rows and two 16-row strips. The "both strips" column confirms their availability in the PNGs. Their simultaneous drawing depends on the game's commands and the displayed frame. The `nearest_strip_rows` field measures the distance between color indices per placement row and serves as a hypothesis about each strip's destination.

The 191 automatic pairings respect `PC index = Saturn ID - 1`. Among the pending ones, the top visual candidate by ranking respects that rule in 102 of 113 rows, including 38 of the 42 in chapter 1. In chapter 1, the four pending entries with a different candidate are `004f`, `00ef`, `013b`, and `013c`. No pending entry got a zero distance. The index provides an additional signal for reviewing each portrait across its three regions.

Chapter 1 pending ranges in hexadecimal

```text
0013-0014 001d 0040-0041 0044-0045 0049-004a 004f 005b 0064
006b 006d-006e 007f 0088 0091-0096 0098 009b-009c 009e 00a1
00c0 00c2-00c3 00c5 00ee-00f0 00f2 00f4 013a-013c 013f 0169
```

## Saved states and Yoneda's portrait

Among the 160 available states, 79 had a portrait command at the expected position and used the expected palette. 63 unique matches were obtained against the HD catalog and 16 had no match. The 16 unmatched cases had an exact Saturn identity among the pending ones. Six states were captured with one active strip and none with two. The states `maria-face-discovery.state` and `maria-exit.state` show, respectively, the eyes and mouth of `0176` at the same relative row 16 at different moments.

Yoneda's civilian expressions `00e2–00e7` have both HD PNGs complete. Both strips of each Saturn atlas have their minimum distance at relative row 8. The eyes command of `00e2` confirms that row in `office-return-6000.state`.

| Sample | Saved command | Comparison with the capture |
| --- | --- | --- |
| `office-return-3000.state` | Base `00e3` | The 1,920 pixels match the Saturn palette colors. |
| `office-return-6000.state` | Base `00e2` and eyes at row 8, an HD match | 1,901 pixels differ from the unblended base and 1,904 from the composite of the saved commands. The 1,920 pixels match when blending the base without the eyes strip toward white. |

The 6000 sample exactly satisfies `(base_channel * 27 + 248 * 5) >> 5` per channel, with RGB555 white expanded to 248. The state describes the pending VDP1 commands. The capture shows the base portrait under blending, consistent with an offset between the saved commands and the presented image. The `PortraitPixelsVisible` guard requires equality with the unblended Saturn color and would therefore reject that portrait. The atlas, palette, and byte-level recognizer did pass the checks against the saved commands.

The report includes 42 capture/state pairs. In 36 pairs, the base matches the capture unblended. Three show exact blending toward white with weights 5, 15, and 25 over 32. The remaining three require more evidence to explain their differences. The audit validates these saved frames and atlas availability. The frequency of these dropouts during a continuous run is outside this sample.

## FCE atlas attribution (TP6)

`audit_portrait_coverage.py` now writes `fce_atlases` (per `disc:file`, the identities each FCE holds) and `hd_chapter_coverage.py` uses it for the atlas-file rows of `portraits`. In the initial 112-atlas snapshot, 16 held only identities in `config/hd-portrait-recipe.json` (`hd`), 4 are empty 160-byte atlases (`excluded`), and 92 also hold `0169` (four also `00a1`), the only two identities outside the runtime recipe, so they stay `unknown` with the `uncovered` list. The 302 identities are `hd`; `00a1` (strips swapped, T45) and `0169` (different PC card design) remain T52.


## Residual portraits 00a1 and 0169

The stock 40×80 atlases agree byte-for-byte across the two prepared
discs. `00a1` occurs in `0102FCE` and `0700FCE` on each disc, and
`0169` occurs in 46 atlases per disc. Their whole-atlas FNV-1a
fingerprints are `12CC7FF05270E3C5` and `7D561BC49817D46E`.

**00a1.** The base is the same Iris expression as KAO.SPR subimage 160,
which ranks first out of 394 PC bases with the decoded native palette
`B20B13D34869E11A`. Holding the base fixed and exchanging the two
32-row PC strips reduces their RGB RMSE from 47.93 to 31.06 and from
48.07 to 33.57 on the 40×80 Saturn grid. The prepared alpha at both 1×
and 2× exactly matches the Saturn mask. Both native strips independently
best match the region starting at base row 16. The archive review
checked 438 candidate state files and found no exact active `00a1` portrait
command. The coverage register records the pairing. The swapped
strips still need a scene that exercises each of the two commands.

**0169.** The Saturn portrait shows the troupe emblem. The two
40×16 strips both equal the base region at row 16 exactly. In three
archived states, an active strip starts at row 16 and matches both
native strip payloads, so those commands reference the unchanged
base region. KAO.SPR indices 348 and 360 have the same PC base,
also identical to KAO_P.SPR subimage 24. These alternatives use the
same emblem motif with different proportions and framing. Their PC
strip data differs from the static native region. The register records
the examined PC candidates and retains Saturn artwork.

At this stage both portraits were outside the runtime recipe. The
[chapter 1 closure](#chapter-1-portrait-closure) applies the later decisions.

The measured workspace was 60,240,718,418 logical bytes with hard
links counted once and reparse points excluded, above the 20 GB cap.
The delivered development ZIP remains 6,315,009,692 bytes.


## Chapter 1 portrait closure

The reviewed recipe now prepares Iris `00a1` from KAO.SPR index 160.
It exchanges the two 32-row PC strips before applying the Saturn
alpha mask. The PC base and the native coordinates stay fixed.
At both integer densities the review pins the expected RGBA after
the reorder. The preparer also checks the original Saturn bytes and
the source KAO archive. An identity that fails its content check
retains the native portrait.

The production preparer produced 303 identities. All 604 PNG
variants for the previous 302 were byte-identical to the baseline.
The existing pack auditor checked the final 606 variants against
both discs and the 394 PC sheets, with zero validation errors.
The runtime matcher selects the 00a1 base and its two independent
row-16 strips uniquely across all 304 native atlas payloads.

Three test fixtures take the exact 00a1 index bytes and place them
in existing saved portrait-command slots. An unchanged development
runtime draws the base and, in the other two fixtures, each strip
at row 16. All 69,120 pixels in each 240×288 portrait rectangle
match the expected prepared composition at 2560×1440. Guest
hashes match with the pack enabled and disabled throughout the
40-frame base and two 12-frame strip replays. Early Enhanced
captures show each strip active, with every changed pixel confined
to the verified portrait rectangle. The strip controls in Original
match in RGB with the pack present and absent, and
each run reports zero interpreted blocks. These fixtures verify
the three draw paths. The later [natural Command Room replay](#iris-00a1-command-room-portrait) covers all three.

The owner decision keeps the Saturn emblem `0169` by design.
There are 303 HD identities and one native choice. Coverage now
closes the six chapter-1 FCE atlas entries. Across both discs,
108 nonempty atlas entries contain prepared identities and any
explicit native choices. The four empty atlas entries remain
excluded. No release package was built.

At block close the workspace measured 62,111,789,211 logical bytes
with hard links counted once and reparse points excluded, above the
20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.


## Maria 0176 natural strip verification

English disc 1 Chapter 1, portrait `0176`, uses KAO.SPR index 373
without shifts. The native 3,200-byte atlas SHA-256 is
`08c2c9ce28ebb6724451b1cc21f57a3d23485f7b6d8f56fa0c5c35ade784f61d`.
The prepared 80×160 RGBA SHA-256 is
`0e04080f34ba658e2d977bd3fc2a5017686b93dbfc0644cafeb684bbd0c1bad8`.

The original, unmodified `maria-face-discovery.state` and
`maria-exit.state` each contain one active 40×16 VDP1 strip at
relative row 16. Their payloads match the first and second
strip, respectively. For each state the muted 2560×1440 replay
used the same development executable, with one exact portrait
record installed or absent. The two Original profiles provide
the asset-present and asset-absent control. All four profiles
agree in every guest hash over 12 frames and report zero
interpreted blocks.

| State | Runtime selection | Enhanced difference bounds (exclusive) | Guest log SHA-256 |
| --- | --- | --- | --- |
| `maria-face-discovery.state` | `0176`, density 2, patch 1, y=16 | (404,1011)–(644,1299) | `e215c715237682017299a6b5a673c60c824d5539a22661b939b71adee25e6184` |
| `maria-exit.state` | `0176`, density 2, patch 2, y=16 | (428,996)–(668,1284) | `c7e263e461d5c9b14f0e31bba2a8b7dbff3c3fc51c5e33503c2d2b4f0de575c2` |

All 69,120 RGB pixels inside each bound equal the expected
prepared base and active strip, expanded by the integer scale.
Enhanced differences are confined to that rectangle. Original
RGB matches with the portrait asset present and absent in both
capture frames. The two strips appeared in different scenes
on these routes. The chapter register adds verification to
this occurrence without expanding the claim to other portraits.

The T45 Iris route remains separate. The English Chapter 1
`0102.BIN` selects `00a1` at file offset `0x2DEE` and then
requests table record 10312 in the underground Command Room.
The [natural Command Room replay](#iris-00a1-command-room-portrait) later reached that branch.

At block close the project measured 63,129,173,134 logical bytes
with hard links counted once and reparse points excluded, above the
20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.


## Yoneda 00e9 storage portrait

The English disc-2 Chapter 9 natural storage briefing ends with
the exact `00e9` VDP1 base and no active strip. The archived
`chapter9-after-storage/terminal.state` is unchanged, SHA-256
`946f5869b4f17c4cd746bb06eeb0f6bb66ad80282db3c965ef03729b0b55cbfa`.
The prepared atlas is KAO.SPR index 232. Its native atlas SHA-256 is
`2b4e014a32b4ed8c1165d8754c61e50bdd47743ef01503e7909bf18958db281b`,
and the prepared 2× RGBA hash is
`da69e3b1378b05773b2f1fd2973d81e399c4ec1b77db6bef7070ed05fdb04c1e`.

The same muted development runtime replayed 12 strict-native frames
with the one-portrait pack present and absent, in Enhanced and
Original. All four guest logs match, SHA-256
`27935605ffd961da7321963025b8480b189c9cf5542824ff21701210cd200275`.
All runs reported zero interpreted blocks. At 2560×1440 the runtime
logged `00E9 density=2 patch=0 y=0`. Enhanced changes only the
portrait rectangle (404,1090)–(644,1378), and all 69,120 RGB pixels
in the rectangle equal the prepared base. Original RGB matches
at both sampled frames. The register marks this Chapter 9 base
occurrence only. Its Chapter 1 occurrence and both animation
strips stay outside this verification scope.

The bounded Iris Command Room investigation replayed the
unmodified `prebattle-3000` state with normal A inputs. The trace
reached English record 10261 before the wall-clock limit, short
of the 10312 selector for `00a1`. The [later relay](#iris-00a1-command-room-portrait) verified both strips.

At block close the project measured 63,922,050,823 logical bytes
after removing the duplicate trial pack. The delivered development
ZIP remains 6,315,009,692 bytes.


## Iris 00a1 Command Room portrait

The English disc-1 route resumed the unmodified `prebattle-3000.state`.
Seven short segments advanced the dialogue through (10252, 10260, 10268,
10300, 10307) to 10312, with 420, 650, 720, 630, 800, 535 and 340 guest
frames respectively. The first segment used ordinary A presses every
45 frames from frame 20 and the subsequent segments used A every
25 frames from frame 15, with a six-frame hold. The last checkpoint,
`route06/f337.state`, has SHA-256
`57e7ba5a9ef7dd468b73d634f02413db7d6c6ef466f872d86cc78f495fe9f5c8`.
Its `0102TBL` cursor at `0x0606851C` holds `0x00229FFA`.
The associated LIPS cursor at `0x060685B4` starts at `0x00206E60`.
The complete English `0102FCE.BIN` is resident at `0x00251000` in the
three sampled snapshots. Its SHA-256 is
`a92e1f3e10355f51c2d54061df38a5688502133d5d0fc3ba9522e1edcfed6992`.

With no further input, frame 8 has the exact 40×48 `00a1` base
(FNV-1a `F9026B5B4506D108`). Frames 33 and 36 each add the exact
40×16 native strip at row 16 in order 1 then 2. The prepared 2× atlas
uses PC `KAO.SPR` index 160 with the strips exchanged. Its SHA-256 is
`8c5ca642b8e8f2b1bfbd0bc845b0ce83b93fd134325f8e559f5bcaf997217c3f`.

The patch 0141 executable replayed each unmodified snapshot for 12 muted,
strict-native guest frames with the portrait pack present and absent in
Enhanced and Original. The bundled `KABE00` background selected the
normal narrative layout. At pass 2, the runtime picked patch 0, 1 and 2
respectively. Each 2560×1440 Enhanced capture matches all 69,120 expected
prepared pixels in the rectangle (404,1090) to (644,1378) and has zero
differences outside it. Strip 2 carries the measured VDP2 white mix of
3/32 toward RGB555 white (248), applied to the prepared pixels.
The Original captures match in full, all four guest logs match per
snapshot, and every run reports zero interpreted blocks.

| Native activation | Local snapshot | Snapshot SHA-256 | 12-frame guest log SHA-256 |
|---|---|---|---|
| Base | `lip-8/f8.state` | `2aeed5f460bd57c59de6930f6c247bda6f22122cf29fc9d90de07d0921916621` | `16aa6a0d8914f184607a2bce917ac09e073679021f7fd0716296a6a2918fbc8a` |
| Strip 1 | `lip-33/f33.state` | `7632ddb1b5dc80bff9db19d45fc108764640f1f5f9e8d402ab34724f8f241c31` | `e23dd64b711f81bd17e0210d3b2c19b01fc5c7fc91dae6bcc1915267ed46f061` |
| Strip 2 | `lip-36/f36.state` | `977294ba87417194020e48d88ebd82f7ece276fe3e129fc42c490f6715a9fca6` | `c50ee5c18668af88cf867c2fffaa412221615e81c295884fc5caa311e87a6136` |

The Chapter 1 occurrence has verified HD draws and the atlas file has
resident status. Chapter 7, disc-2 playback and full Chapter 1 parity
remain outside this sample. The inputs, snapshots, captures and logs
are in the ignored `local/work/codex-tp3c/t45-natural-iris` folder.

At block close the project measured 64,374,989,543 logical bytes, above
the 20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.
