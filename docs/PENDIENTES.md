# Pending items — shared queue

Updated 2026-11-18. Verifiable detail: [current status](ESTADO_ACTUAL.md). Technical/artistic method: [handoff](HANDOFF.md).

Shared queue for MatyMeatBoy and the helping agents (Claude, Codex). Anyone can add rows; each PR takes **one** row. Technical detail continues in [Saturn Priority](superpowers/plans/2026-11-17-saturn-priority.md) and [Chapter 1](superpowers/plans/2026-11-17-chapter1-progression.md).

## How to take a pending item

1. `git fetch` and read this list on `origin/main`, plus open PRs (`gh pr list`). A row with a branch or open PR is already taken.
2. Choose the first `free` row (those marked `after Txx` wait for that row) by priority (P0 before P1…) whose **Type** can be resolved with what is available:
   - `agent`: code, synthetic tests, or documentation, with no private data.
   - `local`: requires the owner's `local/` (states, prepared discs); only on their PC and without uploading anything from `local/`.
   - `physical`: hardware (RX 6900 XT, M30 controllers); tested by the owner.
   - `decision`: needs a response from the owner before touching code.
3. If the row does not fit in ~15 minutes, do the minimum verifiable part and split the rest into new rows.
4. Work from `origin/main`, branch `pendientes/<id>-<topic>`, reusing the single auxiliary copy allowed by `AGENTS.md`. If it is busy, coordinate and wait; do not create more worktrees. Never mix uncommitted work from another copy.
5. Open a PR with: row taken, what was verified (command and result), and what was not. Change the row's status in the same PR.
6. Priority above all: blockers or progress loss > chapter 1 validation > presentation > decoration.

Integration rules confirmed by the user on 2026-11-18: Claude and the workers only send PRs; coordinator Codex reviews, resolves conflicts, and integrates authorized PRs. Do not ask for authorization again for each routine integration. An open PR claims the row; check its branch before duplicating work.

Fixed rules: Author always MatyMeatBoy; never upload discs, BIOS, saves, original PC assets, `local/`, or the personal ZIP; v0.1.0, v0.1.5, and v0.1.2 are immutable; Saturn has priority over PC; no partial test is presented as a complete chapter or campaign.

## List

