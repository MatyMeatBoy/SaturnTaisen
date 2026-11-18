# Current pending items — SaturnTaisenFirst

Updated: 2026-11-18. Development list; it does not describe as available changes that are not yet in a ZIP. Method and entry point for another bot: [HANDOFF](HANDOFF.md) · [Shared queue](PENDIENTES.md).

Saturn is the priority. **v0.2.0-test.2 is published as a test build and its private ZIP is prepared and verified after extraction.** It includes the available widescreen paths and HD, with the declared gaps. The full chapter 1 and the campaign are still not certified; previous packages remain intact.

## P0 — before the next test ZIP

- [x] **Tactical menus:** overlap fixed in Enhanced, five tabs and confirmation/camera paths verified; independent review with no blockers and patch updated. Included in test.1; later regressions preserve the fix.

- [ ] **Continuous chapter 1 path:** reach victory of the first battle, exit, save, and reload without jumps between states. There are attacks and several turns tested; there is still no verified victory/complete chapter.

- [x] **Reproducible AOT discovery of K001–K019:** integrated in PR6. The EVT02 and EVT06 entries extended the candidate to 674,023 blocks. The combined candidate with patches 38–46 repeats the chapter 2/4 loads: 21,501 hashes and RGB matches identical to the reference, zero interpreted. This does not certify their battles or the full campaign; test.1 keeps its earlier code.

- [ ] **Widescreen per scene/transition:** close remaining gaps through the end of the chapter, including loading, interlude, maps, battle, fades, and return to title. The state sweep is partial coverage, not a complete playthrough.

- [ ] **Loading:** polish the phase/join of the LOADING generative mosaic with the native center. The widescreen layout works, but the seam is still provisional.

- [ ] **HD dialogue text:** integrate preloaded catalog and synchronization with real pagination/reveal. The English catalog is already exported locally; it is not yet the runtime's text source. Review all lines, overflows, page changes, vibration/blending with native ink, and inner centering.

- [x] **Two/three-row English HD LIPS choices:** PR16/patch0045, glyph plate and its own clip in Zoom/set. Ten profiles keep 240 hashes per scene and clean closing with no leftovers. Natural expiry and coverage of the remaining choices are still missing; the tested cases are included in test.2.

- [ ] **HD portraits/animations:** cover the chapter's pending items and maintain HD in blinking, mouth, idle, and VDP2 blends. 91/123 chapter identities have a prepared replacement; 32 remain pending. Total 201/304. The new reviews pin base and both strips by hash; only declared runtime observations certify animation. The tested white blend for 25/32 is fixed in PR9; other identities and combinations remain.

- [ ] **PC videos:** extract, identify, and integrate the equivalents in the HD mod. They are not certified as integrated. Preserve subtitles/lyrics and sync; use the maximum image area in integers.

- [ ] **Bodies, poses, HUD, and equivalent HD menus:** complete verifiable matches. Maintain uniform proportion and the head/spine/torso axis; do not deform to fill rectangles or promote ambiguous candidates.

- [ ] **Review and packaging:** record the patch tree, run final regressions, and issue a package with a new identity. Single private ZIP with English disc 1 and processed HD, without a full PC installation. Extract into a new folder and test with Windows PATH, without an external toolchain/BIOS. Physical RX 6900 XT testing is left for the target.

## Implemented/verified in development, pending delivery

- [x] Integer scale and maximum 16:9; Original and Zoom kept separate. The approved Zoom geometry is maintained.

- [x] Stage01 right extension in map coordinates: generated 39×224 strip at (656,24), anchored to scroll. Sprites outside the boundary are rasterized separately; unknown units and effects are preserved.

- [x] Day/night map backgrounds extended following their native rows.

- [x] Interlude with logo palette: secondary identity validated against the presented IC01 image, avoiding accepting other screens due to a shared palette.

- [x] Offset-free anchoring on odd windows, including 705×513.

- [x] Four transition playbacks: 3,750 hashes per frame matching between Original/Enhanced, zero interpreted blocks. These are paths from local states.

- [x] Sakura and Sumire attacks tested against the same SDK's interpreter; local base extended to 614,024 static candidates/blocks. This does not measure executed coverage of the whole campaign.

