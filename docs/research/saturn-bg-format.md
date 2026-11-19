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

**Variant B** (marker `00 01 00 02`, 30 files): the big-endian width and height in cells are at 0x04/0x06, count at 0x08 and RGB555 palette at 0x10. A two-word VDP2 pattern-name table begins at 0x610 and is followed by contiguous 64-byte 8 bpp tiles. See the T105d verification below for relocation, flips and BG4302. The original variant-A layout is unchanged.

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

### T108 visual review

The 68 top-ranked candidates were inspected side by side using the decoded Saturn disc 1 pictures and PC subimages. Both were shown within a 112×112 bounding box on a neutral background with their aspect ratio preserved. The 26 confirmed matches share the artwork and card composition. ITEM03, ITEM12 and ITEM27 show the right subject in PC icon sheets but lack the full card, so they are excluded along with 39 incorrect top matches. `config/hd-item-review.json` binds each verdict to the actual PC file, subimage and SHA-256. The offline table generator now accepts the 26 full cards alongside the 12 content matches, still excluding ambiguous palettes. In-game palette allocation and presentation remain open in T109.

### `NC*.BIN` update: the strips are eye animation frames (2026-11-19)

Reading the data after the palette of `SAKURA1/NC10.BIN` (palette at 0x410, data from 0x610) as consecutive 56x32 blocks of 8 bits per pixel (1,792 bytes each, palette index 0 transparent) shows Sakura's **eye animation frames** (open, half-open, closed, looking aside) from about the fifteenth block on; each block ends with a run of zero (transparent) bytes of 280 bytes or more, which is the zero gap seen every 1,792 bytes. The first blocks do not line up on that grid (they decode as noise), so they are the body pieces, stored in other sizes before the 56x32 strips. The 9-byte records from 0x10 (a 0x3C/0x3D byte and four u16 values below 0x100) are probably the rectangles of the parts (position and size). So NC is the large character as a set of VDP1 textures (body pieces plus eye and mouth strips, like the portrait atlas), and the next step is to parse the records into (offset, width, height) per part, check the body piece sizes against the PC `NC10.SPR` pictures (one 326x320 body and 148x99 parts), and then match the VDP1 texture bytes on screen the way the portrait pack does. Not decoded yet: the record layout and the body pieces.

The record list of `NC10.BIN`, parsed: from 0x10 a count byte (0x43 = 67?) is followed by 41 nine-byte records up to 0x182 (`type`, then four big-endian u16: x1, y1, x2, y2); 11 have type 0x3C and 30 have type 0x3D, and every coordinate fits a 170x144 area (x up to 170, y up to 143), which is the size of the character as composed on screen. Some records are boxes (0x3C: 40,83,105,143; 100,102,117,143 ...), the 0x3D ones are smaller and some have x2 < x1 (153,132 to 148,136), so they are probably the rectangles that say where each eye or mouth strip goes on the body rather than texture sizes. That leaves the byte offsets of each strip unexplained: they are either implied (consecutive 56x32 blocks after the body pieces) or stored in the zero-filled bytes 0x182-0x410 region the dump shows as gaps; check with a second `NC` file (the files of other sizes, 49,936 and 132,944 bytes, have different counts of records) before assuming either.

Across the 147 `NC*.BIN` files (sizes 104,528 / 93,712 / 132,944 / 66,064 / 49,936 / 46,480 / 45,712 / 47,056 and others, 40,848 for `NC16`) the layout is the same: header `00 02`, a record area from 0x10 that is zero-filled up to **0x410**, a 256-word palette at 0x410 and image data from **0x610**. The record count byte at 0x10 does not equal the number of nine-byte records that follow (`NC10`: 0x43 against 50; `NC11`: 0x3B against 44; `NC12`: 0x2E against 47), so it counts something else (parts, perhaps, with some parts using more than one record). Only the size of the data after 0x610 changes between files, so one parser for the record area and the strip run should cover all of them.

### `NC*.BIN` decoded: the body is a flat bitmap (2026-11-19)

The body of an `NC*.BIN` is a plain 8 bpp bitmap at 0x610 (index 0 transparent, palette at 0x410), `stride` pixels per row (176 for `NC10`, found as the lag with the smallest mean difference between rows: 152, 168, 184, 208 ... for the others) and 144 rows; the face is blank, the eyes and mouth are the separate strips that follow. `tools/decode_saturn_bg.py decode_nc` reads 144 of the 147 files (`NC3125`, `NC3126`, `NC4138` have no usable stride; the stride search runs 60 to 419 and ignores pairs of transparent pixels, because a mostly transparent body makes plain differences pick a wrong, longer lag). The records are rectangles on that 144-row body (the face areas and the strip targets); their y2 can be smaller than 144, so they do not give the height.

`tools/match_hd_bodies.py` pairs the bodies with the PC `SAKURA1/NC/*.SPR` (the largest picture of each, on a chroma background: green, or cyan for the NC30xx set): `config/hd-body-map.json` has 64 firm pairs (the same-numbered PC file is the best of all 147 and correlates >= 0.75; 16 chosen at random were looked at side by side and are the same character and pose, the PC bodies also have blank faces) and 80 candidates. Not integrated: a runtime recogniser for the VDP1 sprites of a body, the eye and mouth strips, and the pairing of the candidates.

Review of the body pairs (2026-11-19): with the stride fixed, `config/hd-body-map.json` has 104 firm pairs and 40 candidates (the earlier 64 and 80 were inflated by wrong strides). Looking at the 40 candidates side by side, all are the same character and pose except where the PC picture is a **full frame with its background painted in** (the PC `NC3060`, `NC3109`, `NC3124`, `NC3128`, `NC3129` and others: a transparency under 4 percent after removing the chroma colour flags them) and two Saturn bodies whose stride is still wrong (`NC3290`, `NC3517`). `config/hd-body-review.json` lists the 15 rejected files and the confirmed candidates; the same transparency flag also removes eight firm pairs (`NC3013`, `3047`, `3057`, `3058`, `3173`, `3285`, `3286`, `NC92`). 129 bodies are usable as pairs; the eyes and mouths (separate strips, 56x32 on the Saturn side against 148x99 parts on the PC side) are not paired yet.

