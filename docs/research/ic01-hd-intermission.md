# IC01 HD intermission

The palette-first IC01.BIN picture supplies Sakura, flowers and the Sakura Wars logo on VDP2 layer 4. Both tested disc-1 states showed the same picture underneath the Save/Status/Resume panel. The entire panel and its ornaments occupy native (184, 16, 112, 127) on layer 0. The approved wide extension remains in place.

The PC counterpart is IC0100.SPR subimage 0, a 640 × 480 picture with the same pose, flowers and baked logo. The PC picture has its original 4:3 proportion. Patch 0107 fits its height to the integer-scaled 320 × 224 canvas and anchors Sakura five native pixels from the left edge. A narrow blend follows the donor perimeter. The background color correction comes from the witnessed darkened composition.

Enhanced with HD backgrounds enabled checks the presented palette, exact layer footprint and native RGB outside the menu. The original menu and ornaments remain visible through the protected rectangle. The PC file must match its verified size and fingerprint. Unknown compositions, Original and missing assets fall back to the current native rendering.

## Verification

At 2560 × 1440 the native canvas is (320, 48, 1920, 1344), the proportional donor is (350, 48, 1792, 1344), and the untouched menu is (1424, 144, 672, 762). Strict-native comparisons on the runtime composed with RetroAchievements matched 200 guest hashes per pair and used zero interpreted blocks. Both disc-1 states drew the HD donor. Original, an unavailable PC resource and the ambiguous ICLOGO palette were pixel-identical to their controls. Each active capture changed only pixels in the donor outside the menu. Save was highlighted in captures 78 and 132. Status was highlighted in capture 198 through the same native menu pixels.

The IC catalog was rechecked against both discs and the extracted PC directory. All 16 unique IC pictures have 320 × 224 Saturn sources with byte-identical disc-1 and disc-2 copies, and 640 × 480 PC counterparts with the same artwork and logo. Scores range from 0.9893 to 0.9992 using the existing luminance signature. See [screen pair metadata](../../config/hd-screen-map.json) and the `tools/match_hd_screens.py` decoder workflow. IC01 is the only IC identity with a verified HD draw. The disc-2 copy has the same source identity and awaits a runtime witness. Further IC identities and live transitions remain open. The private build and replay receipts are under `local/work/codex-tw2`. No release package was changed.
