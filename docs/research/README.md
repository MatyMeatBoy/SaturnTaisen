# Research index

One line per document. The JSON files are the machine-readable evidence for their document; those without their own document appear at the end. `tests/test_research_index.py` checks that every file in this folder is listed here.

## Recompilation and CPU

- [2026-11-17-investigacion.md](2026-11-17-investigacion.md) — initial research, candidate projects, and references ([projects.json](projects.json), [upstream-evidence.json](upstream-evidence.json)).
- [2026-11-17-casos-recomp.md](2026-11-17-casos-recomp.md) — Saturn recompilation cases and decisions for Sakura.
- [2026-11-17-cobertura-estatica.md](2026-11-17-cobertura-estatica.md) — static coverage expansion ([static-program-analysis.json](static-program-analysis.json), [static-program-eager-analysis.json](static-program-eager-analysis.json)).
- [2026-11-17-validacion-nativa.md](2026-11-17-validacion-nativa.md) — native boot and arrival at the theater ([runtime-validation.json](runtime-validation.json)).
- [macl-48bit-regression.md](macl-48bit-regression.md) — MAC.L with 48-bit saturated accumulation ([macl-48bit-regression.json](macl-48bit-regression.json)).
- [cheviman-saturn-toolchain.md](cheviman-saturn-toolchain.md) — references from cheviman's thread.

## Engine, discs, and progress

- [sakura-engine-notes.md](sakura-engine-notes.md) — Sakura engine-specific knowledge.
- [sakura-sdk-and-loading.md](sakura-sdk-and-loading.md) — Sakura SDK and loading ([sakura-sdk-inventory.json](sakura-sdk-inventory.json)).
- [chapter1-battle-progress.md](chapter1-battle-progress.md) — chapter 1 battle validation ([chapter1-battle-progress.json](chapter1-battle-progress.json)).
- [save-import.md](save-import.md) — save import ([public-save-fixtures.json](public-save-fixtures.json)).
- [sh2-dispatch-speed.md](sh2-dispatch-speed.md) — T104: where the SH-2 dispatch time goes and the second chain table (patch 0074).

- [vdp-software-speed.md](vdp-software-speed.md) — T103: where the VDP software drawing time goes, the one pixel-identical change shipped (patch 0073) and what is left.
- [vdp2-line-reuse-design.md](vdp2-line-reuse-design.md) — VDP2 line reuse measurements and design.
- [t118-fastpath-notes.md](t118-fastpath-notes.md) — VDP1 textured line fast path and measurement limits.

## Presentation and HD

- [Ending bank pairs](ending-bank-pairs.md) — TP3c multi-record layouts, confirmed counterparts and compositor boundaries.
- [saturn-background-loading.md](saturn-background-loading.md) — background loading and HD mod ([saturn-background-loading.json](saturn-background-loading.json), [saturn-background-compression.json](saturn-background-compression.json)).
- [saturn-background-workers.md](saturn-background-workers.md) — multi-core background preparation ([saturn-background-workers.json](saturn-background-workers.json)).
- [saturn-hd-characters.md](saturn-hd-characters.md) — PC characters for the HD mod ([pc-character-inventory.json](pc-character-inventory.json)).
- [pc-menu-hud-inventory.md](pc-menu-hud-inventory.md) — T23 inventory of PC menus/HUD and Saturn candidates ([pc-menu-hud-inventory.json](pc-menu-hud-inventory.json)).
- [pc-spred-resources.md](pc-spred-resources.md) — first verified decoding of PC assets ([pc-background-inventory.json](pc-background-inventory.json)).
- [hd-font-proportions.md](hd-font-proportions.md) — HD font proportions.
- [pixelgen-v1.md](pixelgen-v1.md) — PixelGen v1, decorative extensions.
- [stage01-pc-ground.md](stage01-pc-ground.md) — Stage01 ground from the PC edition and Saturn camera and sprite comparisons.
- [Stage21 ground](stage21-pc-ground.md) records the independently verified source-4 substitution in episode 4.
- [bg2250-bg1002-visual.md](bg2250-bg1002-visual.md) — Disc 1 salute gradient and theatre lobby at 1440p.
- [bbg204-tactical-inset.md](bbg204-tactical-inset.md) — Verified BBG204 tactical illustration in HD.
- [scene-spot-check.md](scene-spot-check.md) — Spot checks of connected HD scene pictures.
- [episode-title-pc-pairings.md](episode-title-pc-pairings.md) — PC counterparts for the episode title cards.
- [bg2238-still.md](bg2238-still.md) — BG2238 in the Chapter 9 dream at 1440p.
- [bg2533-pan.md](bg2533-pan.md) — Verified BG2533 pan from the PC edition.
- [bg2248-pan.md](bg2248-pan.md) — Chapter 1 vertical blossom panorama with exact viewport verification.
- [bg1207-pan.md](bg1207-pan.md) — Chapter 1 horizontal panorama with the original Saturn foreground.
- [bg1285-pan.md](bg1285-pan.md) — Chapter 10 horizontal panorama of the burning city.
- [bg2295-pan.md](bg2295-pan.md) — Exact crop and runtime wiring for the damaged Koubu panorama.
- [forest-vertical-pans.md](forest-vertical-pans.md) — Exact pairing of six Chapter 10 forest variants.
- [scroll-table.md](scroll-table.md) — Shared scroll geometry and four additional registered panoramas.
- [bg2159-disc2-visual.md](bg2159-disc2-visual.md) — Disc 2 Chapter 8 city view at 1440p.
- [v011-floral-background.md](v011-floral-background.md) — v0.1.1 panoramic floral background ([kabe-backgrounds.json](kabe-backgrounds.json)).

