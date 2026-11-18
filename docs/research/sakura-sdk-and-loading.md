# Sakura SDK and loading: evidence for v0.2

## Identified components

The reproducible inventory `tools/audit_sdk.py` reads the four local images without extracting or modifying files. Results are in `sakura-sdk-inventory.json` and distinguish embedded components from confirmed execution.

- `/SAKURA`, initially loaded at `06004000`, contains `GFS_SBL Version 2.10 1996-02-01` and `CPK Version 1.23 1996-04-09`.
- `/SAKURA2/CPK.BIN` contains CPK 1.20; its presence does not prove it replaces the resident player in a specific scene.
- `SLG.BIN`, its alias `0SLG.BIN`, and several minigames contain GFS_SBL 2.10.
- `EVT01.BIN` contains 292 `.text` symbol entries, including CDC, GFS, DMA functions and engine-specific names; disc 2's `EVT18.BIN` contains another 136. These are listings preserved inside resources, **not authenticated symbols of the active revision**. Their addresses require cross-checking before use as hooks.

This grounds studying SBL/GFS and Cinepak. The name `SLG.BIN` does not prove use of the SGL library: it is a game module, not an SDK identification.

## Contracts that must be preserved

[Sega's GFS manual](https://antime.kapsi.fi/sega/files/ST-136-R2-093094.pdf) distinguishes the number of sectors requested, the destination's maximum bytes, and pointer advancement. `GFS_NwFread` requests work; `GFS_NwExecServer` progresses requests, in order. The [function reference](https://www.infochunk.com/saturn/segahtml_en/prgg/prg1/file/hon/p08_14.htm) describes server completion/error. Do not turn an asynchronous operation into an immediate success without verifying its consumers.

[Sega's historical documentation](https://docs.exodusemulator.com/Archives/SegaDTSMirror/software/soft.htm) distinguishes SBL and SGL. Modern toolchains that adapt SGL to GCC do not prove which version Sakura linked against.

## Cases from other projects

- [Fighters Megamix](https://github.com/tmcleroy/fighters-megamix-recomp/releases): restored Fread via the guest unit after sound-effect failures caused by immediate reads; load times increased by roughly two seconds according to its author. Do not run that game or present its figures as Sakura measurements.
- Deep Fear: documentation already pinned in `2026-11-17-casos-recomp.md` describes a palette overwritten before VBlank by a CD that is too fast.
- Hyper Duel: the GFS/CD-DA fixes documented there distinguish track, FAD, pregap, and 588 samples per audio sector.

## First local optimization

Host cache of up to four 64 KiB blocks, allocated on demand; it preserves commands, scheduling, guest timing, and sector content. It serializes seek/read operations, invalidates on opening another image, and keeps WAV data out of the delivered PCM. The `SATRECOMP_DISC_CACHE=0` mode provides a no-cache comparison. `SATRECOMP_DISC_IO_STATS=1` reports requests, hits, physical library reads, bytes, and host I/O time. Do not confuse these reads with physical SSD accesses: the operating system also keeps its own cache.

The synthetic test serves 80 sectors with three library reads and checks concurrency, limits, and reopening. This **does not yet demonstrate a reduction in Sakura's perceived load time**; it requires repeated comparisons and hashes with the cache enabled/disabled. Speeding up the CD clock remains pending scene-specific research.

## English source

[NoahSteam's](https://github.com/NoahSteam/RomHackingTools/blob/master/SakuraTaisen/SakuraTaisen.cpp) tools document ASCII indices, 8x12 spacing, and 16x16 narrative tiles; the SLG translation uses 8x12 tiles. The 56 KNJ files on English disc 1 share the same SHA-256 `7d373f80bb217b153a7ba0c94d948a41192acffbf38cfeb0ea13df586e6eca57`. A real Iris capture confirms 16x16 sprites with 8-pixel advance and texture codes consistent with that table. Use exact atlas/tile checks and real commands; no per-frame OCR nor inferences based solely on pixel color.