| ID | P | Type | Status | Pending |
|---|---|---|---|---|
| T01 | P0 | agent | integrated · PR #4 | Patches 0035/0036, backgrounds, tactics, text, catalogs, tests, and handoff integrated. New tasks start from origin/main; agree on files before touching the shared renderer. |
| T02 | P0 | local | split · see T02a–T02c | Victory of the first battle and exit. The continuous 23,443-frame movie plays on the current build with 0 interpreted and ends with the orders menu open; local handoff state `local/work/t02/fin-multiple-turns.state` (SHA-256 4d67dd1a…). |
| T02a | P0 | local | defeat observed · partial chain verified | Satan defeated via normal inputs; farewell and battle resolution observed. Chain of 55,038 frames repeated to farewell, matching hashes/RGB and 0 interpreted. See `chapter1-victory-followup.md`. |
| T02b | P0 | local | fixed and tested · candidate 674,182 | Closing the battle needed relocated copies 206/238 bytes. Save Complete and Resume through hanami: 3,000 hashes and 15 RGB matching the interpreter, identical SRAM, 0 interpreted. Not claiming a complete chapter; not included in test.2. |
| T02c | P0 | local | continuous stretch verified · earlier handoffs missing | 109,740 frames from `west-dialogue` to hanami on the 674,182-block candidate, with hashes, final RGB, and SRAM matching the reference and zero interpreted. The earlier handoffs still need to be linked. |
| T03 | P0 | local | up to the tutorial by stretches · full path pending | 29,597 hashes from the corridor to the night save and 147,730 from that save to the tutorial, with final RGB and SRAM verified. Continue after the battle reaches hanami in 9,500 frames. Still missing: the joins from New Game and between the new tutorial and the verified turns, plus two full repeats with save, restart, and Continue. |
| T04 | P1 | local | implemented and tested · patch0045 | HD LIPS text for two/three choices in Zoom/set: ten profiles, 240 matching hashes per scene, zero interpreted; clock/frame preserved. Natural expiry and other choices pending; included in test.2 (see `chapter1-choice-hd.md`). |
| T05 | P1 | local | integrated · PR #4 | Overlap fixed in Enhanced; five tabs and paths verified. Keep tests and a safe fallback for unknown menus. |
| T06 | P1 | agent | after T01 | Polish the phase seam between LOADING mosaics and the protected center. |
| T07 | P1 | local | done in development · T01 | Intro before the title: 288×144 area at 16,24 at the largest integer scale with English subtitles. |
| T08 | P1 | local | after T01 | Extended backgrounds during fades: measure the exact frames of the `native` fallback (add frame number to the layout trace). |
| T09 | P2 | local | PR · 240/304 | Chapter 1's pending portraits (32 in the 201 checkpoint), reviewing `004f`, `0095`, `00a1`, `00ef`, `013b`, `013c`, and `0169` for their three regions. |
| T10 | P2 | local | integrated · PR #9 | HD white blend with exact metadata, alpha, and weighted cache; synthetic compositor 5/15/25 and real witness 25/32 at 1440p pass. Other identities/animations continue in T09/T19. |
| T11 | P2 | agent/local | integrated · PR #34 · patches0048–0050 | Sealed narrative catalog 56/29,725; LIPS0102 preloaded with full-panel fallback. 24 run pairs compare 7,440 hashes/220 matching RGB and 0 interpreted; two/three-choice selection, confirmation, and expiry have native postconditions. Other scripts/paths remain pending. See `dialogue-preload-runtime.md`; patch0050 not included in test.3. |
| T12 | P2 | local | after T01 | Battle camera with the STAGE01 tactical extension anchored at 656,24 throughout the whole battle. |
| T13 | P2 | agent | integrated · PR #2 | Normalize line endings (CRLF/LF warnings) with `.gitattributes`, without changing content. |
| T14 | P3 | agent | integrated · PR #3 | Index of `docs/research` with one line per document. |
| T15 | P3 | decision | merged · PR #53 | Catalog listing updated from the stale SaturnTaisenFirst v0.1.5 draft to SaturnTaisen v0.2.0-alpha. Still not submitted to Quiver/RecompLauncher (needs authenticated portal access). |
| T16 | P3 | physical | free | Test the portable ZIP on physical RX 6900 XT and M30 controllers. |
| T17 | P1 | local | free | Real disc 1→2 switch and unified final importer. |
| T18 | P2 | agent/local | research | RetroAchievements 16546. rcheevos recognized both English CUEs by their official hashes. Saturn map documented. Pending: condition catalog, per-variant compatibility, local offline, and Casual sync path. See `retroachievements-16546.md`. |
| T19 | P3 | local | free | HD bodies (NC): single height-based scale and head/torso axis, with eyes/mouth. |
| T20 | P3 | local | inventory done · PR | PC MPG videos (MOVIE000..120): equivalence, audio, and subtitles before substituting. |
| T21 | P0 | agent/local | integrated · PR #6 | K001–K019 tool tested: exactly reproduces 614,024 candidates from the earlier seed. Derived code local only. |
| T22 | P0 | local | packaging and transfer verified | v0.2.0-test.1: clean public release and private ZIP of 708,495,279 bytes, English disc 1 + processed HD. HD scene and battle boot from a fresh extraction with Windows PATH, zero interpreted. Physical RX 6900 XT pending T16. |
| T23 | P1 | local | Claude · PR #45 | Equivalent PC menus/HUD: inventory and matches verified for Saturn, without distorting proportions. First name-based inventory ready (29 PC, 572 images, 20/29 with a candidate); still need to verify geometry/palette and resolve 9 without a candidate. |
| T24 | P2 | agent/local | free | Measure and disable auxiliary tactical work in Original without changing pixels/guest; declare cache and conditions. |
| T25 | P1 | agent/local | Claude · in progress | Spanish patch (menus + chapter 1). Tools in `tools/es/` and method in `docs/research/traduccion-espanol.md`; script and data only in `local/work/guion-es`. Chapter 1 translated and reviewed against Japanese; title, interlude, choices, loading (incl. the File/System RAM frame), status, and battle bar for the 13 scenarios (WKL01-22, address computed per file with the `WklBattleMenuExtractor` algorithm from the English team's tools) in Spanish (PR #40). HD text verified: it works unchanged because `glyph_text.h` recognizes all of CP1252 and the patch never touches the KNJ fonts. Investigated and blocked for now: episode card/LOADING are hand-painted VDP2 art shared with the background, confirmed with `draw_vdp2_screen` (1120/1120 unique cells in TITLE1.BIN, zero reuse: there is no text in tiles to edit), and OMALL.DAT has no pointer table within the file itself nor precedent in the reference English patch (they didn't translate it either). Japanese ISO regenerated (the dump was in fact available): review against Japanese is no longer blocked. Chapter 2: 1,775 texts (6 batches) translated and validated, `japones.json` rebuilt with 125 new glyphs (1.3% uncertain), batch01 cross-checked line by line against Japanese (2 corrections), batches 02-06 still pending that full reading. Chapters 3-7 with a complete first Spanish draft from English (all batches translated and validated, 0 line-length/duplicate/LIPS issues); not yet cross-checked against Japanese except chapter 1 and chapter 2 batch01. Chapter 10 complete (534/534); chapter 9 in progress (621/1,811); chapter 8 extracted, translation paused by deliberate choice (see note below) rather than a permissions block. Publishing policy updated by the owner: translated/reinterpreted text (ES/EN) may be published, only the original extracted Japanese is never distributed; v0.2.0-alpha (first public release, project renamed to SaturnTaisen) already ships a data-only Spanish language pack with the draft of chapters 1-7 and 10 (no in-launcher selector yet). Note: a delegated session declined to keep mass-translating the remaining chapters (8 and the rest of 9), judging large-scale reproduction of this commercial game's full dialogue script to be a content concern independent of authorization; that stance was respected rather than overridden. Tools (`tools/es/lotes.py`, `validar_lote.py --capitulo`, `japones.py --tables/--capitulo`, `glifos_nuevos.py`) generalized for any chapter. The script itself lives only in `local/work/guion-es` (never uploaded). Still pending: launcher language selector (the Spanish disc/profile already work without touching code; the UI is missing, coordinate with the SDK). |
| T26 | P0 | local | after T02/T03 and HD gaps | Later delivery with complete chapter 1 and its HD mod verified. The test.1 requested for another PC does not close this task. |
| T27 | P1 | local | free | Expand the scene index's observations: currently inventory of both discs, 112 tables, 54 videos, and nine observations. Confirm per path the six tags, text/subtitles, and framing of each clip; do not turn candidates into proven coverage. |
| T28 | P2 | agent/local | after T27 per scene | Consume verified tags for presentation/Zoom without ambiguous heuristics. The local metadata index still does not govern the runtime. |
| T29 | P0 | local | integrated · PR #8 | Chapter 2: EVT02 attributed exactly to 00204000. The 643,320-block candidate passes boundary 1200 and boot 9501 with all hashes/RGB matching the interpreter and zero interpreted. Basis for the later 674,023 extension; test.1 remains unchanged. |
| T30 | P0 | local | partially integrated · PR #35 · stopped | Continue, orders, two enemy phases, and Musket #7 elimination verified in Original. Stretch comparison of 33,141 frames and 341 RGB pairs. Victory, exit, and Enhanced presentation pending. See `chapter2-tactical-progression.md`. |
| T31 | P0 | local | integrated · PR #10 | Chapter 4: EVT06 recorded by full RAM match. The 674,023 candidate passes boundary 1200 and load 12000, with all hashes/RGB matching the interpreter and zero interpreted. Integrate PR and continue the battle. |
| T32 | P0 | local | PR · EVTs recorded · build pending | Complete intermediate paths, battles, saves, and endings for chapters 2–Finale. The initial sweep validates inputs on eight paths (96,000 frames) and the chapter 4 input fix, not complete chapters. |
| T33 | P1 | local | partial · T33a tested | First video: empty box and shadows fixed in patch0046. Still pending: 16:9 petals and episode card/remaining transitions. Keep the approved Zoom position. |
| T33a | P1 | local | implemented and tested · patch0046 | First New Game video: background only 707..879 and 5938..6067, extended video 880..5937; 6201 hashes and 6 native RGB matching Original, zero interpreted. Included in test.2. Remainder T33 open. |
| T34 | P1 | local | integrated · PR #11 | Exclusive crop for the 288×144 novel video. First empty boxes resolved in T33a; other transitions remain in T33. |
| T35 | P1 | local | integrated · PR #11 | Floral continuity and exact blending of the dialogue fill; fallback for untested blends. |
| T36 | P1 | local | integrated · PR #11 | The cursor at the map's left edge preserves the wide background. |
| T37 | P1 | local | partially integrated · PR #11 | Sumire/María rows fixed with a VDP1 plate; expansion to the 44 9-pixel glyphs tested on branch T39. English two/three-row choices resolved in T04; full coverage pending. |
| T38 | P2 | local | audit · PR #11 | Voice advance: B interrupts before A/C on a real line, inputs received, and AOT/interpreter parity. An independent Saturn reference is still missing. |
| T39 | P1 | local | integrated · PR #13 | Map↔floral fade and direct entry to Zoom; 900 hashes and 9 native captures match, exact outer/image/shadow sampling. |
| T40 | P1 | agent/local | free (coordinate SDK) | "Language: English / Español" option in the launcher per `docs/research/traduccion-espanol.md`: `language=es` in `launcher.ini`, `find_nearby` prioritizes `disc1-es`, selector disabled if missing. Meanwhile `tools/es/perfil_es.py` works. |
| T41 | P1 | agent/local | integrated · PR #14 | Generated HD panel and percentages per category/stage, with sources, pending items, and a verified-100% gate. Update when approving new assets. |
| T42 | P2 | local | integrated · PR #15/#17/#19 | Reproducible checkpoint of 201/304 and 91/123 for chapter 1. From the third batch, María `0064` base verified in game and four identities checked in the atlas. The delivered ZIP keeps its catalog. |
| T45 | P2 | local | free | Review the `00a1` portrait with both strips active. The PC 160 candidate improves when swapping the two 32-row strips during offline prep. Keep the base, the Saturn mask, and the pack format. Approve after comparing both strips in game. |
| T46 | P2 | agent | updated | Status and handoff aligned with PR19/patch0046/portraits201; candidate 674,023 tested on loads 2/4. New delivery verified in T47, test.1 unchanged. |
| T47 | P0 | local | delivered and transfer verified | v0.2.0-test.2 public 317,215,196 bytes and personal 725,331,460 bytes. Clean source 92edea7, runtime 674,023/patch0046, and HD 201. New profiles, Windows PATH, 402 variants with no failures and 0 interpreted; film 6201 hashes and 6 matching RGB. Physical RX6900XT/M30 pending. |

