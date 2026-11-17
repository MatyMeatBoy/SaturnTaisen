# Sakura v0.2 presentation implementation plan

Execute inline, without workers, as requested by the user.

**Goal:** Deliver a verified v0.2 with Sakura presentation selection, integer widescreen composition, modern in-game settings and reliable launcher handoff.

**Architecture:** Keep guest video/state unchanged. Separate window-resolution UI from integer-scaled content. Extend only recognized scene backgrounds; retain Original composition as fallback. Use the existing settings and menu action model so save/load and input blocking remain authoritative.

**Tech stack:** C++20, SDL3, pinned Dear ImGui/Inter already used by launcher, Python verification and dependency patches.

**Spec:** Original approved design plus user amendments in this chat and `docs/research/v011-floral-background.md`. Target changed from v0.1.1 to v0.2 by the user.

## Constraints

- Existing v0.1.0 release and user saves stay intact.
- All game/background scaling uses integers and nearest-neighbor; only decorative excess may be cropped.
- Original retains native composition; nominal 4:3 label does not authorize fractional pixel deformation.
- Present both mode choices with truthful examples in launcher and at startup, using Sakura themed cards.
- Do not discard subtitles or actor overhang; unrecognized scenes retain original composition.
- Close interactive launcher only after confirmed game readiness; preserve errors and direct CLI wait behavior.

## Review focus

- Startup failure before first frame must retain launcher and error.
- Keyboard/controller presses used to dismiss UI must not reach guest.
- Tiny windows and ultrawide outputs must not deform content or hide UI controls.
- Sprite plane combines actors/text/frame; plane separation alone is insufficient for text replacement.
- A preliminary generated asset must not be advertised as original-preserving pixel-perfect.

## Tasks

- [x] Add and test ready-file protocol, unique per launch, first-present acknowledgement and error retention.
- [x] Expose menu view model and test navigation/actions independent of rendering.
- [x] Render Sakura menu at window resolution using embedded Inter and existing action routing.
- [ ] Add persistent presentation setting, launcher selector and initial choice cards with examples.
- [ ] Add recognized-scene integer compositor with original fallback; preserve subtitled frames.
- [ ] Finish chosen floral background and validate integer cover across resolutions.
- [ ] Investigate actual translated glyph resources and implement only verified font replacements.
- [ ] Record reproducible dependency patches, run relevant regression/parity/UI checks and inspect screenshots.
- [ ] Package v0.2 separately, verify contents and publish release with accurate coverage/limitations.

## Checkpoint: PC resource validation

English confirmed by the user: adapt the Saturn translation with its original credits. PC SPRED decoding now has bounded input/output, direct RGB555 and compressed-stream fixtures. Native local export verified KABE0100 at 640×480; its floral colors match the expected day theme. BG0000 is a flat cyan resource, so file dimensions alone do not imply a useful HD replacement. Launcher PC execution, script reinsertion and cross-version asset mapping remain unimplemented.

The frontend fixtures pass 11/11 and the actual SDL night-theme regression passes. Patches 1–13 compose to the local dependency source tree. These checks do not establish full campaign compatibility or release readiness.

## Checkpoint: PC extensions and fades

The user explicitly requested PC-derived decorative extensions when PC resources are loaded, including the PC route and Saturn+PC-HD. Separate PC day/night cherry-blossom masters now exist under assets/generated/pc-backgrounds; their provenance marks source-pixel preservation and runtime integration as unverified. All19 native PC WALL backgrounds decode at640×480. Four additional PC families are being generated from their own native references.

Enhanced Saturn backgrounds now follow NBG3 signed9-bit color offsets and sharp text samples native ink colors during fades. VDP2 sign/bank-selection tests and11 frontend fixtures pass;58 full tests pass in local/logs/v02-tests-current.log. Real1280×720 day movie/night narrative captures were inspected in local/art/v02/window-qa. The packaging resource gate now accepts only generated PNGs pinned by provenance SHA256, rejecting unpinned resources and path traversal;2 packaging tests pass.

## Development checkpoint verification

VERSION is0.2.0-dev, not a release tag. All19 PC decorative variants now have preliminary generated masters and separate provenance; runtime integration and visual corrections remain pending. The complete58-test suite passes in64.414s (local/logs/v02-tests-checkpoint.log), including actual night output and synthetic texture readback before/after color offsets. Current native runtime and launcher builds succeed.17 dependency patches compose to the local source tree. Generated asset hashes verify20/20 Saturn and19/19 PC; staged files contain no disc/BIOS/save/audio/movie formats.

Lazy loading prepares only the matching enhanced-mode background, deduplicates the identical90/91 theme, retries the program asset if a profile override fails, and leaves original mode independent of generated textures. Real owner-data previews are local only; automatic portable preview generation still needs implementation. Probar SaturnTaisenFirst v0.2 desarrollo.bat launches the local build with a separate development profile and passes its --check. The v0.1.0 release and original BAT remain intact.