### Bodies on screen: one VDP1 texture, recognised by hash (2026-11-19)

`SATRECOMP_BODY_TRACE=1` (patch0062) prints the large VDP1 textures of the presented frame. In a scene with a large character the body is **one sprite** (type 0, 8 bpp, 152x144 or 176x144 at y=8) and the bytes of its texture are exactly the body bitmap of the `NC*.BIN`: the FNV-1a hash of `data[0x610:0x610 + stride*144]` equals the hash of the sprite's pixels (`NC20` with `9E12AD191E9779AF` in `post-3000`, `NC82` with `E75682BF38A2E1B5` in `office-return-6000`, `NC97` with `8BEDACB1B882EDAF` in `after-options-3000`). So the runtime can tell which body is shown without any palette or screenshot work; a table of those hashes comes from the same decoder that built `config/hd-body-map.json`.

What stops a body from being drawn in HD right now: the face is blank in the body bitmap on both sides, the eyes and mouth are separate small VDP1 sprites over it (Saturn strips of 56x32, PC parts of 148x99), and the HD body would need the matching PC eye and mouth parts or the native strips would show as small pixels on a sharp body. The portrait pack solves the same problem for the 40x48 faces by matching the sprite parts against an atlas; the bodies need the strip table (which Saturn strip equals which PC part) first.

### Eye and mouth frames of a body (2026-11-19)

`SATRECOMP_BODY_TRACE_MIN=64 SATRECOMP_BODY_TRACE_BYTES=1` (patch0063) also lists the small VDP1 textures. In `after-options-3000` (body `NC97`, 152x144 at 88,8) the face is two small sprites over the body: **eyes** 64x24 (1,536 bytes) at 128,40, that is (40,32) from the body's corner, with three distinct frames, and a **mouth** 24x16 (384 bytes) at 152,64, that is (64,56), with six frames. Searching those bytes in `NC97.BIN` finds them directly after the body bitmap: the three eye frames at 0x5B90, 0x6190, 0x6790 (the body ends at 0x5B90 = 0x610 + 152 x 144) and the six mouth frames at 0x6D90 + k x 0x180; the file ends 0x40 bytes after the last mouth frame. The nine-byte records are therefore not the strip rectangles (they look like regions of the body that sit in front of the face, such as hair); the strip positions come from the sprite commands at run time.

The PC side lines up with that order: `NC97.SPR` has the 272x320 body, then three eye parts of 136x63 and six mouth parts of 32x63 (green areas are transparent), in the same order as the Saturn frames. Frame k of the eyes is PC image 1 + k and frame k of the mouth is PC image 1 + (eye count) + k. To draw the face in HD a runtime would: recognise the body by the hash of its texture (above), recognise each face sprite by finding its bytes among the frames after the body (or by a table of their hashes), and draw the matching PC part centred on the sprite's rectangle, scaled with the body's HD scale. Offline pieces still missing: the frame sizes for every body (the records do not give them; NC97 is 64x24 and 24x16), and the placement of each PC part (the parts carry margins, so centring on the scaled Saturn rectangle is an assumption to check).

### Solving the strip sizes (tools/solve_nc_strips.py, 2026-11-19)

Two findings first: the body is not always image 0 of the PC `NC*.SPR` (it is the largest picture; in `NC24` it is image 7), and the parts after it come in runs of equal size (eyes then mouths in most files, one run in a few, up to twelve in others).

`tools/solve_nc_strips.py` takes the byte count after the body bitmap and the run lengths of the PC parts (n1 eye frames, n2 mouth frames) and looks for E and M with n1 E + n2 M = bytes, E = w1 h1 and M = w2 h2 (widths multiples of 8), choosing the pair of widths whose rasters are smoothest (mean difference between a pixel and the one a row below, ignoring transparent pairs). It is right for `NC97` (64x24 x3, 24x16 x6; the true answer ranks first) and gives a result for 76 of the 129 usable bodies (one or two runs only; 53 are left because they have three to twelve runs, no integer solution or an unclear score). Looking at the first frame of every run of 24 random solved bodies next to the first PC part, about three quarters look right (`NC41`, `NC76`, `NC56`, `NC3001`, `NC3004`, `NC3025`, `NC3014`...) and the rest are wrong sizes (`NC60`, `NC94`, `NC43`, `NC82`, `NC3011`...). The scores do not separate the two groups (roughness, margin and the correlation with the PC part, which is low anyway because the PC parts carry margins), so the result is **not written as data**: it would need a better check, for example comparing every frame of a run with every part of the run.

A different way round the same problem is to learn the sizes at run time: the VDP1 command of a face sprite gives its exact width and height, and its bytes can be found in the `NC*.BIN` (read from the disc by name), so the runtime would not need the offline sizes at all, only the PC part list of the body in order; the ordinal of a frame then comes from counting frames of that size from the start of its run.

### HD character bodies in the runtime (patch0064, 2026-11-19)

The runtime now draws the PC body and face parts for a recognised body (`tools/gen_body_table.py` makes `port/body_table.h`: 129 bodies by the hash of the NC bitmap, the disc file and the PC file). It works for bodies whose PC parts form **one or two runs** of equal size (about 76 of the 129; the others keep the native body). For each frame:

