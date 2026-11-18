<h1 align="center">🌸 SaturnTaisen</h1>
<p align="center"><strong>Sakura Wars / Sakura Taisen · Sega Saturn</strong><br>Static SH-2 recompilation · Windows x64</p>
<p align="center">
  <a href="https://github.com/MatyMeatBoy/SaturnTaisen/releases/tag/v0.2.0-alpha"><img alt="v0.2.0-alpha first public release" src="https://img.shields.io/badge/release-v0.2.0--alpha-9a4564?style=flat-square"></a>
  <img alt="Windows x64 portable" src="https://img.shields.io/badge/Windows-x64_portable-77445b?style=flat-square">
  <a href="docs/research/chapter1-battle-progress.md"><img alt="Static SH-2 AOT" src="https://img.shields.io/badge/SH--2-static_AOT-bf914d?style=flat-square"></a>
  <a href="docs/releases/v0.2.0-test.3.md"><img alt="Local validation documented" src="https://img.shields.io/badge/testing-local_report-5d755d?style=flat-square"></a>
  <a href="https://github.com/MatyMeatBoy/OptiPort"><img alt="OptiPort method" src="https://img.shields.io/badge/method-OptiPort-617b91?style=flat-square"></a>
  <a href="LICENSE"><img alt="GPL-3.0-only" src="https://img.shields.io/badge/license-GPL--3.0--only-646464?style=flat-square"></a>
</p>

A return to the Imperial Theater with recompiled SH-2 code, integer-scaled pixels, and optional presentation upgrades. Public project by **MatyMeatBoy**.

**v0.2.0-alpha is the first public release, not the certified complete game.** It includes the AOT fix for the first battle's closing sequence, HD narrative from the preloaded catalog, the 201-portrait checkpoint, and a first Spanish-language draft of chapter 1 (translated and cross-checked against the Japanese script), with all limits documented below. Chapter 1 end-to-end and the full campaign are not yet verified. [Scope of this release](docs/releases/v0.2.0-test.3.md). The [v0.1.2](docs/releases/v0.1.2.md) and [v0.1.5](docs/releases/v0.1.5.md) packages are kept intact. The launcher defaults to English; a Spanish script/menu patch is available (see Development below) and more languages are planned.

## Play

Extract the Windows release into a writable folder and open **Play.bat**. DLLs and the save importer are bundled: you don't need to install Python, MSYS2, compilers, or an SDK to play. This build boots without an external BIOS.

The standard Git release **does not include discs, BIOS, binary translations, save files, or original PC assets**. Bring your own translated discs. The owner's personal transfer package is separate and not published: it bundles the build with only their own English disc 1 and processed HD assets, already placed for auto-detection.

The final game is planned as a **unified release with mandatory import of both discs**. A personal single-disc test does not certify that transition or replace the pending work on the final importer.

## Presentation and controls

| Option | Behavior |
|---|---|
| Original | Keeps the original Saturn composition and integer scale of the original raster. |
| Enhanced | Recomposes recognized scenes, up to 16:9, with an original fallback. |
| Original Display | Image and dialogue share a single scale. |
| Zoom Display | Image and dialogue use independent integer scales to best fit; a shadow sits behind the dialogue. |
| HD Text | Optional font with uniform proportions and native advance, clipped inside the text box. |
| HD Mod | Compatible backgrounds and portraits; can use an already-processed pack without a PC install. |
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
| Spanish translation | Chapter 1 complete, translated and cross-checked against Japanese. Chapters 2-7 have a first English→Spanish draft, validated for line/length/choice rules but not yet cross-checked against Japanese. Chapters 8-10 in progress. Menus pending a language selector in the launcher. |

PC body assets will keep a single height-based scale, with the head/torso axis aligned to the original; they will not be stretched to fill a box. Full hardware compatibility across all M30 firmware revisions and the target machine's RX 6900 XT still needs checking there.

[Progression and combat](docs/research/chapter1-battle-progress.md) · [M30 controllers](docs/research/m30-controller-profiles.md) · [PixelGen v1](docs/research/pixelgen-v1.md) · [Saves](docs/research/save-import.md)

<!-- BEGIN HD PROGRESS -->

## Progreso HD

[![Retratos HD preparados](https://img.shields.io/badge/Retratos_HD_preparados-300%2F304%20%2898.6%25%29-9a4564?style=flat-square)](docs/HD_PROGRESS.md) [![Fondos KABE preparados](https://img.shields.io/badge/Fondos_KABE_preparados-19%2F19%20%28100%25%29-5d755d?style=flat-square)](docs/HD_PROGRESS.md) [![HD global verificado](https://img.shields.io/badge/HD_global-Indeterminado-646464?style=flat-square)](docs/HD_PROGRESS.md)

**Objetivo global: 100% verificado. Estado: Indeterminado.**

| Área | Preparado | Verificado en juego |
| --- | --- | --- |
| Retratos y animación | 300/304 (98,6%) | Sin dato |
| Vídeos | 0/50 (0%) | 0/50 (0%) |
| HUD y menús PC/Saturn | 0/572 (0%) | 0/572 (0%) |
| Fondos decorativos KABE | 19/19 (100%) | Sin dato |
| Personajes grandes NC | 0/3596 (0%) | 0/3596 (0%) |
| Escenas y transiciones | Sin dato | Sin dato |

| Área | Integrado | Verificado en juego |
| --- | --- | --- |
| Retratos y animación | 300/304 (98,6%) | Sin dato |
| Vídeos | 0/50 (0%) | 0/50 (0%) |
| HUD y menús PC/Saturn | 0/572 (0%) | 0/572 (0%) |
| Fondos decorativos KABE | 19/19 (100%) | Sin dato |
| Personajes grandes NC | 0/3596 (0%) | 0/3596 (0%) |
| Escenas y transiciones | Sin dato | Sin dato |

- **Integración global indicativa (media de 5/6 categorías con total): 39,7%.** Cada categoría pesa igual.
- **Integración global ponderada por unidad: 319/4541 (7%).** Mezcla unidades distintas; solo orienta.
- Categorías sin total confirmado: Escenas y transiciones.

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
