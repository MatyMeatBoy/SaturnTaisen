# Initial research — November 17, 2026

## Conclusion

There are SH-2 AOT tools that allow investigating a static recompilation. No confirmed public recomp of Sakura Wars 1 for Saturn was found in the searches performed. A decompilation of the Windows port does exist, as do reverse-engineering tools for the Saturn translation. The compatibility of either runtime with Sakura Wars remains untested.

## Priority references

| Project | Type and usefulness | Relevant limit |
| --- | --- | --- |
| [NoahSteam/RomHackingTools](https://github.com/NoahSteam/RomHackingTools) | Translation team tools; contains specific work for Sakura Taisen and Saturn Explorer. Priority for understanding formats. | Not a full decompilation nor a recomp of the game. Check license per component. |
| [sakurayaku/re.sakurataisen](https://github.com/sakurayaku/re.sakurataisen) | French translation for Saturn based on the English work; extraction/insertion and asset documentation. | Confirm licenses before reusing code. |
| [sakurayaku/sakurayaku-platform](https://github.com/sakurayaku/sakurayaku-platform) | Collaborative translation platform. | Its README states it has no code license; do not assume copy permission. |
| [CalciumSigma/Sakura_Wars_1-PC-Decompilation](https://github.com/CalciumSigma/Sakura_Wars_1-PC-Decompilation) | ADVcore decompilation of the 2006 Windows DVD port. May help understand the logic. | Needs the PC executable and old tools. Does not directly consume our Saturn dumps nor their xdelta. Its figures are the author's, not verified here. |
| [vinheim3/sakuraWars1-disasm](https://github.com/vinheim3/sakuraWars1-disasm) | Disassembly of Sakura Wars GB, per its README. | Game Boy Color, not the first Sakura Wars on Saturn. |
| [vs-sr-dev/saturnkit](https://github.com/vs-sr-dev/saturnkit) | Disc analysis, SH-2 to C++ recompiler, and shared runtime. | Experimental and dependent on each game's needs. Evaluate hardware and overlays used by Sakura. |
| [callumjenkins/saturn-recomp](https://github.com/callumjenkins/saturn-recomp) | Fork with independent evolution from saturnkit; SH-2 AOT, C++20, SDL3, and comparison with Beetle Saturn. | VDP2 and hardware functions still incomplete per README. MIT with components and a GPL option that require review. |
| [tmcleroy/satrecomp](https://github.com/tmcleroy/satrecomp) | AOT based on blocks discovered through execution; runtime and validation tools. | Trace coverage does not guarantee covering all branches. Its README and the port repos may be updated at different times. |
| [sonsegajp/SaturnRecomp](https://github.com/sonsegajp/SaturnRecomp) | Research runtime and disc inspection. | The current README clarifies that the playable path uses an interpreter and that there is no complete public AOT emitter. Do not pick it as proof of a finished static recomp. |
| [mattkuhnQAAI/sfiii-native](https://github.com/mattkuhnQAAI/sfiii-native) | Saturn RPG reference with translation profiles, overlays, and saves. | The author expressly limits validation of full campaigns. Do not extrapolate compatibility to Sakura. |
| [vs-sr-dev/pc-deepfear](https://github.com/vs-sr-dev/pc-deepfear) | Reference for loading, streaming, and a multi-disc game over saturnkit. | Its disc swap nor full game has been verified here. |
| [vs-sr-dev/pc-virtualhydlide](https://github.com/vs-sr-dev/pc-virtualhydlide) | Recompilation case with multiple SH-2 programs. | Specific contribution from another game. |
| [yaz0r/Azel](https://github.com/yaz0r/Azel) | Reverse engineering of Panzer Dragoon Saga in C++. | Specific reimplementation, not a universal recomp tool. |
| [Xeeynamo/sotn-decomp](https://github.com/Xeeynamo/sotn-decomp) | Cross-platform decompilation with a Saturn target. | Separate Saturn progress from PSX/PSP progress. |
| [Panzer Dragoon Trilogy, devMiyax](https://www.yabasanshiro.com/pds-recompile) | Builder announced by the author for the trilogy; includes the four Saga discs. | User-experience reference. This research does not audit its implementation nor its compatibility. |

## Extended catalog

`projects.json` keeps links, categories, descriptions, and metadata of the repository consulted via GitHub. It includes more Saturn ports and translations of other Sakura versions. The latter serve as format context, not as a replacement for the Saturn version. Entries without detailed technical reading are flagged as discovery; no verified compatibility is attributed to them.

## Observed local material

- Two discs identified by their names as the Japanese 6M edition, each with a MODE1/2352 data track and a separate CD-DA audio track. The name is not edition verification; hashes and headers still need to be cross-checked.
- Data tracks: disc 1, 635,917,296 bytes; disc 2, 617,896,272 bytes. Audio tracks: 5,357,856 bytes each.
- Two xdelta and two CUE files from the package labeled v2_1. The readme keeps history up to v2.01; do not infer the effective version from the folder name alone.
- The readme states that user data must be extracted with IsoBuster before applying xdelta. The patch's CUE files use MODE1/2048 and WAV.
- There are ODT translation notes; not yet inspected.
- The originals have not been modified; the patch has not been applied nor validated yet.

## Uncertainties that must be resolved experimentally

## BIOS provided after the initial inventory

The local folder `Sega Saturn BIOS` contains eleven 524,288-byte files. Their hashes were computed without modifying the originals. `Bios Saturn 1.01 (J) [!].bin` matches the Japanese BIOS `sega_101.bin` from [Mednafen's official documentation](https://mednafen.github.io/documentation/ss.html), SHA-256 `dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac`. The documented hash for US/Europe is also present. This verifies the identity of those files, not yet the game's boot. No further BIOS dump is needed to start the reference.

## Pending checks

1. Exact reconstruction of the input expected by xdelta, including final sectors. Do not disable checks to make an incompatible patch pass.
2. Code and overlays added by the patch, not just translated assets.
3. Runtime coverage: two SH-2s, synchronization, VDP1/2, audio, video, CD, and save.
4. Screen aspect ratio and resolution modes actually used by the game; pixel aspect and square pixels are not automatically equivalent.
5. Real mechanism of the disc 1 to 2 transition: save, mount, restart, or continuation read. Do not automate using timers or text captures.

## Method and scope

Web and GitHub searches: Sakura Taisen, SakuraWars, Sakura Saturn, Sakura reverse engineering/decompilation; Saturn recomp/decompilation and saturnkit. Primary sources and READMEs of the priority candidates were consulted. The searches are not proof of non-existence, and the code of all repositories has not been exhaustively audited. No games or BIOS were downloaded from the Internet.
