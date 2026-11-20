# Chapter 1 widescreen transitions

The native Windows executable, the translated disc 1, and the owner's local states were used. Captures correspond to a hidden 1280×720 SDL window with the Zoom view. Each run used an independent copy of backup memory. Frames are relative to the loading of the indicated state.

| Start | Replay | Observed result |
| --- | --- | --- |
| `intro1799.state` | `tests/chapter1-opening-skip.movie` | `opening → row-gradient → title → native → title`. Captures 91 and 181 are black. The title appears by capture 271 at the latest. |
| `title-final.state` | `tests/chapter1-title-new-game.movie` | `title → native → row-gradient → native → row-gradient → backdrop → movie`. Title menu at 200, LOADING screen with 4:3 frame at 400 and 650, panoramic narrative movie at 1000 and 1450. |
| `map-room.state` | `tests/chapter1-map-dining-hall.movie` | `row-gradient → native → backdrop → narrative`. Map at 250 and 330, fade to the dining hall at 500, dialogue at 750. |
| `theater.state` | `tests/theater-dialogues.movie` | The same layout sequence from map to dialogue. Scene with Sumire at 250 and conversation at 1000–2700. |
| `resume-chapter-6000.state` | `tests/chapter1-lips-confirm.movie` | The night-time LIPS menu is visible at 8 and 32, disappears by frame 59 at the latest, and the answer is complete at 230. All 450 frames stay on `narrative`. Another LIPS, from `prebattle-3000.state`, kept the same layout. |

Run the tests with `python -m unittest discover -s tests -p test_widescreen_transitions.py -v`. They verify the opening, New Game, dining-hall and LIPS transitions and compare the hashes of every frame between the Original and Enhanced presentations. Each route is skipped when its private states are missing. The input videos contain only controller presses.

## Findings in the build examined

- **Loading screen.** A state saved before frame 400 of the New Game route contains the entire LOADING screen on layer 4. The 512-byte FNV-1a fingerprint of the palette is `74EA8ADC9B0340CC`, matching the start of `SAKURA1/LOAD.BIN` (76,672 bytes). 93 non-trivial 256-byte blocks match the state's VRAM.
- **Intermission.** `intermission-down.state`, `intermission-up.state` and `night-patrol-12000.state` showed the Save/Status/Resume menu with a 4:3 frame. Layer 4 contains the full background, Sakura, and the logo. Layer 0 contains the selection box. Layer 4's palette `E9107F892185CCC8` matches both `ICLOGO.BIN` and `LOAD01.BIN`, so the fingerprint alone is ambiguous. All three states share the page signature `79F284B5622630A4`. In `intermission-down.state`, 86 blocks of `IC01.BIN` were recovered in VRAM, mostly at file offset `+0x48C80`, and 41 of `ICLOGO.BIN` at `+0x34280`. `exit-battle-save.state` already uses `anchored-menu`, with the `IC01.BIN` palette `530FF280499422C3`. Layer 4 is disabled in `intermission-save.state`, which shows the status screen.
- **HD text in LIPS.** Two runs of the same night-time route with HD Text Style and Original produce identical captures while the options are visible at frames 8 and 32. At 230, after selection, 8,008 pixels of the answer line change within the capture rectangle `(346,510)–(946,542)`. The current filter only accepts dialogue rows from source coordinate Y=160. The upper box's options fall outside that filter. These runs recorded no verified portrait substitutions.
- **Fades.** The trace emits layout changes without a frame number. The sampled captures support the indicated frames and leave the exact boundaries of the `native` fallback during fades unmeasured. The local-states audit also does not establish continuous chapter coverage.

Logs, captures and layer probes are in `local/work/worker-wide-transitions`. The `opening-skip`, `title-start`, `map-room`, `theater-dialogues`, `lips-patrol` and `lips-original-text` subfolders correspond to the routes in the table and to the text comparison.

## LIPS glyph capture

The VDP1 listing of `resume-chapter-6000.state` contains normal glyph sprites with mode `0080` and size `0210` (16×16). The glyphs match byte for byte with the English atlas used by dialogue. Inactive options use color `C510`. The selected option uses `C570` and also keeps the highlight on the VDP2 layer. All three rows start at Y=54, 78 and 102. The LIPS in `prebattle-3000.state` uses Y=62 and 94. These two cases require recognizing both colors and different heights.

