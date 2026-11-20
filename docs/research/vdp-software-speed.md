# VDP software drawing speed (T103 / S6)

Goal: make the VDP2/VDP1 software drawing cheaper without changing a single output pixel or guest hash. Result: the
profile is flat, one small pixel-identical change is shipped (patch 0073, about 0.1 ms of 4.4-7.7 ms), and the larger
gains need structural work that is split into T116-T118.

## Method

- Runtime: `local/build/rebuild-674182-clean/sakura.exe` is the A side. The B side is a copy of that build directory
  (`local/build/rebuild-s6`, paths rewritten in `build.ninja`, `cmake .` once) where only the three video objects were
  recompiled and the executable relinked; the 674,182-block AOT objects were reused, so no 25-minute rebuild.
  Flags are the CMake Release defaults, `-O3 -DNDEBUG -std=gnu++20` (the `-O2` in `tools/build_runtime.py` belongs to
  the `check-video` test harness only, not to the shipped runtime). LTO and PGO are untried.
- Scenarios (1,200 frames each, hidden 1280x720 window, unthrottled, strict-native, HD portraits off, 0 interpreted
  blocks): `office` = `office-return-3000.state` + `advance.movie`, `resume` = `resume-chapter-6000.state` +
  `resume-chapter.movie`, `attack` = `chapter1-first-attack.state` + `advance.movie`. `tools/vdp_parity_bench.py`
  runs them, writes the per-frame state hash (it includes the picture) and the shot of frame 1,198, and does the
  interleaved A/B (3 runs each, median of the `video (vdp phases)` line of `SATRECOMP_FRAME_PROFILE`).
- Two temporary measurement aids (`tools/vdp_profile_sampler.h`, `tools/symbolize_samples.py`): per-function timers
  and a sampling thread that records the emulation thread's RIP every ~150 us. Neither is part of the patch.

## Where the VDP time goes

Baseline (A), ms per frame: office video 4.46 / emulation 9.63 (SH-2 3.55, sound 1.17); resume video 4.85 /
emulation 10.33; attack video 7.70 / emulation 11.57 (SH-2 2.2).

Share of the emulation thread, sampled (function level, inlined callees included):

| function | office | attack |
| --- | --- | --- |
| `NormalLine` (4 scroll screens) | 10.6% | 7.5% |
| `ComposeLine` pixel loop (`composite` lambda + loop) | 7.9% + 4.8% | 5.6% + 4.5% |
| `SpriteLine` (VDP1 framebuffer to sprite layer) | 6.2% | 9.6% |
| `RasterTexturedLine` (VDP1 sprite drawing) | 2.7% | 13.2% |
| `SampleNormalPresentation` (widescreen map columns) | - | 10.3% |
| `vector::assign` of the presentation planes in `BeginFrame` | 2.6% | 2.2% |
| SH-2 `Dispatch` (not VDP) | 23% | 8.6% |

Timed scopes (office, per frame): `ComposeLine` 3.7 ms = pixel loop 1.5 + `NormalLine` 1.0 + `SpriteLine` 0.6 + rest
0.6; VDP1 `DrawCommand` 0.4 ms (70 commands, 5.5 us each); `BeginFrame` 0.35 ms. In `attack` the pixel loop is
3.3 ms and VDP1 drawing 1.95 ms (240 commands per frame). No function is above 13%; line-level samples inside them
are spread over dozens of lines (the hottest single line, the palette lookup of `NormalLine`, is 3% of the thread).

## Tried, no effect

Measured with the interleaved A/B (office 4.459 -> 4.443 ms, resume 4.853 -> 4.841, attack 7.702 -> 7.716, all inside
the run-to-run spread of 0.02-0.05 ms): plain pointers and per-line flags for the `ComposeLine` pixel loop, plain
pointers for `SpriteLine`, and a cached `getenv("SATRECOMP_LAYER_PROBE")` that was called twice per line. The timed
build seemed to show 0.6 ms for the `getenv` change, but the untimed executable did not move, so it was an artefact of
the timers. Those edits are not in the patch.

## Shipped: patch 0073

`NormalLine`, plain 16/256-colour cell path: the line vectors, window, colour RAM pointer and mode are read once per
line and the palette entry is converted inline (`To888(Be16(...))`, or `CramLong` in the 24-bit mode), the same value
`Color()` returned. A/B medians of three interleaved runs with `tools/vdp_parity_bench.py ab` (video phases, ms per
frame; an earlier independent set of runs gave -0.07 to -0.10 ms):

