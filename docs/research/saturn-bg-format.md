# Saturn `BG*.BIN` format and BG pairing by file number (T67)

Solved 2026-11-19 by looking at the data instead of tracing the loader: the earlier probes (`pc-asset-census.md`) looked at the whole file as one bitmap and at the wrong offsets.

## Format

| Offset | Content |
| --- | --- |
| `0x0000` | header, 0x50 bytes; starts `00 01 00 01`, the rest is zero |
| `0x0050` | 288x144 picture, 8 bpp, as 36x18 cells of 8x8 pixels (64 bytes per cell, row-major cell order) |
| `0xA250` | palette: 256 big-endian RGB555 words (Saturn layout, bits 0-4 R, 5-9 G, 10-14 B) |
| `0xA450` | trailing data, not needed to draw; 45,120-byte files are zero padded to the end |

687 of the 726 `BG*` files on disc 1 are exactly 45,120 bytes and decode this way (`tools/decode_saturn_bg.py`); 39 have other sizes (92,192 / 79,952 / 71,384 bytes) and are not decoded yet. `SAKURA1/BG1001.BIN` renders as the theatre lobby, matching the PC picture. `tests/test_saturn_bg_decode.py` covers the layout synthetically.

## Pairing with the PC pictures

`BGnnnn.BIN` and the PC `BGnnnn.SPR` share the file number. This held for all 12 pairs confirmed by eye in `config/hd-scene-bg-pairs.json`, and 460 of the 687 Saturn pictures also have the same-number PC picture as their best content match (`tools/match_bg_files.py`: 48x24 luminance signature, Saturn 288x144 against the PC 576x320 top and bottom 288 rows).

`tools/build_bg_map.py` writes `config/hd-scene-bg-map.json`: 680 pairs, 542 with tier `content` (same number is the best content match or scores <= 0.10) and 138 with tier `number` (same number only; another crop, lighting or palette variant, so it needs an eye check or runtime evidence before being drawn), 7 Saturn files without a same-number PC file. Each pair carries `cells_sha256`, the SHA-256 of the 41,472 picture bytes, which is the key T74 needs to recognise the native picture at runtime (the game copies those cells to VDP2). 20 cell hashes occur twice (identical Saturn pictures under two numbers): the runtime must treat a duplicate key as ambiguous unless both numbers map to the same PC picture.

## What this does not claim

- Visually confirmed pairs are still the 12 of `hd-scene-bg-pairs.json`; the rest is number + content evidence, not an eye check, and nothing is integrated: T74 (the runtime consumer) is open and needs a runtime build (see T95).
- Disc 2 (`SAKURA2`) and the 39 other-sized BG files are not mapped.
- `NC*.BIN` (T67's other half) is not decoded; this method (look at the data per hypothesis) is the next thing to try there.
