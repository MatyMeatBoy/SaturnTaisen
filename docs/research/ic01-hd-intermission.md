# IC01 HD intermission

The palette-first IC01.BIN picture supplies Sakura, flowers and the Sakura Wars logo on VDP2 layer 4. Both tested disc-1 states showed the same picture underneath the Save/Status/Resume panel. The entire panel and its ornaments occupy native (184, 16, 112, 127) on layer 0. The approved wide extension remains in place.

The PC counterpart is IC0100.SPR subimage 0, a 640 × 480 picture with the same pose, flowers and baked logo. The PC picture has its original 4:3 proportion. Patch 0107 fits its height to the integer-scaled 320 × 224 canvas and anchors Sakura five native pixels from the left edge. A narrow blend follows the donor perimeter. The background color correction comes from the witnessed darkened composition.

Enhanced with HD backgrounds enabled checks the presented palette, exact layer footprint and native RGB outside the menu. The original menu and ornaments remain visible through the protected rectangle. The PC file must match its verified size and fingerprint. Unknown compositions, Original and missing assets fall back to the current native rendering.

## Verification

At 2560 × 1440 the native canvas is (320, 48, 1920, 1344), the proportional donor is (350, 48, 1792, 1344), and the untouched menu is (1424, 144, 672, 762). Strict-native comparisons on the runtime composed with RetroAchievements matched 200 guest hashes per pair and used zero interpreted blocks. Both disc-1 states drew the HD donor. Original, an unavailable PC resource and the ambiguous ICLOGO palette were pixel-identical to their controls. Each active capture changed only pixels in the donor outside the menu. Save was highlighted in captures 78 and 132. Status was highlighted in capture 198 through the same native menu pixels.

The IC catalog was rechecked against both discs and the extracted PC directory. All 16 unique IC pictures have 320 × 224 Saturn sources with byte-identical disc-1 and disc-2 copies, and 640 × 480 PC counterparts with the same artwork and logo. Scores range from 0.9893 to 0.9992 using the existing luminance signature. See [screen pair metadata](../../config/hd-screen-map.json) and the `tools/match_hd_screens.py` decoder workflow. IC01 is the only IC identity with a verified HD draw. The disc-2 copy has the same source identity and awaits a runtime witness. Further IC identities and live transitions remain open. The private build and replay receipts are under `local/work/codex-tw2`. No release package was changed.

## Other IC identities (TP1, 2026-11-19): not wired, and why

The later [IC0501 witness](ic0501-intermission-witness.md) reaches the Chapter 5 intermission naturally on disc 1. Its native plate, menu and fade are now documented.

The pairs for IC02, IC03, IC04, IC0501, IC0502, IC06-IC09 and IC1001-IC1006 are unchanged in `config/hd-screen-map.json` (palette fingerprints and PC counterparts are listed there). They were not wired in this pass because nothing could be witnessed:

- The original sweep found only chapter 1 (IC01) intermission states. At that point the other IC palettes had no live witness.
- Patch 0107 is not a table lookup. IC01 needs an anchored native screen backdrop (`kScreenBackdrops` PAUSE01, with a second palette during loading), an exact layer check (menu rectangle on layer 0, everything else on layer 4), a hash of the native RGB outside the menu, and values fitted by eye to one witnessed frame (five-pixel anchor, perimeter blend, the 17/17/16 darkening). Each of those would have to be measured again per picture, and the menu rectangle itself is only known for IC01.
- Wiring them blind would draw an unverified, possibly misaligned picture over a screen the owner has not seen. Original is unaffected either way.

To finish: reach each intermission once (chapters 2-10, both discs) with `SATRECOMP_IC01_TRACE=1`, record the palette fingerprint, layer footprint and RGB hash, add one `kScreenBackdrops` entry per identity and generalise the patch 0107 block into a table of (palette, rgb hash, PC file, size, hash, anchor, menu rectangle). Disc-1 and disc-2 copies of each picture are byte-identical, so one entry covers both.

## Attempt to reach the other intermissions (2026-11-19)

The public battle saves of banks 3, 5 and 7 were continued with `tools/chapter_jump.py` (12,000 frames, 0 untranslated blocks); the saved state at frame 11,999 is inside a dialogue. Pressing Start there for 400 frames with `SATRECOMP_IC01_TRACE=1` showed no IC picture. IC pictures belong to the intermission between episodes, which a battle save does not pass through. To unblock IC02-IC1006 a backup RAM saved at the intermission of each chapter (or a full play to the end of each episode) is needed.
