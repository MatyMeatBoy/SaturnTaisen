# Saturn unit banks (`SAKURA2/UNITnn.BIN`) format (TS11a)

Decoder: `tools/decode_saturn_units.py` (tests `tests/test_decode_saturn_units.py`). Data: `config/hd-saturn-unit-images.json` (names, offsets, sizes, SHA-256; no pixels) and `config/hd-tactical-unit-pairs.json` (pairing result). Verified on all 27 banks of both discs (10 distinct contents).

## Layout

- `0x00`: 26 pairs of big-endian u32 `(offset, size)`, 0xD0 bytes. Entries are contiguous from 0xD0 and end exactly at the end of the file. Slots 1-11, 16 and 17 are empty in every bank.
- Slot 0 is a compressed image set: the game's LZ (`tools/es/red_lz.py`, SH-2 routine 0x0600A164). The whole slot is consumed up to its end marker (`size - 2` bytes used). UNIT04: 0x71AC bytes -> 66,512.
- Slots 18-22 and 24 are raw (uncompressed) image sets.
- Slots 12-14 are 64-colour palettes (0x80 bytes), slot 15 is 32 or 16 colours, slots 23 and 25 are 16 colours: big-endian RGB555 words, bit 15 set when opaque. Banks differ mostly here (colour variants). The 8-bit images only use indices below 64 (maximum seen 61).

## Image set

`u16 count`, 14 zero bytes, `count` records of 16 bytes (`u16 w, u16 h, u16 format, u16 colour field, u32 offset, u32 size`), then the pixel area; `offset` is relative to the pixel area. Format 4 is 8 bits per pixel (`size = w*h`), format 0 is 4 bits per pixel, high nibble first (`size = w*h/2`). Index 0 is clear. Pixels are linear (VDP1 sprite layout). The colour field is a per-set constant (0x5F0, 0x300, 0x3A0, 0x5E0; 0 for the 8-bit sets), probably a VDP1 colour bank value; its meaning is not verified. Every set ends exactly where its records say (the validation used for all banks).

| Bank group | Slot 0 | Slot 20 | Slot 21 | Banks |
|---|---|---|---|---|
| Disc 1 and `UNIT12/13` | 120 images, 66,512 bytes | 62 images (8 bit) | 24 | UNIT01-11, 12, 13, 21, 22 |
| Disc 2 `UNIT14-20, 23-26` | 121 images, 73,120 bytes | 53 images (8 bit) | 15 | UNIT14-20, 23-26 |

Slots 18, 19, 22 and 24 are identical in every bank (8, 40, 10, 43 images). 461 distinct images in total (`distinct_images` in the inventory).

## What the images are

A local look (not stored) shows the images are **body pieces** (torso with head, arms, legs, small attachments) of a Koubu in the palette of slot 12, 8 to 40 pixels wide, not whole frames. The tables that say how pieces are assembled into a frame are not in these banks (slots 1-11, 16, 17 are empty): they must live in the program or in another bank (leads from TS11: `Nnn`, `Knn`, `Hnn`, `Gnn`, `GKnn`, `FIXnn`, `GATTAI.BIN`; not opened here).

## Pairing attempt with the 291 PC SPR

Result: 0 paired, 3 ambiguous leads, everything else without counterpart (`config/hd-tactical-unit-pairs.json`).

1. A silhouette signature (bounding box, 32x32, like `match_hd_items.py`) gives high scores only for plain square blocks and ties (margin 0); it cannot tell pieces apart.
2. A masked greyscale cross-correlation of each piece of 24x24 or more (43 of UNIT04 slot 0, palette slot 12) inside each PC image reduced by 2, over the first 40 PC `PLAYER` files, reached at most 0.76 (`OOGAMI/BU_KOUBU.SPR`, three pieces at 0.72-0.76). The tier `content` needs 0.90, so nothing is confirmed. The remaining 251 PC files and the other banks were not scanned (a scratch numpy probe, about 2 minutes for 40 files; not committed because `tools/` does not depend on numpy).

What is missing: (a) the frame assembly tables, to compare whole frames with the PC frames; (b) the 256-colour table the 8-bit sets use (palette slots only hold 64 colours); (c) which PC folder corresponds to which bank (the PC has per-character folders `PLAYER`, `PL_AT`, `PL_SP`, `ZAKO`, `BOSS`...). Next step: trace the SH-2 code that loads `UNITnn.BIN` to find the frame/layout tables, then assemble frames and reuse the correlation. The register statuses of the 26 `tactical-units` entries stay `unknown`, so `docs/HD_PROGRESS.md` and `config/hd-chapter-coverage.json` are not regenerated.
