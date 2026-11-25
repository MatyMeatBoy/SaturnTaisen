# PC build flags from the GA36 port (status: not measured)

Goal: carry the GA36 (ARM) build split to the Windows x64 `sakura.exe` so it builds faster and uses fewer resources. Stopped at the owner's request before any build. **Nothing here is implemented, measured or packaged yet.**

## What GA36 did (from `origin/codex/ga36-rc2-diagnostico`, `docs/research/ga36-handoff.md`)

- Generated AOT units (`work/sakura/gen/blocks_*.cpp`, about 674k blocks): `-Os -DNDEBUG`.
- `-O3` only for the hot core: `machine/{sh2,machine,vdp,cd}.cpp`, `video/{renderer,layers,vdp1,raster}.cpp`, `sound/{chip,m68k}.cpp`, `port/{main,frontend_sdl}.cpp`, `runtime/recomp.cpp`.
- A linker script for ARM section layout (`tools/ga36_arm_aot_layout.py`), needed only for `.ARM.exidx` reach on ARMv7; not relevant to x64.

## Current PC state (read, not changed)

- `tools/build_runtime.py` configures `-DCMAKE_BUILD_TYPE=Release`, so every source, including the 1,688 generated units (1.3 GB of C++), is built with CMake's default `-O3 -DNDEBUG`. No per-file flags exist in the SDK `CMakeLists.txt`; the game target only adds `-Wno-unused-parameter`.
- Recent PC executables are 857-877 MB.

## Planned candidate (to do)

1. SDK patch (reserved number 0341): `set_source_files_properties(${GEN_SOURCES} PROPERTIES COMPILE_OPTIONS -Os)` (or an option `SATRECOMP_AOT_OPT`), keeping `-O3` for the rest; optionally `-Wl,--gc-sections -Wl,--icf=all -s` with lld if the clang64 toolchain links with lld.
2. Build baseline (origin/main flags) and candidate the same way in an isolated clone with its own SDK copy (pinned commit + 325 patches, verified: `patch stack ok: 325 patches, last 0339`) and its own build dir on D:, reusing the existing generated sources (copied, not regenerated).
3. Measure for both: exe size and SHA-256, full build time, startup time, peak RAM, unthrottled headless FPS over the opening-film replay (`title-final.state` + `tests/chapter1-title-new-game.movie`, `SATRECOMP_SKIP_CHOOSER=1`, `SATRECOMP_STRICT_NATIVE=1`, `--hash-log`, repeated runs) and a heavier scene; `frames.hash` byte-identical with `interpreted 0`.
4. Adopt only if FPS is not lower within noise and parity holds.

## Done so far

- Isolated clone `D:\01Claude\wt-buildflags` and SDK copy at the pinned commit with the full stack applied; `tools/check_patch_stack.py` passed.
- Located inputs: shared `local/work/sakura/gen` (1,688 units), `local/work/intro-enhanced/title-final.state`, replay pattern `clip_v026.py` (archived under `D:\01Claude\Papelera\SaturnTaisen-archivo-work-20261121\t53`).

## Not done

No build, no measurement, no patch, no parity run. `-Os` on AOT units could lower FPS on x64 (the hot path of the game runs inside the generated blocks), so this must be measured, not assumed.
