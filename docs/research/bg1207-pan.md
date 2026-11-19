# BG1207 horizontal panorama

Chapter 1 on the English Saturn disc enters the blossom park panorama during normal dialogue. The runtime just before the change presents its native 512×144 picture through the 288×144 picture region in Zoom. The camera pans right, pauses at x = 208, and returns to the left while Saturn VDP2 NBG0 draws the actress in front of the picture.

The PC donor is subimage 0 of SAKURA1/BG/BG1207.SPR (1024×320). For a verified Saturn origin x, the PC crop is (2x, 16, 576, 288). The runtime checks the Saturn file, the live NBG2 palette and cell fingerprints, the exact visible NBG2 pixels and the PC file before drawing. A small NBG0 foreground can be preserved when its layer has no color calculation, line color, shadow, or color offset. Other owners, ambiguous offsets and unsupported blends retain the native composition. The inset stays in the existing Zoom rectangle.

## Evidence

- 700 strict-native guest frame hashes matched between HD enabled and the missing-donor control. The guarded HD path drew 672 frames.
- At 2560×1440, captures at frames 60, 100, 160, 230, 300, and 450 located the corresponding PC crop at x = 28, 68, 128, 198, 208, and 208. Captures at frames 560 and 680 located the return crop at x = 149 and 64 with the actress excluded from the background comparison.
- The native NBG0 patterns identified 837 actress pixels in each return capture, including colors shared with the native backdrop. Every corresponding 7×7 destination block matched bit for bit (41,013 destination pixels per capture).
- The opening blend at frame 25 matched the native capture. Original mode and the altered-file control also matched their paired same-settings baseline. The independent 205-frame BG2248 replay retained its guest hashes and six sampled renders.
- The Saturn BIN has identical bytes on disc 2. The natural runtime witness is for disc 1. Package inclusion remains open.

Private workspace evidence is in local/work/codex-tp2a/ab1207/audit.json. The replay starts at the archived Chapter 1 checkpoint local/work/codex-nc50/iris-relay/f01200.state using local/work/codex-tp2a/native1207/input.movie. The replay script checks the viewport geometry and derives the NBG0 ownership mask from the matching archived VDP2 states.
