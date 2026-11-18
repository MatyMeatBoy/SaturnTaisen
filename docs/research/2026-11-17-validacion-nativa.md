# Native validation of boot and arrival at the theater

The reproducible run `tests/theater.movie` goes from boot to narration, English dialogue, and the theater map. Its A presses choose one initial route; they do not test every choice nor the full campaign. The combined discovery contains 8,488 block variants across the two discs and both languages. The data and generated C++ remain in `local/`.

## CD initialization failure found

The game called the exit BIOS service, through `0x0600026C`, from `0x06052C36`. The runtime printed a warning and returned zero, allowing it to continue after a failed initialization. The title appearing did not prove a correct initialization.

The owner's Japanese BIOS dump and its RAM in Beetle Saturn allowed identifying the real service. A trace of the original code showed the failure: the CD command `1100 0200 0000 0000` asks to seek track 2, but the runtime only updated the position when it received a FAD address. Leaving the previous position caused the game's CD library error.

Patch 0005 moves the reader to the requested track, preserves position with pause, and distinguishes an invalid track. After fixing it, that initialization's original return is zero and the exit BIOS call disappears. It is tested with synthetic bus commands and with the real disc's boot. The track/FAD distinction is documented in [Yabause's command reference](https://wiki.yabause.org/index.php5?title=CDCommands) and in [Sega's CD communication manual](https://antime.kapsi.fi/sega/files/ST-162-062094.pdf).

Patch 0006 makes strict AOT also reject unimplemented BIOS services. The research interpreter keeps its diagnostic; a production build cannot approve this case by returning provisional success.

## VDP2 composition

Patch 0004 implements normal blending of two screens, saturated sum, foreground/background ratio selection, post-blend color offset, and posterior shadow. It also decodes sprite ratios, their four enable conditions, and the color calculation window. The tests use synthetic VRAM, CRAM, and framebuffer with the real renderer.

The formulas and composition order were cross-checked against [Beetle Saturn's compositor](https://github.com/libretro/beetle-saturn-libretro/blob/master/mednafen/ss/vdp2_render.c). The special per-character/dot modes, extended modes, and line-screen mode remain pending; they keep their diagnostic. The long tested route shows no pending-composition warnings.

## Evidence and limits

- 30,000 state hashes per mode: interpreter, conservative AOT, and AOT replay are identical across every frame. Local evidence `local/work/sakura/parity-5ttcykm7/report.json`.
- The AOT ran that route with no SH-2 interpretation nor unknown BIOS services. Grouping functions/binding calls remains disabled due to a previous divergence at frame 116.
- The Japanese profile preserves the original CUE's data bytes and timings; only its representation changes to ISO/WAV. Its RA hashes match those of the English discs.
- The reference for the hashes is the interpreter on the same runtime. It alone does not prove full hardware fidelity; comparison against Beetle must continue, and the logic, sound, and graphics of the remaining scenes must be validated.
- The measured performance in this run is headless. Concurrent development tasks prevent treating it as a final product measurement with window, audio, and controllers.
- Campaign, battles, minigames, save/load, and the real 1→2 swap are still missing, along with the final launcher, controller, achievement, and mod functions. The recomp is not declared finished.
