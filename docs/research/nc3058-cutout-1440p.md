# NC3058 cut-out at 1440p

The retained English disc 1 Chapter 5 scene draws NC3058 with a 288 × 144 VDP1 body at (16, 8) and four active face-strip commands. The body hash is `16BC42F123C0E1D9`. The 27,544 opaque body pixels and the active native face strips together occupy 38,298 native pixels in the picture. The released PC edition supplies `SAKURA1/NC/NC3058.SPR`.

The old cut-out path masked the texture at PC donor resolution, then sampled it linearly. It changed 8,524 output pixels beyond the exact native VDP1 silhouette at 2560 × 1440. Most were near the filtered body edge. Some came from PC face strips extending past the corresponding native strip area.

Patch 0142 clips the existing linear texture sampling to opaque native row spans within the picture. The cache rebuilds the spans and PC mask when the native silhouette changes. The renderer reuses the vertex and index buffers. If a mask or geometry draw fails, the affected body or face redraw uses the native foreground. Native face redraws for unclear donor expressions keep their existing order.

## Verification

- Six muted strict-native profiles agree on all 54 guest hashes. The SHA-256 of each hash log is `efa0de582591d6f8544be3a0edba7a111f2ea2c897ed0c8c350cea2ae5c245ec`.
- In three 1440p samples each with and without the common scene donor, the body changes 1,516,538 output pixels inside the silhouette and zero outside it. Both native face-fallback rectangles match the body-disabled control pixel for pixel. The full Original comparison is identical. The PC texture remains linearly sampled. SDL’s geometry path changes 1,991 in-mask pixels by at most one per RGB channel relative to the prior path.
- The witnessed mask has 313 row spans. The full-body geometry batch uses 1,252 vertices and 1,878 indices. The clipped face batches use subsets of these spans. The renderer uses no output-resolution mask.
- A local 600-frame 1440p comparison matches all guest hashes. Presentation mean and p95 are 4.549 and 4.590 ms in the previous build, and 4.492 and 4.486 ms with the patch. Backdrop/composite mean and p95 are 3.010 and 3.271 ms before, and 2.994 and 3.199 ms after. This measures the witnessed stationary scene on the test host.
- The non-cut-out NC50 control matches all 60 guest hashes and the sampled 1440p RGB. The headless opening matches all 1,500 guest hashes.

The register marks the observed disc 1 NC3058 appearance. The remaining cut-outs, other expressions and package verification remain open. Replay inputs, controls and the native mask proof are retained under `local/work/codex-nc3058/`.

## Exact facial registration in patch 0223

The same natural Chapter 5 checkpoint exposes the two native mouth rectangles retained by the previous path. The Saturn file stores 18 face strips directly after the body in four contiguous runs of 3, 6, 3 and 6 frames. PC expression table 6 uses matching groups. Tables 8 and 9 give their placement in the 576 × 320 source. Patch 0223 pins the whole-disc and PC file fingerprints, the 18 native hashes and dimensions, and all four authored positions. This uses the same registration mechanism as [NC3057](nc3057-ending-faces.md).

The sampled appearance selects PC parts 1, 4, 10 and 13. The two native mouth rectangles no longer break either face outline. Five 1440p samples each match 19,351 independently projected flat source texels across the four facial regions. Each sample changes 1,869,517 pixels inside the same 38,298-position native silhouette, including when the BG2058 donor is installed. Seven muted Direct3D 11 profiles match 55 strict guest hashes and final SRAM. Original with and without the donor and Enhanced with a missing or truncated donor reproduce the corresponding native RGB. NC3057 retains its exact 55-field replay, SRAM and 10 RGB captures.

This verifies the four active strips in the sampled appearance. The other authored ordinals remain unwitnessed here. Package inclusion is pending. Private comparisons and commands are under local/work/codex-tp3c/residual0223.