`frontend_sdl.cpp` accepts `C510` and Y=160–196. `NarrativeInkFits` restricts ink to the lower box and `SakuraUi::GameText` applies `NarrativeClip`. In Zoom view, the options box belongs to the image transform. The lower dialogue uses a different transform. A transform and a crop need to be assigned to each line group.

The layer probe shows the frame, the timer, Sakura's figure, and the options' ink on VDP1. VDP2 layer 3 contains the box's fill and highlight. `underSprites` recomposes the pixel without the entire VDP1 layer. Restoring an option's ink pixels this way can also remove Sakura's pixels that should show through under the translucent box. A faithful substitution requires compositing each pixel without the glyph and keeping the VDP1 value prior to that command. Auxiliary data can be kept outside of state serialization.

To verify a future substitution, repeat the night-time route in HD and Original. The change must stay confined to the box's text while the options are visible, preserve frame, timer, highlight and portrait, and keep the game's hashes equal. Repeat in Zoom view and in the view that preserves the original framing.

### Cases to validate a glyph plate

| Case | Expected evidence |
| --- | --- |
| Three night-time options from `resume-chapter-6000.state` | HD modifies only the glyph area relative to Original, including those of the selected row. The VDP2 highlight, timer and frame match for the same frame. |
| Two options from `prebattle-3000.state` | The rows are recognized at Y=62 and Y=94. The selected row keeps its color. |
| Ink above the VDP1 figure | When a row is hidden, the plate preserves the figure under the panel with its color blend. A synthetic case with the same VDP1 value written by a glyph and by a later sprite verifies that visibility follows draw order. |
| Unrecognized glyph, occluded row, or a plate with no data from the displayed framebuffer | The row's native pixels remain intact. After restoring a state, a valid plate is expected before removing ink. |
| Zoom view and original framing | HD text follows the panel's transform and stays within its edges. The lower dialogue keeps its own position. |
| Confirmation and timer expiry | The options text disappears with the box. The answer, the selection, and every frame's hashes match between Original and Enhanced. |

Initial audit status: the plate was not yet implemented. The later implementation and its real tests are in [HD choice text](chapter1-choice-hd.md). The current automated replay checks layout and state parity. The HD/Original comparison of captures 8, 32 and 230 documents the starting point for testing the substitution.

## Fixes after the audit

The intermission accepts the logo's secondary palette only if the native IC01 image matches the displayed framebuffer: at least 80% of samples, at least 60% per quadrant, and sufficient visible diversity. A uniform fade does not satisfy this check. All three affected states and the battle-exit menu with the `anchored-menu` layout were verified. The LOAD.BIN screen now has a provisional generative background and keeps its original animated column. The phase alignment between its tiles and the protected center still needs visual polishing; having a widescreen layout does not prove a finished visual transition.

## Ogami map entry performance

At 2560×1440, entering the first chapter's dining room from the map switches to the backdrop composition at replay frame 404. On v0.2.9, that frame took 51.90 ms on a fresh profile cache and 47.32 ms on a repeat with the disk cache intact. The backdrop and composite portion accounted for 31.04 and 29.85 ms. Much of the remaining transition continued to spend about 12–15 ms per frame in composition. The game entered narrative layout at frame 482 in both runs. Raw traces are in `local/work/codex-ogami-map-perf/`.

This reproduces the entry hitch independently of whether an on-disk cache is present. Same-session repeat visits and return-to-map still need separate measurements. The owner also reported an inspection cursor at any of the four screen edges changing the Zoom geometry, and a brief dark interval in the early letter-to-Sakura transition. Those visual reports have separate replays in progress.

The later prologue probe sampled every composed SDL backbuffer through Sakura's entrance (3,348 at 1440p per disc). Both disc runs began from the archived English letter checkpoint and produced 3,111 narrative and 237 floral-only frames. The floral plane remained selected, no inset went black, and no sampled tile darkened and recovered within three frames. The Spanish-disc comparison without readback preserved all 3,350 guest hashes and 20 sampled captures. These runs leave cold Spanish-script playback and the reported PC's physical display open. Evidence is private at `local/work/codex-prologue-black/evidence.md`.

Patch 0164 composes and uploads only the strips outside the native viewport. Within a strip it reuses rows and runs of columns that sample the same integer source pixels. This renderer path runs on any verified map fade, independently of chapter, language or map identity.

