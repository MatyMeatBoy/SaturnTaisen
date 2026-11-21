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
