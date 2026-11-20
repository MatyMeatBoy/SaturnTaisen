<h1 align="center">🌸 SaturnTaisen</h1>
<p align="center"><strong>Sakura Wars / Sakura Taisen · Sega Saturn</strong><br>Static SH-2 recompilation · Windows x64</p>
<p align="center">
  <a href="https://github.com/MatyMeatBoy/SaturnTaisen/releases/tag/v0.2.3.1-alpha"><img alt="v0.2.3.1-alpha" src="https://img.shields.io/badge/release-v0.2.3.1--alpha-9a4564?style=flat-square"></a>
  <img alt="Windows x64 portable" src="https://img.shields.io/badge/Windows-x64_portable-77445b?style=flat-square">
  <a href="docs/research/chapter1-battle-progress.md"><img alt="Static SH-2 AOT" src="https://img.shields.io/badge/SH--2-static_AOT-bf914d?style=flat-square"></a>
  <a href="docs/releases/v0.2.0-test.3.md"><img alt="Local validation documented" src="https://img.shields.io/badge/testing-local_report-5d755d?style=flat-square"></a>
  <a href="https://github.com/MatyMeatBoy/OptiPort"><img alt="OptiPort method" src="https://img.shields.io/badge/method-OptiPort-617b91?style=flat-square"></a>
  <a href="LICENSE"><img alt="GPL-3.0-only" src="https://img.shields.io/badge/license-GPL--3.0--only-646464?style=flat-square"></a>
</p>

A return to the Imperial Theater with recompiled SH-2 code, integer-scaled pixels, and optional presentation upgrades. Public project by **MatyMeatBoy**.

<a href="https://recomplauncher.com"><picture><source media="(prefers-color-scheme: dark)" srcset="https://recomplauncher.com/assets/press/launcher/badge-light.svg"><img alt="Get it on RecompLauncher" src="https://recomplauncher.com/assets/press/launcher/badge-dark.svg" height="48"></picture></a>

**v0.2.3.1-alpha is a public alpha, not the certified complete game.** You bring only your own files — the two Sakura Taisen Saturn discs and, optionally, the PC edition — and the launcher prepares everything else on your PC: English or Spanish, and the HD mod. Chapter 1 end-to-end and the full campaign are not yet verified. [Scope of this release](docs/releases/v0.2.3.1-alpha.md). Earlier packages are kept intact.

## Play

1. Extract the Windows release into a writable folder (about 3 GB free) and open **SaturnTaisen.exe**. Nothing has to be installed or downloaded: no Python, MSYS2, compilers, BIOS or SDK.
2. In **Preparar juego** choose the folder with your files, or any one of them (the rest are looked for beside it), and press **Preparar**. It takes a few minutes the first time.
3. Pick the language (Español / English) and press **Jugar**.

| Your file | Accepted forms |
|---|---|
| Sakura Taisen disc 1 and disc 2, Sega Saturn (Japan, GS-9037 V1.005) | Original dump, or one already patched with the English translation v2.1. `.cue` with its tracks, a single `.bin`/`.img`, a plain `.iso`, a `.zip`, or a folder with any of them. |
| PC edition (optional, for the HD mod) | Disc image (`.mdf`/`.iso`), a folder with its cabinets, or the installed game folder. |

Every disc is recognized by the SHA-256 of its data track and each step is checked; your files are only read. What is already prepared is recognized and kept, so extracting a newer release over the folder rebuilds only what changed. The language layers are differences that are useless without your own discs: **no discs, BIOS, save files or original game assets are distributed.** Credits of the English translation team and the layer details: [parches/CREDITOS.md](parches/CREDITOS.md).

For RecompLauncher, select the folder containing both discs, then choose your language, presentation and window mode from the game's settings. The profile is in [recomplauncher.json](recomplauncher.json). Other frontends can use `SaturnTaisen.exe --rom "<file or folder>" --language es --no-launcher`. See [the command-line integration](recomp-launcher.json) and `SaturnTaisen.exe --help`.

The final game is planned as a unified release with both discs; automatic disc changes during play are still pending.

## Presentation and controls

| Option | Behavior |
|---|---|
| Original | Keeps the original Saturn composition and integer scale of the original raster. |
| Enhanced | Recomposes recognized scenes, up to 16:9, with an original fallback. |
| Original Display | Image and dialogue share a single scale. |
| Zoom Display | Image and dialogue use independent integer scales to best fit; a shadow sits behind the dialogue. |
| HD Text | Optional font with uniform proportions and native advance, clipped inside the text box. |
| HD Mode | One switch on the home page: 19 decorative backgrounds and 302 of 304 portraits prepared from your PC edition. |
| HD Preload | Loads enabled assets before playing; optional, with higher memory use. |
| Controllers | SDL3 with remapping; M30 Bluetooth/2.4G profiles, with manual selection when XInput hides the model. |

Pixels are scaled with nearest-neighbor and integer multipliers. Output keeps the square raster; no fractional aspect correction is applied. On wider surfaces the 16:9 area is centered, with no ultrawide mode. The frame sits outside the playable content.

**F11** toggles fullscreen. **Esc/F1** or **Start+Select/Back** opens settings. The launcher and the game share configuration; the launcher closes once the first frame is confirmed ready. **View logs.bat** opens diagnostics. Save import works on copies, without modifying the sources.

## Verifiable status

