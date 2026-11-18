# SaturnTaisenFirst — proposed design

Status: design approved by the user on 2026-11-17, with later extensions incorporated below. Continuation is authorized until the recomp is complete. The concrete runtime is decided through testing.

## Intent and scope

Run Sakura Wars 1 for Saturn as a native program, keeping its English translation, both discs, and the original presentation. First platform proposed by the implementer: Windows x64, as the available environment. It is not assumed that the complete game is compatible with a current toolkit.

The first milestone is a reproducible feasibility test: identify both discs, prepare validated translated copies, and obtain the first interactive scene from a recompiled SH-2. If hardware or coverage is missing, log the specific blocker. A menu, a finished import, or a boot via interpreter do not count as a playable recompilation.

## Approaches considered

1. **AOT of the Saturn version (chosen).** Evaluate saturnkit/saturn-recomp and satrecomp with the same programs and scenes. Preserves the supplied material; requires adapting hardware and discovering all reachable code.
2. **Integrated emulation.** Would allow an earlier playable reference, but the user chose static recompilation. Can be used as a comparison instrument.
3. **Decomp of the Windows port.** Can provide engine understanding, but requires other files and does not directly apply the Saturn patch. Research reference.

Toolkit selection will start with disc analysis, license, instructions, overlays, and a minimal build. One main candidate will be chosen and scenes tested there; another will only be carried through those scenes if a blocker or a difference appears that justifies it. Do not fix a dependency by its name or by figures from other games.

## Preparation and execution

- Keep original dumps and patches. Compute hashes and verify CUE, sectors, product, and version.
- Convert copies to the exact input expected by xdelta; preserve CD-DA, pregaps, and track relationships. Verify the delta's checks and log output hashes. Stop that preparation on incompatibility; do not force it.
- Analyze both translated versions: boot, resident executables, overlays, and code changes. Code added by the translation must also be recompiled.
- Keep Sakura-specific knowledge in a game-specific layer and pin the toolkit commit. Log undiscovered indirect calls and never simulate a successful return to hide them.
- At the AOT milestone and in the final executable, both SH-2 must run recompiled code, without falling back to an interpreter to complete missing code. Interpretation is only allowed for discovery or reference and is logged as such. Hardware components that are interpreted, such as the audio CPU, will be documented separately.

## Presentation

Preserve the internal resolution and framing of each observed mode. Propose as default the original presentation aspect ratio, with the largest crisp scaling compatible with it, with no cropping or blurry filtering. Also offer a strict integer-scale mode of the source pixels if aspect correction prevents meeting both properties at once. Confirm the effective dimensions before fixing factors or promising 4:3 in every mode.

The frame occupies only the area outside the game. Initial proposal: a discreet thematic frame, adaptable to window, 16:9, and ultrawide, without covering subtitles or the interface. Its concrete art remains pending; it is not a condition for testing AOT.

## Two discs and persistence

A single game profile groups both translated images and one shared persistent backup memory. Resource identifiers include the disc to avoid collisions between files with the same name.

First observe the actual change in the reference. Then detect the request via known state or function and perform the mount and, if the game requires it, the corresponding continuation/reinitialization. Do not blindly merge the ISOs or switch discs based on elapsed time. Preserve saves atomically, keep a copy before a migration, and restore the correct disc when reopening the program.

## Settings, controllers, and mods — added requirements

The launcher and the in-game pause menu share persistent configuration: image, scale, frame, audio, controls, mods, and achievements. Start + Select opens/closes the menu; Select is a port action, not a Saturn button that was invented. Reserve the combination, trigger it only once until released, and prevent buttons held while closing from reaching the game. Include a keyboard shortcut, full controller navigation, and reconnection without held keys.

General support via SDL for Xbox, PlayStation, Nintendo, generic controllers, and all M30 models that expose accessible inputs on PC. Automatic Saturn profiles for recognized devices/modes; remapping and a wizard for unrecognized ones. User settings take precedence. Do not identify an M30 solely by a generic Xbox name. GUID/VID/PID/transport/mode tuples with provenance and confidence; manually selectable profiles when the mode hides the model. Keep Saturn A/B/C and X/Y/Z, L/R, Start, and Select labels from the port. Treat the D-pad as a hat or axes, and C/Z or L/R as buttons or axes with hysteresis. The owner has a Bluetooth M30 but it is not available for physical validation.

