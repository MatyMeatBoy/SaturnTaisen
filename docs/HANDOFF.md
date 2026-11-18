# Technical and artistic handoff

Updated: 2026-11-18. For another bot or collaborator joining SaturnTaisenFirst. Operational status in [PENDIENTES](PENDIENTES.md); the research documents keep the detailed evidence.

## Goal and user agreements

AOT static recompilation of Sakura Taisen Saturn, Windows x64, both SH-2. Saturn first; playable PC/PC translation afterward. PC assets are already used for the Saturn HD mod. English translation reused/adapted from the Saturn team; the corpus is not published in Git.

Original preserves the native presentation. Enhanced recomposes scenes to **16:9 maximum**, without ultrawide and with integers/nearest. Do not horizontally enlarge the raster to simulate widescreen. Scene Original keeps joint scaling; Zoom uses independent integers for image and dialogue. The user approved the current Zoom framing and canceled the last +2 px shift: **do not move it again on your own initiative**. Image and box shadows are independent, drawn in the correct order, with no duplicate shadow.

The launcher offers modes and examples and closes once the game confirms it is ready. In-game settings open with Start+Select/Back. HD/text are optional; substitutions require identity and evidence, with a fallback when a valid asset is missing. The final product unifies both discs; the single-disc personal package is an already-authorized testing exception.

## Upon joining

1. Read `AGENTS.md`, this guide, and `docs/PENDIENTES.md`; check the date and later changes.
2. Run `git status --short`, `git branch --show-current`, and check active collaborators. Do not clean up someone else's dirty tree.
3. Integrated base for this block: `main` at `d54919e`, after PR32/33. Always check the current HEAD, branch, and status before working. `VERSION`: 0.2.0-test.3, prerelease published from `72affb2`. Its runtime is 674,182/patch0049 (`377cb29b…`); do not infer the local executable from the version. T11/patch0050 is integrated via PR34 with an independent candidate (`df68e9db…`), not packaged; test.3 keeps patch0049.
4. Agree on your own files and a specific task. Do not edit `frontend_sdl.cpp`, the renderer, or patches at the same time as someone else; do not build on top of another bot's incomplete edit.
5. Create a private, exclusive results folder per trial. Images can be overwritten by accident: check absolute path, visual content, and SHA before drawing conclusions.

When closing this update, `wide_transitions` finished the fix and released `video/renderer.h`, `renderer.cpp`, `layers.cpp`, and `port/tactical_menu.h`. The coordinator integrated the block and patch 36 via PR #4, with review and tests. **Check with them before touching those files or recapturing the patch.** Agent names and this assignment are session state, not a permanent reservation.

Useful work for a second bot without stepping on that integration: improve the inventory/matching of the chapter's 42 pending identities, prepare offline catalog/text-page tools, or inventory PC video/HUD equivalences. Agree on a single task and its files; deliver a manifest/proposal and evidence, without automatically promoting doubtful candidates or rewriting the renderer. If you discover a bug in someone else's file, send a reproduction and proposal to the owner.

## Workspace map

### Cleanup and transfer — 2026-11-18

Six old worktrees were removed via Git, preserving their commits. What remains is the main repository and a single auxiliary copy. New tasks must respect the limit and the cleanup rules in `AGENTS.md`.

The measurement after cleanup was **19,857,953,183 bytes (18.494 GiB), 67,822 files** in the main project. Verified duplicates and regenerable intermediates were removed; dumps, BIOS, scripts, prepared assets, selected checkpoints, and issued packages were kept. The SDK48 reference is kept compressed, with CRC and SHA of the restored executable verified. Detailed private reports are alongside the delivery, outside the project.

The already-delivered development ZIP remains immutable: `D:\01Claude\SaturnTaisenFirst-DEV-transfer-20261118\SaturnTaisenFirst-Development-Completo.zip`, 6,315,009,692 bytes, SHA256 `806b9e8803574e9fdea58ffce9b8ca1247a691f1e49295499f399ee5425e2059`. After restoring it on the other PC, update from Git to get these rules added after its creation. The cleanup does not certify new campaign progress nor change the test version.