- [x] Local English catalog: 29,725 records per disc, 59,450 with context from both discs; offsets, IDs, bytes, and hashes preserved. Game data outside Git.

- [x] Portrait audit: 191/304 global identities accepted, 113 pending; 382 prepared variants reviewed. Coverage does not equal all animations during gameplay.

- [x] Packagers: unique names, collision rejection, and real dimension check for the tactical strip; never include the original map context in the normal release.

## P1 — complete Saturn and unified product

- [ ] Validate the full campaign, overlays of all chapters, and alternate routes, avoiding hangs and progress loss.

- [ ] Both discs mandatory in the final product; real and natural transition, with save/reload before and after.

- [ ] Import and compare saves from emulator formats; keep sources and document formats actually tested.

- [ ] Check LIPS inputs and dialogue advance/skip with animations, latency, and sustained presses against the original.

- [ ] M30: validate the documented XInput profile with the user and GUID recognition; physically check Bluetooth/2.4G. DInput still has no report. Maintain remapping and general SDL3 compatibility.

- [ ] RetroAchievements game 16546: exact catalog, 1:1 conditions, local badges, tab, themed popup, offline local mode, and softcore login/sync. Do not announce support as available: it is still pending. Do not guess conditions or replace them with custom achievements.

- [ ] Launcher and in-game settings: finish controller navigation, Original/Enhanced selector with examples, exit tests once the game is ready, and persistent configuration.

- [ ] Complete background inventory per chapter, map/novel seams, and palette variants; extend each correct identity, with no incorrect global background between scenes.

- [ ] Measure real loads and first-use pauses, cold/warm cache, RAM/VRAM, and GPU. Remove the auxiliary widescreen raster from Original mode when safe. Do not attribute improvements to SSD/multicore without measurement.

- [ ] README, badges, and reports tied to the actually published version; never invented campaign percentages.

## P2 — after Saturn

- [ ] Playable PC path and adaptation of the English Saturn translation.

- [ ] PC background extensions when that mod is loaded, keeping proportions.

- [ ] Parallel Spanish patch, handled by Claude per the user's new instruction. Already provide the structured English scripts and their controls; do not wait until the end of Saturn for that preparation. Other languages will be decided later.

## Evidence and documents

[Handoff](HANDOFF.md) · [Progression](research/chapter1-battle-progress.md) · [Transitions](research/chapter1-wide-transitions.md) · [Independent menu reference](research/tactical-menu-independent-reference.md) · [PixelGen v1](research/pixelgen-v1.md) · [Catalog](research/dialogue-catalog.md) · [Portraits](research/portrait-animation-coverage.md).

Update this list when closing each block. Mark a task only with the corresponding evidence, and note whether the change is still local or already packaged.

## Integrated checkpoint after test.1

Main `d7e94cd` includes patches up to 0046 and the 201 reviewed portraits. The [HD_PROGRESS](HD_PROGRESS.md) report separates preparation, integration, and verification. There is no verified global percentage while denominators and tests for all categories are still missing.

- PR11/13: continuous floral panel, Sumire/María border text, left map cursor, and direct Zoom entry during the dining-room fade.
- PR16: HD text for two/three-row English choices.
- PR18: first New Game film with clean background before/after and extended video; 6201 hashes and six native RGB preserved. 16:9 petals and episode card are still T33.
- PR15/17/19: ten additional reviewed matches, prepared from 191 to 201; animations only verified where evidence is recorded.

The combined candidate of 674,023 blocks is in the owner's `local/build/polish-test2-final/sakura.exe`, SHA256 `a12b26d1990cabf9c54da562e4f05a9c842c7078d1b5c8ae3fe935a426c91418`. Its chapter 2/4 loads pass 9501/12000 frames respectively. It is included in test.2 and its transfer is verified; see the delivery receipt. PC videos, equivalent bodies/HUD, and RetroAchievements remain pending.

## test.2 delivery

Public release 317,215,196 bytes and personal ZIP 725,331,460 bytes, with clean source 92edea7. The latest fixes up to 0046 and the 201 prepared are included. New extraction: launcher, HD scene, battle, and first film 6201 frames with Windows PATH; 402 variants with no failures and zero interpreted. [Validation](releases/v0.2.0-test.2-validation.json). Test.1 and previous packages remain intact. This does not close T02/T03 or T26.
