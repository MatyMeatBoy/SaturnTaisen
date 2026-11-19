# BG2159 city view on disc 2

The Chapter 8 Spanish disc 2 replay starts at the retained
`d2-ep8-continue/final.state` with the matching backup RAM and
`movie-d2-ep8-largo.movie` rebased at frame 9500. The 275-frame relay
saved the city view at frame 274. Its BG2159 tile bytes are at VDP2
VRAM 0x34840 and its palette at CRAM 0x200. The native inset matches
the decoded Saturn picture with luminance correlation 0.99989.
The retained state SHA-256 is
`d1d2330a1eff56073f4e36a15353b31277ab59ccf502d72b0c897f93b25bc07c`.

Two 60-frame Enhanced Zoom replays loaded that state without inputs at
2560×1440. Both used the v0.2.6 campaign runtime with SHA-256
`6fcd9aba866a1f3c14c706b8c1a9edc4b40ad4f5a555daa2454c9a59a9269482`.
The HD profile could see only BG2159.SPR and reported a usable texture.
The control pointed to an empty PC asset directory. Both runs reported
zero interpreted blocks. All 60 guest hashes match (log SHA-256
`0eb1ba0c3e206bbf78894ad9a8f94d086a644254b734137d3a20c61c0ba91ce9`).

Captures at frames 20, 40 and 58 differ only in (272,29)–(2288,1037),
right and bottom exclusive. The rooftops, street and canal align
with the native composition by eye. The dialogue panel and surrounding
presentation are pixel-identical. The coverage register attributes this
visual occurrence to disc 2 Chapter 8 and keeps the disc 1 campaign trace
with its own evidence. No runtime or package was built.

The main workspace measured 50,982,181,910 logical bytes with hard links counted
once and reparse points excluded, above the 20 GB cap. The existing development ZIP remains
6,315,009,692 bytes.