| scenario | before | after | change |
| --- | --- | --- | --- |
| office | 4.454 | 4.386 | -0.068 (-1.5%) |
| resume | 4.836 | 4.762 | -0.074 (-1.5%) |
| attack | 7.752 | 7.628 | -0.124 (-1.6%) |

Parity against `local/build/sakura-674182-validated.exe`: 1,200 of 1,200 identical frame hashes in each scenario and an
identical 1280x720 RGB shot, 0 interpreted blocks (`vdp_parity_bench.py run` for both executables, then `compare`).
`tests/test_vdp2_color.cpp` (built as `check-video` does) passes.

## Follow-up opportunities

1. Frame/line reuse: in static scenes (office, dialogue) the whole `ComposeLine` work (about 3.5 ms) recomputes the same
   picture. It needs exact change tracking of VDP2 VRAM, colour RAM, registers and the VDP1 framebuffer, and a replay of
   the side effects (fetcher state, stats, presentation planes). Up to ~3 ms in static scenes, high risk. T116.
2. Presentation planes: `BeginFrame` clears about 7 MB per frame and the pixel loop stores seven planes per pixel; lazy
   clearing of written rows and a struct-of-arrays pixel loop; `SampleNormalPresentation` recomputes the widescreen
   map columns every line although the map signature and scroll are unchanged most frames. T117.
3. VDP1: `RasterTexturedLine` walks Bresenham state per pixel; a fast path for unclipped, ungouraud, unmeshed quads
   would cut the 13% in tactical scenes. T118.

## T118 indexed VDP1 rows

Patch 0170 specializes fully visible horizontal rows with one texel per pixel in the
16- and 256-color bank modes with end codes disabled. VDP1 command widths are
multiples of eight pixels. The specialized path reads each packed byte once in
16-color mode and calls the existing pixel writer for nonzero indices, preserving
framebuffer writes and presentation ownership. Clip, flip, scaling, end-code,
mesh, and Gouraud cases continue through the existing walker.

A/B on the composed stack through 0168, including the 0166 dialogue voice fix.
Each replay used strict-native mode and a 2560×1440 hidden window. The Spanish
Yoneda dialogue and Chapter 1 first attack each matched 240 guest hashes and five
window RGB captures. A separate diagnostic link compared both physical VDP1
framebuffers byte for byte in each of the 240 presented frames per replay. The
glyph plate, VDP2 color, and VDP2 line reuse tests also passed.

Three interleaved timing runs per binary measured average Yoneda VDP work at
4.313 to 3.982 ms per frame by median. Four further interleaved runs per binary
pinned to the same logical core measured 3.915 to 3.590 ms, with emulation at
8.747 to 8.292 ms. Pinned first-attack medians measured 9.204 to 8.904 ms,
while the raw-buffer control measured 8.360 to 8.361 ms. Host load also moved
unrelated phases. These trials support the Yoneda improvement and leave the
size and direction of the first-attack timing change unresolved. These
incremental builds cover the two replays only. Release packaging remains pending.

## T119 VDP2 background priority

Patch 0174 ranks the enabled backgrounds once inside the pixel compositor and
then inserts a visible sprite at its original priority. A nonzero sprite
priority wins ties. The two ranked backgrounds supply the colors beneath
sprite pixels using the existing blend and capture rules.

Strict A/B on the stack through 0171 matched every guest hash and every measured
presentation-plane hash over 435 Ogami map-to-dining frames, 240 held Spanish
Yoneda frames, and 240 first-attack frames. Fourteen 1440p window captures also
matched. The probes exercised nonempty map edges in 32 Ogami frames, glyph
ownership in 239 Yoneda frames, and up to 34,867 sprite-top pixels per first-attack
frame. After rebasing onto 0173, all three traces matched again. A fourth strict
240-frame LIPS replay matched the cover plane on every frame and four additional
1440p captures. Its cover contained up to 12,976 pixels and was active in 239
frames. Native glyph plate, VDP2 color, and VDP2 line reuse tests passed.

Four timing runs per binary were interleaved on the same logical core. Ogami
VDP work measured 4.340 to 4.190 ms at the first transition frame and 4.900 to
4.645 ms across frames 405–430. The first-attack median moved from 8.489 to
8.330 ms. The Yoneda median moved from 4.089 to 3.365 ms while SH-2 and sound
also sped up. The post-transition Ogami span gives the clearest measured
improvement. Release packaging remains pending.

## Not verified

Three scenarios of 1,200 frames only; the GPU video path (`NormalLine` is shared) and other resolutions, interlace and
24-bit colour RAM modes were not run; no play test; the build was an incremental link of three video objects, not a
`build_runtime.py` rebuild.