Two alternating real-time runs per executable at 1440p reduced median whole-frame work on the first transition frame from 42.45 to 38.38 ms. The fade had 61 frames above 16.67 ms in each baseline run and 22 and 55 in the candidate runs. Among subsequent frames captured by the slow-frame logger, median composition was 11.22 versus 3.68 ms. The first-frame spike is still present. Separate strict runs at 1440p and 1080p matched 1,100 guest hashes and 18 sampled RGB pairs, including fade boundaries, with zero interpreted blocks.

Patch 0165 keeps the CPU-only logical surfaces prepared by existing background workers within a 40 MiB allowance. The render thread claims a prepared surface when the game first shows that background and creates the GPU texture on demand. It keeps synchronous loading when workers are disabled, their result is late, or setup failed. It uses the existing normalized source grid and adds no display-size copies. Measurements of smaller GPU allocations for the fade alone did not establish a clear first-frame gain.

Three alternating real-time runs at 1440p reduced the median first entry frame from 35.81 to 29.61 ms relative to 0164 on the same profile. The backdrop operation on that frame dropped from 8.94 to 2.31 ms median. Separate 1440p and 1080p comparisons matched all 1,100 strict guest hashes and 18 sampled RGB pairs. Presentation still exceeded the frame budget on the first fade frame. Raw timings and the rejected compact-texture experiment remain local.

A separate instrumented 0165 replay broke down transition frame 404 at 31.85 ms. It spent 9.60 ms on guest work, 3.00 ms on the retained backdrop upload and 5.50 ms on the fade exterior, within 22.25 ms of presentation. The native-size mixed layer first appeared in the trace at frame 406 and took 1.06 ms of composition plus 3.87 ms for upload and cache bookkeeping. Optimizing that later mixed layer cannot account for the earlier peak. First-frame allocation, upload, and presentation remain under investigation. The isolated trace is `local/work/codex-ogami-map-perf/warm-first-frame-breakdown/run.log`.

## Narrative-to-map exit performance

In the English disc 1 Chapter 1 upstairs route, the narrative gives way to the floral backdrop at replay field 288 and the theater map appears at 353. The retained 4300 checkpoint yields the same 760 guest hashes as the continuous route. The first map-fade exterior appears at field 289. In a stage-timed diagnostic, its repeated fields spent a median 3.34 ms composing and submitting the exterior, including 1.32 ms in texture updates. Other composition and presentation still contribute to the first field.

Patch 0186 keeps the last fully uploaded exterior while the backdrop, integer viewport geometry, blend recipe and all verified map-edge pixels match. A different field takes the existing composition path. A resize, renderer reset or failed texture upload invalidates reuse. The cache keeps one 14 KiB row buffer alongside the existing texture. A separate paired diagnostic shows that 32 of 64 exterior fields reuse the texture, avoiding all exterior uploads on those fields.

The exact 0185 and 0186 SDK trees were timed on the same Windows Direct3D 11 machine with a Ryzen 7 7435HS and an RTX 4060 Laptop GPU, hidden 2560 × 1440, dummy audio, normal pacing and no screenshot readback. Each run covers 530 fields and includes the settled map. The cold and warm cache sets each alternate two runs per executable. The table shows medians of the run statistics for the 64 exterior fields.

| Cache | Whole-frame median before → after | Whole-frame p95 before → after | Composite median before → after |
| --- | ---: | ---: | ---: |
| Fresh profile cache | 23.32 → 20.45 ms | 27.43 → 25.31 ms | 4.35 → 3.12 ms |
| Existing disk cache | 25.10 → 23.48 ms | 27.25 → 27.61 ms | 4.51 → 3.19 ms |

In the two fresh-cache runs, fields exceeding 16.67 ms drop from 62 and 63 to 57 and 59. In the warm-cache runs they drop from 63 and 64 to 57 and 57. On field 290, the first repeated exterior, median whole composite time across both cache conditions drops from 4.35 to 0.84 ms. The first new exterior at field 289 still needs to be built and uploaded. Its timings vary from 26.40 to 38.29 ms before and 28.80 to 40.38 ms after. This trial leaves first-use latency and the warm-cache tail open. Peak process commit across the eight runs spans 923–930 MiB before and 918–928 MiB after. GPU memory and physical frame presentation were not measured.

Separate strict 760-field 0185/0186 runs matched all guest hashes, decoded PCM and backup RAM. The fixed 1440p viewport and two resize steps during the fade matched all 48 RGB pairs, including 42 at 1440p and six at 1080p. A diagnostic pairing with an injected SDL device reset at field 309 matched all 24 RGB pairs and the same guest, PCM and backup results. These tests cover the replay and synthetic reset. Physical device loss, other host and renderer configurations, and package inclusion remain open.

