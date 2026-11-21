# HD minigame overlay

Patch 0326 adds 15 PC subimages from the SAKURA3 minigame assets.
These files are prepared by the HD loader. They are outside the
fixed 1,430-element progress inventory.

| PC asset | Subimages | Use |
| --- | --- | --- |
| SYSTEM/MM_TIME3.SPR | 0-9 | Shooting and cooking timer digits |
| SHOT/SHITA_KI.SPR | 0-3 | Lower and side shooting-gallery trim |
| SHOT/WAKU.SPR | 0 | Top shooting-gallery trim |

The timer has ten exact native texture fingerprints and one shared
palette. The five frame pieces use pinned native commands, palettes
and source textures. Exact visible RGB and later sprite bounds mask
the overlay, and native color is retained when applying PC detail.
The donor files are decoded asynchronously.

The offline archived shooting-gallery comparison changes 63,133
trim subpixels and 112 subpixels in the two visible timer digits.
The runtime releases the overlay texture on renderer reset and
shutdown. Syntax and patch application passed. Linked HD playback
and packaging remain pending.
