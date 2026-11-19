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

## Full-screen pictures with the palette first (T96, variant D)

`IC*.BIN` (16 eyecatches), `OMAKE*.BIN`, `LOAD*.BIN` and `KABE*.BIN` (76,672 bytes) are 320x224 pictures: 256 big-endian RGB555 palette words, then a table of 40x28 big-endian **u32** entries (2 x cell number; 4,480 bytes), then 8x8 8 bpp cells (71,680 bytes = 1,120 cells). The tables seen so far are the identity map; the decoder uses them to place the cells anyway. `IC01` is the Sakura Wars eyecatch with Sakura on the left. `TITLE1..10.BIN` (76,736 bytes) are the same layout with the table starting at 2 and one more cell in the file; all ten decode. They are the episode title cards: `TITLE1` reads "Episode 1: The Capital's Floral Assault Troop!" in pink lettering with a white outline over blue sky and blossoms, 320x224, with the English text already painted in (the PC `TITLE*.SPR` carry the Japanese text, so they cannot replace these). `TITLE.SD2` (115,248 bytes) is something else (signed small values, not a picture).

`tools/match_hd_screens.py` pairs them with the PC pictures by content (names differ: `IC01.BIN` is `IC0100.SPR`): `config/hd-screen-map.json` has 16 firm pairs, all the `IC` eyecatches against `SAKURA1/ICATCH` (correlation 0.989 to 0.999, the runner-up 0.06 to 0.41 lower), and 8 candidates that need an eye check (`LOAD.BIN` 0.835 against `ICATCH/LOAD.SPR` with `SYSTEM/NOWLOAD.SPR` at 0.825, `OMAKE11-13` against `WALL/OMAKE2`, `SIS_BG3`, `OMAKE3` at about 0.72, and `LOAD01`, `OMAKE01-03` with no convincing PC picture). Not integrated: no runtime consumer yet; the eyecatches are the episode cards of T87, which the owner wants widened to 16:9, so the consumer has to settle the framing first. `ITEM*.BIN` (13,056 bytes, palette first), `FUKA`/`TMAP` (71,680 bytes) and `NC*.BIN` (147 files on each side) follow other layouts.

## `NC*.BIN` large characters (T67/T19, structure only)

Observed on `SAKURA1/NC10.BIN` (104,528 bytes; 147 `NC` files on each side, the same count as the PC `NC` folder, whose `NC10.SPR` holds 94 pictures: one 326x320 body and many 148x99 parts). Header `00 02` and 14 zero bytes; from 0x10 a list of short records that start with 0x3C or 0x3D followed by u16 values (looks like part rectangles: x, y, width, height style numbers below 0x100); a zero gap at 0x26C-0x410; a 256-word RGB555 big-endian **palette at 0x410**; then the image data, which has zero gaps of 280-360 bytes about every 1,792 bytes (0x700) further on, so it is stored in strips or parts, not as one bitmap. Not decoded: the record layout and the strip format. Next step: dump the VDP1 commands of a dialogue with a body on screen (the bodies are VDP1 sprites, like the portraits) and match the texture bytes against this data to learn the part sizes and the colour depth; the runtime recogniser would then work like the portrait pack.

## Event pictures `EVE*` and `WALL1` (T96)

Scanning every file of both discs with the decoders also reads `SAKURA2/EVE*.BIN` (9 files on disc 1, 3 on disc 2, 288x144; same offset/size table as the `BBG` variant), `SAKURA1/WALL1.BIN` (320x224) and one `K` and one `S` file. Compared with the PC pictures (normalised correlation of the grey signature), the `EVE` pictures do not match `ENDING` but the PC `SAKURA2/BG/BBG*.SPR` set: `EVE207` with `BBG207` 0.999 (runner-up 0.61), `EVE202` with `BBG202` 0.895 (0.44), `EVE205` with `BBG205` 0.915 (0.77), `EVE102` with `BBG102` 0.807 (0.58), `EVE002` with `BBG002` 0.824 (0.74); `EVE0116` and `EVE0118` point at `BBG201` and `BBG101` with less margin and `EVE0101` and `EVE105` have no convincing match. `WALL1.BIN` is `WALL/KABE0100.SPR` (0.996). These are candidates for an eye check, not pairs: the numbers do not follow the BG rule and nothing is in the pair map. The `ENDING` and `CG` pictures of the PC have no decodable Saturn counterpart yet (the mini-game `HANA*`/`MINI*` files in `SAKURA3` are `.GCG` and `.BIN` of 220-740 KB in a different format).

## Item pictures `ITEMnn.BIN` (T23/T54)

80 files of 13,056 bytes on disc 1: a 256-word RGB555 big-endian palette, then a 112x112 picture at 8 bpp, line by line; palette index 0 is the transparent key (cyan on screen). `ITEM01` is a framed photograph of Sakura. `tools/match_hd_items.py` decodes them and pairs each with the best of the 112 pictures of the PC `SAKURA1/ITEM/*.SPR` by normalised correlation of a 32x32 grey signature (both on mid-grey; the PC pictures are bigger and have another aspect): `config/hd-item-map.json` has 12 firm pairs and 68 candidates. Looking at the first forty by eye, the eight that have a same-number PC file (`ITEM01`, `02`, `04`, `06`, `08`, `10`, `11` and its neighbours) are the same object with a similar frame; the other PC names (`BURO*`, `ITEMICON`, `BUROICON`) are not number-matched. Not integrated: items are VDP1 sprites in the menus, so a runtime consumer would work like the portrait pack (match the sprite's texture bytes), not like the scene pictures.

### `NC*.BIN` update: the strips are eye animation frames (2026-11-19)

Reading the data after the palette of `SAKURA1/NC10.BIN` (palette at 0x410, data from 0x610) as consecutive 56x32 blocks of 8 bits per pixel (1,792 bytes each, palette index 0 transparent) shows Sakura's **eye animation frames** (open, half-open, closed, looking aside) from about the fifteenth block on; each block ends with a run of zero (transparent) bytes of 280 bytes or more, which is the zero gap seen every 1,792 bytes. The first blocks do not line up on that grid (they decode as noise), so they are the body pieces, stored in other sizes before the 56x32 strips. The 9-byte records from 0x10 (a 0x3C/0x3D byte and four u16 values below 0x100) are probably the rectangles of the parts (position and size). So NC is the large character as a set of VDP1 textures (body pieces plus eye and mouth strips, like the portrait atlas), and the next step is to parse the records into (offset, width, height) per part, check the body piece sizes against the PC `NC10.SPR` pictures (one 326x320 body and 148x99 parts), and then match the VDP1 texture bytes on screen the way the portrait pack does. Not decoded yet: the record layout and the body pieces.

The record list of `NC10.BIN`, parsed: from 0x10 a count byte (0x43 = 67?) is followed by 41 nine-byte records up to 0x182 (`type`, then four big-endian u16: x1, y1, x2, y2); 11 have type 0x3C and 30 have type 0x3D, and every coordinate fits a 170x144 area (x up to 170, y up to 143), which is the size of the character as composed on screen. Some records are boxes (0x3C: 40,83,105,143; 100,102,117,143 ...), the 0x3D ones are smaller and some have x2 < x1 (153,132 to 148,136), so they are probably the rectangles that say where each eye or mouth strip goes on the body rather than texture sizes. That leaves the byte offsets of each strip unexplained: they are either implied (consecutive 56x32 blocks after the body pieces) or stored in the zero-filled bytes 0x182-0x410 region the dump shows as gaps; check with a second `NC` file (the files of other sizes, 49,936 and 132,944 bytes, have different counts of records) before assuming either.
