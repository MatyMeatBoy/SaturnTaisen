# Full-stack AOT build (T55-fullstack-aot)

One executable that carries the complete patch stack of `origin/main` (231 patches, last `0245-sakura-nc40-episode6-mouths`, main at `72ab4b8`) and the AOT of 1,411,614 blocks (EVT01..27 of both discs plus `ENDING_DISC2_EN_FULL`, see [the EVT overlay registry](evt-overlay-registry.md)). Before it, the "full stack" executables ran in interpreter mode and the AOT executables lacked the newest patches. The block list is derived from the owner's discs and stays under `local/`; only hashes and counts are versioned.

Status: built and verified (2026-11-20). Executable `local/build/sakura-full/sakura-full.exe` with `art/` beside it (backgrounds, pc-backgrounds, screen-backgrounds, tactics).

## Inputs (all under `local/`, nothing here is committed)

| Item | Value |
| --- | --- |
| SDK tree | `local/deps/satrecomp-full`: copy of the shared tree, `git reset --hard` to the pinned commit `67a5fd45...`, `git clean`, then the 231 patches applied in order with `git apply` (`core.autocrlf=false`). The shared `local/deps/satrecomp` is stale versus main and was not touched. |
| Stack check | `check_patch_stack.py` (with `DEP` pointed at the copy): `patch stack ok: 231 patches, last patches/0245-...`. `dependency()` of `build_runtime.py` also passes on the copy, so it was **not** bypassed (the earlier `-evt`/`-end2` copies had to). |
| Seed | `handoff/current-aot/blocks.txt` (674,182, SHA-256 `eeb6cf3a498d2ca5434b036f5dc5aca3d3379b19406230ce2df7c3a484c668ae`) and its `block-order.json` |
| Block list | 1,411,614 blocks, `local/work/fullstack/blocks.txt`, SHA-256 `461933ebb1b1dc9e6c5170988d72d002e69174b7935f0af4ea994e758ce1803c` (byte-identical to the #600 `-end2` list) |

## Commands

```powershell
$env:PATH = 'D:\01Claude\TaisenFirst\toolkit\msys64\clang64\bin;' + $env:PATH
# Fresh SDK checkout from the pinned commit. Use the recorded project commit 72ab4b8 for the patch list.
if (Test-Path -LiteralPath 'local/deps/satrecomp-full') { throw 'Use an unused SDK directory; preserve the existing checkout.' }
git clone --no-local --no-checkout local/deps/satrecomp local/deps/satrecomp-full
git -C local/deps/satrecomp-full checkout --detach 67a5fd456609f702817c08164e77e1420dc91138
# Apply the recorded config/dependencies.json patches in their original order to satrecomp-full.
# block list (disc 1, then disc 2 on top of it, plus the ending module)
python tools/discover_registered_overlays.py --image "local/prepared/disc1/Track 01.iso" --module EVT01 --module EVT03 --module EVT04 --module EVT05 --module EVT07 --module EVT08 --module EVT09 --module EVT10 --module EVT11 --module EVT21 --module EVT22 --module EVT27 --seed-blocks handoff/current-aot/blocks.txt --sdk-root local/deps/satrecomp-full --output local/work/fullstack/d1
python tools/discover_registered_overlays.py --image "local/prepared/disc2/Track 01.iso" --module EVT12 --module EVT13 --module EVT14 --module EVT15 --module EVT16 --module EVT17 --module EVT18 --module EVT19 --module EVT20 --module EVT23 --module EVT24 --module EVT25 --module EVT26 --module ENDING_DISC2_EN_FULL --seed-blocks local/work/fullstack/d1/blocks.txt --sdk-root local/deps/satrecomp-full --output local/work/fullstack/d2
# compile: build_runtime.py recompile with ROOT = this checkout, DEP/WORK/BUILD = the -full paths, 16 threads
```

The generator reports 674,182 -> 979,690 (+305,508) -> 1,411,614 (+431,924 = 377,846 EVT disc 2 + 54,078 ENDING). The compile wrapper is the `run.py` pattern of the registry document (module-level `ROOT`, `DEP`, `WORK`, `BUILD` reassigned, `--parallel 16`, FetchContent ImGui/Inter from the launcher build cache); it is the same script with `dependency()` left intact.

## Result

| Item | Value |
| --- | --- |
| Executable SHA-256 | `96d48742606321825f94bf9a2b0c07ec915b091adb2c82cdf6bea0624df1b6ee` (1,773,563,392 bytes) |
| Blocks | 1,411,614, all with native code, 0 skipped; 14,749,860 instructions, 3,530 generated files |
| Patches | all 231 of `origin/main` `72ab4b8`, last `0245-sakura-nc40-episode6-mouths` |
| Compile | 7,190 ninja steps, 16 threads, one process, about 29.5 minutes (recomp generation included) |

Verification (strict native, no `SATRECOMP_NO_BLOCKS`, at most two executables at a time):

- Opening film `tests/opening.movie`, English disc 1, cold, 10,500 frames, headless: exit 0, `interpreted 0 (0.00%)`, 10,500 per-frame hashes byte-identical (cmp) to `sakura-reattr` (1,357,536 blocks); hash log SHA-256 `c3bac7be0ee0d895f98baf9762cffd0229be650b934b12680dad835e98b35351`.
- Public Finale (Sumire ending), English disc 2, cold backup plus the extended movie, `tools/chapter_loads.py --frames 45000`: exit 0, 45,000 hashes, `interpreted 0`, hash log SHA-256 `1048cfd409e90fb877f5cb5e8d0334f21631881b28ede846530bd45146972e65`, identical (cmp) to the earlier #600 run (`sakura-end2`); no stop at `06080000`.
- Drawing patches: `tools/scene_draw_probe.py --exe sakura-full.exe --state local/work/rb-full/a.state --pc-assets local/work/pc-cab/out-bg --size 2560x1440` reports `DRAWN: SAKURA1/BG/BG1119.SPR (trace and capture agree; the captures differ)`; the probe runs strict native and leaves out `SATRECOMP_NO_BLOCKS`.

## Warnings

- The executable is a development runtime for local verification, not a release. Never commit it, the block list, states or captures.
- Frame hashes of scenes that the newer patches change on purpose will differ from older executables; the opening film does not.
- Not verified: frames past 45,000, other endings, 40,000-frame sweeps of the 17 EVT entries with this build, package inclusion.
- `chapter_loads.py` and `check_patch_stack.py` resolve `local/` from the checkout; in a worktree link `local/prepared` (a junction) or pass paths under the checkout.


## Second build: main plus the tactical ground table (`sakura-full2`, T55-fullstack-with-grounds)

The `sakura-full` executable above lacks the generated tactical ground table of PR #440 (patch 0188 on its branch), so the signatures of MAP03, 07, 08, 09, 11, 17, 18, 20, 22, 24, 25 and 26 are not in it and those grounds cannot be probed. Status of the table on `origin/main` `0ffde69`: **not merged**. Number 0188 is taken on main by `0188-sakura-scroll-row-minimum-offset` (and PR #442 also asks for 0188), so the table patch is renumbered to the next free number, `0253-sakura-tactical-ground-table`, listed last in `config/dependencies.json`.

What changed against the #440 branch (it predates MAP12 to MAP16 and the 0214/0240/0242 grounds):

- `kStage12` to `kStage16` are now hand-written entries on main. In `tools/gen_tactical_ground_table.py` they join `HAND` (status `hd`, signatures equal to the derived ones), so the generated `.inc` lists the other 12 maps only: MAP03, 07, 08, 09, 11, 17, 18, 20, 22, 24, 25, 26. Table counts: `hd` 11, `wired-unverified` 12, `native` 2 (MAP10, MAP19), `needs-assembler` 1 (MAP23).
- The patch was regenerated against the stack (a hand-written `kGenerated[]` include plus a loop in `tactical_ground::Find`, after `kStage21`), not re-anchored by script; the `.inc` is the output of `gen_tactical_ground_table.py --derive` from the owner's discs and PC files.
- `config/dependencies.json` also lists `0252-sakura-bg1120-night-corridor`, whose file is on main but was missing from the list (`check_patch_stack.py` refuses unlisted files).
- `tools/hd_chapter_coverage.py` and `config/hd-chapter-coverage.json` of #440 are **not** taken: the branch predates the main versions and would revert them. Moving a map to `hd` there stays for its witness.

| Item | Value |
| --- | --- |
| Patches | the 239 of `config/dependencies.json` (238 of main up to `0252`, plus `0253`) |
| Stack check | `python tools/check_patch_stack.py`: `patch stack ok: 239 patches, last patches/0253-sakura-tactical-ground-table.patch`; `gen_tactical_ground_table.py --check` ok; `python -m unittest tests.test_gen_tactical_ground_table` 22 tests ok |
| SDK tree | `local/deps/satrecomp-full2`: copy of `-full`, `git reset --hard 67a5fd45...`, `git clean -fd`, the 239 patches in order (`git apply`, `core.autocrlf=false`); `dependency()` not bypassed; the shared `local/deps/satrecomp` untouched |
| Block list | the same 1,411,614 blocks, `local/work/fullstack/blocks.txt` copied to `local/work/rebuild-full2`, SHA-256 `461933eb...` (byte-identical to #600 and #621) |
| Build | `local/work/rebuild-full2/run.py` (same wrapper as above, `-full2` paths), `local/build/rebuild-full2`, 16 threads, one process |

### Result of the second build

| Item | Value |
| --- | --- |
| Executable SHA-256 | `914167a20edd7c5f52fbb866d2d82270979c78b7e30dd3a6d4874401b44e3c9d` (1,773,575,680 bytes), `local/build/sakura-full2/sakura-full2.exe` with `art/` beside it |
| Blocks | 1,411,614, all with native code, 0 skipped; 14,749,860 instructions, 3,530 generated files |
| Compile | 7,190 ninja steps, 16 threads, one process, about 27.5 minutes from start of the recomp generation to the link (1,651 s) |

Verification (strict native, no `SATRECOMP_NO_BLOCKS`, at most two executables at a time):

- Opening film `tests/opening.movie`, English disc 1, cold, 10,500 frames, headless: exit 0, `interpreted 0`, the 10,500 hashes are byte-identical (`cmp`) to those of `sakura-full`; hash log SHA-256 `c3bac7be0ee0d895f98baf9762cffd0229be650b934b12680dad835e98b35351` (same as the first build).
- Public Finale (Sumire ending), English disc 2, `tools/chapter_loads.py --disc 2 --frames 45000` with the cold backup (SHA-256 `efe16833...`) and the extended movie (SHA-256 `e0cdea12...`): exit 0, 45,000 hashes, `interpreted 0`; `frames.hash` identical (`cmp`) to the `sakura-end2` run (so identical to `sakura-full`, which matched it); its SHA-256 is `837014384090cc006f9b7026319e85d334ec651ac2630edeeae4f1396d3f29b5`.
- Draw probe: `python tools/scene_draw_probe.py --exe local/build/sakura-full2/sakura-full2.exe --state local/work/rb-full/a.state --pc-assets local/work/pc-cab/out-bg --size 2560x1440`: `DRAWN: SAKURA1/BG/BG1119.SPR (trace and capture agree; 2032066 pixels differ from the control)`.
- Signatures: the 12 new 8-byte map signatures (MAP03, 07, 08, 09, 11, 17, 18, 20, 22, 24, 25, 26) and the 12 `MAPnn_A.SPR` path strings are in `sakura-full2.exe`; the MAP07 signature is not in `sakura-full.exe`.
- Ground probe (THD16 version of `tools/tactical_ground_probe.py`, PR #677; 240 frames, 2560x1440, guest hashes identical with and without the donor, same SRAM, `interpreted 0`): MAP14 (`local/work/sweep/run2-bank-8-battle-2/state-6999.bin`, disc 2) `DRAWN`, 1,859,328 of 2,580,480 centre pixels (72.1%), 0 outside; MAP19 (`run2-bank-10-battle-2/state-6999.bin`) `NOT-DRAWN`, 0 changed pixels (native by review).

Not verified: no state reaches any of the 12 new maps, so none has been seen drawn (they stay `wired-unverified`); the table itself changes only host code, so guest hashes of the opening and the Finale are unaffected, which is what the identical hash logs show. Frames past 45,000, other endings and package inclusion are open. The executable is a development runtime, never to be committed.