| Path relative to `D:\01Claude\Sakurawars` | Use |
| --- | --- |
| `local/deps/satrecomp` | SDK pinned in `config/dependencies.json`; local edit, changes exported as patches. |
| `patches/0035-...patch`, `0036-...patch` | HD/GUID consistency and new extensions/presentation. 36 already contains the menu fix and the test.1 version; recapture only for new SDK changes. |
| `local/build/sakura/sakura.exe` | Development runtime; may be later than the public ZIP. |
| `local/work/sakura` | States and private AOT discovery base (`blocks.txt`, `gen`, `block-order.json`). |
| `local/prepared/disc1`, `disc2` | Own prepared translated discs; do not publish. |
| `local/art/tactics/stage01` | References, generations, approved composition, and `approved.json`; includes proprietary context. |
| `assets/generated` | Selected generative assets, manifests, and hashes; do not copy full game references here. |
| `local/work/worker-wide-transitions` | Layer probes, transitions, commands, and menu fix. |
| `local/work/worker-menu-oracle` | Independent Beetle Saturn reference; private harness/states/captures. |
| `local/work/dialogue-catalog-worker` | Extracted English catalog JSONL/CSV, local only. |
| `local/work/portrait-coverage-worker` | Portrait coverage and blend audit. |
| `local/releases` | Already issued packages: immutable. |

Never publish discs, BIOS, original SPR/FILM/MPG, scripts, states, or extracted images. A manifest does not turn a composition with original pixels into publishable generative art. The personal ZIP may include the own files expressly authorized; it is not uploaded to GitHub.

## Debugging and validation method

T02: closing the first battle revealed two routines copied to 06002000. The previous state contains 238 bytes from /SAKURA; on execution, 0SLG replaces them with 206 bytes. The WATCH test of the execution instant is the correct attribution for the 06002042 failure. Logging both variants produces 674,182 blocks; isolated candidate e7dd1c0… passed Save Complete/Resume with 3,000 hashes and 15 RGB matches identical to the interpreter and 0 interpreted. The 109,740-frame chain is still being tested. See [battle follow-up](research/chapter1-victory-followup.md); do not use candidate 674,110 as a fix or modify test.2.

Reproduce before changing anything. Save initial state, SRAM copy, inputs/movie, settings, executable/hash, and logs. Isolate profiles and remove inherited `SATRECOMP_*` variables except those explicitly chosen. Use `SATRECOMP_STRICT_NATIVE=1` and check zero interpreted blocks for AOT paths.

In LIPS tests, a panel still visible may already be confirmed and closing. Equality between two executables proves parity, but not that the `select` trial changed the choice. Require postconditions: highlight bank on another row, panel closed before the control without inputs, and the corresponding response destination; for timeout, leave neutral input and observe the later destination. If a seed does not allow selecting, look for an earlier state without modifying the clock or the guest. In T11 the earlier three-option seed already allowed observing those differences; the evidence and limits are kept in PR34.

Separate three questions: does the native logic fail, does the host presentation fail, or is it a defect in the translated disc? Compare Original/Enhanced and, when relevant, AOT/interpreter of the same SDK. That last comparison **is not independent**: they can share an emulated hardware defect. Beetle Saturn has been used only as a diagnostic oracle; it does not replace the project's AOT runtime.

Per-frame hashes cover the `StateHash` contract, not every serialized field. Add pixel, audio/input, or save comparisons depending on the failure. A correct capture does not prove the transition; an attack does not prove victory; a test from a saved state does not prove a full boot. Review images individually with their label/path to avoid associating one capture with another.

When analyzing states, read the actual serializer. In the current format: vector 0 HighRAM, 1 LowRAM, **2 sound RAM**, 3 VDP1 VRAM, 4/5 framebuffers, **6 VDP2 VRAM**, 7 CRAM. A previous misreading that confused sound RAM with VDP2 was corrected; do not reuse that assumption.

Host changes must not modify the guest's RAM/VRAM, framebuffer, or inputs. Capture commands/palettes/textures associated with the **presented framebuffer**, not the last one written. In animated sprites, distinguish phase delay, missing data, occlusion, and VDP2 blending. Do not hide a matching failure with an approximate substitution.

## PixelGen v1: how we are making the art

