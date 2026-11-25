# PC frame-time spikes (THD30)

Status: **not measured, no code change.** The session was stopped by the owner
before any build or replay. This note records what was set up and found so the
next attempt can start directly.

## Scope

Measure the frame time (p50/p99/max) in Enhanced mode at 2560x1440 for
three cases: when a dialogue line starts, when the game enters a map, and when
an HD scene picture or body loads. The THD30 row asks to start with the
continuous MAP14 replay. Then fix the worst host-side cause in
`port/frontend_sdl.cpp` or nearby host code. The fix must keep the guest
`frames.hash` byte-identical with zero interpreted blocks, and sampled RGB
identical.

## Findings so far (setup only)

- This machine has no Windows build of the current `main` runtime.
  `local/build/sakura` was last built on 2026-11-19 and has no `sakura.exe`.
  The newer build trees under `local/build` (`ga36-a33`, `r36s-opti36s`) are
  handheld/ARM targets.
- Earlier release runtimes were linked from objects instead of a full CMake
  build. See `local/work/codex-th1/release-next/link.py`. That script composes
  the SDK tree in a temporary git index (pinned commit plus patches), uses a
  clang `-ivfsoverlay` to compile only the changed units
  (`frontend_sdl.cpp`, `renderer.cpp`), and links them against a response file
  that lists the earlier AOT block objects, including the MAP14 EVT14 variant
  objects. A frontend-only A/B should copy that recipe into a private
  directory. That avoids recompiling the 1,686 generated block files, which the
  2026-11-19 ninja log puts at about 38,000 CPU-seconds.
- Reference outlier to explain: MAP14 at 1440p had one 319.28 ms field.
  About 300 ms of it was outside the SH-2/VDP/audio buckets of RunFrame, with
  diagnostic state hashing on (see
  [park speech performance](park-speech-performance.md#disc-2-tactical-routes)).
  The first step is to rerun that route with and without `frames.hash`
  logging. That separates hashing/IO from host presentation.
- MAP14 inputs: the 8,200-field File 1 entrance receipt is cited at
  `local/work/codex-th1/release-0215/map14-package-receipt.json`, but that
  folder is no longer present. The segments and profiles in
  `local/work/codex-th1/map14-ground` are the remaining candidates.

## Not done

No baseline or candidate build, no timing, no parity check, and no SDK patch.
Number 0342 was reserved for this work and remains unused.
