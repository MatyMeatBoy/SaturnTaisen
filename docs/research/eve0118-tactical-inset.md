# EVE0118 tactical inset

The episode 1 farewell on English disc 1 shows the four-character victory pose against blossoms. The VDP2 layer 5 palette is `D53405084F3310B9` and the opaque RGB plate hashes to `C36AFC31CF935785`. The plate occupies native (16, 8) through (303, 151).

The matching PC asset is subimage 0 of `SAKURA2/BG/BBG101.SPR`. A visual comparison and the 2:1 correlation fit identify the crop (0, 24, 564, 282) in the 576×320 source. The measured luminance correlation is 0.948. The Enhanced tactical presenter checks the native palette and opaque plate, then uses the shared inset loader to verify the PC file and draw at the tactical canvas's integer scale.

## In-game verification

At 2560×1440, the candidate and its prior runtime used the same Enhanced settings and PC assets. All 2,803 guest frame hashes matched, with zero interpreted blocks. The active sample at pass 2601 differed exactly within (416, 96) through (2143, 959). Samples at passes 2401 and 2801 were pixel-identical. Original mode retained identical captures and guest hashes with PC HD backgrounds on or off. The missing-PC control and the disabled-PC control retained identical native output.

Private receipts and captures are in `local/work/codex-tw2/eve0118-composed`. Validation covers the opaque disc 1 farewell witness. Disc 2 and blended variants remain open. No package change.
