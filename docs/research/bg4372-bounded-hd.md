# BG4372 moving hanami figure

A 145-field disc 1 replay from the retained `0100` checkpoint reads
BG4372 with no interpreted blocks. The file is an 8,016-byte, 512 × 144
variant-B panorama with one transparent foreground figure. The PC donor
contains the full picnic scene, so the registered region covers only the
figure. Seven native layer captures each match all 837 foreground pixels
at the measured horizontal origins.

The runtime checks the VDP2 palette, resident cells, camera geometry and
native file hash. It selects the camera origin by matching source-owned
RGB near the live scroll register and declines ambiguous positions. The
cutout cache includes the verified origin so a moving figure refreshes
at its correct position. Source-4 coverage continues to occlude it.

Candidate `34edae4908df57ba8eb9300f7a3b30f4a81d2ebcf0c99c9e6620e59f05b1bc33`
passed strict 1440p comparisons from six camera checkpoints. The four
occluded checkpoints remained pixel-identical with the donor enabled.
At the two visible checkpoints, 28,256 pixels changed in each and the
change bounds moved horizontally by 504 output pixels with the figure.
The Original controls were pixel-identical and each donor/control pair
had identical guest hashes. Package inclusion remains pending.
