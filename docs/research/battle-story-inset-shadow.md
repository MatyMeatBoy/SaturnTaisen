# Narrative vignette shadow in the first battle

The vignette with the three antagonists appears in the English reference `local/work/sakura/battle-entry-ref-002500.png`. The same image is still active in the state `battle-entry-ref-3000.state`, which shows a later line. The second sample was checked via a native 320×224 capture and a layer probe of the same frame. **The battle vignette does not cast a rectangular shadow.**

## Native composition

- The vignette occupies exactly the rectangle `x=16, y=8, width=288, height=144` in VDP2 NBG3, layer 5 of the probe. Its mask contains 41,472 valid pixels, all inside the rectangle. Terrain remains visible on the sides and between the image and the dialogue.
- The unit sprites and the dialogue box with its dark trim appear in VDP1, layer 0. The vignette and the box are separate pieces.
- The state's VDP2 registers have `CLOFEN=007F`, `CLOFSL=0000`, and `COAR=COAG=COAB=01FC`. This subtracts 4 from each composition channel with saturation at 0. The adjustment also affects terrain far from the vignette. `CCCTL=0001` enables NBG0's color calculation.

The strips where a shadow shifted down and to the right would fall were compared, in native coordinates and with exclusive final bounds.

| Region | RGB comparison |
| --- | --- |
| Right, X=304–308 and Y=8–152 | The 576 pixels match a visible plane after the global −4 adjustment. |
| Below, X=20–308 and Y=152–156 | 972 pixels match the visible plane after the global adjustment. Another 97 match NBG0's color blend with ratio 0. The remaining 83 match VDP1's half-darkening after the global adjustment, in the localized footprint of a unit sprite between X=235 and X=268. |

The VDP1 footprint below the image occupies 17, 20, 22, and 24 pixels in those four rows. It is localized to the unit that crosses the strip and does not form a rectangular band under the box.

## Enhanced presentation

With the isolated binary of 643,320 blocks, the two test profiles logged `native` for this state. The full central area of 320×224 matches pixel by pixel between Original and Enhanced, and the game's 12 hashes match. An earlier capture of the same state with the `tactical` trace and the side extension active also matches in every center pixel. The tactical route widens terrain on the sides. The observed scene does not use the narrative Zoom's shadow pass.

If this vignette is recomposed in a future presentation, the shadowless edge of the image, the dialogue box's trim, and the units' local shadows should be preserved. The test is limited to this chapter 1 tactical vignette.

The artifacts are in `local/work/battle-story-inset-shadow`. `frame1/frame-000001.png` and `frame1/layer-layer{0..5}*.png` contain the capture and the synchronized planes. `check-frame1.py` repeats the count. The earlier panoramic capture is at `local/work/chapter1-wide-state-coverage-v2/battle-entry-ref-3000/shot.png`.