OptiPort instructions were checked against upstream commit a328c5a1b5aabc62f29aa9f1b5a96a59ad2d4ee1. Private evidence and regeneration commands are under local/work/codex-scene-exit-perf. Cleanup removed 2,596,813,653 bytes of diagnostic binaries, objects and extra states. The project measured 121,914,969,297 logical bytes with existing private assets and packages. The immutable development ZIP measured 6,315,009,692 bytes.

### First exterior field on Direct3D 11

On the same Chapter 1 exit at 2560×1440, four serial hidden replays with
the 0186 runtime showed one field over 16.67 ms among the 64 exterior
fields. That first field took 20.21–21.51 ms. Whole-frame p95 across the
64 fields ranged from 12.43 to 13.67 ms in these quieter runs.

The same instrumented executable alternated ordinary present and a
diagnostic `SDL_FlushRenderer` before present, in off/on/on/off order.
Ordinary present took 7.517 and 6.708 ms. With the split, the flush took
0.938 and 0.842 ms and the remaining present took 6.376 and 6.455 ms.
The combined time stayed within the ordinary range, leaving most of
the delay in the backend present path. These timings do not isolate
GPU scheduling, DXGI swap-chain policy or Windows composition.

There is no production change from this diagnostic. The private
commands and logs are under
`local/work/codex-scene-exit-perf/first-field-analysis/`. The visible
display and the user's other PC remain unmeasured.

## Held empty dialogue position

During Chapter 1, the Enhance Zoom dialogue box rose briefly when a picture
finished fading and only the empty box remained over the floral background.
The hold remembered the native crop and discarded the bottom shadow row count.
The viewport then used zero shadow rows to recompute the box position.
Patch 0163 retains the shadow row count of the last displayed Zoom layout.

In a 2560×1440 disc-1 relay from the archived letter checkpoint, the dialogue
top moved from y=1048 to y=1038 during frames 77–115 and 941–1118 and returned
to y=1048 with the next image. The candidate keeps y=1048 in both intervals.
Six sampled RGB changes were confined to x=362–2197 and y=1038–1439.
The six before/after samples and all twelve Original samples matched.
Each mode preserved all 1,150 guest hashes with zero interpreted blocks.
The replay candidate used the 0160 runtime plus the local change. The full
pinned stack through the later 0161 also applied with the 0163 patch.

The separate reported black flash did not occur in the local 2,200-frame
English letter-to-park trace or the 1,600-frame Spanish Sakura-entrance
trace. The floral plane remained selected throughout those replays.

## Inspection hand at the viewport edges

The owner showed a closed Chapter 1 doorway in Enhanced Zoom. The background
matches BG1011. The same doorway and white hand are visible in the archived
María inspection, with María drawn over the door. The actor-free doorway route
confirmed the art, and its sampled checkpoints did not contain the cursor.

The native hand is a 24×24 normal sprite with mode 0080, bank C520 and texture
fingerprint EE0629C4601E9F26. Its actual ink previously counted as a scene or
dialogue edge. Near the top and sides the fit dropped back to a grouped crop.
At the bottom the dialogue bounds reduced the picture's integer scale.

Patch 0167 uses the hand's exact command, texture, source layer and live ink
colour to exclude its visible pixels from the framing analysis. The current
picture and dialogue draw the in-crop hand pixels. The renderer draws the
verified overhang in each corresponding viewport, clipped at the window edge.

At 2560×1440 the 940-frame replay reached x=0, x=296, y=0 and y=200 in native
coordinates. All 939 samples after the automated resize kept picture bounds
(272,29,2016,1008) and dialogue bounds (362,1048,1836,402), given as x, y,
width, height. Both center captures, all 11 Original capture pairs, and the
940 guest hashes per mode matched. All runs reported zero interpreted blocks.
Five Enhanced edge captures matched every predicted visible cursor texel.
The window clipped four texels at the extreme top and 40 at the bottom.
The pinned SDK stack through 0165 plus the candidate applied cleanly.

## Parallel exterior composition on map transitions

Patch 0271 uses the existing row workers to compose the exterior of
a map crossfade. Each band writes disjoint rows and uses the same
sampling and blend formula. The renderer uploads a strip after all
its rows are ready, and exact repeat fields still reuse the texture.

