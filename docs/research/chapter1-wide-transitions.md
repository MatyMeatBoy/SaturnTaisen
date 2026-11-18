# Chapter 1 widescreen transitions

The native Windows executable, the translated disc 1, and the owner's local states were used. Captures correspond to a hidden 1280×720 SDL window with the Zoom view. Each run used an independent copy of backup memory. Frames are relative to the loading of the indicated state.

| Start | Replay | Observed result |
| --- | --- | --- |
| `intro1799.state` | `tests/chapter1-opening-skip.movie` | `opening → row-gradient → title → native → title`. Captures 91 and 181 are black. The title appears by capture 271 at the latest. |
| `title-final.state` | `tests/chapter1-title-new-game.movie` | `title → native → row-gradient → native → row-gradient → backdrop → movie`. Title menu at 200, LOADING screen with 4:3 frame at 400 and 650, panoramic narrative movie at 1000 and 1450. |
| `map-room.state` | `tests/chapter1-map-dining-hall.movie` | `row-gradient → native → backdrop → narrative`. Map at 250 and 330, fade to the dining hall at 500, dialogue at 750. |
| `theater.state` | `tests/theater-dialogues.movie` | The same layout sequence from map to dialogue. Scene with Sumire at 250 and conversation at 1000–2700. |
| `resume-chapter-6000.state` | `tests/chapter1-lips-confirm.movie` | The night-time LIPS menu is visible at 8 and 32, disappears by frame 59 at the latest, and the answer is complete at 230. All 450 frames stay on `narrative`. Another LIPS, from `prebattle-3000.state`, kept the same layout. |

Run the tests with `python -m unittest discover -s tests -p test_widescreen_transitions.py -v`. They verify the opening, New Game, dining-hall and LIPS transitions and compare the hashes of every frame between the Original and Enhanced presentations. Each route is skipped when its private states are missing. The input videos contain only controller presses.

## Findings in the build examined

- **Loading screen.** A state saved before frame 400 of the New Game route contains the entire LOADING screen on layer 4. The 512-byte FNV-1a fingerprint of the palette is `74EA8ADC9B0340CC`, matching the start of `SAKURA1/LOAD.BIN` (76,672 bytes). 93 non-trivial 256-byte blocks match the state's VRAM.
- **Intermission.** `intermission-down.state`, `intermission-up.state` and `night-patrol-12000.state` showed the Save/Status/Resume menu with a 4:3 frame. Layer 4 contains the full background, Sakura, and the logo. Layer 0 contains the selection box. Layer 4's palette `E9107F892185CCC8` matches both `ICLOGO.BIN` and `LOAD01.BIN`, so the fingerprint alone is ambiguous. All three states share the page signature `79F284B5622630A4`. In `intermission-down.state`, 86 blocks of `IC01.BIN` were recovered in VRAM, mostly at file offset `+0x48C80`, and 41 of `ICLOGO.BIN` at `+0x34280`. `exit-battle-save.state` already uses `anchored-menu`, with the `IC01.BIN` palette `530FF280499422C3`. Layer 4 is disabled in `intermission-save.state`, which shows the status screen.
- **HD text in LIPS.** Two runs of the same night-time route with HD Text Style and Original produce identical captures while the options are visible at frames 8 and 32. At 230, after selection, 8,008 pixels of the answer line change within the capture rectangle `(346,510)–(946,542)`. The current filter only accepts dialogue rows from source coordinate Y=160. The upper box's options fall outside that filter. These runs recorded no verified portrait substitutions.
- **Fades.** The trace emits layout changes without a frame number. The sampled captures support the indicated frames and leave the exact boundaries of the `native` fallback during fades unmeasured. The local-states audit also does not establish continuous chapter coverage.

Logs, captures and layer probes are in `local/work/worker-wide-transitions`. The `opening-skip`, `title-start`, `map-room`, `theater-dialogues`, `lips-patrol` and `lips-original-text` subfolders correspond to the routes in the table and to the text comparison.

## LIPS glyph capture

The VDP1 listing of `resume-chapter-6000.state` contains normal glyph sprites with mode `0080` and size `0210` (16×16). The glyphs match byte for byte with the English atlas used by dialogue. Inactive options use color `C510`. The selected option uses `C570` and also keeps the highlight on the VDP2 layer. All three rows start at Y=54, 78 and 102. The LIPS in `prebattle-3000.state` uses Y=62 and 94. These two cases require recognizing both colors and different heights.

`frontend_sdl.cpp` accepts `C510` and Y=160–196. `NarrativeInkFits` restricts ink to the lower box and `SakuraUi::GameText` applies `NarrativeClip`. In Zoom view, the options box belongs to the image transform. The lower dialogue uses a different transform. A transform and a crop need to be assigned to each line group.

The layer probe shows the frame, the timer, Sakura's figure, and the options' ink on VDP1. VDP2 layer 3 contains the box's fill and highlight. `underSprites` recomposes the pixel without the entire VDP1 layer. Restoring an option's ink pixels this way can also remove Sakura's pixels that should show through under the translucent box. A faithful substitution requires compositing each pixel without the glyph and keeping the VDP1 value prior to that command. Auxiliary data can be kept outside of state serialization.

To verify a future substitution, repeat the night-time route in HD and Original. The change must stay confined to the box's text while the options are visible, preserve frame, timer, highlight and portrait, and keep the game's hashes equal. Repeat in Zoom view and in the view that preserves the original framing.

### Cases to validate a glyph plate

| Case | Expected evidence |
| --- | --- |
| Three night-time options from `resume-chapter-6000.state` | HD modifies only the glyph area relative to Original, including those of the selected row. The VDP2 highlight, timer and frame match for the same frame. |
| Two options from `prebattle-3000.state` | The rows are recognized at Y=62 and Y=94. The selected row keeps its color. |
| Ink above the VDP1 figure | When a row is hidden, the plate preserves the figure under the panel with its color blend. A synthetic case with the same VDP1 value written by a glyph and by a later sprite verifies that visibility follows draw order. |
| Unrecognized glyph, occluded row, or a plate with no data from the displayed framebuffer | The row's native pixels remain intact. After restoring a state, a valid plate is expected before removing ink. |
| Zoom view and original framing | HD text follows the panel's transform and stays within its edges. The lower dialogue keeps its own position. |
| Confirmation and timer expiry | The options text disappears with the box. The answer, the selection, and every frame's hashes match between Original and Enhanced. |

Initial audit status: the plate was not yet implemented. The later implementation and its real tests are in [HD choice text](chapter1-choice-hd.md). The current automated replay checks layout and state parity. The HD/Original comparison of captures 8, 32 and 230 documents the starting point for testing the substitution.

## Fixes after the audit

The intermission accepts the logo's secondary palette only if the native IC01 image matches the displayed framebuffer: at least 80% of samples, at least 60% per quadrant, and sufficient visible diversity. A uniform fade does not satisfy this check. All three affected states and the battle-exit menu with the `anchored-menu` layout were verified. The LOAD.BIN screen now has a provisional generative background and keeps its original animated column. The phase alignment between its tiles and the protected center still needs visual polishing; having a widescreen layout does not prove a finished visual transition.
