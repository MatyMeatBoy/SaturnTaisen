# T116: reuse of unchanged VDP2 lines (patch 0144)

Status: implemented, pixel/hash-identical in ten scenarios, measured faster in static scenes, neutral elsewhere. Not played.

## What it does
`Renderer::RenderLine` composes a VDP2 line from VRAM, colour RAM, the VDP2 and VDP1 registers and the displayed VDP1
framebuffer. When none of those moved, the line is the same as last frame's, so it is copied back instead of composed.

- **Change counter** (`m_stateGen`): bumped by every value-changing write to VDP2 VRAM and colour RAM (`BusWrite8/16` in
  `machine.cpp`; equal-valued writes do not count), by value-changing VDP2 and VDP1 register writes, `SetField`,
  `LatchDisplayMode`, `SetResolution`, `Reset`, state load and `NoteVideoMemoryWrite`. Those are the only writers of the
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

## Not verified
Play test; GPU video path; interlace, 24-bit colour RAM and other resolutions are excluded, not tested; the HD
presentation consumers were not looked at beyond the planes being equal (checked in `=check` mode only with the planes the
benchmark's settings capture: glyph plate on, tactical/scroll off).
