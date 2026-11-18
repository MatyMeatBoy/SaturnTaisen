# Dialogue box compositing in Zoom

The native box blends its fill and shadows with the native floral background. In the Enhanced presentation, the compositor stores the already-blended color as an opaque `foreground` pixel. Zoom shifts that image, and the scaled-up floral background is painted with its own transform. That's why the flower pattern stays pinned to the old position inside the box while the pattern outside follows the host background.

The user's capture shows the theater lobby. The dialogue record visible in the capture is in `0100TBL.BIN`, ID 50035, index 469. The lobby test uses a different moment of the same background. A capture was not reused as a pixel source for the test.

## Blend measured on Saturn

Local states were restored in the isolated test.1 and, in a single frame, the native 320 × 224 output and the individual layers' masks and colors were captured. Pixels were measured between Y=153 and 219, where only layers 3 and 5 of the composition have coverage. Layer 3 is NBG1 and wins priority. Layer 5 is NBG3 and provides the floral background.

Ordinary states have `CCCTL=0002`, which enables NBG1 color calculation, and `CCRNA=0A1F`, with ratio 10 for NBG1. `SFCCMD`, `LNCLEN`, and the calculation window are zero in the sample. NBG1's weight is 21/32 and NBG3's is 11/32. The exact per-channel result is `(21 * panel + 11 * background) >> 5`.

| Source state | RGB equality in the isolated area | Visible native glyphs |
| --- | ---: | ---: |
| `after-options-3000.state`, lobby | 14,043 of 14,043 | 111 of 111 pixels equal to the VDP1 color |
| `office-return-3000.state` | 11,191 of 11,191 | 2,966 of 2,966 |
| `iris-correct-room-3000.state` | 12,599 of 12,599 | 1,492 of 1,492 |
| `office-return-6000.state`, portrait blend separate | 14,154 of 14,154 | No footer glyphs in the sample |
| `resume-chapter-6000.state`, footer during LIPS | 14,154 of 14,154 after applying the color offset | No footer glyphs in the sample |

Layer 3 contributes RGB colors (248, 248, 248), (80, 80, 80), and (120, 120, 120) in the measured regions, including the light fill and the shadows. For example, at (56, 160) of the lobby, the background (232, 232, 184) and the fill (248, 248, 248) give (242, 242, 226). At (29, 153), the shadow gray (80, 80, 80) blends with (224, 240, 192) and gives (129, 135, 118). Reducing the whole box to white with a single transparency would lose those shadows.

In the LIPS state, `COAR/G/B=01F0` applies −16 to all three channels. All 14,154 pixels match if the subtraction happens after the bit shift and is clamped to [0,255]. Subtracting first, only from the top color, gave zero matches. In the portrait-fade state, `CCCTL=0042` also enables sprite color calculation. The table measures exclusively the panel pixels outside sprite coverage. The C510 glyphs of the three ordinary states were checked by non-zero ink nibbles against layer 0. In those states they keep VDP1's opaque colors.

## Minimal metadata to recompose

At the point of native compositing that already knows the winning layers, capture a panel recipe only when the formula to be reproduced applies to that pixel.

- Use the real `top` and `second`, before `presentationSource` reassignment. In the first implementation, accept NBG1 on top and NBG3 below with a normal two-screen blend. The `source` ID alone can point at the lower layer. For example, during the first movie's entrance, `CCCTL=000A` allows blending NBG3 and `PRINB=0500` gives it priority 5, above NBG1.
- Store the 24-bit top RGB before blending and the lower weight (w = ratio + 1). A weight value of 0 can indicate the current opaque pixel is kept. The signed RGB offset must correspond to the top layer and be applied after `>> 5`. If grouped by line or recipe, keep the frame's register changes. For a first, limited scope, use only zero offset and keep the other native pixels.
- Preserve the current path for unreproduced modes, pixels with extra sprite shadow, portraits, and visible ornaments. The top RGB preserves the shadows that do belong to NBG1. Operations without a valid recipe still go through the native path.
- When native ink is erased to draw an already-validated HD glyph, also capture the same recipe for the layer pair used by `underSprites`. Consume it only at the positions where that ink is removed. Otherwise, the erased positions would show the floral pattern pinned to its origin again. Native glyphs and visible portraits keep their treatment and order.

For each destination pixel, use the integer transforms in effect to look up the top color in the box and the lower floral color at the background position corresponding to that same destination. Start with the host background with no color offset for the blend, and apply the top layer's offset once at the end. Keep the draw order of the image, its shadow, and the box. The native denominator is 32, and truncation is integer. Conventional 8-bit alpha has a different denominator.

## Proposed validation

First verify that the recipe reconstructs all measured pixels when fed the native background. In Zoom view, compare the box's upper and lower bound against the host background at the same coordinates and check the shadows, the portrait, and the text position. Repeat with original and HD text, and with a state that has a color offset. Keep guest frame-hash parity and check the fallback for out-of-scope blends.

The local evidence is in `local/work/dialogue-panel-audit`, with state hashes, logs, single-capture layers, and the counts of `exact-mix.json` and `offset-exact.json`. The audit validates the blend model on the indicated samples. Host-side recomposition is still a proposal.

`port/panel_compositing.h` implements the per-pixel calculation in `CompositePanelPixel`. The recipe expresses the lower weight and the subsequent signed offset. If the recipe is empty or exceeds the supported ranges, the native pixel is returned. `tests/test_panel_compositing.cpp` checks the lobby, Iris, and LIPS samples, plus saturations and the fallback. The renderer does not yet capture or consume these recipes.

## Integration in development

Patch40 captures the recipes in the compositor and recomposes the panel over the host background in screen coordinates. Framing and the upper region are preserved: in the office-return-3000 witness at 1440p, all 12 guest hashes match and every pixel above Y=1048 is identical to test.1. The RGB difference stays in (386,1048)–(2198,1440), within the dialogue group and its shadows. Local visual review approved pattern continuity; this does not yet prove every fade or panel in the game. Erased HD glyphs use the underPanelMix recipe; unsupported blends keep native RGB.

The same block preserves the map background when the cursor hides the border: underSource proves the lower background is NBG0 before using underSprites. From map-room.state, tests/map-left-edge.movie replays 200 frames: test.1 changes row-gradient→native, the candidate stays on row-gradient, guest hashes are identical, and there are zero interpreted blocks. Private evidence: local/work/map-left-edge-probe.
