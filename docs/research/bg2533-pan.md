# BG2533 horizontal pan

The Episode 5 replay uses the existing bank-5-battle SRAM and
bank-5-battle-strict movie. During the opening scene it loads 32 sectors
at FAD 152746. BG2533 is displayed by frame 12000. The 512×144 picture
begins at (16,8) in the NBG2 map and its tile pool is at 0x4A000.
At offset 75 all 41,472 native pixels match the decoded crop. At offset
224 the first 272 columns match. The remaining two tile columns contain
a game-supplied edge and are kept.

The PC runtime uses subimage 0 at 2× with a 16-pixel vertical crop offset.
Only the verified part of the inset is replaced. An eight-column ramp
moves with the source pixels and blends the PC art into the native edge.
Matching uses the presented layer and exact RGB values, keeping the
native picture when a scene is occluded or blended. The two installed
asset signatures are pinned. There is no change to the Zoom viewport.

## Verification

The 1080p checkpoint covers offsets 50–129. The 1440p checkpoint covers
150–224. Each A/B pair compares 160 guest frames with the same executable
and with only BG2533.SPR removed from the PC directory in the control.
Twelve captured frames show differences confined to the verified part
of the inset. At the final offset the 112 output pixels on the right
are native, from x2176 through x2287. Original matches all 160 guest
hashes and its six captures with and without the PC asset. All six
replays report zero interpreted blocks. Runtime SHA-256
`989f5f9b7a2fe85617bc5b5516cfe9f87ccfc4b4caf6feafbe5630983a2f9a10`.

The standalone C++ test checks full and clipped pan measurement and
native fallback on changed pixels, wrong layers and missing assets.
Compile `tests/test_bg2533_pan.cpp` with the SDK `port/` include path.
BG2252 keeps its native rendering. Other horizontal and vertical
scenes need individual PC geometry and replay witnesses. No release
package was built.