Two alternating real-time A/B pairs on the dining-room entry at
2560 × 1440 measured 22 and 13 fields over 16.67 ms in the stock
78-field fade, compared with 10 and 3 with the patch. These timing
runs took no screenshots. Their 550 guest hashes matched with zero
interpreted blocks. The first fade field still varied between runs:
24.75 and 45.00 ms on stock, 54.69 and 24.43 ms with the patch.

The entry comparison also matched nine RGB captures per resolution
at 720p, 1080p, 1440p and 2160p, with equal guest hashes and SRAM.
The 1440p exit comparison matched 24 RGB captures, all 760 guest
hashes, SRAM and the PCM output. Release packaging is pending.

## Compact map fade textures

Patch 0272 packs the two side strips into one texture and the top and
bottom into a second texture. It submits two updates and draws from
the four exact packed rectangles. At 3840 × 2160 the pixel payload of
these textures falls from 31.641 to 9.492 MiB. At 2560 × 1440 it falls
from 14.062 to 4.219 MiB. These figures describe the two fade
textures alone, excluding renderer staging and other GPU resources.

The route into the dining room matched nine RGB captures at each
of 720p, 900p, 1080p, 1440p and 2160p, with identical guest hashes
and save memory. The exit matched 24 captures at 1440p, all 760 guest
hashes, save memory and the PCM output.

An initial 1440p comparison of the compact textures found lower
first-field times in two of the alternating replays. The initial
implementation repeatedly resized its CPU scratch buffer to match
the smaller of the two textures, then grew it again. The final
implementation grows the buffer only when necessary.

Two alternating 4K A/B pairs for this final version, without
readback, measured the first fade field at 39.92 and 53.09 ms on
patch 0271 and 26.24 and 25.01 ms on patch 0272. Fields above
16.67 ms across the fade fell from 7 and 28 to 4 and 5. A later
field still reached 46.53 ms. Peak process commit dropped about
19–21 MiB in those runs. Peak working set rose by roughly 1–2 MiB.
These are host process measurements and do not measure total VRAM.

The target hardware reference is 8 GB system RAM and a GPU with
2 GB of video memory. The replays were run on the development PC.
A physical test on the minimum configuration remains open.

## Packing repeated rows in the 4K map fade

The interior layer at field 406 occupies the full 2880 × 2016 target,
so cropping cannot reduce the upload. Patch 0274 uploads one row
per run of equal native and backdrop row indices and draws it at the
same integer height. The ordinary path handles geometry that packs
poorly and specialized intermission and scene fades.

In two alternating 4K entry pairs, mixed-layer uploads fell from
931,841,280 to 436,250,880 bytes over 550 fields, with the same 107
updates and 153 cache hits. Field 406 measured 55.93 and 31.94 ms
before and 22.08 and 33.51 ms after. It still exceeds 16.67 ms.
The eleven sampled entry captures, guest hashes and SRAM match.

At 4K, 24 exit captures match with all 760 guest fields, SRAM and PCM.
The Direct3D 12 entry comparison also matches its 11 RGB captures
and guest trace. The 4K timing numbers above are Direct3D 11 without
readback. Release packaging is pending.

## Composing packed rows directly

Patch 0275 determines the repeated row runs before blending eligible
map fades. It blends one row per run and uses the same texture geometry
as patch 0274. In two alternating 4K Direct3D 11 entry comparisons,
field 406 went from 32.17 and 25.41 ms to 20.91 and 20.89 ms. Across
fields 404–481, counts over 16.67 ms went from 11 and 8 to 4 and 3.
Some frames still exceed the budget.

All 11 sampled entry captures match RGB exactly. The guest hash log
and SRAM are byte-identical. These timings are from the development
PC. The 8 GB RAM and 2 GB VRAM configuration remains a minimum test
target. Full campaign coverage and release packaging remain pending.

The 4K exit replay matches 24 RGB captures, 760 guest fields, SRAM
and PCM. The Direct3D 12 entry matches 11 RGB captures, guest hashes
and SRAM. Screenshot runs are excluded from the timing comparison.

A separate alternating memory run recorded peak process commit of
1.053–1.054 GB before and 1.054–1.055 GB after (decimal units). In that
run, counts over 16.67 ms were 2 and 6 before and 3 and 4 after.
The two timing runs show that host timing still varies. Process
commit is a host metric and does not measure video memory.