1. The body is the big VDP1 sprite whose bytes hash to an entry. Its NC file is read from the disc by name and the PC picture is decoded on a worker thread (the native body shows until it is ready).
2. Every other sprite that overlaps the body rectangle above the dialogue box must be a face frame: its bytes are searched in the NC data after the body; the frame ordinal comes from the offset (frames of equal size in runs, the first run starting right after the body, the second after `count x size` of the first, with the run lengths taken from the PC parts). Any sprite not found means the body stays native; so does any blend (sprite white weight other than 0, colour offsets).
3. The body and face sprite pixels inside the rectangle are cleared from the native layer, the PC body is drawn over the scene picture, and each PC part goes where the same part fits best on the PC body: the position is the Saturn sprite's centre as a prediction, refined once per run by sliding the part over the PC body within 12 pixels (best agreement of the pixels both have, results in the log with `SATRECOMP_BACKGROUND_STATS`).

Checked in game on three saved scenes: `NC97` (the girl with short hair) and `NC82` (the man with glasses) draw with their HD faces and no visible seam; `NC20` has five runs and stays native. The guest hashes are identical to v0.2.2 over 900 frames (0 interpreted) and the composite costs about 0.7 ms a frame more with the HD scene picture and body. Not checked: the other bodies, expression changes over time (frames beyond the first seen), fades with a body on screen, and bodies with three or more runs.

Which bodies draw (scan of the 36 saved states with the HD pack, `SATRECOMP_BACKGROUND_STATS=1`, patch0065 prints why a body is skipped): bodies seen are NC10, NC11, NC20, NC30, NC55, NC82 and NC97. `NC97` and `NC82` draw. `NC20` (5 runs) and `NC55` (11 runs) are skipped as unsupported. `NC10` and `NC11` are drawn only when nothing else overlaps the body: in the choice (LIPS) scenes of the saved states the choice interface sprites cross the body rectangle, so the body stays native there, and when the interface is absent the frame offsets do not fit the assumed layout: in `NC10` the PC parts are 33 pieces then 60 pieces, the Saturn eye frame (1,792 bytes) sits at offset 62,160 or 67,536 and the mouth frame (256 bytes) at 69,328, so the eyes are not 33 frames of 1,792 bytes starting at the end of the body (that would start before the body ends); the file has a different arrangement of runs than the PC part order suggests. `NC30` (42 pieces then 12) shows frames (512 and 384 bytes) at 34,576 and 36,112 and fails the same check. So the layout is not the same for every body: the first run does not always begin where the body bitmap ends, and the general solution needs the sizes of every run (see `tools/solve_nc_strips.py`) or a different anchor than the end of the body (the frames seen in a scene, their offsets and the PC part order could be matched pairwise instead).

### Bodies by content (patch0066, 2026-11-19)

Patch0066 removes the dependence on the arrangement of the frames in the file. The face frames are still found by searching their bytes in the NC data (any sprite over the body that is not found there means native), but the PC part for each frame is now chosen by looking at it when the arrangement does not fit: the frame is painted with the NC palette (palette at 0x410, index 0 clear), reduced to a 24x24 normalised grey signature and correlated with the signature of every PC part of the body (cached per frame; accepted from 0.30). The exact layout (frames of equal size in one or two runs that start at the end of the body, in the order of the PC parts) is tried first because it is exact where it fits (`NC97`, `NC82`); the content match covers the rest, with no limit on the number of runs.

Seen in game on the saved scenes (1280x720, HD pack): `NC82`, `NC97`, `NC11` (the girl in the pink kimono) and `NC20` (the girl with the white hairband) draw as smooth HD bodies with HD faces; `NC55` and `NC30` stay native (some mouth frames are nearly blank and no part reaches 0.30; `NC10` in a choice scene stays native because the choice interface sprites overlap the body). The guest hashes of `prebattle-3000` are identical to v0.2.2 over 900 frames, 0 interpreted. A frame matched by content can be the wrong expression when two parts look alike (correlations are 0.4 to 0.7), so expressions over time should be watched on a longer run before trusting it.

Patch0067 adds two rules to the content match: a frame that is nearly clear (under 3 percent opaque pixels, as the blank mouth of a body that draws its mouth in the bitmap) takes the PC part with the fewest opaque pixels if that part is also nearly clear; and frames of 600 pixels or fewer (mouths) are accepted from a correlation of 0.12 instead of 0.30. With them `NC55` (the girl in the pink nightcap, 11 runs) and `NC30` (the blond woman in the dark kimono) draw as HD bodies with HD faces on the saved scenes; the grey fringe on the right of the body in `NC30` is the original drop shadow, not the HD body. A mouth accepted at 0.12 to 0.17 can be the wrong shape, so mouths are the first place to look for wrong expressions.

### Expression check and a stricter content match (patch0068, 2026-11-19)

A 2,500-frame run with random input from `post-3000` (body `NC20`), HD and native screenshots at the same frames (the guest is identical), showed the content match of patch0066/0067 choosing the **wrong expression** in several frames: wide-open eyes in the HD face while the native face had calm eyes. A wrong expression is worse than the native picture, so patch0068 only accepts a content match that is clear: a correlation of at least 0.50 for frames above 600 pixels (0.30 below that) and a lead of at least 0.05 over the second best part; otherwise the body stays native. The same run repeated afterwards agrees with the native expression in every captured frame.

The price is coverage: with the stricter rule `NC11`, `NC20`, `NC55` and `NC30` fall back to native in the saved scenes (their frames correlate 0.3 to 0.6 with several parts at once); only the bodies whose frame layout is exact, `NC97` and `NC82`, still draw. Ideas to get them back without wrong expressions: compare the face region with context instead of the isolated frame (the frame composited over the Saturn body at its position against each PC part composited over the PC body at its refined position, so the surrounding skin and hair take part in the comparison), solve the frame sizes of every run so the layout is exact (`tools/solve_nc_strips.py` gets about three quarters right), or take the PC part index from a sequence the game uses (the frames change in a fixed order for a blink or a mouth cycle).