## Controllers

- [m30-controller-profiles.md](m30-controller-profiles.md) — M30 controllers and SDL.
- [controller-mapper.md](controller-mapper.md) — mapper by physical inputs.

## Evidence without its own document

- [discs-inventory.json](discs-inventory.json) — disc inventory.
- [prepared-disc1.json](prepared-disc1.json), [prepared-disc2.json](prepared-disc2.json), [prepared-japanese-discs.json](prepared-japanese-discs.json) — image preparation.
- [translation-code-impact.json](translation-code-impact.json) — code affected by the translation.
- [logo-module-analysis.json](logo-module-analysis.json), [ending-module-analysis.json](ending-module-analysis.json) — LOGO and ending module analysis.
- [mods-status.json](mods-status.json) — status of evaluated mods.

## 2026-11-18 integration

- [chapter-sweep.md](chapter-sweep.md) — nine later routes, verified residencies, and EVT06 expansion for episode 4 ([result](episode4-aot-fix.json)).
- [portrait-white-blends.md](portrait-white-blends.md) — exact white-blend metadata and fade preservation in HD portraits.
- [later-chapter-validation.md](later-chapter-validation.md) — verified saves, EVT02 lock, and tracking of later-episode loading ([AOT fix](episode2-aot-fix.json)).
- [battle-overlay-reproduction.md](battle-overlay-reproduction.md) — verifiable reconstruction of the battle expansion ([manifest](battle-overlay-reproduction.json)).
- [spanish-translation-workflow.md](spanish-translation-workflow.md) — English scripts with IDs, controls, and aliases across discs for Claude's Spanish patch.
- [scene-tagging.md](scene-tagging.md) — six simple tags, inventory of both discs, and links to the scripts, distinguishing candidates from observations.
- [battle-overlay-family.json](battle-overlay-family.json) — evidence or report of the presentation block and chapter 1 coverage.
- [chapter1-continuous-battle.json](chapter1-continuous-battle.json) — evidence or report of the presentation block and chapter 1 coverage.
- [chapter1-wide-transitions.md](chapter1-wide-transitions.md) — evidence or report of the presentation block and chapter 1 coverage.
- [dialogue-catalog.md](dialogue-catalog.md) — evidence or report of the presentation block and chapter 1 coverage.
- [portrait-animation-coverage.md](portrait-animation-coverage.md) — evidence or report of the presentation block and chapter 1 coverage.
- [tactical-menu-independent-reference.md](tactical-menu-independent-reference.md) — evidence or report of the presentation block and chapter 1 coverage.

- [dialogue-panel-compositing.md](dialogue-panel-compositing.md): Exact Saturn blend and background continuity inside the panel.

- [hd-text-row-rejections.md](hd-text-row-rejections.md): Sumire and María replays: valid glyphs outside the bound.

- [intro-petals-transition.md](intro-petals-transition.md): Baked petals, fallback during flashes, and the first video.

- [battle-story-inset-shadow.md](battle-story-inset-shadow.md): Layer-by-layer test for the absence of shadow in the tactical vignette.

- [dialogue-voice-advance.md](dialogue-voice-advance.md): A/B/C presses, real voice, and AOT/interpreter comparison.

- [wide-map-crossfades.md](wide-map-crossfades.md): Map/floral crossfade with 16:9 continuity, direct entry to Zoom, and native parity.

## Translation

- [traduccion-espanol.md](traduccion-espanol.md) — Spanish patch: Japanese → English → Spanish method, dialogue/battle/menu formats, ISO with fixed slots.

