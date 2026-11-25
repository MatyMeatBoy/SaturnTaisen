# Handoff: v0.3.9 RC (PC optimizations from the GA36 port)

State on 2026-11-25 01:00. No RC was published: no runtime with these changes was built yet. Main is v0.3.8 + #857 (patch 0339).

## Work in flight (five parallel workers, stopped at 0:59; each leaves a draft PR saying what is done, measured and not done)

| Patch (reserved) | Topic | Own clone | Source of the idea |
|---|---|---|---|
| 0340 | Lazy AOT block registration by 4 KiB page + fast dispatch (`runtime/recomp.cpp`) | `D:\01Claude\wt-aotpages` | `patches/platform/r36s-aot-pages.patch`, `ga36-aot-fast-dispatch.patch` on `origin/codex/ga36-rc2-diagnostico` |
| 0341 | Build flags: `-Os` for generated AOT units, `-O3` for the hot core, linker savings (exe is ~850 MB) | `D:\01Claude\wt-buildflags` | `docs/research/ga36-handoff.md` (RC1 flags) |
| none (platform) | GA36 port brought into main, platform patches refreshed onto 0339, apply check | `D:\01Claude\wt-ga36` (+ `wt-ga36-sdk`) | `origin/codex/ga36-handoff`, `origin/codex/ga36-rc2-diagnostico` |
| 0342 | PC frame-time spikes (THD30: talking, map entry, HD scene load) in the frontend | `D:\01Claude\wt-perf` | THD30 row |
| 0343 | Loop fixes from the GA36 alpha (DynaBrothers GA36 work in `D:\01Claude\Dynabrothers1+2`, `D:\01Claude\dyna-ga36-workers`) that apply to the same SDK | `D:\01Claude\wt-loops` | owner: "se arreglaron algunos loops que aplican a todo" |

## How to finish the RC

1. Review each draft PR; adopt a change only with guest `frames.hash` byte-identical to a baseline built from main (opening-film replay: `title-final.state` + `tests/chapter1-title-new-game.movie`, `SATRECOMP_SKIP_CHOOSER=1`, `SATRECOMP_STRICT_NATIVE=1`, `--hash-log`, 0 interpreted blocks) and no FPS loss.
2. Integrate in order 0340, 0341, 0342, 0343 (all touch different files except where noted in the PRs), renumbering if main moved; `tools/check_patch_stack.py`.
3. Build the full runtime from a clean stack copy (never the shared SDK tree while someone has unrecorded changes), replay, then package: VERSION `0.3.9`, `docs/releases/v0.3.9.md`, `tools/build_launcher.py --with-importer --with-setup`, `tools/package_release.py --runtime ... --video-patches local/work/taisen-parches/v0.2 --no-archive` (writes `release.marker`), clean-install check with `preparar-juego prepare` on a copy, zip, `gh release create v0.3.9-rc1 --prerelease`.
4. Clean up the worker clones/build dirs listed above once their PRs are merged or closed (no unique local data).

## Notes

- The shared checkout `D:\01Claude\Sakurawars` was on branch `pendientes/THD48-bg3060-bg3165` with uncommitted `.gitignore` and `config/dependencies.json` changes from another collaborator; nobody touched it.
- GA36 physical-board figures (RC1 ~9 FPS, QEMU 13-14 FPS, target 59.94 Hz) are in `ga36-handoff.md` / `ga36-handhelds.md`; nothing here was tested on the board.
