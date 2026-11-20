# Full-stack AOT build (T55-fullstack-aot)

One executable that carries the complete patch stack of `origin/main` (231 patches, last `0245-sakura-nc40-episode6-mouths`, main at `72ab4b8`) and the AOT of 1,411,614 blocks (EVT01..27 of both discs plus `ENDING_DISC2_EN_FULL`, see [the EVT overlay registry](evt-overlay-registry.md)). Before it, the "full stack" executables ran in interpreter mode and the AOT executables lacked the newest patches. The block list is derived from the owner's discs and stays under `local/`; only hashes and counts are versioned.

Status: STATUS_PLACEHOLDER

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
# SDK copy with the whole stack
copy local/deps/satrecomp -> local/deps/satrecomp-full ; git -C local/deps/satrecomp-full reset --hard 67a5fd456609f702817c08164e77e1420dc91138 ; git clean -fd
# apply config/dependencies.json patches in order: git -C local/deps/satrecomp-full apply --whitespace=nowarn <patch>
# block list (disc 1, then disc 2 on top of it, plus the ending module)
python tools/discover_registered_overlays.py --image "local/prepared/disc1/Track 01.iso" --module EVT01 --module EVT03 --module EVT04 --module EVT05 --module EVT07 --module EVT08 --module EVT09 --module EVT10 --module EVT11 --module EVT21 --module EVT22 --module EVT27 --seed-blocks handoff/current-aot/blocks.txt --sdk-root local/deps/satrecomp-full --output local/work/fullstack/d1
python tools/discover_registered_overlays.py --image "local/prepared/disc2/Track 01.iso" --module EVT12 --module EVT13 --module EVT14 --module EVT15 --module EVT16 --module EVT17 --module EVT18 --module EVT19 --module EVT20 --module EVT23 --module EVT24 --module EVT25 --module EVT26 --module ENDING_DISC2_EN_FULL --seed-blocks local/work/fullstack/d1/blocks.txt --sdk-root local/deps/satrecomp-full --output local/work/fullstack/d2
# compile: build_runtime.py recompile with ROOT = this checkout, DEP/WORK/BUILD = the -full paths, 16 threads
```

The generator reports 674,182 -> 979,690 (+305,508) -> 1,411,614 (+431,924 = 377,846 EVT disc 2 + 54,078 ENDING). The compile wrapper is the `run.py` pattern of the registry document (module-level `ROOT`, `DEP`, `WORK`, `BUILD` reassigned, `--parallel 16`, FetchContent ImGui/Inter from the launcher build cache); it is the same script with `dependency()` left intact.

RESULTS_PLACEHOLDER
