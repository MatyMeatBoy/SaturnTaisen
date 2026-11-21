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

The existing floral-cover recipe can reconstruct the confirmed region.
The remaining visible area needs its own source and blend attribution.
An opaque replacement would discard the transition. BG2059 stays pending
until a linked candidate reproduces the complete visible blend and the
transition back to the native scene.