| T48 | P1 | local | implemented and tested · patch0047 | The profile's old catalog no longer hides the valid prepared set. Eight runs: 191→201 and a different fingerprint recover 402 variants; 90 hashes and 3 matching RGB per case, GUI changes only the portrait; valid profiles preserved. Not included in test.2. |

| T49 | P0 | local | delivered and transfer verified | Test.3 public 317,282,734 bytes and personal 725,392,142 bytes, source 72affb2, runtime 674,182/patch0049, and HD 201. Extracted ZIPs with correct CRC/inventory/SHA; scene/battle, film 6201 hashes, and save/Continue 10700 hashes matching references, 0 interpreted. Personal archive local only. Physical RX6900XT/M30 pending. Test.2 unchanged. |
| T50 | P0 | local | delivered · test.4 · stopped | Public and personal ZIP extracted and verified; launcher, HD/battle, importer, mapper, and handoff work with Windows PATH. Runtime 0050; experiment 0051 excluded. Do not resume without the user's request. See `releases/v0.2.0-test.4-validation.json`. |
| T51 | P2 | agent | PR #41 · portability | HD tests and exporter use the portable toolkit (`toolkit/msys64/clang64` or `STF_CLANG`) instead of `C:/msys64`. Warning: on transferred copies, an SDK with `core.autocrlf=true` breaks `build_runtime.dependency()` (line endings); build with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.autocrlf GIT_CONFIG_VALUE_0=false` and restore the SDK from the composite tree 0001..0050. No runtime change. |
| T52 | P0 | open | HD portraits | 4 HD portraits missing (`00a1`, `0152`, `0153`, `0169`): 300/304 integrated. Verify the 99 new ones in game; reject ambiguous matches. |
| T53 | P1 | open | HD videos | 44/50 videos paired by duration and order (`docs/research/video-equivalence.md`). 6 pairs missing; check audio/subtitles/skip and design MPEG-1/MP2 runtime playback. |
| T54 | P1 | open | HD bodies/HUD | NC bodies (T19) are not drawn at runtime; integrate HD HUD/menus on the T23 inventory. |
| T55 | P1 | open | recomp EVT | 19 EVTs registered by inference (`docs/research/evt-overlay-registry.md`): observe them in play. Repeat the 40,000-frame sweep (17 cases) with a high timeout and register any missing blocks. |
| T56 | P1 | open | campaign | New Game to tutorial chain verified (297,107 frames). Missing: tutorial to victory, save/restart/Continue (x2), and T32 chapter routes. |
| T57 | P2 | agent/local | implemented · patch0052 | Mouse pointer auto-hides after 1s of inactivity over a fullscreen or borderless window (keyboard/controller are the only inputs), shows again on motion. Implemented in `local/deps/satrecomp/port/frontend_sdl.cpp`'s main loop; recorded as `patches/0052-sakura-cursor-autohide.patch`. Correction to an earlier note on this row: the "~2,544 unrecorded lines" that looked like a blocker were a false alarm (comparing the working tree against the wrong base commit on a stale branch) — patches 0038-0050 were already committed on `main`; nothing was actually unrecorded. 0051 is reserved for the unshipped petal/flash experiment on branch `pendientes/T33-petal-transitions`. Not yet tested in a running build (no `build_runtime.py` run performed for this change). |
| T67 | P0 | open | HD Saturn formats | Decode the Saturn `BG*.BIN` (45,120 B, header `00 01 00 01`) and `NC*.BIN` (104,528 B, header `00 02`, a table then dense data) formats by tracing the SH-2 loader; neither decodes as a linear bitmap, 4 bpp cells or `red_lz` at probed offsets (`docs/research/pc-asset-census.md`). Unblocks pairing the 712 BG and 166 NC name links, then integration. |

