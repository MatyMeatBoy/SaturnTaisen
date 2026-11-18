# Saturn priority until its scope is complete

The user confirmed that Saturn has priority. PC execution and translation are shelved; useful findings are noted, but that platform is not integrated now. Using PC resources for the Saturn HD mod, including its extended backgrounds, remains authorized.

## Protection and evidence

- v0.1.5 published and immutable: e6910ec5152e070e10636e606dc219c3af94e62c. Main BAT and stable package preserved.
- Development: implementation/enhanced-v011, base 77b43c6; 0.2.0-dev. No delegated workers.
- Dumps, the owner's saves, and original references stay local. Tests use copies and separate profiles.
- OptiPort checked against 9673006504bf6712b320da70965bc3f65f2dd41a; installed copy identical. Consulted the general protocol, profiling, graphics/memory, and runtime adaptation.

## Work order

1. Measure and reduce Saturn/HD background preparation without changing their pixels, their quality, or the guest CD's timings. Compare empty and primed background cache, noting that the OS cache is not cleared.
2. Complete the HD mod integration for Saturn and the resource selector, keeping optional text and verified identities. Do not present a playable PC path.
3. Review scenes, subtitles, shadows, motifs, and palettes; integer composition and the maximum set that fits different resolutions. Keep the original fallback when a usable substitution is missing.
4. Complete local presentation examples in the launcher and initial selector, settings, and controller navigation; the launcher closes only after confirming the game is ready.
5. Continue validation of saving, importing, progression/battles, and a real disc swap. Prioritize any reproduction of a lockup or progress loss over optimizations or decoration.
6. Complete controllers and RetroAchievements within the confirmed scope, with explicit tests and limitations.

## Findings for later

Record PC information in the existing research documentation, distinguishing resources useful for Saturn from work needed to run/translate PC. The 19 background identities and their experimental import remain useful for the Saturn HD mod; the PC game path and its scripts remain pending.

Do not use an approved suite or a checkpoint as proof of a complete campaign. Record implemented, verified, and integrated work separately.

## Verified compact cache block

Patch 20: lossless cache for palette 8/RGB555/RGBA, migration from the previous format, DEFLATE evaluated and disabled for latency. 64 approved tests and 38 identical images; final comparison 5.128 → 1.960 s of preparation, with no general hot-path improvement. This does not equal speeding up every game load. Optional renderer diagnostics and per-background loading; reused tint buffer.

Immediate pending item: separate CPU preparation from texture upload, measure 1/2/4/8 workers against memory and cost, and avoid heavy preparation on first use. Current GPU: Direct3D11 composition verified; Saturn GPU rasterizer not yet validated. Keep the two SH-2s coordinated.

## Execution: multi-core preparation

Base 7b2b126. Runs on the existing development branch, with no agents and without touching v0.1.5.

1. Separate CPU preparation from GPU upload, keeping the public loaders. Test: prepare from a worker with no renderer and compare cache/pixels against the existing load.
2. Add early preparation with bounded workers, tasks that own their inputs, stop and join before closing SDL. Only derived cache; discs and saves are untouched. Test limits, cancellation, error, and restart.
3. Measure 1/2/4/8 workers on the same 38 backgrounds, comparing hashes and cold/hot cache. Choose a configuration from evidence.
4. Build the runtime, validate the real scene and suite, record patch 21, review, and push the block.

Ruling: the first phase pre-warms caches without holding onto surfaces or creating textures from workers; the upload stays on the window thread and the synchronous loader keeps its fallback. It avoids changing the displayed image while results arrive and bounds memory to the resources in flight. It does not yet promise to eliminate every first-use pause.

Multi-core preparation: tasks 1–4 completed. Patch 21 validated against the composed tree; native build approved; full suite 67 tests in 122.711s. Full scene identical with 0/4 workers, 19 future caches prepared. Final benchmark of 38 images: 2.102s (1 worker) → 0.478s (8), prepared cache 0.262 → 0.104s. Limits and memory in docs/research/saturn-background-workers.*.

Separate self-review (no delegation): reviewed input/surface ownership, SDL affinity, cancellation before shutdown, pool limits, concurrent publication failures, and absence of changes to guest state. Reproduced and fixed a Windows access-denied error with eight producers; acceptance only after a full comparison against the existing result. No additional critical findings in this block. This does not replace independent review or a complete campaign.

Launcher HD: HD MOD · SATURN card implemented. Folder selection or typed path, normalization of SAKURA1/WALL folders, verification/preparation in a separate process, selection persisted only after completing the 19 backgrounds, and an Enabled/Disabled control independent of the text one. The launcher keeps drawing while preparing; the dialog callback keeps shared state until closing. Build and description test approved. Real capture and activation with a virtual controller verified in an isolated profile: 19/19 prepared with 8 workers, zero failures. It does not run the PC game or import its translation.

Explicit user expansion: Saturn HD includes girl sprites, other characters, portraits, and expressions. Reproducible inventory and runtime decoding: 147 NC, 3,596 images, 147 names with Saturn candidates. KAO/KAO_P inventoried separately. Masks and compositing are still pending; HD characters are not drawn yet. See docs/research/saturn-hd-characters.md.

