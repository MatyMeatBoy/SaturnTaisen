# Sakura NC12 face registration in Chapter 1

Patch 0184 registers the four eye poses and six mouth poses used during Sakura's Chapter 1 theater sortie introduction. Enhanced draws those parts at their authored PC positions. The existing matcher and native fallback handle other NC12 expressions.

## Asset and placement evidence

The full cold Chapter 1 route recognizes NC12 between fields 248,400 and 248,460. A compact replay from the Yoneda introduction checkpoint advances to Sakura, then lets the voice finish. The baseline keeps native eye overlays and can select the wrong mouth for the neutral pose. Both issues are visible after the fade.

The native 184 × 144 body starts at offset 1,552 in /SAKURA1/NC12.BIN and has FNV-1a CA9E33074DCFC2B0. The full asset has FNV-1a 4758979916DC8F3C in the prepared English and Spanish editions of both discs. The PC donor SAKURA1/NC/NC12.SPR has FNV-1a 088DA609868B0E6D and a 346 × 320 body at ordinal 2.

The native eye and mouth runs follow the NC10 park expression bank, at offsets 34,960 and 40,336. NC12's group 1 in SPRED table 6 has four eyes starting at ordinal 11 and six mouths starting at ordinal 47. Their native strips match the corresponding banks in NC10 and NC11, and the three PC donors have identical decoded face images at those ordinals. Table 7 places NC12's body at (−10, 0). Tables 8 and 9 place the eyes at (60, 66) and the mouths at (92, 116). The resulting body-relative positions are (70, 66) and (102, 116).

| Native offset | Texture FNV-1a | Dimensions | PC ordinal |
| --- | --- | --- | --- |
| 34,960 | DFD3D991DBBF0B17 | 56 × 24 | 11 |
| 36,304 | 84804DFD08203750 | 56 × 24 | 12 |
| 37,648 | 438C12D07F5B9D48 | 56 × 24 | 13 |
| 38,992 | D0376F38B4CCBF77 | 56 × 24 | 14 |
| 40,336 | BED90A33F0A5F2AA | 16 × 16 | 47 |
| 40,592 | 705CC47CE9FCCEB6 | 16 × 16 | 48 |
| 40,848 | 580157F8642147F0 | 16 × 16 | 49 |
| 41,104 | D8373D7C4BFA8E9B | 16 × 16 | 50 |
| 41,360 | 764F284DD45DD3BD | 16 × 16 | 51 |
| 41,616 | E7900E701C6CFEE5 | 16 × 16 | 52 |

## Replay results

The exact 0183 and 0184 builds match all 900 guest hashes, decoded PCM and final backup RAM in each of the Enhanced, Original, missing-donor and altered-donor pairs. All runs report zero interpreted blocks. The altered donor changes one byte in SPRED table 12 outside the image decoder. All 18 sampled Original and donor-control images are RGB-identical at 2560 × 1440.

The Enhanced runs exercise all ten parts. Eighteen changed 1440p samples differ only within (1102, 253) to (1567, 541). Nine earlier samples, including frames 90–122 across the transition, match exactly. The independent PC decode confirms every eye and mouth pose at its authored position. Mean absolute RGB error on the eye samples falls to 1.69–2.20 from 21.18–26.36, and on the mouth samples to 0.59–1.45 from 5.00–23.51.

Live evidence covers the English disc 1 scene. Spanish and disc 2 live playback, other NC12 expressions and package inclusion remain open. Private evidence and build files are in local/work/codex-nc12-expression. Cleanup removed 391,676,752 bytes of intermediate checkpoints. The project measured 116,228,703,786 logical bytes including existing private assets and packages. The immutable development ZIP measured 6,315,009,692 bytes.