### Frames by shape (patch0069, 2026-11-19)

Two attempts after patch0068 to get `NC11`, `NC20`, `NC55` and `NC30` back without wrong expressions. Comparing the frame with its surroundings (the frame over the Saturn body against each PC part over the PC body) did not help: every part scores 0.77 to 0.80 because the skin and hair around dominate, and the best and second best differ by 0.00 to 0.01. Comparing the SHAPE did: the pixels that are dark (outlines, pupils, lips; luminance under 80) of the Saturn frame against the same pixels of each PC part, resampled onto the frame's grid at the place the frame predicts and shifted by up to three frame pixels each way, scored with the Dice overlap of the two dark masks (best shift per part). For eye frames the best part scores 0.57 to 0.72 and wrong parts 0.3 to 0.6; two near-identical parts can tie (0.72 against 0.71), which is harmless because they look the same, so a match is accepted from 0.50 without a lead. Frames with fewer than six dark pixels (most mouths) cannot be compared this way and stay as the native sprite.

Policy now: a recognised body is always drawn from the PC picture; each face frame is drawn from its matched PC part, and a frame with no match stays as the native sprite, drawn again over the HD body (so the expression is always right and the body never switches between HD and native from one frame to the next). Checked with the 2,500-frame HD/native comparison of `NC20`: the expression agrees in every captured frame. Where a frame stays native it shows as a small pixelated patch with its own skin tone on the HD face (two of the captured frames of `NC20`, the eyes of `NC11`): it is correct but visibly blocky. Seen drawing in the saved scenes: `NC97`, `NC82` and `NC20` (mostly HD faces), `NC55` (HD eyes, native mouth), `NC11` and `NC30` (HD body, native face patch). Guest hashes identical to v0.2.2 over 900 frames on `iris-correct-room-3000`, 0 interpreted.

To remove the patches: match mouths and other low-contrast frames by colour (lips are red), or solve the frame sizes so the file layout is exact, or use the frame order the game plays for blinks and mouth cycles.

### Mouths by lip colour (patch0070, 2026-11-19)

Frames with fewer than six dark pixels, most mouths, are now compared by their reddish pixels (red at least 130, red minus green at least 45, red minus blue at least 25) with the same Dice overlap and shift search, and the near-tie rule for shape matches is tightened to: accepted from 0.65, or from 0.50 with a lead of 0.04 over the second best (patch0070). A lip-colour match carries less shape, so it needs 0.75. A first try at 0.50 chose a mouth with the tongue out in a frame of `NC20` whose native mouth is a flat line; at 0.75 only the clear matches pass and the 2,500-frame comparison agrees with the native expression in every captured frame again.

Result on the saved scenes: `NC11` (the girl in the pink kimono) now draws a full HD face, eyes and mouth (`16x16` mouth at 0.77); `NC55` draws HD eyes and, where it matches, the mouth; `NC20` draws HD eyes with the native mouth patch; `NC30` stays with the native face because its frames match at 0.48 to 0.52. Guest hashes identical to v0.2.2 over 900 frames on `prebattle-3000`, 0 interpreted.

### Episode cards in 16:9 (patch0071, 2026-11-19)

The ten title cards (`TITLE1..10.BIN`) are on **VDP2 layer 4** (a layer trace in `title-final.state` plus `chapter1-title-new-game.movie` shows layer 4 taking the palette fingerprint `F84F4FA528984E99` of `TITLE1` at frame 6040 of that run, after the loading screen and the flower plane). Patch0071 widens them without any asset: when layer 4 has one of the ten card fingerprints, the window area around the native 320x224 picture is filled from four strips made of the displayed picture's own border (the left and right strips are the average of the eight outermost columns for every row, smoothed over nine rows; the top and bottom strips the average of the four outermost rows for every column, smoothed over nine columns), stretched with the linear filter, and the native picture is drawn again over them. Nothing of the game's art leaves the player's machine. The fade-in over the flower plane works the same way because the strips come from the frame as displayed.

Seen on `TITLE1` at 1920x1080 (frames 6050-6400): the sky continues to the left, the white blossoms to the right, the lettering stays inside the native picture. It is a plain extension, not painted art: the right side shows a faint vertical banding next to the picture's right edge where the native columns mix pink and white. The generative art the owner asked for (a painted 16:9 card) would replace it; the Spanish cards from `tools/es/portadas_es.py` use the same layer and fingerprints (the palette is not changed), so they widen too. Guest hashes identical to v0.2.2 over the 6,400 frames of that run, 0 interpreted.

### Event pictures matched visually (T105b)

Reviewed every decodable EVE image against the three strongest candidates among the
48 PC SAKURA2/BG/BBG*.SPR files. The 12 disc observations represent nine unique files:
EVE0101, EVE0116 and EVE0118 are byte-identical across the two prepared discs.
For each PC SPR, the comparison uses its largest picture and the 32×16 luminance
signature in match_hd_all.py. Used the score to rank candidates and checked the
actual characters, props and scenery side by side.

| Saturn | Disc | PC | Score | Common features |
|---|---|---|---:|---|
| EVE002 | 1 | BBG002 | 0.824 | Airship and daylight clouds |
| EVE0101 | 1, 2 | BBG001 | 0.673 | Three figures and red band behind them |
| EVE0116 | 1, 2 | BBG201 | 0.923 | Silver-haired face and green headdress |
| EVE0118 | 1, 2 | BBG101 | 0.828 | Four characters against blossoms |
| EVE102 | 1 | BBG102 | 0.807 | Five characters with green foliage |
| EVE105 | 1 | BBG105 | 0.594 | Group pose against stone ruins |
| EVE202 | 1 | BBG202 | 0.895 | Close-up with red forehead jewel |
| EVE205 | 1 | BBG205 | 0.915 | Frontal close-up with hair ornaments |
| EVE207 | 1 | BBG207 | 0.999 | Open-mouth portrait on purple |