Finding derived from requested research: saturated MAC.L included inactive bits on both paths; synthetic reproduction recorded before the change. Ruling: fix this semantics before continuing with visual integration, because it's a concrete defect shared by native/reference. Patch 23 recorded; 11,616 cases per path and 11 approved machine tests. AOT regeneration and game build approved; full suite in progress. This case is not attributed to any observed lockup, nor is a complete campaign claimed.

MAC.L: full build approved (580,328 blocks, 708 files regenerated), full suite 68 tests in 103.707s, including real paths of 600 and 4,200 frames with zero interpreted guest instructions. Self-review of changes and tests: accumulation and saturation with no signed overflow, modular S=0 unchanged, read/alias order and flags preserved. No delegation and no claim of a complete campaign.

Characters: besides 3,596 NC, the runtime decoder processed 394 KAO portraits and 25 KAO_P: 4,015 images verified in total. Correspondence and in-game HD drawing are still pending. The exploratory fields only match on 59 of 147 pairs, so no universal index-based correspondence is used.


Later progress: patches 24–30 add an HD font with uniform proportions and ink/clip limits, a local matching tool, a first HD-portrait consumer validated by bytes/palette/origin, and an optional Zoom mode. The catalog has 304 native identities, 394 PC candidates, 191 conservative proposals, and 113 pending. The first real scene changes only the portrait; this does not equal complete NC bodies. Integration suite for that block: 76 approved tests. Zoom was tested geometrically at several resolutions and in a real 1440p scene with identical image/ink; Original remains the default option. The final composite adds a 1px adjustment top/bottom.

Next pending item: enable and validate the portrait pack in the development profile, test densities/expressions/fallbacks, and advance NC body identification. After that, campaign, disc swap, controllers, and RA continue; none of these are declared complete by these visual tests.


Test checkpoint requested in 20 minutes: 0.2-dev build to test chapter 1, without declaring the chapter/campaign complete. Added: 16:9 limit (bars on wider surfaces), preload of all enabled HD resources, M30 Bluetooth/2.4G profiles with XInput override and explicit priority bindings, reviewed menu copy, and native NC inventory with an exact link to Iris. Final verification: 82 tests in 148.379s, native build and launcher correct. Real preload: 38/38 backgrounds and 382 variants of 191 portraits with no failures. PC bodies will keep a single scale based on height and the head/torso axis; their base with no eyes/mouth is not published as a finished replacement. 16:9 tactical/HUD and PixelGen v1 extensions anchored to the map are still pending; the temporary GPU test was restored and excluded from production. Local shortcuts and an independent profile in docs/releases/v0.2-chapter1-preview.md.


## 0.1.2 portable checkpoint

- OptiPort 58843a2: README and badges with real scope, no stability percentages.
- 88 approved tests; HD processed identical to originals and corruption fallback validated.
- Launcher detects the disc and resources prepared alongside the executable; move with no toolchain tested at 1440p.
- Authorized personal delivery: English disc 1 only and processed HD resources; that ZIP is never published. Git release with no original entries.
- Pending: physical RX 6900 XT/M30 test, full continuous chapter 1, HD bodies, 16:9 tactical, and a natural disc transition.


## Visual feedback on the 0.1.2 checkpoint (current priority)

- Pre-title intro: scale the real 288×144 area located at 16,24 up to the largest integer scale; keep the embedded English subtitles. The video after Start already works.
- Intro's lilac background and title's pink background: PixelGen v1 at 16:9 with its original layers separated. Masters generated; integration and verification pending.
- Keep extended backgrounds during all scenes and transitions where a known background appears, even if the compositor doesn't recognize the dialogue.
- Global Zoom in Enhanced: image/dialogue boxes, sprites over the image, and LIPS choices; tactical keeps its real/whole plane and relative HUD.
- HD text: fix rows mixed with native ones, fourth line/descenders, stability while advancing, slightly lower the baseline and center it; glyphs/font prepared before display and coherent per-frame replacement. Include LIPS choices.
- Collect recognized text in local tables with IDs/context for future localization; do not claim a complete corpus nor publish the owner's full translation.
- PC ModHD includes MPG videos (MOVIE000..120 found), equivalent menus/HUD besides backgrounds/portraits; validate equivalence, subtitles/audio/English, and proportions before replacing. No PC execution priority.

### HD text bottom-margin adjustment

Reproduced with `post-3000.state`, Sumire's four-line dialogue. Native recognition keeps up to y212 to recognize descenders; HD drawing now clips at y208 and places rows with a fixed step of 11 pixels, versus 12, with the origin one pixel higher. Font, size, horizontal advance, and Zoom geometry are preserved. The position depends on the original row, never on the letters visible while typing.

Real capture reviewed at 2560×1440: `local/work/text-safe-margin/shot.png`, detail `dialogue.png`; first and fourth lines complete and separate from the frame. Correct local build, 22 frontend tests approved in 34.580s, Zoom geometry test approved, and a composed tree of 35 patches verified. Adjustment in the development build; previous ZIPs unmodified. The validated reader for English tables is added as a base, still without integration of the preloaded catalog.
