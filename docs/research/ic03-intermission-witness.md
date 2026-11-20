# Chapter 3 IC03 intermission

A natural English Saturn disc-1 route continues from the verified BG2290
stage-wing scene through Kanna's training and the later Maria dialogue.
The route reads IC03.BIN at FAD 158051 in 38 sectors. The 76,672-byte file
has SHA-256
`a9610eae300a4cd39e5d686b53fa549cea97f8812a8de23a10dd85944ba7b0fe`.
The disc-2 copy is byte-identical. Its displayed composition remains
unwitnessed.

The live source-4 plate uses VDP2 page `0x44000`, palette
`E9107F892185CCC8` and the unshifted protected-area RGB fingerprint
`6469CD72E7963265`. The source-2 emblem and menu occupy the same
half-open rectangle (184,16)–(296,144) as IC0501. The PC counterpart
is IC0300.SPR subimage 0, 640×480, 185,398 bytes, FNV-1a
`7A7ED93DF49A6CE5` and SHA-256
`45d503ff541ece13887cbfa8ca882cab666c448acc8b500fd91066b5f15dd80f`.
The complete image fits the same 640×448 registration rule as IC0501.
Whole-picture grayscale correlation is 0.99915. The Maria silhouette
and the logo both peak at zero translation in the sampled alignment.

Patch 0162 adds this plate to the existing exact source and RGB guard.
Each donor retains its own texture state. The compositor applies the
existing integer-scale guide and Saturn color-calculation weights
while leaving the menu and emblem as native pixels. Both the bundled
wide floral path and the stock native backdrop path use the same
protected rectangle.

## Bounded presentation proof

The 740-frame entrance replay starts before the intermission reveal.
The 450-frame exit replay starts in the Save, Status and Resume menu,
selects Resume and reaches the next scene. The 340-frame IC0501
regression exercises its existing menu and floral exit. All comparisons
are muted and strict-native. The A/B guest hashes and SRAM match within
each route with zero interpreted blocks.

The 2560×1440 oracle reconstructs the donor placement and 1/32 native
blend weights against each bundled-wide capture. It checks all
2,064,384 screen pixels outside the rectangle inside the native
viewport at every substituted sample. Entry weights include 9, 14, 19,
24, 29 and 32 out of 32. Exit weights include the opaque plate and
decreasing weights toward the native scene. Both paths preserve the
menu/emblem pixels and pixels outside the viewport. The missing and
same-length corrupt donor controls keep the same native RGB as the
reference. Original and IC0501 match their controls.

The certificate covers this disc-1 appearance. The full chapter,
other appearances and release packaging remain open. Private
replays and comparison scripts are under
`local/work/codex-th1/ic03-live/`.