1. Identify the actual scene/asset/layer/palette. Separate background, characters, image/video, box, and HUD before generating. The user's annotated captures guide this; they do not serve as the sole geometry source.
2. Save a clean reference and keep the original intact in `local/`; define a protected zone and the missing strip. Request generation with context, the same visual language, silhouettes/materials/palette/dithering, and pixel density. Do not ask for a redesign of the center.
3. Use the built-in ImageGen tool for generation/editing. Read the applicable skills. Do not silently switch to a paid API or replace generation with programmatic editing. The deterministic exporter does crop/normalize **the already-approved strip** as technical integration processing.
4. Review at native size and at real integers: outlines, scale of flowers/bricks/grass, light, repetition, seams, and absence of noise/mixed densities. A good thumbnail is not enough. If the center changes, do not accept it as a full replacement: keep only the authorized generated zone.
5. Normalize to the native grid and palette at runtime. Do not claim pixel-perfect just because the PNG is large or looks sharp. Save the generated source, prompt/summary, chosen variant, SHA, geometry, and provenance.
6. For maps, anchor in **world and scroll coordinates**, never to the screen edge. Keep units/effects/HUD in front, with no new tiles or collisions. Validate by moving the camera and changing resolution.
7. For backgrounds with a protected original center, align the center of the extended texture with the same integer viewport; derive the anchor from the native center to avoid rounding differences on odd windows. Preserve fades and color offsets.
8. Integrate only selected generated assets with an allowlist and manifest. Reject incorrect hashes, dimensions, or identity when packaging. Document what is provisional: LOADING still needs the pattern phase at the seam polished.

Approved Stage01 case: the output reference is **940×448**, equivalent to native **438×224** with world origin (277,24), not a uniform ×2 enlargement. The approved generated zone x814–895 is exported to **39×224** and placed at **(656,24)**. The map ends at x655. Do not revert to the old provisional 41×224/origin (655,48) calculation. The exported strip is at `assets/generated/tactical-extensions/STAGE01-right-v1.png`; original context only in `local/`. See [PixelGen v1](research/pixelgen-v1.md).

Floral motifs change depending on scene/palette. Extend each identity and follow its real transition, without keeping the pink background where it should be blue, map, or interlude. The floral background with more flowers was the user's preferred variant. Generated screen backgrounds and the tactical strip have separate allowlists.

## HD mod and text

PC substitutions keep uniform proportion, height-based scale, and the head/torso axis of the original. No stretching width/height independently. Distinguish body/pose, portrait, and eye/mouth parts; animations require the full family or a coherent fallback. Ambiguous matches are rejected. Check VDP2 blends before attributing a blink to a missing animation.

The HD font must respect native size, advance, and spacing with natural proportion, with no wide appearance. Four lines must fit with margin inside the frame. Glyphs are prepared before the first frame and the English catalog is preloaded once when HD is activated. Verified narrative uses catalog views with a native-cell mask; choices keep command recognition until their full set is identified. The exported catalog keeps IDs, CP1252 bytes, controls, offsets, and disc context for integration and future translations. Do not use OCR as the sole source if a native table exists.

T11/patch0048 adds a sealed catalog and a logging witness captured alongside the framebuffer by software. The full table in Low WRAM 0x00224000 must match; the BE32 pointer is in High WRAM 0x0606851C. It keeps 29,725 records, 29,723 preparable; the two tabulators remain intact. Patch0049 lends the preloaded lines with a mask tested per tile/cell: it does not show the whole record just because the pointer matches. Command origin x64, ink clipping x56; do not confuse them or move the UI. 14 cases checked 2,280 hashes and 104 identical RGB pairs, with 0 interpreted. LIPS needs to identify the full set separately, and other paths require coverage. Detail in [dialogue preload](research/dialogue-preload-runtime.md); test.2 remains unchanged.

LIPS requires transformation of the top panel and a pixel plate that preserves the character under the transparency. `underSprites` removes the entire VDP1 layer: it does not work to erase only the choice glyphs. See [transition diagnosis](research/chapter1-wide-transitions.md).

## Commands and environment precautions

PowerShell; toolchain `C:\msys64\clang64`. The normal environment's Python has Pillow. If MSYS is prepended to PATH before calling `python`, a different Python without Pillow may be chosen. Use a separate process or the absolute path to the usual Python.

```powershell
git status --short
python -m unittest discover -s tests -p test_frontend_safety.py -v
python -m unittest discover -s tests -p test_package_art.py -v
python -m unittest discover -s tests -p test_personal_bundle.py -v
python -m unittest discover -s tests -p test_chapter1_widescreen_runtime.py -v
python -m unittest discover -s tests -p test_widescreen_transitions.py -v
```

Runtime tests require private fixtures and must skip missing paths. Add tests targeted at the failure; do not repeat expensive suites without new changes that justify it. Camera/menu tests must preserve hashes and pixels outside the zone deliberately changed.

To build an already-consistent dependency with agreed ownership:

