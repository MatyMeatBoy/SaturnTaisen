# Dialogue rows that keep the Saturn font

The rows flagged in Sumire's and Maria's scenes keep the Saturn font for the same reason. In both, the last cell contains a valid nine-pixel-wide glyph with an advance of eight. The ink overshoots the recognition limit by one pixel. The catalog keeps all three rows of each record.

## Reproduction

From `local/work/sakura/theater.state`, run `tests/theater-dialogues.movie` on English disc 1. States saved before frames 1,499, 1,504 and 1,520 contain the three rows at Y=160, 172 and 184. The run was done on the isolated binary with strict AOT and zero interpreted blocks.

In all three states, the last letter of row Y=172 is a `w` at X=296. Its 16×16 tile matches byte for byte the verified English ASCII-119 glyph from atlas `0100KNJ.BIN`. Tile FNV-1a `66BBC3BE84C1B486`. The row has a single entry per X and all its other glyphs are recognized. The `w` contributes exactly two pixels outside the recognition limit, at `(304,176)` and `(304,177)`. `NarrativeInkFits` requires X<304 and flags the whole row as invalid. The other two rows pass this check.

## Another case with the same limit

Maria's final row corresponds to record `1:/SAKURA1/0100TBL.BIN:50064:498`. From `local/work/sakura/chapter1-continuous-47999.state`, run `tests/maria-click.movie`. States saved before 719, 839 and 959 keep the same trailing ellipsis. The tile placed at X=296, Y=184 matches CP1252 `0x85` (U+2026) unambiguously, FNV-1a `283D49C0BB2786CE`. A single ink pixel at `(304,194)` falls outside `NarrativeInkFits`. There are no duplicate positions or unknown glyphs.

| Scene | Row | Native tile | Ink outside X<304 |
| --- | --- | --- | --- |
| Sumire, dining room | Y=172 | `w`, X=296 | `(304,176)` and `(304,177)` |
| Maria | Y=184 | U+2026, X=296 | `(304,194)` |

## Border pixels and fix criteria

Synchronized captures show the three out-of-area pixels in RGB `232,232,232`, with the same VDP1 contribution in the final output. At X=304, the VDP2 dialogue plane is already in the dark border tone `120,120,120`. At X=303 it's still the light fill. The neighboring gold frame molding in that same column also belongs to VDP1.

In Sumire's scene, two strokes from adjacent rows also coincide. The descender of `p` at X=112, Y=160 and the ascender of `h` at X=112, Y=172 share `(113,173)` and `(114,173)`. Restoring those pixels must include both rows and recover what was there before the first glyph.

To convert all cells to HD while keeping the X<304 crop, the plate must accurately restore the VDP1 pixel that was under each glyph. The `underSprites` buffer excludes the whole VDP1 layer and by itself does not provide that restoration. The plate would need to preserve the molding before the glyph and the VDP2 layers, and verify draw order, ink match and overflow extent. Unknown glyphs, duplicate positions, occlusion or a missing plate must keep the safe fallback. Glyph identity and its out-of-area pixels must be validated before removing them.

To test the fix, capture both lines before and after the last cell appears. Each row's baseline must stay stable while revealing. Keep the output crop and check the border against an inkless plate. Also compare hashes against Original.

`local/work/hd-text-row-rejections` contains the states and the VDP1 command audit script. `frame1` and `maria-frame1` hold the synchronized plane captures. The diagnosis covers both observed rows.

## Glyph plate verification

The tested candidate records the VDP1 value before the first glyph and the identifiers of up to two glyphs writing the same pixel. It reuses the native compositor to recover the image before the ink. If two rows overlap, it validates all their cells before restoring the shared area. Later writes unrelated to the glyph invalidate the capture, even when they repeat the same value. The HD crop stays at X<304.

In both scenes, 1600×900 captures were taken with the same assets and three combinations: Original, Enhanced with HD text, and Enhanced with Saturn text. The trace confirms a valid plate and HD text at Y=160 and Y=172 for Sumire and at Y=184 for Maria. In the three positions that had invaded the molding, the native ink gray is restored to the molding's gold: RGB `152,112,40` and `88,56,0` in Sumire's scene and `152,112,40` in Maria's. Original's captures match test.1 pixel for pixel. The 12 hashes per scene match across all profiles tested, with zero interpreted blocks.

The synthetic test `tests/test_glyph_plate.cpp` covers a molding under the glyph, two writers, an unrelated write with the same value, invalidation by a guest write, and applying the native color adjustment. Visual verification is limited to these two already-written samples. Substitution of the LIPS choices remains a later application.
