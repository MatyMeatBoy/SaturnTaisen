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

## What would give more (not done)

1. Frame/line reuse: in static scenes (office, dialogue) the whole `ComposeLine` work (about 3.5 ms) recomputes the same
   picture. It needs exact change tracking of VDP2 VRAM, colour RAM, registers and the VDP1 framebuffer, and a replay of
   the side effects (fetcher state, stats, presentation planes). Up to ~3 ms in static scenes, high risk. T116.
2. Presentation planes: `BeginFrame` clears about 7 MB per frame and the pixel loop stores seven planes per pixel; lazy
   clearing of written rows and a struct-of-arrays pixel loop; `SampleNormalPresentation` recomputes the widescreen
   map columns every line although the map signature and scroll are unchanged most frames. T117.
3. VDP1: `RasterTexturedLine` walks Bresenham state per pixel; a fast path for unclipped, ungouraud, unmeshed quads
   would cut the 13% in tactical scenes. T118.

## Not verified

Three scenarios of 1,200 frames only; the GPU video path (`NormalLine` is shared) and other resolutions, interlace and
24-bit colour RAM modes were not run; no play test; the build was an incremental link of three video objects, not a
`build_runtime.py` rebuild.
