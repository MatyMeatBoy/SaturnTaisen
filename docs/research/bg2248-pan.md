# BG2248 vertical pan

Chapter 1 of the English Saturn disc pans down the cherry-blossom avenue before the park scene. BG2248 has a 288×296 native image and a corresponding 576×592 PC subimage. BG2248 and the static BG2251 avenue share a palette. The renderer identifies BG2248 by the layer-4 cell fingerprint and confirms every pixel of the opaque inset against the pinned native image. The PC crop starts at twice the verified Saturn row and uses the existing Zoom placement.

The 2560×1440 test sampled six native row offsets of 63, 73, 91, 110, 137 and 152. All 41,472 inset pixels matched the native crop at every offset. Each HD capture matched the expected PC crop with a luminance correlation above 0.99995 and all visual changes stayed inside (272,29)–(2288,1037), right and bottom exclusive. All main route controls matched the same 205 guest frame hashes with zero interpreted blocks.

The older runtime used BG2251 during the BG2248 pan when only the shared-palette donor was available. With that donor still present, the candidate retains the native pan if BG2248.SPR is unavailable or altered. All Original captures matched. The earlier Spanish BG2251 route continued to draw in HD at 2560×1440, with the base and candidate matching all 60 guest hashes and all RGB captures.

Private evidence is in `local/work/codex-tp2a`. The BG2248 asset is byte-identical on both prepared English discs. The live BG2248 witness covers disc 1. No package change.
