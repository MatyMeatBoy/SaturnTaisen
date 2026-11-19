# BG2238 Chapter 9 dream image

The English disc 2 Chapter 9 public-slot replay loads `BG2238.BIN` at
FAD 127528. The 6,951-frame relay starts from the archived `public-9-strict`
state at frame 9000 and advances with A pulses eight frames long every
48 frames, starting at frame 32. The frame-6950 checkpoint SHA-256 is
`217c10afad38fdc7b1453d0e00d90ac67487979d01fd4e634c07f017dfa19d05`.
VDP2 layer 2 draws the leftmost 288×144 pixels of the 320×144 picture in
the native window at (16,8). The direct correlation is 0.999913.

Patch0123 checks the layer-2 palette `5DEDEF54BF2F059D`, the 46,016
consecutive named cell bytes from VRAM 0x34840 (FNV-1a
`CA9BDE72C500A276`), and all 41,472 RGB and layer samples in the
witnessed viewport. The blank tile at 0x34800 repeats in the pattern-name
table as the fill. BG2338 shares the palette but its cells differ and
its 320×160 presentation still requires a distinct runtime witness.
The guard also excludes fades and foreground overlaps.

Subimage 0 of the pinned `SAKURA1/BG/BG2238.SPR` is 592×320. The
proportional 544×272 crop at (8,28) matches the figure placement and
background alignment, with 0.897 normalized luma correlation. The
compositor draws it in the current Zoom picture rectangle. The blur
belongs to the source scene and is visible in both editions.

At 2560×1440 the 60-frame asset-present and missing runs share every guest
hash (SHA-256 `90f7bd2913c8ac17e34d3b06dfe34d6bf13754f934d93a2fff2afc60e6cff757`).
At frames 20, 40 and 58, RGB changes only in (272,29)–(2288,1037),
with the right and bottom edges excluded. The same-size one-byte donor
mutation, Original mode, and the white exit fade all match their native
controls pixel-for-pixel. Each 60-frame pair has identical guest hashes
and each run reports zero interpreted blocks. The candidate SHA-256 is
`13956d613b79f1eb0f5d7072506c5c824bb9742d93562696ce9d6e800424ea05`.
The 900-frame opening-skip route also matches the previous executable
in all guest hashes and three 1440p captures.

The direct runtime witness covers the still in Chapter 9 on disc 2.
The local workspace measured 52,113,285,062 logical bytes with hard
links counted once and reparse points excluded. The delivered
development ZIP is 6,315,009,692 bytes. No package was rebuilt.