```powershell
$env:PATH='C:\msys64\clang64\bin;'+$env:PATH
cmake --build local/build/sakura -j 8
```

`python tools/build_runtime.py build` first checks the patch tree. `recompile` needs the private base `blocks.txt`; it is not equivalent to automatically discovering every function of the game. Do not regenerate AOT for a UI tweak. The independent-menu repro is documented in [tactical reference](research/tactical-menu-independent-reference.md).

To close the SDK patch: create a temporary Git index in the dependency, start from the pinned commit, apply the previous patches to the index, compute that base tree, add the local tree to the **temporary** index, and export the binary diff of the last block. Do not use/reset another collaborator's real index. The current private script is `local/work/capture-current-patch36.py`; review its scope before running it. Then validate `build_runtime.dependency()`. Do not do this while there are half-edited SDK files.

## Deliveries and communication

When closing a task: explain what changed, what was tested, what is still pending, and whether it is only in development or in a package. Update `docs/PENDIENTES.md` and the area's report. Keep the names and hashes of previous ZIPs; new delivery, new identity. Never claim the campaign or chapter is complete from passing partial tests.

Normal release: code, DLL, and allowed generative assets; game assets provided by the user. Personal ZIP: new build + own English disc 1 + already-processed HD, all together for transfer, without a full PC game. It must boot after extraction into another directory without Python/MSYS/toolkits. The final product will require both discs. RX 6900 XT and physical M30 variants require user testing on the corresponding hardware.

## PR integration

The user expressly authorized the Codex coordinator to integrate PRs on 2026-11-18. Claude and the other workers deliver PRs; the coordinator reviews the diff, head SHA, tests, and conflicts, integrates, and updates the queue. Each branch takes an ID from `docs/PENDIENTES.md`; check main and open PRs before claiming it. Avoid direct commits to main and PRs that mix unrelated tasks. An integration does not automatically publish a release.

PRs #1 (queue), #2 (line endings), and #3 (research index) were reviewed and integrated. The #2 conflict was resolved by keeping the newer queue; never restore an old list to make a PR fit. When adding reports, also update `docs/research/README.md`, checked by `test_research_index.py`.

## Delivery and current material for Claude

v0.2.0-test.1 published; private personal ZIP of 708,495,279 bytes, with own English disc 1 and processed HD. Tested after extraction into a new folder and Windows PATH: HD scene and battle, 38/38 backgrounds, 382 variants, zero interpreted blocks. PC videos not integrated: the Saturn videos are on the included disc 1. No complete chapter is claimed, nor physical RX6900XT testing.

Editable scripts: `local/work/spanish-translation`, 56 tables, 29,725 canonical EN entries with an empty ES field and alias to disc2. Index: `local/work/scene-index`, six simple tags (video, dialogue, choice, map, battle, menu). It inventories both discs and 54 videos, but only nine runtime observations are annotated; do not assume a video has no text, nor authorize Zoom based on a file candidate. The index still does not control runtime presentation.

## Automated tests without interrupting the owner

To test the runtime, run the isolated binary `sakura.exe` directly, with absolute `--disc`, `--settings`, `--backup`, and `SATRECOMP_WINDOW_HIDDEN=1`. Do not use the launcher's `--play` for a replay that is not testing the launcher itself. If testing the launcher, prepare a valid private profile and an absolute `SATURN_TAISEN_FIRST_HOME` before starting it: a missing profile can open the setup dialog on top of the owner's game. Do not kill processes by name or overwrite an executable in use. On November 18 this warning was observed while a test of the Spanish preview used `timeout … SaturnTaisenFirst.exe --play`; the Spanish launcher.ini kept its configured disc. Local log: `local/work/coordination-current.json`.

## Handoff of the patch0046 and portraits201 checkpoint

PRs up to 19 are integrated into main `d7e94cd`; always check the current HEAD. The shared SDK matches the composite tree 0001..0046 of the coordinator's checkout. The changes are already exported: do not restore the SDK to fit an old `config/dependencies.json` from another worktree. Bring in the new commits or use the updated checkout, preserving any changes made by others.

Different candidates, all private: `local/build/visual-fixes-candidate/sakura.exe` tests presentation with 614,024 blocks; `local/build/polish-test2-final/sakura.exe` combines the same host with 674,023 and passes the 9501/12000 loads of chapters 2/4. The shared CMake recovered its usual output directory, without building on top of the owner's exe. Before another build, check processes again and choose an isolated destination.

