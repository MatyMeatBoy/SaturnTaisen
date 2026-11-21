# BG1339 bounded HD kitchen variant

The archived disc 1 frame identifies all 41,472 native pixels on
source 2 with page 0x40000, no color calculation and no color offset.
The PC art registers to 199 valid landmarks, with a mean error of
0.58 PC pixels. The bounded compositor reuses the kitchen geometry
from BG1340 and matches the native lighting of this variant.

The offline comparison changes 117,328 2x samples, all within the
registered donor overlap. The bounded luminance correlation is 0.983
and detail correlation is 0.957. The renderer uses the exact palette,
cells and visible ownership and prepares the texture in the existing
background worker. Linked HD playback and packaging remain pending.
