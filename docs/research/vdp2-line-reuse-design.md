# T116: reuse of unchanged VDP2 lines (measurement and design, nothing activated)

Status: measured, designed, prototype written but not built or validated. No patch is added and no behaviour changes.

## Measurement (shadow probe, T103 scenarios, 1,200 frames each, strict native)
Compared at the start of each frame: VDP2 VRAM, colour RAM, VDP2 registers, displayed VDP1 framebuffer (content, not index: the
index flips every frame), picture size.
- office-return-3000: inputs equal to the previous frame in 1,130 of 1,200 frames; picture equal in 1,021; 111 frames had equal
  start inputs but a different picture (mid-frame writes), so a frame-start comparison alone is NOT exact.
- resume-chapter-6000: inputs equal 1,043; picture equal 834; 209 equal-input frames with a different picture.
- chapter1-first-attack: VRAM changes in 1,199 of 1,200 frames; no reuse possible.
Upper bound: about 85% (office) and 70% (resume) of the ~3.5 ms `ComposeLine` work, 0% in attack. Not measured as a speedup.

## Design
1. Exact change tracking: a state counter bumped on every value-changing write to VDP2 VRAM and colour RAM (`BusWrite8/16` in
   machine.cpp, compare old and new), VDP2/VDP1 register writes (value changed), `SetField`, `LatchDisplayMode`, `SetResolution`,
   `Reset`, state load. The displayed VDP1 framebuffer and the VDP1 registers are compared by content at the frame's first line
   (swap and erase happen before it).
2. Per-frame homogeneity: keep a frame's lines only if the counter did not move during it and equals the previous frame's first-line
   value; replay in the next frame only while the counter is unchanged; any change mid-frame drops the cache (needed because
   scroll accumulators depend on earlier lines).
3. Replay set per line: `m_framebuffer` row, presentation planes (source, topSource, underSource, foreground, underSprites,
   spriteWhiteWeight, panelMix/underPanelMix/floralCoverMix, mapFadeEdges), `m_lines`, `m_layerLines`. Never cache lines that touch
   `episodeBlendSamples`, approximation/reference counters, glyph plates (disable when glyph capture is on, so HD portraits give no gain
   at first), scroll capture, interlace, rotation screens.
4. Proof tool: `SATRECOMP_VDP2_LINE_REUSE=check` composes every line and compares it with the kept one; must report 0 mismatches
   in all scenarios plus one with scroll/fade (after-options-3000) before any activation.

## Not done
Build and validation, hash/RGB parity, A/B timing, synthetic invalidation test. A prototype (renderer.cpp/h, machine.cpp edits) was
written in the local tree but its build did not finish; it is not part of this PR.
