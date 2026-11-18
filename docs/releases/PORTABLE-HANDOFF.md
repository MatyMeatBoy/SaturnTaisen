# Transfer to another PC — v0.2.0-test.4

## To play

1. Extract **the entire** ZIP into a folder with write permission. Do not run the program from inside the ZIP.
2. Open `Jugar.bat`. In the personal package, the included English disc 1 and processed HD are detected.
3. Choose Original or Enhanced and the Original or Zoom display. F11 toggles fullscreen; Esc/F1 or Start+Select/Back opens settings.
4. For a quick test use `Probar escena HD.bat` or `Probar combate.bat`. These are personal-package shortcuts and use separate test saves.

The public package requires your own discs. The personal one is a local testing exception with disc 1; it is not published. The final unified game will need both discs. The videos included in this delivery are the Saturn ones: substitution with PC videos is still pending.

## What is included

- Launcher, Windows x64 runtime, and its DLLs: SDL3, libc++, iconv, and zlib.
- `import-saves.exe` and the importer built into the launcher.
- `Mapear M30.exe`, a standalone tool to register buttons and save a JSON report. Its source and guide are in `tools/` and `docs/research/controller-mapper.md`.
- Scripts, configuration, own fonts, and reproducible project patches. The processed HD and the disc are only in the personal ZIP.

**To play you do not need to install Python, MSYS2, compilers, an SDK, or an external BIOS.** The `.py` scripts are development and maintenance tools, not boot steps. If a diagnostic reports a missing DLL, keep the message and check that you extracted the whole folder; do not download loose DLLs.

## Saves, controllers, and diagnostics

`Jugar.bat` saves the portable profile in `user/`. Keep that folder when updating; normal saves are in `user/saves/`. Make a copy before importing or replacing files. The test shortcuts keep their backups separate from the normal save.

The documented M30 XInput mapping uses A→A/South, B→B/East, C→RT, X→X/West, Y→Y/North, Z→RB, L→LB, and R→LT. A device that presents itself as generic Xbox may require manually selecting the M30 profile. DInput and the target PC's hardware are not certified by these tests. `Mapear M30.exe` saves reports; it does not apply the mapping to the game automatically, nor does it send any information over the Internet.

If something fails, open `Ver logs.bat` and keep `user/logs/`, `user/settings.ini`, version, reproduction steps, resolution, GPU, and controller mode/connection. For a button issue, add the JSON created by the mapper. Do not publish discs, BIOS, PC assets, or private saves in a public issue.

## For whoever picks up development

Read `docs/PENDIENTES.md`, `docs/HANDOFF.md`, this version's notes, and the area's research. The delivered runtime has 674,182 AOT blocks and patches 0001–0050; its SHA256 is `df68e9dbe2c7d9efe273e0e716c504774ba5c5f5f0826abc783a2e3d6bffcbd3`.

The dependency is pinned in `config/dependencies.json`; modifications are recorded as patches. Rebuilding requires a separate development environment with Python, CMake/Ninja, and LLVM/Clang from MSYS2 clang64, plus the owner's own dumps and the AOT discovery procedure. The game ZIP does not install that environment nor does it contain code derived from the discs.

The flash experiment 0051 was left out of this delivery, preserved on branch `pendientes/T33-petal-transitions` (`7888d08`). It only covers a subset of the flash; there are still partial phases and petals to resolve. The shared SDK was reverted to stack 0050. Do not apply that experiment as if it were validated or included.

Work is stopped at the user's request after closing this delivery. The private chapter 1/2 handoffs and their limits are documented; they do not amount to a complete campaign.