EVE0101 and EVE105 match the same artwork at different framing, which explains why
their whole-frame scores are low. The nine candidate palette fingerprints are unique
within the set and do not occur in the current scene map. Placement, fingerprints in
the presented VDP2 layer and PC substitution in the two-disc runtime still require
in-game evidence. Keep the approved Zoom framing and native fallback.

### EVE presentation witness (T105e)

Replayed two disc-1 states on runtime SHA-256
cc7fa58737c37075efaea76a72cbe390454d21847ebadf1ca1b030e75ac046c2
with Enhanced at 1920×1080 and layer tracing. Both produced 12 strict-native frame hashes
with zero interpreted blocks. Each fingerprint matched both the source palette and the
presented layer-5 palette.

| EVE | State | Palette | Presentation |
|---|---|---|---|
| EVE0101 | battle-entry-ref-3000 | D3C319A0279AEDB3 | Tactical map behind the character group inset |
| EVE202 | chapter-2 cold-native finish | 0D97B7C3CC0B3C31 | Tactical map behind the jewel portrait inset |

Both visible insets occupy 288×144 at native (16,8) at the captured frame, with the
dialogue panel and surrounding map visible. Layer 5 is enabled, with zero scroll and a
256,256 increment. EVE replacement needs to preserve that inset and the compositing
order. The PC image still needs a validated transform inside the inset. EVE002 tiles
were also found in one save, but its full palette was absent from CRAM in that save,
so presence in VRAM alone is insufficient evidence of visible presentation.
Disc-2 runs, additional EVE identities and safe HD rendering remain open.

### Wide variant B visual review (T105a)

The earlier offset 0x210 yields displaced tiles and coloured bands. In the 30 disc-1 BG files
with marker 00010002, the big-endian dimensions are at 0x04 and 0x06, and the declared tile count
is at 0x08. The width × height big-endian u32 pattern names start at 0x610. Tile bytes start
immediately after that table. Each tile is 64 bytes and the low 30 bits of each pattern name
are twice its tile index. The high bits can request flips. The review reconstruction used
bit 30 for horizontal and bit 31 for vertical, pending a runtime witness for the flip mapping.

The table and tile spans account for the exact file length in 29 of 30 files. BG4302 declares
1,333 tiles and contains 1,273. All pattern indices in the 30 files fit the bytes present.
The map includes formerly undecoded BG2290, BG2518, BG2533 and BG4372. Existing catalog
fingerprints still reflect the earlier implementation and need regeneration with the decoder correction.

For the 12 wide pairs already in the plan, reconstruct native tiles in table order
with the RGB555 palette at 0x10, select the largest picture in the same-number PC SPR,
and compare side by side at half PC size. Each row below matches the same artwork by eye.
Whole-image scores use the 32×16 luminance signature of match_hd_all.py. The provisional
crop search uses a box the size of the native frame, scans half-PC pixels every 4 horizontally
and 2 vertically, and reports its highest correlation. These are offline measurements.

| BG | Visible match | Whole | Best crop x, y | Crop score |
|---|---|---:|---|---:|
| 1207 | Hanami groups, lanterns and trees | 0.988 | 0, 6 | 0.966 |
| 1257 | Collapsed red gate and brick walls | 0.883 | 80, 0 | 0.827 |
| 1280 | Painted battle, pine and gold clouds | 0.713 | 56, 16 | 0.901 |
| 1282 | Breaking wave and sea wall | 0.962 | 0, 8 | 0.970 |
| 1283 | Ruined avenue and brick viaduct | 0.950 | 0, 8 | 0.914 |
| 1285 | Burning street and silhouettes | 0.962 | 0, 8 | 0.977 |
| 1310 | Wave above the coastal town | 0.884 | 0, 10 | 0.829 |
| 2077 | Soldiers confronting the creature | 0.988 | 16, 10 | 0.758 |
| 2093 | Distant winged figure | 0.927 | PC narrower than Saturn | — |
| 2130 | White machine beside the ruins | 0.997 | 0, 8 | 0.953 |
| 2238 | Close-up of the winged figure | 0.797 | PC narrower than Saturn | — |
| 2515 | Couple by the window | 0.998 | 0, 8 | 0.988 |

BG1280 is the strongest crop candidate. For BG1257 and BG2077, the whole-image score
beats every fixed-size crop, and BG2093 and BG2238 cannot be handled by that crop model.
Even among equal-width pairs, a fixed vertical crop can score below the resized whole scene.
Use in-game scroll and stable landmarks to validate each transform before enabling it.
No runtime, pack, release, or approved Zoom geometry was changed in this review.


### Variant B decoder and catalog verification (T105d)

The decoder reads the full map before the tile payload. The even 15-bit character number
selects the offset in 32-byte units. The high bits flip the tile along the horizontal
(bit 30) and vertical (bit 31) axes. The two-word reads in the SDK renderer
(`video/layers.cpp`) use the same bits in the normal and line-rendering paths.

A real BG2252 witness came from the local Spanish load-confirm state. Its whole 79,168-byte
file tile payload is verbatim in VDP2 VRAM at 0x4A000. All 1,332 pattern names in the
36 x 37 file map match the VRAM map at 0x44108 with 256-byte row strides, character-base
addition 0x2500 and palette bits 0x00700000. The horizontal entry at column 1, row 10
changes from 0x4000020C to 0x4070270C (VRAM 0x44B0C). The vertical entry at column 7,
row 7 changes from 0x80000190 to 0x80702690 (VRAM 0x44824).

