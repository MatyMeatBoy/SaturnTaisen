# SH-2 block dispatch speed (T104 / S7)

Goal: make `Dispatch` in `runtime/recomp.cpp` cheaper without changing a guest hash. Result: one change (patch 0074)
removes about 0.85-1.05 ms of the 2.7-3.9 ms the two SH-2 CPUs take per frame in the office and resume scenes;
the tactical scene (`attack`) does not change.

## Method

Same as T103 (PR #168, `docs/research/vdp-software-speed.md`): `tools/vdp_parity_bench.py` (now also prints the `sh-2 cpus`
phase), the three 1,200-frame scenarios (hidden 1280x720 window, unthrottled, strict-native, HD portraits off),
`local/build/rebuild-s7` = copy of `rebuild-s6` (paths rewritten, `cmake .`, copied with `cp -a` so the stored
dependency times stay valid) with only `runtime/recomp.cpp` recompiled. A = `rebuild-s6` executable (SDK with patch
0073), B = same plus patch 0074. Reference for hashes: `local/build/sakura-674182-validated.exe`. Flags `-O3 -DNDEBUG`.
The sampling thread (`tools/vdp_profile_sampler.h`, started at the top of `Dispatch`) and a few temporary counters
were used for the profile and removed before the measured build.

## Where the time went

Sampled share of the emulation thread, `office`: `Dispatch` 21.4%, `Matches` 2.7%, `Run` 2.5%; `attack`: 8.2%, 1.2%,
1.8%. In `Dispatch` one spot held 6% of all samples (the load of `e->lift` of the first entry of the chain: a cache
miss on a cold `Entry`). Counters over 1,200 frames of `office`: 123.6 M dispatches (103,000 per frame, the game
spins in short loops), 1,107.6 M chain entries visited (9 per dispatch), of which 890.7 M (7.2 per dispatch) were
entries that start in the middle of a block (`start != 0`), which a free-running dispatch always skips, and 122.8 M
the entry that matched at once. In `attack`: 101.5 M dispatches, 1.0 entry per dispatch (the chains there are short).

Cause: the table by `offset / 2` chains, for each address, one entry per block that starts there plus one for every
block that passes over that address. Hot loop heads sit under many blocks, so a lookup walked and skipped (and cache
missed on) about seven dead entries before the one it ran.

## Patch 0074

`Region::fast` is a second table by `offset / 2`, chained by `Entry::nextFree`, holding only what a free-running
dispatch can act on: hand-written (lifted) routines and entries that start at instruction 0, in the same order
as `table` (lifts first; later insertions at the front). `Dispatch` (free-running modes) and the call-linking lookup
walk it; the other modes and every other user keep `table`. The entries skipped were skipped with no side effect,
so the selection is the same. Memory: two more pointer tables (about 8 MB) and 8 bytes per entry.

## Measurement (interleaved A/B, 3 runs each, median, `SATRECOMP_FRAME_PROFILE`, ms per frame)

| scenario | SH-2 A | SH-2 B | emulation A | emulation B |
| --- | --- | --- | --- | --- |
| office | 3.568 | 2.726 | 9.609 | 8.729 |
| resume | 3.896 | 2.863 | 10.315 | 9.262 |
| attack | 2.151 | 2.109 | 11.419 | 11.419 |

Run-to-run spread of emulation: 0.1-0.2 ms in office/resume. Video phases did not move (4.415/4.396, 4.774/4.764,
7.571/7.600).

## Parity

`vdp_parity_bench.py run` for `sakura-674182-validated.exe` and the B executable: the per-frame hash files are
byte-identical in the three scenarios (1,200 of 1,200 frames each) and the frame-1,198 PNG shots are byte-identical;
0 interpreted blocks.

## Not done / not verified

- `after-options-3000` at 1,500 frames (the 8.5 ms/frame total the owner measured) was not run.
- No play test, no `build_runtime.py` rebuild (incremental recompile of one object), Debug/ASan or
  `SATRECOMP_VERIFY_CODE=1` not run, `check-*` tests not run.
- The sampler was not re-run on B; what remains in `Dispatch` after the change is unknown.

## What would give more

1. Per-dispatch fixed cost in the idle loops (103,000 block runs per frame in office): `Run`/`Matches`/waiting
   bookkeeping, `Access::GetRegisters` for the wait detector on every dispatch. Profile B and decide. T120.
2. Entry layout: the fields read on every dispatch span two cache lines of a 96-byte entry; packing them and
   compacting the chain heads could save further misses. T121.