The most recent prepared set contains 201 portraits and 19 backgrounds, in `local/work/portrait-chapter1-third-review/prepared-hd`; the coordinator reproduced its 404 portrait files byte for byte from the original project's 191 and the ten hash-locked approvals. Testing the unobserved animations and the remaining 32 identities of chapter 1 is still pending. T45 proposes offline reordering for 00a1; not yet approved or implemented.

First video: use the witness captured with the framebuffer; never infer playback from a residual FILM header or the absence of subtitles. The phases and their limits are in first-film-script-phase.md and first-film-transition-fix.md. The episode label shares a cursor with the exit and is kept because of its image layer. The fixes from this checkpoint were later incorporated into test.2; test.1 remains intact.

## Packaging from an updated worktree

package_release.py accepts --owner-root to read the owner's private dependencies/licenses and --build-dir to select an isolated launcher/importer; the code, VERSION, allowed art, and manifest commit remain those of the checkout that was run. --runtime selects the AOT candidate. package_personal_bundle.py accepts --owner-root to locate only the private disc, previews, and fixtures. Both reject existing delivery destinations.

For test.2, the launcher is prepared in local/build/launcher-test2 with output local/build/test2-package-binaries and GAME_VERSION 0.2.0-test.2; it does not overwrite the owner's launcher. The personal profile keeps HD enabled (background/portrait values 0) and preload 1. The personal manifest also lists hashes of generated BAT/defaults/text, aside from their source assets; it excludes itself from the recursive inventory.

## Verified test.2 delivery

v0.2.0-test.2 published with clean source 92edea7; public ZIP 317,215,196 bytes. Personal bundle 725,331,460 bytes, local only, English disc 1 and HD 201/19 backgrounds. Clean extraction with Windows PATH: launcher, HD scene, battle, and 6201-frame film work; 402 variants with no failures and zero interpreted. The public metadata receipt is in docs/releases/v0.2.0-test.2-validation.json; the private detail in local/work/test2-relocation-report.json. The bytes and label of previous packages are not changed.

Later work: wide_transitions continues T02a without modifying RAM or the SDK. T48 was recorded in patch0047 and the composite tree was validated. Its isolated candidate 674,023 passed four profiles/8 runs of 90 frames with 402 variants. The header no longer has unrecorded edits; check the integrated commit before the next build. The test.2 binary and its ZIPs remain unchanged during this work.

## Candidate after test.2: portrait catalog fallback

local/build/portrait-fallback-candidate/sakura-674.exe contains patch0047; it does not replace the test.2 binaries. The runtime tests the included package when the profile's catalog fails authentication, preserving the priority of a personal mod that does pass validation. PNGs are still verified on load; their deferred fallback is a separate case. Test integrated in research/portrait-pack-profile-fallback.md. Do not change the ZIP or the release to include a later fix.

## Requested closure — test.4

v0.2.0-test.4 is being prepared with the tested 674,182/patch0050 runtime, without experiment 0051. The guide for another PC and the toolkit is `docs/releases/PORTABLE-HANDOFF.md`. The user asked to stop upon delivery: do not automatically continue with new tasks. Workers closed their tests and are not keeping active processes.

Experimental T33 was left in `pendientes/T33-petal-transitions`, commit 7888d08. The fixture passes and the candidate recognizes some white frames, but the uniform-screen assertion at 114 fails: only 118/119 are fully wide in the fine probe. Other uniform/particle phases still revert to 4:3. Do not package or promote that patch0051 as a complete fix. The shared SDK was restored exactly to 0001..0050 and CMake goes back to the `local/build/sakura` output.

Private handoffs to resume only when requested: chapter1 `corridor-bridge/new-sumire-turn/finish.state` SHA f9780d38285655a7f54252b2856c56b886021a280e3bd7add757f630e51317de, backup 5c71f717…; new Sakura attack tested 3,199 hashes/RGB/SRAM matching, no victory on this route. Chapter2 `t30-chapter2-followup/maria-elimination/finish.state` SHA f1084a893b337712195d700b110855138e6f20b00104bd108742c7100302ca01; paired original SRAM 4c22bf1e…. PR35 documents the stretches; the later continuous test was canceled and is not presented as approved.

Test.4 delivery published and checked. The final receipt is `docs/releases/v0.2.0-test.4-validation.json`. The ZIPs and the tag 4406c13… remain unchanged. No workers or own tests remain active. Goal paused due to the stop request; the campaign is not considered complete.
