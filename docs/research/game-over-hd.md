# Koubu defeat backdrop

Patch 0309 registers the complete picture from SAKURA2/BG/GO_KOUBU.SPR
ordinal 0 for the K_OVER.BIN defeat screen. The native file is byte-identical
across disc 1 and disc 2, in English and Japanese. A retained disc 1 dock
battle defeat state matches all 1,120 active name words and 67,840 native
pixels outside the menu. The original Return to Title and Restart sprites
are restored over the PC art.

The VDP2 NBG0 gate requires page 0x40000, no scroll or color offset, palette
fingerprint 341D7151F625DA9D and the 60,032-byte cell fingerprint
8ED370D18D06677A. The PC file is 275,897 bytes (FNV B87A28F4D6D8F851) and
decodes off the render thread. The crop at (12, 0), 592 by 432, maps onto
the 640 by 448 integer lattice within the existing native viewport.

The S_OVER.BIN variant remains pending. Its PC candidate GO_JINBU has a
different pose and insufficient source pixels for the native framing.
Offline frame matching, syntax and patch application passed. Linked build,
beta playback and packaging remain pending.
