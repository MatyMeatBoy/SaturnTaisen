# GA36 loop fixes: inventory for the Saturn SDK

Status: **unfinished, stopped by the owner**. This is a review of the sources only. No SDK patch was written, nothing was built, and nothing was measured. Patch number 0343 is reserved and still unused.

## Sources reviewed

- `origin/codex/ga36-handoff` and `origin/codex/ga36-rc2-diagnostico` (Sakura GA36).
- `D:/01Claude/Dynabrothers1+2`: CHANGELOG, STATUS, `docs/r36s-debug.md`, `docs/handoff/`, and the git history (searched for loop, hang, idle, spin, wait, stall, starvation and pacing).
- `D:/01Claude/dyna-ga36-workers/*`: last commits of opus-threads, rc, s1-pgo, s2-cpu, s3-video and s4-diag.

## Main finding

DynaBrothers is a Mega Drive port. It runs on `mstan/segagenesisrecomp` (pinned in `docs/research/upstream-pins.json`), not on satrecomp. Its fixes live in that engine's runner, its 68000 step adapter, or DB1 game code. **None of them can be applied as a patch to satrecomp.** The two Sakura GA36 branches contain no loop or hang fix. Their only change to the SH-2 dispatch path is a fast-dispatch tweak in `runtime/recomp.cpp`, and that already belongs to the 0340 worker.

## Fixes found

| # | Fix | Source | Applies to Sakura? | Why |
| --- | --- | --- | --- | --- |
| 1 | Audio bridge repeat limit during queue starvation (15 ms, then fade to silence) | Dyna `784b57a`, `runner/recomp_audio_drc.h` in segagenesisrecomp | Not as a patch | Genesis runner audio bridge. Whether satrecomp `sound/`/`port/` audio has an equivalent conceal loop still needs checking. |
| 2 | Audio ring: one modulo per filter instead of per tap (ARMv7 64-bit division) | Dyna `6c370b6` | Not as a patch | Same bridge. Satrecomp's resampler still needs checking for `% cap` inside a per-tap loop. |
| 3 | DB1 VDP-status and RAM poll loops retired in batches (`games/db1_poll.inc`), off by default | s2-cpu `5f2e9b3` | No | Specific to DB1 68000 addresses. The Saturn analogue would be SH-2 idle-loop detection in satrecomp, which was not reviewed. |
| 4 | Native 68000 instruction chaining (`DYNA_NATIVE_CHAIN`), off by default | s2-cpu `5f2e9b3` | No | Specific to the 68000 engine. |
| 5 | Continuous IRQ entry at instruction boundaries (IRQ/raster deadlock) | Dyna STATUS, `db2-continuous-native-irq.md` | No | Genesis IRQ model. |
| 6 | Extras stall: `host_ui_modal` loop with `SDL_Delay(16)` reading real OS input | Dyna `b65ddd8` and related | No | Genesis runner UI. |
| 7 | DB1 title stall (precomposed title art) | Dyna `c7b5aba` | No | Game art. |
| 8 | AOT dispatch: skip the page loader when the queue is empty; one redundant check removed | Sakura `ga36-aot-fast-dispatch.patch` | Owned by 0340 | It is not a loop fix. In QEMU the hashes were equal, and the gain was inconclusive. |

## Not done

- Review of satrecomp for its own counterparts: SH-2 idle/busy-wait loops in `machine/` and `runtime/recomp.cpp`, CD and VDP wait loops, and the sound thread loop.
- Patch 0343, the baseline and candidate builds, the headless opening-film replay with frames.hash parity and 0 interpreted blocks, and the FPS comparison.

An isolated SDK copy is ready at `D:/01Claude/wt-loops-sdk/satrecomp`: the pinned commit plus the 325 patches from `origin/main` c06a9d6, composite tree `5b81aa5d06fb43ed015be3dd92d1789aa7706813`.
