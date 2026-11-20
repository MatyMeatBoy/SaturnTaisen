# Headless scene-picture draw: why it showed nothing, and how to reproduce it

Workers on TP9 (PR #377) and THD01 (PR #595) reported that no `scene picture:` line appeared and that a `--pc-assets` capture equalled the control, on several builds and states. The cause is not the pack, the state or a setting.

## Cause

The PC scene picture is drawn only by the enhanced presentation (floral backdrop plus the Zoom scene path, `scene zoom:` / `presentation layout: narrative`). That path needs the floral backdrop texture, which the runtime loads from an `art/` folder **beside the executable** (`art/backgrounds`, `art/screen-backgrounds`, `art/pc-backgrounds`, `art/tactics`; about 104 MB) or beside the settings file. The runs copied only the `.exe` into `local/build/sakura-<name>/` (the rule in docs/SHARDS.md "run from your own copy"), so `art/` was missing. Then the log shows only `presentation layout: native`, there is no `presentation layer N` or `scene zoom:` line, and every capture is the plain native frame with or without a donor. The state, the build, `--pc-assets`, `pc_hd_backgrounds` and `scene_view` were all fine.

Checked here: the same executable (a copy of `local/build/sakura-reattr/sakura-reattr.exe`, `sakura-probe`) on the same state with no `art/` printed no `scene picture:` line; after `cp -r local/build/rebuild-evt/art local/build/sakura-probe/art` it printed `scene picture: SAKURA1/BG/BG1209.SPR usable=1` and the capture differs from the control.

## Command

Copy the executable and its `art/` folder (the toolchain `clang64/bin` must be on PATH for the DLLs):

    cp local/build/sakura-reattr/sakura-reattr.exe local/build/sakura-probe/sakura-probe.exe
    cp -r local/build/rebuild-evt/art local/build/sakura-probe/art
    export PATH="$PWD/../toolkit/msys64/clang64/bin:$PATH"
    python tools/scene_draw_probe.py --exe local/build/sakura-probe/sakura-probe.exe \
        --state local/work/rb-full/a.state --backup local/work/rb-full/backup.bin \
        --pc-assets local/work/pc-cab/out-bg --size 2560x1440

It runs the state twice (with and without `--pc-assets`) and prints `DRAWN: SAKURA1/BG/BG1119.SPR (trace and capture agree; ...)`, exit 0; it exits 1 when nothing was drawn and 2 when a precondition fails (it refuses an executable with no `art/` beside it).

Underlying settings and environment, as the tool sets them:

- settings.ini: `[features]` `preset=custom`, `presentation_mode=1`, `scene_view=1`, `text_style=0`, `run_ahead=0` (`pc_hd_backgrounds` stays at its default 0 = on).
- environment: `SATRECOMP_WINDOW_HIDDEN=1`, `SATRECOMP_SKIP_CHOOSER=1`, `SATRECOMP_BACKGROUND_WORKERS=0`, `SATRECOMP_STRICT_NATIVE=1`, `SATRECOMP_PRESENTATION_TRACE=1`, `SATRECOMP_HD_STATS=1` and, **required for the trace line**, `SATRECOMP_BACKGROUND_STATS=1` (the `scene picture:` line is printed only with it).
- `SATRECOMP_WINDOW_KEYS=2:SIZE=2560x1440,<n-3>:WINDOWSHOT=<png>,<n>:QUIT` (the path must be a Windows-style path such as `D:/...`, not an MSYS `/d/...` one; the exe silently writes no capture otherwise).
- `--disc local/prepared/disc1/game.cue --state-load 0:<state> --backup <copy> --mute --unthrottled --pc-assets <extraction root>`. The pack is the raw PC extraction root `local/work/pc-cab/out-bg` (it holds `SAKURA1/BG/BG*.SPR`); the helper's `hd-resources/pc` works the same. `local/work/v02-pc-game/_t_@_C__` (the default of `tools/coverage_campaign.py`) does not exist on this machine and gives no donor. The prepared HD pack (`v012-prepared-hd`) is for portraits and is not needed.

A `--backup` that is an empty file is rejected ("Invalid backup image"); give a real backup copy or none.

Results with the 2026-11-20 build `sakura-probe` (a copy of sakura-reattr):

| State | Result |
|---|---|
| `local/work/rb-full/a.state` (cold route frame 119,780, corridor), 2560x1440, 200 frames | `scene picture` BG1119 drawn, capture differs |
| cold route of `rb-full/input.movie`, saved at frame 8,799 (letter), 2560x1440, 200 frames | BG1209 `usable=1`, capture differs |

Parameters ruled out as the cause: the build (the other builds have no `art/` beside them either; only reattr was rerun), `scene_view`, `pc_hd_backgrounds`, the pack name, the state, the window size (1280x720 and 2560x1440 both draw once `art/` exists), 600 frames versus 200.

## Not verified

Only BG1119 and BG1209 were drawn here. The other builds named in the reports were not rerun with an `art/` folder. A scene whose palette is not in the scene table, or one with a fade on screen, correctly gives `NOT DRAWN`.

## Matched control packs

For attributing pixel changes, give both runs a PC asset root. Construct two small roots with the same layout. Place the scene SPR under test in the donor root only and pass the other with `--control-pc-assets`. Both runs then select the same floral backdrop. With the packaged v0.2.16-alpha runtime and the Episode 1 corridor checkpoint, the 56-field 1440p comparison traced BG1119 only in the donor run. The matched comparison changed 2,032,062 pixels; the no-pack comparison also changed the floral backdrop and gave 3,558,000. BG1119 already had a verified row.

A successful scene verdict now requires a usable donor trace, changed RGB pixels, the requested number of strict guest hashes and equal donor/control guest hashes and final SRAM. Pillow is required for RGB comparison. A trace-only match remains diagnostic and exits with code 1. An incomplete or divergent replay exits with code 2.