| Area | Status and evidence |
|---|---|
| Boot and AOT | Cold boot and tested paths without a guest SH-2 interpreter. |
| Exploration | 119,781 continuous frames of one exploration route; does not equal a complete chapter. |
| Save/load | Specific points in episode 1 and research save files; full campaign and real disc swapping still pending. |
| Combat | Tutorial, movement, defense, and Sakura/Sumire attacks tested. Separate submenus in Enhanced mode; AOT/interpreter SDK tests do not certify victory or campaign completion. |
| HD | Backgrounds and portraits integrated with validation and fallback. Full bodies/poses/expressions still pending. |
| PixelGen v1 | Stage01 right-hand strip integrated and anchored to world scroll; camera and sprites checked on specific routes. |
| Tactical 16:9/HUD | Stage01 enabled in Enhanced mode with corrected menus. Other stages, the full HUD, and the entire battle remain pending. |
| RetroAchievements | Pending: no online/offline achievements are announced as available. |
| PC | Assets are used for the Saturn HD mod; running and translating the PC version itself are on hold. |
| Spanish translation | All ten chapters and the battle text of both discs, reviewed against the reconstructed Japanese; menus redrawn. Selected in the launcher. Played in the game: chapters 1 and 2 plus spot checks; chapters 3–6, 9 and 10 verified on the built image only. Episode cards, LOADING, the extra menu and video subtitles remain English. |

PC body assets will keep a single height-based scale, with the head/torso axis aligned to the original; they will not be stretched to fill a box. Full hardware compatibility across all M30 firmware revisions and the target machine's RX 6900 XT still needs checking there.

[Progression and combat](docs/research/chapter1-battle-progress.md) · [M30 controllers](docs/research/m30-controller-profiles.md) · [PixelGen v1](docs/research/pixelgen-v1.md) · [Saves](docs/research/save-import.md)

<!-- BEGIN HD PROGRESS -->

## Progreso HD

[![Retratos HD preparados](https://img.shields.io/badge/Retratos_HD_preparados-304%2F304%20%28100%25%29-9a4564?style=flat-square)](docs/HD_PROGRESS.md) [![Fondos KABE preparados](https://img.shields.io/badge/Fondos_KABE_preparados-19%2F19%20%28100%25%29-5d755d?style=flat-square)](docs/HD_PROGRESS.md) [![HD global verificado](https://img.shields.io/badge/HD_global-Verificaci%C3%B3n%20pendiente-646464?style=flat-square)](docs/HD_PROGRESS.md)


| Área | Preparado | Verificado en juego |
| --- | --- | --- |
| Retratos y animación | 304/304 (100%) | Sin dato |
| Imágenes de escena | Sin dato | 149/1167 (12,7%) |
| Escenas y transiciones | Sin dato | Sin dato |
| Vídeos | Sin dato | Sin dato |
| Modo táctico | Sin dato | Sin dato |
| HUD y menús PC/Saturn | Sin dato | Sin dato |
| Fondos decorativos KABE | 19/19 (100%) | Sin dato |
| Personajes grandes NC | Sin dato | 47/147 (31,9%) |

| Sección | Integrado |
| --- | --- |
| Retratos y animación | 304/304 (100%) |
| Imágenes de escena | 610/1167 (52,2%) |
| Escenas y transiciones | Sin dato |
| Vídeos | 50/50 (100%) |
| Modo táctico | Sin dato |
| HUD y menús PC/Saturn | 59/229 (25,7%) |
| Fondos decorativos KABE | 19/19 (100%) |
| Personajes grandes NC | 147/147 (100%) |

**HD total: 1189/1916 (62%).** Elementos conectados sobre candidatos de las secciones medidas. La tabla indica por separado la verificación en juego.
- Sin medir todavía (no cuentan): Escenas y transiciones, Modo táctico.

[Inventario, alcance de los porcentajes y pendientes](docs/HD_PROGRESS.md).

<!-- END HD PROGRESS -->

## OptiPort and performance

We apply [OptiPort](https://github.com/MatyMeatBoy/OptiPort): reproductions, comparisons, bounded changes, and evidence tied to the artifact. The badges describe technology, delivery, and documentation; they are not completion percentages or universal stability guarantees.

CPU preparation of 38 backgrounds went from 2.102s with one worker to 0.478s with eight in the recorded measurement; this is asset preparation, **not a demonstrated FPS improvement or a change to overall game loading**. SDL textures are created on the renderer thread. [Conditions and limits](docs/research/saturn-background-workers.md).

## Development

Contributor entry point: [current pending work](docs/PENDIENTES.md) and [technical/art handoff](docs/HANDOFF.md). They distinguish local work from delivered releases and explain the PixelGen v1 method, testing, and coordination between bots.

Python 3.11+, Git, CMake/Ninja/Clang, and SDL3. The satrecomp dependency is pinned by commit and its changes are distributed as reproducible patches. Dumps, saved states, generated code, and original assets stay in `local/`, outside Git.

```powershell
python -m unittest discover -s tests -v
python tools/build_runtime.py build
python tools/build_runtime.py recompile
python tools/build_launcher.py
```

Interpreter-based discovery is used exclusively to investigate coverage; production rejects SH-2 fallback. The reimplemented BIOS/hardware services and the audio 68000 are separate runtime components. The set of candidate blocks does not represent a decompilation percentage or campaign coverage.

[Design](docs/superpowers/specs/2026-11-17-saturn-taisen-first-design.md) · [Saturn board](docs/superpowers/plans/2026-11-17-saturn-priority.md) · [References](docs/research/2026-11-17-investigacion.md) · [Licenses](THIRD_PARTY_NOTICES.md)

Guide for moving to another PC and included tools: [portable handoff](docs/releases/PORTABLE-HANDOFF.md).