- [first-sakura-hd-portraits.md](first-sakura-hd-portraits.md): Reviewed matches for Sakura0013/0014, reproduction, and in-game test limits.
- [Second batch of chapter 1 HD portraits](chapter1-sumire-hd-portraits.md)
- [Third batch of chapter 1 HD portraits](chapter1-third-hd-portraits.md)
- [Fourth batch of HD portraits](chapter1-fourth-hd-portraits.md)
- [Saturn and PC video equivalence](video-equivalence.md)
- [Disc 2 opening film](disc2-opening-film.md)
- [HD portrait pack selection](portrait-pack-profile-fallback.md)

- [chapter1-choice-hd.md](chapter1-choice-hd.md): HD LIPS text for two/three options, glyph ownership, and ten real profiles.

- [first-film-transition-fix.md](first-film-transition-fix.md): Verified phase of the first video, clean background, and continuous test of 6,201 frames.

- [first-film-script-phase.md](first-film-script-phase.md): Research on the 0100.BIN cursor and limits of the image-less phases.

- [RetroAchievements 16546 on Saturn](retroachievements-16546.md)
- [RetroAchievements runtime and offline verification](retroachievements-runtime.md)
- [dialogue-preload-runtime.md](dialogue-preload-runtime.md): Immutable catalog, bounded reading, and preloaded narrative with native reveal cells; global coverage pending.
- [chapter1-victory-followup.md](chapter1-victory-followup.md): Satan's defeat, relocated routines, post-battle lock, and save/Resume validation.
- [LIPS group identification via the cursor](lips-script-cursor.md) — two panels verified with the script, the table, and native tiles.
- [Chapter 2 tactical progression](chapter2-tactical-progression.md) — Continue, orders, enemy phase, and ally attack with AOT/interpreter comparison.
- [EVT overlay registry](evt-overlay-registry.md)
- [bg-matching-progress.md](bg-matching-progress.md): Running log of the PC BG scene-image matching by screenshot; counts only.
- [saturn-bg-format.md](saturn-bg-format.md): Saturn BG*.BIN/BBG*.BIN layouts (three variants) and the mass BG pairing by file number (`config/hd-scene-bg-map.json`).
- [bg-matching-shards.md](bg-matching-shards.md): Split of the 766 PC BG images into shards so the matching can run in parallel.
- [pc-asset-census.md](pc-asset-census.md): Header-level census of the PC edition cabinet that sizes the HD categories.
- [pc-saturn-name-links.json](pc-saturn-name-links.json): Name links between PC and Saturn resource folders (identifiers only).
- [hd-completion-handoff.md](hd-completion-handoff.md): Handoff to finish the HD mod from another PC: state per area, what travels through Git, order of work and rules.
- [HD coverage by chapter](hd-chapter-coverage.md) reports resource evidence, replacement status, and regeneration steps.
- [eve002-tactical-inset.md](eve002-tactical-inset.md) — Verified airship tactical inset in Episode 2.
- [Coverage campaign on v0.2.6](coverage-campaign-v026.md) records the observed draws and the campaign's verification limits.
- [EVE202 tactical inset](eve202-tactical-inset.md)
- [EVE0116 tactical inset](eve0116-tactical-inset.md): disc-1 episode-1 tactical close-up in HD with 1440p verification.
- [EVE0118 tactical inset](eve0118-tactical-inset.md): disc-1 farewell picture in HD with 1440p verification.
- [IC01 HD intermission](ic01-hd-intermission.md): the verified EVE202 picture drawn in HD inside the tactical inset (patch 0099), evidence and limits.
- [Jumping to a chapter or scene](scene-jump.md) (test tool only): Continue from a copied save, states along the way, random exploration; what is not done.
- [HD chapter 1 report](hd-chapter-1.md): what chapter 1 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [HD chapter 2 report](hd-chapter-2.md): what chapter 2 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [HD chapter 3 report](hd-chapter-3.md): what chapter 3 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [th3-native-attribution.md](th3-native-attribution.md) — Exact disc-1 reads and native frame evidence.
- [HD chapter 4 report](hd-chapter-4.md): what chapter 4 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [HD chapter 5 report](hd-chapter-5.md): what chapter 5 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [HD chapter 6 report](hd-chapter-6.md): what chapter 6 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [HD chapter 7 report](hd-chapter-7.md): what chapter 7 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [HD chapter 8 report](hd-chapter-8.md): what chapter 8 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [HD chapter 9 report](hd-chapter-9.md): what chapter 9 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [HD chapter 10 report](hd-chapter-10.md): what chapter 10 shows per resource class, its status, ranked next actions and what needs the owner's discs.
- [HD package gate](hd-package-gate.md) records generated-art validation and clean-profile preparation with PC movies.

- [clip-hook-design.md](clip-hook-design.md) — PC video hook design and the second clip and skip verification.

- [Disc 1 battle insets](disc1-battle-insets.md)

- [Film catalog decisions](film-catalog-decisions.md)