BG4302's 88,352-byte ISO extent and treatment are identical on the prepared Japanese,
English and Spanish discs 1 and 2. Its header declares 1,333 tiles (the map area plus
one). The 36 x 37 map ends at 0x1AE0, and the remaining 81,472 bytes are exactly
1,273 tiles. The largest referenced tile is index 1,272. The parser bounds all pattern
references by the actual complete tile payload. The corrected BG4302 image visibly
matches the same-number PC picture. It remains excluded from the scene table as BG4xxx.

For variant B, `cells_sha256` now covers only the tile payload, starting immediately after
the map. The palette fingerprint is unchanged. The BG2252 witness confirms this payload
can match VRAM verbatim, but a payload hash does not include map arrangement or flips.
The corrected map has 740 decoded files and 9 undecoded files. BG2290, BG2518 and BG2533
were newly decoded and match the same PC artwork by eye. BG4372 is a cut-out against
the PC full-scene image and stays excluded. The already cataloged BG1306 is a now-confirmed
visual pair, held native until its in-game presentation is verified under T105c.

The 459-entry T74 runtime header generated before and after the offline regeneration
is byte-identical. The runtime and package were not rebuilt.


### NC face run inventory (T106d)

Scanned the 129 usable pairs in `config/hd-body-map.json` after excluding all 15
entries under `rejected` in `config/hd-body-review.json`. Counted consecutive
equal-dimension PC images with `solve_nc_strips.runs`, omitting the largest
body image and the 16x16 auxiliary entries as the two-run matcher does. A PC run
counts a sequence of sizes in the SPR. It does not establish a Saturn run or an
expression mapping.

| PC runs | Files | Identities with three or more runs |
|---:|---:|---|
| 1 | 19 | |
| 2 | 86 | |
| 3-11 | 24 | NC20, NC21, NC22, NC23, NC3021, NC3040, NC3042, NC3045, NC3050, NC3056, NC3059, NC3516, NC3518, NC4182, NC4199, NC4281, NC4384, NC50, NC51, NC52, NC53, NC54, NC55, NC80 |

Within that group of 24, five have three runs, seven have four runs, four have
five runs, two have six runs and six have eleven runs.

On the prepared disc 1, used file extent minus the body end
(`0x610 + 144 * catalog_stride`) to test for a whole number of 3,840-byte
periods. Each period holds three 32x16 eye frames and six 24x16 mouth frames.
Decoded those fixed windows with the native palette and inspected all seven
periods of the two accepted cases. For the other byte-count-compatible files,
the first period (and the middle and last where applicable) exposed different
strip geometry or boundaries. Testing alternative widths of the same 512- and
384-byte frames did not produce another complete period.

| Saturn raster result | Identities and arithmetic periods |
|---|---|
| Exact repeated layout | NC30 (6) |
| Exact single period | NC35 (1) |
| Same byte divisibility, incompatible raster | NC3014 (11), NC3015 (6), NC3017 (6), NC3027 (6), NC3032 (6), NC3043 (1), NC34 (1), NC3503 (2), NC36 (1), NC4344 (1), NC98 (9) |

NC30 starts at byte 26,896, with its third eye group at 34,576 and third mouth
group at 36,112, the offsets in the T19 VDP1 trace. Its 54 Saturn frames
reconstruct as 18 eyes and 36 mouths. NC35 starts at 30,352 and has a single
group of three eyes and six mouths. No file with three or more PC runs passes
this exact Saturn repetition rule. The audit leaves other possible Saturn
periods, PC subimage assignment, and runtime integration open.


### NC30 offline face-to-SPR map (T106a)

The largest PC picture is subimage 0. Original SPR indices 6-23 are six triples
of eyes. Indices 30-65 are six sextuples of mouths. The 96x47 dimension run
contains all 18 eyes and the first 24 mouths. The 80x63 run contains the last
12 mouths. Both comparisons retain every image's proportions. The native
eye state and mouth shapes agree with their PC group by visual inspection
across all 54 pairs. In particular, each eye triple moves from open towards
closed, and each mouth sextuple starts closed, opens, and shows visible
teeth in the third frame. The mouth crops include different amounts of
surrounding skin in PC art.

`config/hd-nc30-face-map.json` binds this review to whole-asset SHA-256 hashes,
native byte offsets, frame dimensions and texture SHA-256, and original PC
subimage indices and dimensions. The six prepared ISO language/disc variants
contain identical NC30 bytes. The two source images can be replayed offline
by reading each native slice in row-major order, applying the palette at
0x410 with index zero transparent, and decoding the specified SPR subimage
with the existing green chroma key. Each complete native face texture occurs
once in the post-body payload.

The saved VDP1 command chains provide three distinct native frame witnesses.
All four states below contain the exact 176x144 body texture. Body, eye and
mouth are at (-88,-104), (-24,-72) and (-8,-48) in command coordinates, with
colour register 0x2000. These are native anchors for a replay comparison.

| Saved state | Eye data in VDP1 | BIN offset / PC subimage | Mouth data in VDP1 | BIN offset / PC subimage |
|---|---|---|---|---|
| `maria-face-discovery` | 0x43640 | 34,576 / 12 | 0x43C40 | 36,112 / 42 |
| `chapter1-continuous-47999` | 0x43640 | 34,576 / 12 | 0x43C40 | 36,112 / 42 |
| `post-18000` | 0x43640 | 34,576 / 12 | 0x43C40 | 36,112 / 42 |
| `maria-exit` | 0x43840 | 35,088 / 13 | 0x43C40 | 36,112 / 42 |

For T106a2, resolve the original SPR index before compacting renderer parts
and qualify the match against exact texture bytes and dimensions. An asset
or frame outside the pinned table, or ambiguous placement in the HD body,
keeps the native face sprite. Compare native and HD captures from the listed
states, including progression through blink and mouth frames, and verify
guest hashes with strict AOT. Saved-state command bytes establish native
frame identity. The new HD rendering and placement remain unverified.


