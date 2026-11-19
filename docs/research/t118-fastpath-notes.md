# T118 VDP1 textured line fast path (candidate, not measured, not enabled)

`t118-fastpath-candidate.diff.txt` (against `video/raster.cpp` of the stack through patch 0089) adds a fast loop to
`Renderer::RasterTexturedLine` for lines that are: not Gouraud, no mesh/user clip/MSB-on, replace mode (`mode & 3 == 0`),
16-bit framebuffer, no interlace, no glyph stamp active, both end points at least 2 pixels inside the system clip,
less than 1024 pixels long. Texture walk, end codes, flip, high speed shrink and write order (pixel, then beside) are as before;
everything else takes the existing loop. It is NOT a numbered patch and NOT listed in `config/dependencies.json`.

Status: MEASURED 2026-11-19 (not a patch; no number taken, not enabled). The earlier A/B exes crashed at start (objects of the shared
tree mixed with hand-built ones); A and B were relinked from one consistent isolated build (A = pinned stack through 0089,
B = same plus only `raster.cpp` of the candidate) and run from private copies.

- `python tools/vdp_parity_bench.py run` + `compare` equivalent on office-return-3000, resume-chapter-6000 and
  chapter1-first-attack, 1,200 frames each: per-frame hash files byte-identical A vs B (1,200 lines each), frame-1198 window
  shots byte-identical (so RGB identical), 0 interpreted blocks in all six runs.
- `ab` with 3 interleaved reps, median video ms (A / B): office 4.362 / 4.371, resume 4.771 / 4.773, attack 7.597 / 7.371
  (emulation ms 8.103 / 8.142, 8.633 / 8.659, 11.041 / 10.799).

Result: parity holds, gain is within noise on two scenarios and about 3 percent of video time (0.23 ms per frame) on the
attack scenario only, so it is kept as a measurement and no patch number is assigned. Not verified: that no fast-path pixel can
be clipped beyond these three scenarios (the equal hashes support it only for them).
