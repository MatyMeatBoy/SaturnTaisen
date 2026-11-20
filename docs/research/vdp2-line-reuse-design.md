# T116: reuse of unchanged VDP2 lines (patch 0156)

Status: implemented and verified in strict replay, with lower VDP time in office and park. Play testing and package inclusion remain open.

## What it does
`Renderer::RenderLine` composes a VDP2 line from VRAM, colour RAM, the VDP2 and VDP1 registers and the displayed VDP1
framebuffer. When none of those moved, the line is the same as last frame's, so it is copied back instead of composed.

- **Change counter** (`m_stateGen`): bumped by every value-changing write to VDP2 VRAM and colour RAM (`BusWrite8/16` in
  `machine.cpp`; equal-valued writes do not count), by value-changing VDP2 and VDP1 register writes, `SetField`,
  `LatchDisplayMode`, `SetResolution`, `SetMode`, `Reset`, state load and `NoteVideoMemoryWrite`. Those are the only writers of the
  two memories (grep of the dependency: nothing else touches `m_vram2`/`m_cram`).
- **Content snapshots at the frame's first line** (the VDP1 swap and erase have happened, the displayed framebuffer does not
  change during the picture): the displayed VDP1 framebuffer (256 KB memcmp), the VDP1 registers, the glyph stamps of the
  displayed framebuffer. A difference bumps the counter.
- **Frame states.** A frame whose first-line counter equals the previous frame's is *built* (its lines are kept as it is
  composed); it is kept only if the counter did not move during it. The next frame whose first-line counter equals the kept
  frame's is *replayed*. A change at any moment of a frame (mid-frame write) drops the cache and composes the rest of the
  frame; scroll accumulators run for every line (`LayersPrepareLine/FinishLine` still execute), so replay does not depend on
  earlier lines.
- **Replayed per line:** `m_framebuffer` row, the presentation planes (source, topSource, underSource, foreground,
  underSprites, spriteWhiteWeight, panelMix/underPanelMix/floralCoverMix when the row has any, mapFadeEdges, glyph plate rows
  with an owner), `m_lines` and `m_layerLines`.
- **Never cached:** lines that move the reference/approximation counters or `episodeBlendSamples`; lines inside the item
  card or menu-arrow rows when those captures are on (they keep state from line to line; `ReuseVolatileLine`).
- **Not eligible (whole frame composed):** GPU path, `m_check`, display off, interlace, RBG0/RBG1, scroll capture
  (`scrollWidth`, tactical maps), sizes above 704x512, `SATRECOMP_LAYER_PROBE`.
- **Switches:** `SATRECOMP_VDP2_LINE_REUSE=0` off; `=check` composes every line and compares it with the kept one (stderr
  "reuse check" on a difference, the end-of-run report counts mismatches).

## Evidence (stack = origin/main at ef71af6 plus patch 0144, built with the toolchain in `local/build/rebuild-perf`)
Per-frame state hashes (they include the picture) of A (stack without 0144) and B (with) over 1,200 frames, 0 interpreted
blocks: identical in office, resume, attack, night, interm, cont, options, morning, dining, stairs. The same B with
`=check`: identical hashes and 0 line mismatches in all ten (about 1.0-1.6 million replayed lines in the check runs).
`tests/test_vdp2_line_reuse.cpp`: 600 random frames with mid-frame VRAM/CRAM/register writes, planes and picture compared
with a renderer that composes every line; with `T116_MUTATE=1` (a VRAM write that does not tell the renderer) it fails at
frame 14, so the test can see a missed write.

Timing: see the PR (interleaved A/B, median of three, `video (vdp phases)`).

## Original trial limits
Play test; GPU video path; interlace, 24-bit colour RAM and other resolutions are excluded, not tested; the HD
presentation consumers were not looked at beyond the planes being equal (checked in `=check` mode only with the planes the
benchmark's settings capture: glyph plate on, tactical/scroll off).

## Timing (interleaved A/B, median of 3, `video (vdp phases)` ms per frame; the machine was shared and busy, so absolute values are about 1.8x those measured earlier, compare A with B only)
| scenario | A (without 0144) | B (with) |
| --- | --- | --- |
| office | 7.456 | 4.114 |
| resume | 8.511 | 6.448 |
| night | 7.200 | 3.920 |
| interm | 8.508 | 3.435 |
| options | 8.220 | 6.059 |
| attack (tactical, no reuse) | 14.387 | 14.435 |
An earlier run on a quieter machine (tree older than main, same logic without the item/arrow rule): office 4.479 -> 2.139,
resume 4.779 -> 3.174, attack 7.571 -> 7.544.

## Verification of patch 0156 on dc37400

The exact pinned SDK stack applied through 0156. The private runtime rebuilt all
34 nongenerated translation units and linked the existing 674,629-block AOT
base. The line-reuse unit test matched all 600 randomized frames, replayed
47,118 lines, and rejected the dropped-write mutation at frame 14. The VDP2
colour suite passed.

With reuse disabled, enabled and checking, guest hashes and sampled window RGB
matched at each of these checkpoints with zero interpreted blocks.

| Replay | Frames | RGB samples per run | Reused lines | Check mismatches |
| --- | ---: | ---: | ---: | ---: |
| Office return, reloaded at frame 250 | 500 | 4 | 79,872 | 0 |
| Chapter 1 first attack | 500 | 3 | 0 | 0 |
| Spanish park dialogue, 2560×1440 | 400 | 3 | 32,171 | 0 |

The attack took the unmodified render path. The park detected one mid-frame
change. Check mode also compares every map-fade edge's colour and recipe.
Changing renderer mode invalidates the cache and presentation plane size
changes prevent reuse. The cache is excluded from save state serialization.
The office state reload exercised the cache invalidation during gameplay.

One local run per setting gave average VDP times of 6.807 to 3.444 ms in the
office and 4.755 to 3.550 ms in the park. The attack remained ineligible
throughout. These timings are single-run observations under a shared machine.
The earlier interleaved measurements and their scope are recorded above.
