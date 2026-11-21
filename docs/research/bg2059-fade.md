# BG2059 floral transition

A controlled cursor advance to `0x84EE` in the disc 1 `0502` script
reads BG2059. A neutral 180-field strict replay completes with no
interpreted blocks. The exact BG2059 cells and palette appear on VDP2
source 4 with fingerprints `EA7DE43D593086CD` and `5C4F34289FD6B5AF`.

Reloaded checkpoints expose the isolated layers and native framebuffer
from the same rendered field. For part of the picture, source 5 blends
over BG2059 with the source 4 ratio, then applies an RGB offset of −16.
The offline reconstruction uses the Saturn integer calculation and
matches the following counts in the 288 × 144 viewport.

| Field | BG2059 contribution out of 32 | Exact RGB matches |
| --- | ---: | ---: |
| 15 | 13 | 15,670 |
| 30 | 20 | 15,671 |
| 45 | 28 | 15,690 |
| 60 | 30 | 15,886 |
| 75 | 23 | 15,671 |
| 90 | 15 | 15,671 |
| 105 | 8 | 15,670 |
| 120 | Inactive | 0 |

The other pixels use the VDP1 sprite layer as the lower source under
the same floral cover. Using either lower layer according to the native
composition reconstructs all 41,472 viewport pixels at each of the seven
active checkpoints.

The HD path registers only the cave between the baked figures in the PC
donor. It checks the native lower RGB and fully reconstructed blended
pixel before drawing, then applies the live floral mix to the HD samples.
Sprite-owned pixels are left to the guest compositor. The line cache is
bypassed during this identified scene to retain the cover RGB.

Linked candidate `0d42d63473f98a9ef0b7858be27d35d01b50c86e743787039847b123239b7ec7`
completed four strict 160-field passes at 2560 × 1440 with identical
guest hashes. Seven active samples changed only within the registered
cave strip. At fields 120 and 150, after the fade, the Enhanced captures
matched exactly with and without the donor. The Original captures were
pixel-identical at all nine samples. Package inclusion remains pending.
