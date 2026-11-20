# Tactical ground table (TW6b)

One table now decides which of the 27 Saturn tactical maps draws a PC ground, instead of one hand-written entry and one patch per map. Data is names, sizes, hashes and statuses; no pixel is stored.

- Data: `config/hd-tactical-ground-table.json` (26 rows; the disc 1 and disc 2 `MAP01.BIN` are one row).
- Generator and tests: `tools/gen_tactical_ground_table.py`, `tests/test_gen_tactical_ground_table.py`, `tests/test_tactical_ground_table.cpp`.
- Runtime: patch 0253 adds `port/tactical_ground_table.inc` (generated, 12 rows) and makes `tactical_ground::Find` search it after the eleven hand-written grounds (MAP01, 02, 04, 05, 06, 12 to 16, 21). Nothing else in the renderer or the frontend changes: the compositor, the sampler, the camera maths, the colour offset rules and the placement assembler of patches 0102, 0138, 0139, 0140 and 0153 serve every row.

## The key comes from the BIN

The runtime keys a ground by the FNV-1a of the first 8,192 pattern-name bytes of VDP2 source 4 at page `0x40000`. That page is built by the game from the identical `MAPnn.BIN` (PC and Saturn files match by SHA-256), so the signature can be computed without running the game:

| Part | Where in the BIN |
| --- | --- |
| slot table | 16 big-endian (offset, size) pairs at byte 0 (slot 0 is empty) |
| character base | slot 1 is the first layer's cells; its size / 32 is the character number where the ground cells start |
| names | slot 5, 128 x 128 big-endian 16-bit names |
| page word | `0x00600000 + name + base`, the 64 columns x 32 rows at the top left, four bytes each, big-endian |

The formula reproduces seven of the eight signatures recorded from live runs, with no disc run involved: MAP01 `1CAF3218B4B0F9F0`, MAP02 `25FF56EB6965E424`, MAP04 `451ACDDB5522070E`, MAP05 `A18A5122F7C18729`, MAP06 `B533F608A5E864D1`, and the two live reviews MAP10 `E364F3D731C3D6DE` and MAP19 `FA30687F240C0BEB` (`tactical-pairing.md`). MAP21 does not follow it (its layout is its own) and keeps the recorded signature. A derived signature that never matches in game leaves the map native, because the compositor also checks the page, the PC file size and hash, and the sampler bounds. A wrong key cannot draw a wrong ground.

## Result

| Status | Maps | Count |
| --- | --- | ---: |
| `hd` (hand-written entries, witnessed) | MAP01 (both discs), 02, 04, 05, 06, 12, 13, 14, 15, 16, 21 | 11 |
| `wired-unverified` (patch 0253) | single image: MAP07, 08, 09, 11, 17, 18, 22, 24, 25, 26; tile grids: MAP03 (626 tiles of 64 x 64), MAP20 (96 tiles of 128 x 128) | 12 |
| native by review | MAP10, MAP19 (composition differs from the Saturn drawing, see `tactical-pairing.md`) | 2 |
| needs an assembler | MAP23 | 1 |

MAP03 and MAP20 reuse the placement assembler MAP04 and MAP05 already have (`placementTileSize` 64 and 128, 2,048 x 2,048 plane, 1,024 x 1,024 world). The generator accepts a tile grid only when the SPR placement table fits that square plane exactly. `MAP23_A.SPR` holds four 1,392 x 1,232 images, which are alternatives rather than tiles of one plane (the Saturn name table is 128 cells wide, 1,024 pixels, narrower than one image), so a scene has to choose one image before a sampler can use it; the assembler draws one square tile size only.

## What is verified and what is not

Verified offline: the 12 generated rows load through the real `tactical_ground::Load` (file size, SHA-based asset hash, image count and size, assembler) with the owner's PC files, and every signature is unique across the 23 entries. The build of the stack plus patch 0253 (own copy of the tree and build, `local/build/rebuild-maps`) matches the previous build (stack through patch 0184) in all 200 per-frame guest hashes of each of four saved combat states, Enhanced presentation, strict native, `interpreted 0`: the MAP02 Kohran turn and enemy turn, and two Chapter 1 states (the MAP01 victory follow-up and its west dialogue). The table is host-only, so guest state cannot change. The new signatures are present in the linked executable.

Not verified: no map of the 12 has been seen drawn in game. Their status is `wired-unverified`, never `hd`. The 10 single-image grounds and the two tile grids assume the same one-to-one world grid as MAP02, MAP04, MAP05 and MAP06, which the live reviews of MAP10 and MAP19 show is not true for every map. Each map needs its witness: a state at the battle, a fixed-camera capture at 1440p, and a pixel comparison with the independent PC decode, as in `map02-pc-ground.md` and `map04-pc-ground.md`. These replays do not draw any of the 17 new maps (none has a retained state), so they prove that nothing regressed, not that a new ground draws. Strict AOT of the maps that stop at untranslated overlay blocks, camera travel and the package are also open.

## Regenerate

```powershell
python tools/gen_tactical_ground_table.py --derive --pc <folder with SAKURA2/MAP> --iso1 "local/prepared/disc1/Track 01.iso" --iso2 "local/prepared/disc2/Track 01.iso" --inc <sdk>/port/tactical_ground_table.inc
python tools/gen_tactical_ground_table.py --check
python -m unittest tests.test_gen_tactical_ground_table
python tools/check_patch_stack.py
```

`--check` needs no game data: it compares the table with `config/hd-tactical-map-pairs.json` and with the `.inc` carried by patch 0253. A new witnessed map moves its status in `config/hd-tactical-ground-table.json` and in `tools/hd_chapter_coverage.py` together.
