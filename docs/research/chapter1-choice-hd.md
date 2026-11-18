# HD text for LIPS choices

Patch 0045 replaces the English options using the verified atlas and the commands from the displayed framebuffer. It recognizes two- or three-option panels by their clock, mode, banks, rows, and centering. Every retired pixel requires a glyph plate and owners belonging to the same complete panel; if there is occlusion, incomplete data, or an unknown glyph, it preserves the native text.

The font reuses the existing HD typeface, with uniform transformation and its own panel clipping. Zoom uses the upper image's transformation; the combined view keeps its own framing. It does not change inputs, timer, nor game logic. The replacement is activated with HD text in Enhanced mode and the known English atlas; other languages require their own validated atlas and remain pending.

## Real evidence

Ten profiles were run at 1600x900: Original and Enhanced with Zoom/combined view, each with HD/native text. Two private chapter 1 scenes provided two- and three-option panels. Each profile ran 240 frames, with the same selection and confirmation inputs.

- The 240 hashes per scene were identical across their five profiles; all runs ended with zero interpreted blocks.
- The HD profiles recognized two or three complete rows with saved_under=1.
- Captures 8 and 31: differences limited to the panel's text zones; clock, frame, and highlight do not change relative to the same profile without HD text.
- Capture 59: HD and native are identical after the options disappear; no residual letters remain.
- Capture 230: the lower answer uses the usual HD text. The Zoom panels of both scenes were visually reviewed: text stays within the frame and rows are separated.

Synthetic tests: shared ownership of two glyphs, rejection of an external owner, incomplete rows, centering/clipping, and ambiguous data. They passed the choice fixture and the glyph-plate and VDP2 fixtures. The SDK's composite tree matches patches 0001..0045.

The states, captures, executable, and result.json receipt remain in the owner's local/work/choice-text-qa. These tests do not certify every choice in the campaign nor the clock's natural timeout. The patch is implemented and tested on these routes; it is not included in the previously delivered packages.
