# BG4055 and BG4056 bounded HD cutouts

The PC foreground files use slightly different character groupings.
Each matched figure uses its own measured registration. The shared
loader rejects out-of-bounds and cyan-keyed PC samples. The renderer
checks the native plate, visible layer and native RGB before drawing.
The native silhouette edge and all unmatched poses remain Saturn.

On disc 2, the archived BG4055 scene contains 5,893 native non-key
cells. The offline composition replaces 3,711 eligible cells and
changes 14,815 2x samples. BG4056 replaces 2,601 of 5,411 non-key
cells and changes 10,392 2x samples. The surrounding map and table
stay native. Only exact palette, tile and file keys take the HD path.

Both resources decode and register off the render thread. The
existing foreground compositor masks sprites and preserves native
pixels wherever the PC figure does not fit. Syntax and patch
application passed. Linked HD playback and packaging remain pending.

## BG4053 disc 1

The Chapter 3 Maria route shows all 6,637 opaque native figure cells
in two archived captures. Its saved state has the exact source-4
palette and cells and no color offset. Six region registrations in
patch 0324 accept 3,224 eligible native cells and change 12,869 2x
samples in the offline composition. The native seated figure and
silhouette boundaries remain in place. Preparation uses the same
async decoder and exact owner gate as BG4055 and BG4056. Linked HD
playback and packaging remain pending.

## BG4054 disc 1

A controlled 121-field strict-native replay starts from the
retained 0504 checkpoint with only the script cursor advanced
to the original loading block. The game reads BG1160 and BG4054
and displays all 1,488 native opaque BG4054 cells. The compositor
registers the two matching figure regions with the existing
per-cell ownership guard and asynchronous PC preparation.
Natural branch reachability and linked HD playback remain open.

## BG4057 disc 1

A controlled 181-field strict-native replay from the medical dialogue
advances the chapter 7 script cursor to its original loading block. The
game reads BG4057 and BG1160. All 6,249 opaque BG4057 cells match the
native framebuffer at scene origin (16, 8). The saved state contains the
exact palette and cell data. Five bounded registrations accept 2,488
interior native cells in the offline compositor comparison, with zero
samples outside the native silhouette. The table and the unmatched
figures retain their native art. Linked HD playback and packaging remain
pending.
