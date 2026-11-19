# T118 VDP1 textured line fast path (candidate, not measured, not enabled)

`t118-fastpath-candidate.diff` (against `video/raster.cpp` of the stack through patch 0089) adds a fast loop to
`Renderer::RasterTexturedLine` for lines that are: not Gouraud, no mesh/user clip/MSB-on, replace mode (`mode & 3 == 0`),
16-bit framebuffer, no interlace, no glyph stamp active, both end points at least 2 pixels inside the system clip,
less than 1024 pixels long. Texture walk, end codes, flip, high speed shrink and write order (pixel, then beside) are as before;
everything else takes the existing loop. It is NOT a numbered patch and NOT listed in `config/dependencies.json`.

Status: compiled and linked (isolated copy `local/deps/satrecomp-t118`, `local/build/rebuild-t118`, only `raster.cpp.obj`
and `renderer.cpp.obj` rebuilt, relinked by hand). No parity or timing result exists: the first B build crashed because the
copied shared tree held in-progress T116 edits to `renderer.h/.cpp`; they were replaced by the pinned stack and A/B
(`local/build/sakura-t118-a.exe` pristine, `-b.exe` candidate) were rebuilt, but not yet run.
Not verified: frame hashes, RGB, 0 interpreted, A/B medians, that no fast-path pixel can be clipped.