### NC20 offline face-to-SPR map (T106b)

NC20 has a 152x144 body ending at 23,440 and then 17,280 zero bytes. From
40,720 to the end of the 93,712-byte file, eight consecutive groups each
hold three eye frames followed by six 24x24 mouth frames. To recover the
boundaries, the 24x24 mouth at 48,784 observed in the states provided a
stable transparency footprint. Matching that footprint found the mouth
runs, then the distances to the previous group end gave each eye height.
Reading the native slices with the palette at 0x410 (index zero clear)
produced coherent eyes and mouths in all groups.

| Group | Eye start | Eye size | Mouth start | PC eye indices | PC mouth indices |
|---:|---:|---|---:|---|---|
| 1 | 40,720 | 48x16 | 43,024 | 8-10 | 39-44 |
| 2 | 46,480 | 48x16 | 48,784 | 11-13 | 45-50 |
| 3 | 52,240 | 48x16 | 54,544 | 14-16 | 51-56 |
| 4 | 58,000 | 48x24 | 61,456 | 17-19 | 57-62 |
| 5 | 64,912 | 48x32 | 69,520 | 20-22 | 63-68 |
| 6 | 72,976 | 48x32 | 77,584 | 23-25 | 69-74 |
| 7 | 81,040 | 48x24 | 84,496 | 26-28 | 75-80 |
| 8 | 87,952 | 48x16 | 90,256 | 8-10 | 39-44 |

Group 8 is byte-identical to group 1, frame by frame. The PC has seven
matching visual groups across five size runs. The pinned PC asset contains
body subimage 0 (296x320), 21 eyes and 42 mouths. The eye groups visibly
range from the variants of calm and narrowed eyes to a wide-eyed reaction.
The mouth in the sixth group opens much wider, and its visible teeth agree
with the Saturn artwork in the corresponding frame. Compared all groups
side by side, keeping the respective source proportions.

`config/hd-nc20-face-map.json` records exact asset SHA-256 hashes, dimensions,
and original SPR subimage indices for 63 unique face textures. Each of the
nine repeated textures maps both offsets to the same original SPR index.
Searched the whole face payload for every texture and the only repeated
matches are those nine pairs. The 17,280 zero bytes have no PC candidate.
Unknown identity, dimensions or placement retain the native face sprite.

Two saved VDP1 command chains contain the exact body texture at 0x3D340
(command coordinates -88,-104, colour 0x2000). Both show the same closed
mouth at (-16,-56), 24x24, 0x47540 in VRAM, native offset 48,784 and
PC index 45. At (-32,-72), the 48x16 eyes differ: `post-3000` has
VRAM 0x46C40, offset 46,480 and PC index 11, while `morning-9000` has
VRAM 0x46F40, offset 47,248 and PC index 12. T106b2 will compare the
HD placement and expression progression using these states. The present
witnesses establish native texture identity and command placement.

### NC82 body fade-in witness (T106c)

Replayed English disc 1 from office-return-3000.state with frames 3000 onward
of office-return.movie rebased to zero. Both 1280×720 Enhanced profiles used
the v0.2.4 reference (SHA-256
1a94790eefc8492ca80499bbbd3e7517cb4db565908bcee86ae5b12f44c94b9e).
Only one profile could see NC82.SPR. Its isolated PC directory shared that
file with the owner's assets and provided no PC backgrounds.

Both runs produced 3,000 identical guest hashes and zero interpreted blocks.
At captures 2972–2984, sampled every three frames, Yoneda faded in over his
office. Every full-window RGB pair in that interval was identical. The HD
trace reported a blend over NC82 and the native fallback. At 2987–2996 the
opaque body switched to HD. All four differences stayed within the same
body bounding box (346,50)–(853,482), right and bottom exclusive. Earlier
captures 2960–2969 also matched before the body appeared. This is a
character alpha fade from transparent, not a white or black full-screen fade.
No runtime or package was rebuilt.


### Presented-frame vertical scroll witness (T105c)

Used the known v0.2.4 runtime (SHA-256 `1a94790eefc8492ca80499bbbd3e7517cb4db565908bcee86ae5b12f44c94b9e`)
on prepared Spanish disc 1. Load `guion-es/pruebas/load-file1-ref-es.state`
(SHA-256 `21b68c7870978c6461a314498f8f7f5422f28fd965e7c91ca0c31df9ae446e8f`)
at frame 0 with a separate copy of that directory's `b.bin`. Replay
`5 0400 0` then `11 0000 0` and leave the controls neutral. Keep all
paths absolute and use Original mode, strict native, headless and muted.
A 2,202-frame capture and three shorter repeats had identical overlapping
guest hashes and zero interpreted blocks. Local logs, states and images
are in `local/work/codex-t105c`.

After the menu load, BG2252 is the vertically scrolling theatre exterior.
The 79,168 tile bytes are at VDP2 VRAM 0x4A000. All 1,332 relocated pattern
names match at 0x44108 with 256-byte row stride. The active NBG2 plane starts
at 0x44000, so the image begins at (16,8) in plane coordinates. NBG2 uses
registers SCXN2/SCYN2 at 0x90/0x92, with unit source increment and no
per-line scroll on this layer. The native 288x144 scene window remains
screen rectangle [16,304) x [8,152). The visible source starts at
(0, SCYN2) for these captures.

The screenshot named frame N aligns with the save taken at N-1 in this
harness. Saving at N during the pan puts the register one source row ahead.
Use the scroll from the same presented frame in the runtime and do not
apply a fixed one-row correction. RGB555 values expanded with the native
five-bit shift yield these exact screen comparisons.

