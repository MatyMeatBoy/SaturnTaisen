# Iris NC55 face registration in Chapter 1

Patch 0168 registers five native face textures from the English disc 1 Chapter 1 Iris-room replay. The existing PC body remains the source of her torso and hair. The registered PC eye and mouth parts fill the observed face poses at the PC sprite's authored coordinates. Other poses keep the existing matcher and its native overlay fallback.

## Asset and placement evidence

The VDP1 body pixels in this scene are the 192 × 144 strip at offset `0x610` in `/SAKURA1/NC55.BIN`, FNV-1a `48DFEEC578259DBC`. The whole native asset has FNV-1a `71438806B6CC7698` and is byte-identical in the prepared English and Spanish editions of both discs. The PC donor is `SAKURA1/NC/NC55.SPR`, FNV-1a `57B26C77E879C89F`, with a 368 × 320 body at image ordinal 5. These are the exact identities required by the registration table.

Native offsets came from the live VDP1 eye and mouth commands. The two observed eye banks each contain three 56 × 32 textures and six 24 × 24 mouth textures. The shape and order of the three eyes identify PC groups 7 and 5. Table 6 of the PC asset pairs those groups with mouth starts 83 and 71, respectively. Tables 8 and 9 identify the image ordinal and place it at its authored coordinates. Subtracting the PC body origin (−56, 0) from the face coordinates gives the placement relative to the body. An independent RGB search of each part's unchanged outer pixels ranked the same placement first.

| Native offset | Texture FNV-1a | Dimensions | PC ordinal | PC body position | Witness |
| --- | --- | --- | --- | --- | --- |
| `0x15AD0` | `2B49113EC88410D6` | 56 × 32 | 26 | (144, 89) | First expression, eyes open |
| `0x161D0` | `58D1DFF3A3A37078` | 56 × 32 | 27 | (144, 89) | First expression, partial blink |
| `0x16FD0` | `2BDE5287C1DFE7DC` | 24 × 24 | 83 | (176, 137) | First expression, closed mouth |
| `0x115D0` | `24EF353C40FD9286` | 56 × 32 | 20 | (144, 97) | Second expression, eyes open |
| `0x12AD0` | `83B38D30B6C5BB4E` | 24 × 24 | 71 | (176, 137) | Second expression, closed mouth |

## Replay results

The strict muted A/B used the `iris-correct-room-3000` state and advanced the dialogue with recorded input. The 600-field guest hash history and final backup RAM matched across all eight Iris variants, with zero interpreted blocks. The five registered PC ordinals were selected only with the exact assets in Enhanced mode. Twelve pairs of 2560 × 1440 screenshots changed 28,312–28,447 RGB pixels, confined to the face rectangle (1195, 472)–(1397, 645). The independent SPRED decoder compared flat opaque 2 × 2 donor neighborhoods at the registered placement. In frames 20 and 300 it found 13,021 and 14,521 exact RGB matches for the two mouth parts, including 12,287 and 13,223 matches gained over the previous renderer.

Original mode and both donor controls produced identical full-frame RGB in all 36 paired samples. The missing donor was absent. The altered donor changed one byte of table 12, outside the bitmap decoder, to exercise the file-identity guard while preserving the previous matcher path. The separate Chapter 1 `prebattle-3000` control reproduced NC11's timed-choice occlusion (240 fields, three full RGB comparisons). The `post-3000` control reproduced NC20 stepping aside during a blend (2,500 fields, 34 full RGB comparisons). Both controls preserved every guest hash and final backup byte, and every paired RGB sample matched.

The exact-image evidence covers these two Iris-room expressions on the English first disc. Other Iris poses, live playback on disc 2, and package inclusion remain unverified. Local inputs, logs and comparisons are under `local/work/codex-th1/nc55-live/`.
