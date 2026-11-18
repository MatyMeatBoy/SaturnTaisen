# Sakura: engine-specific knowledge

Research status, 11/17/2026. Primary source: [translation team tools](https://github.com/NoahSteam/RomHackingTools/blob/master/SakuraTaisen/SakuraTaisen.cpp), version pinned in `upstream-evidence.json`. No game resources were copied.

## Material verified here

- Both discs are GS-9037 V1.005 (CD-1/2 and CD-2/2), JT region, booting at 0x06004000. There are 1785 files in each original and in each translation.
- The patch changes 201 files on disc 1 and 199 on disc 2; `translation-code-impact.json` stores sizes and hashes of the relevant candidates. SAKURA and LOGO.SH2 do change: it is not enough to recompile the Japanese version and swap images.
- SAKURA4 and SAKURA5 are large containers without an extension, not monolithic executables that can be inferred from their name. Not all their entries have been classified yet.
- The English title was reached, along with entry into the opening narration, via command scripts. The video and presentation do not yet prove battle, choices, minigames, saving, or the full campaign.

## Contributions from the translation tools

`SakuraTaisen.cpp` contains text extraction/reinsertion, KNJ fonts, palettes, compressed graphics, FCE/FACE faces, WKL menus, EVT events, and subtitles. `FixupSakura` modifies SH-2 instructions for character reading and advancement, with addresses annotated for boot loaded at 0x06004000. This is useful information for naming functions, checking the translated text engine, and locating changes — not a decompilation of the full engine.

Names and offsets from other patches or versions are not applied without checking the exact bytes and disc. Containers must preserve their tables and calls; a graphics mod is not forced by changing a Saturn cell's size.

## Independent reference

Beetle Saturn was downloaded from the official Libretro buildbot for comparison, with SHA-256 hash `8e62cd7a513c0c0f95c8a18856a68cd37d09a43df3a68b898325ed8e79e1aaa0`. It uses the owner-supplied BIOS files and the local translated discs. It identifies disc 1's audio track at LBA 271118, consistent with the patch CUE's POSTGAP and PREGAP.

BIOS boot has an offset relative to the runtime's HLE boot; compare scenes by state and content, not by subtracting an assumed number of frames. Beetle reports 59.8265 Hz for this mode; final speed must respect the guest clock and not depend on the monitor or drawing cost.

## Next work

1. Resolve all state differences between AOT and the toolkit's reference interpretation; keep fallback rejection active.
2. Add VDP2 color calculation and whatever functions the game requires, checking against Beetle scenes/captures.
3. Discover code from both discs and the minigame/battle containers; locate the state machine and disc change.
4. Establish timed-choice, dialogue/voice, battle, minigame, and save tests. Verify these same memory regions when integrating RA.