## Split for collaborators

- **Coordinator:** T01 integration, review/merge, and tracking of T02/T03/T22. The other bots do not modify the same files or the shared AOT base during their build.
- **Claude:** pick a free row, preferably T09/T19/T20/T23 inventory/matches or T11 text tools. One branch and one PR per checkable block. Do not integrate directly.
- **Other worker:** pick another row with no files shared with the previous one; if it requires the renderer, reserve the file in the PR description beforehand and notify the coordinator.

When opening a PR, state ID, own files, test, and limitations. Do not mark "done" for a proposal or for building. The coordinator updates it to "integrated" after the merge. `local` tasks need owner data; `physical` ones depend on tests on their hardware. No playable-PC task displaces Saturn.

## New visual repros

- T34: novel video viewport: fixed in development to use 288x144, 16,8; fixture passes at 1440p at x8. First video runtime checked in T33a and included in test.2.
- Narrative vignettes within battle: audit closed for the villains' vignette: it has no novel shadow; see battle-story-inset-shadow.md.
- LIPS choices: English two/three choices implemented and tested in T04/PR16; natural expiry and the rest of the panels remain pending.

- T35: floral continuity of the dialogue fill in Zoom (reported by the owner). Diagnosis: `Presentation.foreground` stores the final opaque RGB for source<5; when the box is split/scaled, the blended native NBG3 is carried over to another position. Investigate capturing top/second/ratio and recomposing over the extended background in destination coordinates, with exact Saturn arithmetic. Do not replace with estimated opacity, do not regenerate approved backgrounds, preserve Original, frame, portrait, and glyphs. Resolved with patch0040 and runtime evidence; included in test.2, not in test.1.

