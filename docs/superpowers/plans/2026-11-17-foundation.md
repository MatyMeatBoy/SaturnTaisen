# SaturnTaisenFirst Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare both translated discs with reproducible validation, identify their code, and open Sakura's AOT path without replacing it with emulation.

**Architecture:** Python tools keep local data separate from versioned code. satrecomp is the first candidate for the Windows runtime and the interface; decisions are checked against the investigated cases and the game's real calls.

**Tech Stack:** Python 3.11, official xdelta3, C++/SDL3, and an available Windows toolchain. Dependencies pinned by commit.

**Spec:** `docs/superpowers/specs/2026-11-17-saturn-taisen-first-design.md`

## Global Constraints

- Static recompilation of both SH-2s; the interpreter is for discovery/reference only.
- Dumps, BIOS, resources, extracted executables, and generated C++ stay local.
- Both discs, default translation, faithful frame and presentation; launcher/in-game settings, Start+Select, and automatic Saturn profiles.
- Official RA achievements 1:1 online softcore and offline local; no rewards for tests or run-ahead.
- The user authorized continuing until the project is complete, with no further planning pauses. Native execution on branch `implementation/foundation` inside the requested directory.

## Review Focus

- Path with spaces/brackets and a CUE with multiple tracks: don't lose audio or point to the wrong files.
- Truncated sectors or wrong format: fail before writing a valid output.
- Incompatible patch: don't disable checksums or replace originals.
- Different translated image: re-identify code/hash; don't use code generated from another variant.
- Repeat/interruption: don't overwrite existing output or confuse partial files with prepared ones.

## Task 1: Updated evidence and design

Files: `docs/research/2026-11-17-casos-recomp.md`, `upstream-evidence.json`, `discs-inventory.json`, the design doc, and this plan.

- [x] Record SHAs of fifteen candidates and references for twelve failure cases, with fixes and limits.
- [x] Record a real inventory of both discs and RA hashes, with no game bytes.
- [x] Verify JSON and local links; review diff and Git exclusions; commit.

## Task 2: Disc preparation

Files: `tools/prepare_discs.py`, `tests/test_prepare_discs.py`; private output at `local/prepared/disc1`, `disc2`.

Interfaces: `extract_mode1(source: Path, destination: Path) -> int` validates raw sectors and returns the count; `prepare_disc(cue: Path, patch: Path, output: Path, xdelta: Path) -> dict` prepares a fresh output with a SHA-256 manifest, translation, and RA identity. Never modifies the source.

- [x] Write tests with synthetic sectors: content conversion, rejection of truncated/wrong mode, path with spaces, and rejection of an existing destination. Run them and confirm they fail due to missing functionality.
- [x] Implement validated extraction and CD-DA to WAV conversion preserving CUE indices; xdelta with no flags that disable checksums; use temp files and publish the manifest only on completion.
- [x] Run the suite; apply both real patches in private folders; verify hashes, headers, CUE, and audio. If the delta fails, investigate the exact expected representation before changing anything.
- [x] Save non-proprietary evidence metadata and commit.

## Task 3: AOT map and runtime feasibility

Files: game configuration and tools under `games/sakura/` and `tools/`, pinned dependencies; outputs under `local/`.

- [ ] Inspect SAKURA, SH2 modules, and overlays in both translations; record addresses from crt0/real loads, not from file names.
- [ ] Run satrecomp's analysis tools, checking decoding and hardware assumptions against saturnkit.
- [ ] Build a minimal runtime and selftests with no games; resolve Windows failures with targeted regressions.
- [x] Instrumented discovery; emit/compile guest code and test boot/first scene. Record every missing target or device. Don't hide errors with success stubs.

## Project continuation

Each block is detailed once evidence of its real interfaces is obtained: scene and overlay coverage; shared interface and settings; SDL/M30 profiles and combination; presentation/frame/mods; rcheevos adapter and offline catalog; disc transition; campaign and package validation. The initial stage will not be marked as a complete recompilation. The final acceptance suite includes dialogue/voice, choices, battle, minigames, save/load, real 1→2 disc swap, reopening, and official achievements on both discs.
