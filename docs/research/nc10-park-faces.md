# Sakura NC10 face registration in Chapter 1

Patch 0169 registers the ten native face textures used by Sakura's park conversation in Chapter 1. These are the four eyes and six mouths of the first PC expression group. Enhanced uses the authored face placement on the existing HD body. Other expressions retain the existing matcher and native fallback.

## Asset and placement evidence

The native 176 × 144 body starts at offset `0x610` in `/SAKURA1/NC10.BIN`. The registered table requires whole-file FNV-1a `FAF25875698D3053` and PC donor `SAKURA1/NC/NC10.SPR` FNV-1a `CBD86983994FF9C4`. Both language replays reached all applicable asset guards. The native VDP1 eye and mouth rectangles are at (40, 32) and (56, 56) relative to the body.

The native strips form consecutive 56 × 24 eyes and 16 × 16 mouths starting at offsets 28,048 and 33,424. Table 6 of the PC SPRED specifies four eye ordinals starting at 7 and six mouth ordinals starting at 41 for group 0. Table 7 places body ordinal 0 at (8, 0). Tables 8 and 9 place the eyes at (60, 66) and mouths at (92, 116). Subtracting the body origin gives (52, 66) for all four eyes and (84, 116) for all six mouths. The pose sequence and registration also agree with visual comparison of the decoded Saturn and PC strips.

| Native offset | Texture FNV-1a | Dimensions | PC ordinal |
| --- | --- | --- | --- |
| 28,048 | `859F50A3C37AF996` | 56 × 24 | 7 |
| 29,392 | `98B07E572C492182` | 56 × 24 | 8 |
| 30,736 | `6BDEFA40CF2564B5` | 56 × 24 | 9 |
| 32,080 | `EC672C861FB23E59` | 56 × 24 | 10 |
| 33,424 | `EDD6D16FC4252F3D` | 16 × 16 | 41 |
| 33,680 | `F2AFC5C2FBFCA752` | 16 × 16 | 42 |
| 33,936 | `D6AD90A9E05C6DB4` | 16 × 16 | 43 |
| 34,192 | `85671025825DA21A` | 16 × 16 | 44 |
| 34,448 | `2EEF2A091F954C84` | 16 × 16 | 45 |
| 34,704 | `2C8E1A58BD112380` | 16 × 16 | 46 |

## Replay results

The exact 0168 and 0169 executables ran the English `yoneda-pre` and Spanish `voice-mid` replays with recorded inputs. The English replay logged all ten registered ordinals. The Spanish replay logged all four eyes and three mouths. Every 400-field pair had identical guest hashes, decoded PCM and final backup RAM, with zero interpreted blocks. Sixteen of 18 sampled 2560 × 1440 image pairs changed only inside the face bounds (1095, 253) to (1567, 535). The other two images matched before the registered face was visible.

In an independent comparison against decoded donor pixels, the registered eyes gained 1,671–2,100 exact RGB pixels within flat opaque neighborhoods in each changed sample. Mean absolute RGB error at the center of the mouth was 1.45–2.77 against the best matching donor part, compared with 19.34–36.42 in the corresponding baseline images. The crops also show the eyes and lips meeting the surrounding body cleanly.

Original mode and both donor controls matched all 12 sampled full-frame RGB pairs. The altered-donor control flips a byte in table 12 outside the image decoder and exercises the exact asset guard while keeping the legacy matcher active. The missing-donor control exercises the same route without PC assets.

Other NC10 expressions, live playback on disc 2 and package inclusion remain open. Replays, private art comparisons and the reference executables are under `local/work/codex-nc10-expression/`. Closing the trial removed 1,716,960,981 bytes of regenerable prototype executables and objects. The project measured 96,510,714,017 logical bytes including existing local assets and packages. The development ZIP remained 6,315,009,692 bytes.