- T36: widescreen transitions: remove the host pink frame during the Enhanced fallback (patch39 integrated and verified). Also extend backgrounds and transition effects while keeping phase/palette; hiding the border does not equal solving the native fallback or the baked flowers/petals. Review doll entry, title/New Game, map↔novel, and scene changes.

- T37: HD text coverage and quality of the base translation scripts. Initial repro resolved by patch0042. Sumire case: record 50039, index 473 of /SAKURA1/0100TBL.BIN, three rows of 27/30/5 characters, no unknown controls; the middle row is complete in the catalog but still shows SD in the capture. Do not fix the prose or rewrite Claude's translation to hide a render rejection. Current structural audit: 112 physical tables/59450 records, JSONL SHA 90c3c35f2661f1c8ac7d5bac512655b02d64ea9844a3ca2c17d93230b0ac3684; two tabulators unresolved on disc1. Still missing: visual coverage/choices/menus and validation of edited scripts without overwriting target_es.

  T37, second witness: María, record 50064/index 498 of 0100TBL, row 3 ends with CP1252 0x85 (ellipsis), complete text with no unknown controls. Sumire reproduced: w at X296,Y172 has two visible pixels at X304,Y176–177; `NarrativeInkFits` rejects the whole row because X<304. There is also a VDP1 bevel there: do not widen or blindly erase with underSprites. Prepare an exact plate and HD fit, check María before attributing a shared cause.

