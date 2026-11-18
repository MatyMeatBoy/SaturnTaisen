# Saturn recompilation cases and decisions for Sakura

Date: 11/17/2026. Fifteen reference checkouts were downloaded, without games, pinning their SHA in `upstream-evidence.json`. The listed documents were read and saturnkit code points were inspected; the other games were not run and their figures were not verified here. Links are pinned to commits in the manifest to distinguish evidence from changing documentation.

## Documented issues and application

| Case | Documented failure and fix | Application to Sakura |
| --- | --- | --- |
| [Deep Fear](https://github.com/vs-sr-dev/pc-deepfear/blob/c3d3e4aed34678139e97b5cb83c4fd7b0cf1d343/docs/11-runtime.md) | GFS stayed loading: Play 0xFF was interpreted as infinite repeat. Position/repeat was preserved according to real bits. CD reading too fast overwrote a palette before VBlank; speed and seek were restored. | Start with faithful CD semantics/timing. Do not speed up reads to resolve a wait. |
| Deep Fear | Zero coordinates from division mirror registers not updated; 16-byte DMA copied only a quarter; PLAY announced before the first sector caused buzzing. | Trace transfer and registers before blaming the renderer. Test audio from sectors and not just sample presence. |
| [Albert Odyssey](https://github.com/vs-sr-dev/pc-albertodyssey/blob/45d25d632b9f701eb4e72ab0ec9b801e15f41153/docs/10-saturnkit.md) | Overlays called on a common base had to return to the resident; overlay calls and program startup were separated. RBG0, HBlank, and special priorities fixed backgrounds/sprites. | Identify modules by active content and preserve the guest stack. Compare layers and priorities of real scenes. |
| [Dragon Ball Z](https://github.com/vs-sr-dev/pc-dragonballlegend/blob/e285495ca3159e24f9752a0e7f15a0a7c9bf13e0/docs/10-saturnkit.md) | PIC jumps bsrf/braf and add needed propagation; tasks used longjmp-style returns. A framebuffer change one line late reduced apparent speed. | Discovery of indirect targets and legal returns; guest clock independent of the monitor. |
| [DoDonPachi](https://github.com/vs-sr-dev/pc-dodonpachi/blob/f2dd6ddd59ff97eb810c799ba6b075dc50d8dda2/docs/10-saturnkit.md) | Switch with bound before bra; mova pointers saved in delay slots; loader run in low RAM before overwriting boot. | Do not discover by extension alone nor assume a resident executable. Include delay slots and low RAM. |
| [X JAPAN](https://github.com/vs-sr-dev/pc-xjapan/blob/f9566055d4407d09c7d65a77bee3dc2934c77111/docs/10-saturnkit.md) | ISO crossed XA/interleaved tracks; direct PDR and region did not match INTBACK. A reproducible per-VBlank input was added. | Respect CUE and region. A single pad state for all read paths. |
| [Virtual Hydlide](https://github.com/vs-sr-dev/pc-virtualhydlide/blob/74e8e8abfc5a23623dab610cc207e26bbf9d0ec9/docs/10-saturnkit.md) | Multiple programs, functions, and tables; detection by CRC and instruction contrast with interpreter/another tool. | Separate emission, compilation, executed coverage, and fidelity; the selftest does not prove the full campaign. |
| [Shining Force III](https://github.com/mattkuhnQAAI/sfiii-native/blob/f9456e8bde3be3b74c655e872bdbc4a1c34d4b0f/docs/pr-review-2026-11.md) | Native returns and shared context between CPUs; per-thread context was made with an interrupt barrier. Snapshots lost headers of loaded overlays not yet executed. | Per-CPU state; snapshots identified by build/disc and active module. Flush before replacing saves. |
| Shining Force III | Callbacks discovered inside data; literal pool stores in delay slots; reserved SCSP registers altered DSP taps. Limits/guards and specific regressions were added. | Do not seed any value that looks like a pointer. Log unimplemented accesses. |
| [Fighters Megamix](https://github.com/tmcleroy/fighters-megamix-recomp/blob/12302706853742ee965dcdb4547c99e560f5143c/CHANGELOG.md) | Video frozen and crash when skipping it; fine sync between CPUs, resumable CD buffer, and loop preserved by cache. Sound disappeared due to timeout measured on reads that were too fast; immediate read also broke loading. | Primary candidate for product functions and timing reference. Do not replace libraries with instant hooks without testing their contract. |
| Fighters Megamix | Double interlace doubled the foreground height. Old states lost compatibility when musical position was added. | Geometry by observed mode and versioned states. Do not validate scaling with a single screen. |
| [Fighting Vipers](https://github.com/tmcleroy/fighting-vipers-recomp/blob/b4b1942e68e6dcd00f8bb2c0fa551a7ed28553bb/docs/LAUNCHER.md) | Launcher and menu share settings, remapping, button lock on close, data separate from the program, and portable mode. | Useful model for shared settings, Start+Select, and Saturn profiles. Do not import unrelated combat functions. |
| [Hyper Duel](https://github.com/omegakatana92/Hyper-Duel-Recomp-/blob/cfe7c04ad5d46bbfcb74b4203e779f40b4d769ac/docs/DEVELOPMENT_LOG.md) | Missing CD buffer commands blocked GFS; track:index was confused with FAD. CD-DA had to consume 588 samples per sector without filling the data FIFO and exclude the following pregap. | Keep data and audio separate, test pause/resume and real ranges. |
| [Blast Wind](https://github.com/omegakatana92/Blast-Wind-Recomp/blob/a783311be7f692f2fc8af60d8945d91c35f741fe/docs/AUDIO.md) | Reused CD-DA fixes but distinguishes sequenced SCSP soundtrack from CD audio; documents diagnosis by source. | Do not treat all music as CD-DA just because the disc has an audio track. |
| [PAL Saturn](https://github.com/yifengling0/pal-saturn-recomp/blob/5281ab9f3805f65369c925cb72793ca2c05bc553/README.md) | The initial diagnosis of a missing rotating plane was retracted: DMA copied a quarter of the data. SCSP pitch and legal returns outside a host frame were also fixed. | Review endianness/masks and mechanisms before diagnosing by image; out-of-function returns must not be globally ignored. |

## Candidate selection

Fighters Megamix is a priority reference requested by the user. `satrecomp@67a5fd4` offers the launcher, menu, and controls closest to the requested product, but `docs/NEXT_GAME.md` acknowledges specific assumptions, incomplete GPU in several modes, CD support, and syncing according to the games already ported. **The analysis/boot of Sakura will first be tested against satrecomp; saturnkit remains as a technical comparison and alternative.**

`saturnkit@3e03fb9` contains in code RBG0, windows, special priorities, SCU DSP, and overlay changes documented by other games. The fork `saturn-recomp@032fd3b` preserves modern infrastructure and Windows tests, but its README still lists several of those functions as pending. Do not assume the fork is a superset of the original. Do not mix its patches without reviewing interfaces and regressions.

Deep Fear still lists the tray/second disc as pending work in the inspected review: it does not test a resolved multi-disc swap. Shining Force III covers different scenarios/profiles; it is also not equivalent to Sakura's internal transition. This function needs its own test.

## RetroAchievements and controllers

The code of [ReKHCoM](https://github.com/MatyMeatBoy/ReKHCoM) was also inspected, not just historical notes: its old documentation describes stages already superseded. It is a reference for encrypted token, owner-thread callbacks, softcore, and UI. Sakura needs its own Saturn map and official 1:1 evaluation.

Official sources: [rcheevos](https://github.com/RetroAchievements/rcheevos), `src/hash/rc_hash_disc.c` (first 512 bytes of sector 0 data), `src/runtime/rc_consoleinfo.c` (two WRAM windows), `include/rc_client.h` (login, softcore, media change, frame and idle). Both original local hashes match [the accepted ones](https://retroachievements.org/game/16546/hashes). The local preparation already applies the v2.1 translation to both discs and preserves those same RA hashes; the English boot, exploration, and save/load paths are detailed in `runtime-validation.json`.

[M30 manual](https://manual.8bitdo.com/m30/m30_windows.html) and [official FAQ](https://support.8bitdo.com/faq/m30-bluetooth-controller.html): the physical labels of its six buttons do not correspond to an Xbox layout; D-pad configurable as a stick. Profiles must distinguish modes and preserve manual remapping. No physical controller validation is available here.


## Overlay regression and SH-2 cache

A synthetic test with two translations of the same PC detected a third, non-recompiled content that ran the previous translation. It was reproduced in high and low WRAM: loop retention ignored CCR.CE. Patch 0009 limits that retention to P0 with cache enabled and invalidates it when CE is disabled, the CPU is reset, CCR.CP is written, or a matching line is purged. The tests also verify that a write from the other SH-2 preserves the loop before purging and that purging another line does not remove it. 8/16/32-bit writes and CP that clears after being written are covered.

Primary reference: [SH7604 Hardware Manual, section 8](https://antime.kapsi.fi/sega/files/sh7604.pdf), CCR 0xFFFFFE92, P0/P1 areas, and associative purge. This fixes the existing retention heuristic; it does not yet implement a full cache with tags, replacement, and timing. The synthetic tests alone do not prove the fidelity of the entire campaign.

## Graphics packs

The November 17 search did not identify a verifiable HD pack for Sakura Wars 1 on Saturn. A pack is not integrated by assumption based on association with another platform or release. The [publication by the English patch's author](https://segaxtreme.net/resources/sakura-wars-english-patch.96/) indicates that the SSP 2.1.1 edition preserves the translation's content and changes the application format; it does not constitute an HD improvement.
