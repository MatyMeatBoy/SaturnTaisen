# PC AOT registry: generated blocks entered by guest page (T124)

Status: **implemented, not built, not measured** (work stopped by the owner at 0:59 on 2026-11-25).

## Change (patch 0340)

Port of the GA36 lab patches `r36s-aot-pages.patch` and `ga36-aot-fast-dispatch.patch` (branch `codex/ga36-rc2-diagnostico`) to the main SDK stack 0001-0339, for the PC build and not gated on `SATRECOMP_R36S`:

- At start, each generated block is queued in every 4 KiB guest page it covers and its code range is marked for write tracking; the `ScanBlock` validation and the ~one `Entry` per resumable instruction are deferred until the dispatcher, `Call` or `Discover` first looks at that page.
- Order at every address is the build's order, and the build's blocks still go after lifted routines and before blocks discovered at run time (`Discover` loads the pages it covers first), so the tables come out as with eager registration.
- Eager registration (as before) when recording, with `SATRECOMP_EXPERIMENTAL_FUNCTIONS` (functions are entered after the blocks and must stay ahead of them), `SATRECOMP_NO_BLOCKS`, or `SATRECOMP_EAGER_BLOCKS=1`.
- The dispatcher skips the loader with one test when the page queue is empty, and drops the `e->start == 0` test on the free-running `fast` chain (that chain only holds lifted routines and entries at instruction 0).
- `--stats` keeps "blocks in build" as the full registered count and adds `pages of generated blocks entered N of M`. `SATRECOMP_LIST_BLOCK_PAGES=1` traces each page loaded.

## Evidence so far

GA36 (QEMU ARMv7, from `ga36-handhelds.md` on that branch): strict AOT state/audio hashes identical; English boot RSS 528 -> 324 MiB. Not yet reproduced on PC.

## Not done

- No PC build of the baseline or the candidate: the baseline build (own SDK copy and build directory on D:, existing `gen/` copied, not regenerated) was stopped while scanning dependencies. The patch has not been compiled.
- No measurement of startup to first frame, peak working set, or unthrottled FPS; no `frames.hash` parity or strict-native check. The prepared method: `title-final.state` + `tests/chapter1-title-new-game.movie`, 6,201 headless unthrottled frames with `--hash-log --stats`, `SATRECOMP_STRICT_NATIVE=1`, `SATRECOMP_SKIP_CHOOSER=1`, A/B/B/A order; startup timed to the `--ready-file` of a hidden-window boot; peak working set from the process counters.
- No package inclusion. Do not merge before the parity replay passes.

## Measured on PC (2026-11-25)

Same objects, two links (main 0339 vs 0339 + 0340), `measure.py` alternating base, cand, cand, base. Opening-film replay 6,201 frames, strict native: guest `frames.hash` identical (`402b7c2ccb56…`) in all four runs, 0 interpreted blocks; 47 of 160 pages of generated blocks entered.

| | base | 0340 |
|---|---|---|
| peak RAM at startup | 790 MB | 260 MB |
| peak RAM, film replay | 709 MB | 338 MB |
| first frame | 2.15-2.31 s | 1.56-1.80 s |
| unthrottled FPS | 72.6 / 60.5 | 83.9 / 54.7 (noise; no clear change) |