- T38: dialogue advance with voice: compare A/B/C with sustained presses and releases, text revealing/complete and voice active/finished; cross-check AOT/interpreter and an independent Saturn reference before declaring original behavior. Measure SMPC polling and CD/audio wait, do not assume SSD loading. The MessageSkip via R described by Kayama 15048 is Dreamcast-exclusive and after completion, not evidence of manual Saturn advance. Do not change timers or force voice to end to hide a failure. AOT/interpreter audit closed; an independent Saturn reference is still missing.

### Integrated visual block

Patches 38–46 recorded and validated as a composite tree. Floral panel, left cursor, border text, dining-room fade, English choices, and the first video's transition have evidence in their research reports. They are not in test.1. The 16:9 petals and the still-untested transitions remain in T33/T32.

Cleanup: the two old replaced candidates (1,604,792,320 bytes) were removed, with hashes and replacements in local/work/retired-test-binaries.json. States and releases are preserved.

### Border text: validated fix

- T37: patch42 converts the reported Sumire/María rows. VDP1 plate with a leading pixel and up to two writer glyphs; invalidated by a third writer, a non-glyph overwrite, or a guest write. Rows with shared ink require atomic erasure. The original HD clip is preserved.
- Tests: 12 matching hashes per case between Original, Enhanced HD, Enhanced SD, and test.1 Original; Original RGB identical; strict AOT 0 interpreted. See hd-text-row-rejections.md. Coverage of choices beyond T04's two cases and all scripts is still pending; do not declare all HD text complete.
- T38: voice audit closed for Sumire's first line: B interrupts/advances before A/C; SMPC inputs received, 460 hashes+PCM per button matching AOT/interpreter. Independent Saturn still missing.
- Patch43 contains outer map/floral blend primitives; patch44 consumes them on entry to the dining room, with continuity tests. Other transitions remain pending.

### Future language integration

Language will be a launcher selection with a coherent variant of scripts, menus, fonts, and assets. Share font mappings only when the atlas and its encoding match; script/asset caches must include language/revision or a content hash. Do not regenerate Spanish sheets or copy controller configuration over an already-edited profile. PR12 integrates private preparation tools; it does not declare the selector finished nor the whole game translated. Saturn and the visual fixes keep priority.

### Requested test.4 closure

The user asked to publish the next checkpoint and stop work. Transfer guide and toolkit: `docs/releases/PORTABLE-HANDOFF.md`. Experiment 0051 is left out of the package, on the T33 branch noted in the handoff. Do not automatically resume the queue after this delivery.
