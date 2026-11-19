# Saturn `BG*.BIN` format and BG pairing by file number (T67)

Solved 2026-11-19 by looking at the data instead of tracing the loader: the earlier probes (`pc-asset-census.md`) looked at the whole file as one bitmap and at the wrong offsets.

## Format

| Offset | Content |
| --- | --- |
| `0x0000` | header, 0x50 bytes; starts `00 01 00 01`, the rest is zero |
| `0x0050` | 288x144 picture, 8 bpp, as 36x18 cells of 8x8 pixels (64 bytes per cell, row-major cell order) |
| `0xA250` | palette: 256 big-endian RGB555 words (Saturn layout, bits 0-4 R, 5-9 G, 10-14 B) |
| `0xA450` | trailing data, not needed to draw; 45,120-byte files are zero padded to the end |

687 of the 726 `BG*` files on disc 1 are exactly 45,120 bytes and decode this way (`tools/decode_saturn_bg.py`).

**Variant B** (header `00 01 00 02`, 26 files such as BG1207 and BG2207, sizes 92,192 / 79,952 / ...): cells wide and cells high are the two big-endian u16 at 0x04 and 0x06 (BG1207 is 64x18 cells = 512x144, a wide scrolling scene), the palette comes first (256 words at 0x10) and the picture starts at 0x210. The decoder handles both, 713 of 726 files in total; the 13 left are the mini-game backgrounds (`BGHANA`, `BGSLOT`, ... start with a palette) and `BG2338`. `SAKURA1/BG1001.BIN` renders as the theatre lobby, matching the PC picture. `tests/test_saturn_bg_decode.py` covers the layout synthetically.

**Variant C** (disc 2 `SAKURA2/BBG*.BIN`, 23 battle backgrounds): a table of big-endian (offset, size) pairs at 0x00: the unique 8x8 tiles at 0x18, a map of 1296 bytes (36x18 cells) or 2240 bytes (40x28 cells) and a 512-byte palette. Each map word is 2 x the tile number (VDP2 pattern names for 8 bpp cells); tile 0 is unused. All 23 decode (BBG300 is a plain blue gradient). Disc 2's `SAKURA1/BG*` files are the same 726 files as disc 1's.

Decoder coverage: 736 pictures (713 on disc 1, 23 on disc 2). Undecoded: the 8 mini-game backgrounds, BG2290, BG2338, BG2518, BG2533 and BG4372.

## Mass pairing routine

`tools/match_hd_all.py` replaces the screenshot work for BG: one command decodes every Saturn picture of both discs, pairs it with the PC picture of the same file number and scores the content (parallel, about two minutes for both discs). Result in `config/hd-scene-bg-map.json`: 736 decoded, 475 tier `content`, 256 tier `number`, 5 without a PC picture. Same-number PC files for the `BBG` set are `SAKURA2/BG/BBGnnn.SPR`.

## Pairing with the PC pictures

`BGnnnn.BIN` and the PC `BGnnnn.SPR` share the file number. This held for all 12 pairs confirmed by eye in `config/hd-scene-bg-pairs.json`, and 460 of the 687 Saturn pictures also have the same-number PC picture as their best content match (`tools/match_bg_files.py`: 48x24 luminance signature, Saturn 288x144 against the PC 576x320 top and bottom 288 rows).

(Earlier, `tools/build_bg_map.py` wrote the first map for disc 1 variant A only: 680 pairs, 542 with tier `content` (same number is the best content match or scores <= 0.10) and 138 with tier `number` (same number only; another crop, lighting or palette variant, so it needs an eye check or runtime evidence before being drawn), 7 Saturn files without a same-number PC file; superseded by the mass routine above.) Each pair carries `cells_sha256`, the SHA-256 of the 41,472 picture bytes, which is the key T74 needs to recognise the native picture at runtime (the game copies those cells to VDP2). 20 cell hashes occur twice (identical Saturn pictures under two numbers): the runtime must treat a duplicate key as ambiguous unless both numbers map to the same PC picture.

## What this does not claim

- Visually confirmed pairs are still the 12 of `hd-scene-bg-pairs.json`; the rest is number + content evidence, not an eye check, and nothing is integrated: T74 (the runtime consumer) is open and needs a runtime build (see T95).
- The 13 undecoded files are not in the pair map; the 256 `number`-tier pairs (other crop, lighting or palette variants, or wide variant-B pictures whose PC picture has a different size) have not been checked by eye.
- `NC*.BIN` (T67's other half) is not decoded; this method (look at the data per hypothesis) is the next thing to try there.

## Runtime use (T74, patch0059)

The palette the game loads into colour RAM for a scene picture is the palette stored in its BIN (variant A: 256 words at 0xA250), so `Renderer::BackgroundPaletteFingerprint(layer)` (FNV-1a 64 over those words) identifies it: picture layer 2 or 4 of the presentation frame. 687 of the 740 palettes are unique. `tools/gen_scene_bg_table.py` turns the `content` pairs into `port/scene_bg_table.h` (447 entries) and the runtime draws the PC picture under the native overlays. The PC picture is the whole composition (576x320) stretched onto the 288x144 rectangle; an earlier crop-based comparison was wrong and gave misleadingly high scores.

## Full-screen pictures with the palette first (T96, partly decoded)

`IC01..16.BIN` (eyecatches), `OMAKE01..06.BIN`, `LOAD.BIN`, `KABE00..19.BIN` and `TITLE*.SD2` (76,672 bytes; TITLE 76,736 / 115,248) start with a 512-byte RGB555 palette (big-endian words), then a 2,240-byte table (u16 entries 0, 2, 4, ... = 2 x cell number, 40x28 entries), then 8x8 8 bpp cells. Drawing the cells after the table in plain row-major order, 40 cells wide, gives the right 320x224 picture (IC01 is the Sakura Wars eyecatch with Sakura on the left) except for a band at the right edge, so the table is not an identity map there: use it to place the cells. Not integrated: the pictures are not paired with the PC `ICATCH`, `TITLE`, `ENDING` and `CG` files yet, and the KABE backgrounds already have their own HD path. `ITEM*.BIN` (13,056 bytes, palette first), `FUKA`/`TMAP` (71,680 bytes, 320x224 at 8 bpp) and `NC*.BIN` (147 files on each side, the same count as the PC `NC` folder) follow other layouts.