English translation and installed compatible packs will be enabled by default and can be disabled. Keep Japanese and English preparations separate, with identity and generated code for each variant. Do not apply recompiled code from one variant onto a different image. Changes that alter code/resources require a safe restart. Look for existing HD mods and enhancements from authors' sources; evaluate coverage, version, license, and memory/RA impact. Do not present a shader, a PC port, or a pack from another game as a verified HD mod for Sakura Saturn. The original frame remains available.

## RetroAchievements and local achievements — added requirements

Official set https://retroachievements.org/game/16546 (68 achievements as of checking on 2026-11-17). Use exactly its identifiers, conditions, titles, descriptions, and badges: no custom challenges. An Achievements tab in the launcher and in-game, filter/progress, and unlock notices with badge, title, and description, functionally similar to ReKHCoM.

Optional login, softcore forced by rc_client; never request passwords in chat nor store them. Windows protects the token with DPAPI. Keep the account and local progress separate. Download/cache the official catalog and badges with version/provenance, and use rcheevos to evaluate the same definition offline. The first fully offline use needs a catalog that is legitimately available locally; do not promise offline download. Without a catalog, report unavailability without inventing achievements.

Offline achievements are saved locally atomically per game/variant/local user. Keep real evaluation separate from previews, run-ahead, and regressions; the latter do not grant achievements. Do not automatically resend historical awards when connecting a different account, nor simulate an online session offline. The queue/retry of an online session uses only the flow supported by rc_client. Save/restore evaluation state alongside game state, restart in the proper mode on reset, and notify disc changes via rc_client_begin_change_media.

rcheevos' official Saturn map flattens WRAM-L at 0x000000–0x0FFFFF and WRAM-H at 0x100000–0x1FFFFF. Read from the runtime's real memories with correct bounds and byte order, not from host addresses. do_frame runs once per real logical frame, never per presentation frame. The two hashes of the original dumps match those registered on RA; repeat identification and check the memory references after the patch. Do not force the game ID nor substitute hashes to hide incompatibility.

## Validation

- Compare against a mature reference and the same translated discs: boot, video, voiced dialogue scene, choice, battle, minigame, and save/load.
- Captures at reproducible moments for framing, aspect ratio, priorities, transparencies, fonts, and subtitles; also check audio and sync.
- Cover exclusive content from both discs and test the actual 1→2 transition, the first save on disc 2, and closing/reopening after the transition.
- Log what was tested and what remains pending. One test path does not certify every branch nor a full campaign.

## Available material and needs

Discs and xdelta are already available to start the research. The user also provided the local `Sega Saturn BIOS` folder, containing eleven 512 KiB files. An owned BIOS helps as a reference (for example Beetle Saturn/Mednafen) and for diagnosis; the final need depends on the selected runtime. Keep it local and log its hash, without uploading it to the repository. Do not assume that any region or revision works for the chosen emulator.

A save near the end of disc 1 will be very useful for testing the transition. It is not a requirement for analyzing the boot. If it does not exist, that point will have to be reached by playing the reference. Do not confuse an emulator savestate with portable backup memory.

## Limits and pending decisions

There is no product code or Sakura build yet. No FPS improvements, widescreen of the game area, or full compatibility are promised. The runtime selection, patch verification, observed graphics modes, and the disc-change mechanism remain pending. The remote repository will be private; it will only contain documentation, own code, and dependencies redistributable under their licenses. BIOS, dumps, xdelta, saves, extracted executables, resources, and C++ generated from the game are excluded.


## Authorized extension: importing saves from emulators

The user asked to import saves from Saturn emulators and use advanced public saves to extend validation. The launcher will offer importing the full backup memory or individual files, detecting the format by content, and showing the found Sakura saves before activating them. Keep the original file and create a copy; do not silently replace or format an existing save. Cover Mednafen/Beetle, SSF (memory and individual files), Yabause/Yaba Sanshiro/Kronos, BUP, SAROO, and other documented formats. Report formats not yet supported without simulating that they were imported.

An emulator's machine states require specific adaptation and are not equivalent to a save made by the game. Do not load them as BUP memory. Public saves are kept locally with provenance, author, version, hash, and results. They must be checked in the game, not merely converted without errors. Include tests of advanced points, endings, minigames, and the disc transition. Importing must not fabricate RetroAchievements unlocks.