| Shot | Save | SCYN2 | Exact pixels in native inset |
|---:|---:|---:|---:|
| 850 | 849 | 6 | 41,472 / 41,472 |
| 900 | 899 | 31 | 41,472 / 41,472 |
| 950 | 949 | 56 | 41,472 / 41,472 |
| 1000 | 999 | 81 | 41,472 / 41,472 |
| 1050 | 1049 | 106 | 41,472 / 41,472 |
| 1100 | 1099 | 131 | 41,472 / 41,472 |
| 1150 | 1149 | 144 | 41,472 / 41,472 |

The VRAM identity and scroll persist after the pan. Shot 1200 is a blend.
By shot 1250 the room is visible on top, with NBG0 priority 3 and NBG2
priority 2. At shot 1150 those priorities were 2 and 3. This makes
`load-confirm-ref-es.state` a useful occlusion control: its exact BG2252
tile bytes survive, but their presence cannot qualify replacement.

The same-number PC art at 576x592 nominally has exact 2x dimensions.
Its roof and tower are drawn at different screen positions and the windows
shift nonuniformly over the pan. The whole-image luminance signature scored
0.616, and exact 2x source crops over the seven matching native frames
scored 0.295-0.539. BG2252 is excluded as a replacement and retained as a
scroll and occlusion witness. The matching and rendering gates must be
evaluated separately.

Scanned the 15 wide and 14 tall catalog entries over 152 candidate state
files for complete VRAM tile-pool hits. BG2252 is the only complete hit.
A second pass over 165 files with four 256-byte anchors also found partial
BG2247 and BG2252 pools in unrelated views. BG2247 has only 62 of 1,332
relocated names in the NBG2 map in representative hits, so those fragments
do not establish a scrolling route.

T105c2 needs per-identity source geometry and the visible NBG layer's
scroll, plane origin and map bounds carried alongside the captured
presentation. For this example, compute the source offset as live scroll
plus inset origin minus plane image origin. The two origins coincide in
the native frame. Verify wrap, non-unit increments, line effects, colour
offsets, blends and occlusion before extending eligibility. Keep native
in those cases until supported, and preserve the current inset and Zoom
framing. General SDK support and replacement remain open.

### Integer episode center and generated sides during the fade (T107e)

Patch0081 draws the 320×224 episode card at the same integer viewport as the
native center. Generated 39×224 sides use the same scale and are clipped to
the 16:9 presentation. The edge texels fill the extra window pixels outside
the integer fit. An eight-pixel reflected underlay beside the center keeps
the transparent seam from reflecting the lettering farther into the side.
When parts are missing or the captured blend weight is ambiguous, the normal
native-edge fallback applies.

The renderer carries a uniform weight from the presented NBG3-over-NBG2
composition branch; it uses the ratio selected by the emulated VDP2 at the
time of composition and handles a 32/32 card. No guest state changes. The
proof reconstruction from the two captured planes reproduced all 71,680
native RGB pixels at four title points with weights 4, 32, 32 and 27 of 32.
The generated sides are modulated by the same card weight over the already
composited exterior edge. Edge padding is extrapolated to fit the window.

Built an isolated Windows runtime from the existing objects after recompiling
the affected sources, SHA-256
765ea6b96afb383a68311b2e7e3c1027f40050e4ef6bf79a579ef88d20177679.
At 1920×1080, two full 6,550-frame title replays (English and Spanish disc 1)
match the corresponding prior Original run exactly in guest hashes
and report zero interpreted blocks. Passes 6075, 6200 and 6500 each preserve
all 1,146,880 RGB pixels of the 4× center (320,92)–(1600,988). The sides
differ from the mirror controls and change between fade-in, full and fade-out.
The isolated app loaded the 20 package-gated files from its own app-relative
art directory. The gameplay witness covers Episode 1, while the package gate
covers all ten asset pairs. No new ZIP was built. At this checkpoint the
project accounted for 39,407,546,051 unique logical file bytes, above the cap;
the unchanged development ZIP is 6,315,009,692 bytes.

### Full generated episode surrounds (T107f)

Each Saturn card's palette fingerprint selects one 640×360 RGBA artwork
surround. The 320×224 center is zeroed in the PNG and drawn from the guest
frame at the largest integer scale that fits. Only the exterior is clipped
or enlarged to reach the presentation limits. At 1920×1080 the center is
4×, from (320,92) to (1600,988). At 2560×1440 it is 6×, from (320,48)
to (2240,1392). Both use the same 16:9 artwork without stretching in
these modes.

The renderer uses the Saturn card's uniform NBG2 blend weight. During
the blend it draws the selected scene backdrop at the same integer cover
as the normal scene. Original mode never enters the replacement branch.
The PNG manifest pins all ten assets and checks palette identity, format,
and the empty center. The Saturn source cards and local review images
stay under `local/`. This change adds no localized lettering.

The episode layer uses the captured card RGB over the wide floral backdrop
at the native ratio through the center too. When only some pixels have
a verified two-screen recipe, other pixels keep their native composition.
The fully visible center uses the guest frame directly.

Isolated Windows runtime SHA-256 `5c2100ae3265fbcc637a9af931468ea875452f411dccf33f5fea9f13141b1588`.
Two 6,670-frame English Episode 1 replays with the PC backdrop assets,
at 1920×1080 and 2560×1440, had the same first 6,550 guest hashes as
Original and zero interpreted blocks. The fully visible center is
pixel-identical at both scales. At frames 6075, 6095, 6500 and 6545
the measured mean RGB error relative to the same full-screen blend
was below 0.65 per channel in the center and the sampled exterior.
Frame 6570 returns to the same wide background before drawing the next
dialogue. The measured exterior and upper center return exactly.
All ten art files passed the runtime palette identity, opacity, and
package checks. Episode 1 is the gameplay witness. No new package
was built. Main workspace measured 41,263,274,196 logical bytes,
excluding duplicate hard links and junctions; the development ZIP
remains 6,315,009,692 bytes.
