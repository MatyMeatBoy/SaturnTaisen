# Saturn / PC / HD: requested scope

The user added this scope on 2026-11-17 during v0.2 development and explicitly confirmed reusing and adapting the existing English Saturn translation.

## Desired experience

- A launcher lets the player choose between the Saturn recompilation or the PC version.
- When both compatible versions are imported, it offers Saturn with an HD pack adapted from the PC resources.
- English translation, HD pack, and crisp font are independent options. Keep Japanese/original available and configurations/saves separate per platform.
- Preserve the credits of the existing translation: this work adapts its text for PC, it does not present it as a new translation of its own authorship.
- Use image generation to extend all decorative KABE variants, respecting their motifs and palettes, with integer scaling in the presentation.
- Also extend the backgrounds that come from PC when their resources are loaded: both on the PC path and on Saturn with the PC HD pack. Use the PC image as reference and keep its own detail; do not automatically assign the lower-resolution Saturn extension. The extension is part of the enhanced mode, and the original presentation keeps the original framing.
- Keep video, characters, and the dialogue box separate from the extended background, with their anchors and shadows. Scale each verified set in integers and crop only the decorative excess needed for the resolution.

## Implementation decisions

Work first with local import and manifests of identity, dimensions, format, correspondence, and coverage. Do not replace a resource based on name similarity. The presence of both dumps is necessary, but by itself does not prove that a PC asset is compatible or has a usefully higher resolution.

Implementer's technical proposal: local packs with explicit correspondences and a per-resource Saturn fallback. Keep original images/executables, extracted resources, full scripts, and videos out of the repository and the distribution. Distribute tools, manifests, and reproducible adaptations; generate the pack from the owner's own data.

Reuse English text only when scene/line correspondence and the script controls are verified. Preserve LIPS choices, timing, variable names, and subtitles. Log lines with no equivalence for review, and do not fill them in with an invented machine translation.

## Initial PC dump evidence

`Sakura Taisen PC/SAKURA.mdf` is a 1,461,485,568-byte image with ISO9660/UDF and 2048-byte sectors. The installer identifies as Japanese (0x0011), InstallShield 11.0.0.28844; the Readme is dated 2006. The entry executable is ADVcore.exe. The media contains DrvMgt.dll and SECDRV.SYS: it has not yet been verified that the executable runs on a current Windows. Do not run installers or install old drivers to extract resources; use file/CAB reading instead.

Extraction and analysis do not equate to playable PC support, a complete HD pack, or a finished translation. Publish actual coverage at each milestone.

## Work order

1. Complete and verify the Saturn presentation in progress, preserving v0.1.0.
2. Inventory the PC resources and their containers without modifying the dump.
3. Build a PC/Saturn equivalence table with visual examples and real sizes.
4. Test a small pack of backgrounds/portraits and one translated PC scene before expanding coverage.
5. Add platform selection to the launcher once each path can validate its inputs and failures; do not show an unimplemented path as playable.
6. Expand translation and the pack scene by scene, including gameplay, menus, and videos; validate saves and execution separately on each platform.
