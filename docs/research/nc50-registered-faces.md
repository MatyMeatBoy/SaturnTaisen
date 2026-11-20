# Iris NC50 face registration in Chapter 1

Patch 0171 registers the expressions shown in the Chapter 1 lobby staircase replay. Iris uses the existing PC body. The patch fills two observed expressions with eleven PC eye and mouth images at their authored positions. Other poses still use the existing face matcher and native fallback.

## Asset and expression evidence

The live native body is the 144 × 144 texture at offset `0x610` of `/SAKURA1/NC50.BIN`, with texture FNV-1a `6DE2BCDA270A7D21`. The file FNV-1a is `2713B2FC1E22BEC7`, identical in the prepared English and Spanish editions of both discs. PC `SAKURA1/NC/NC50.SPR` has FNV-1a `E7290E1124DB4414`. Its only decoded body is 288 × 320 at ordinal 0.

The native VDP1 command stream shows the first three eye textures, that bank's closed mouth, and the later fixed-eye smile with all six mouth textures. Their visual shapes and order agree with the PC resource's groups 0 and 2. SPRED table 6 links each eye group with its mouth ordinals. Tables 8 and 9 give image offsets relative to the common coordinate system. Subtracting the body origin (8, 0) from table 7 places the images in the PC body.

| Native offset | Texture FNV-1a | Dimensions | PC ordinal | PC body position |
| --- | --- | --- | --- | --- |
| `0x7210` | `117D7BCA82BB3E1C` | 56 × 32 | 7 | (80, 89) |
| `0x7910` | `23DF161157704693` | 56 × 32 | 8 | (80, 89) |
| `0x8010` | `DCB0A14C0185DBD0` | 56 × 32 | 9 | (80, 89) |
| `0x8710` | `30D17E5BC01A64CE` | 24 × 24 | 41 | (112, 121) |
| `0xB710` | `A18C1AF869758A89` | 56 × 32 | 13 | (80, 81) |
| `0xBE10` | `355E93DC98BD7F0F` | 24 × 24 | 53 | (112, 121) |
| `0xC050` | `37E2AB5184DD6B14` | 24 × 24 | 54 | (112, 121) |
| `0xC290` | `2588C055C830901E` | 24 × 24 | 55 | (112, 121) |
| `0xC4D0` | `53049E36BD03F1DA` | 24 × 24 | 56 | (112, 121) |
| `0xC710` | `4A45AD2569B96862` | 24 × 24 | 57 | (112, 121) |
| `0xC950` | `3B1824A64529257C` | 24 × 24 | 58 | (112, 121) |

## Replay results

A 600-field muted replay started from the Chapter 1 disc 1 BG1021 checkpoint used in the [scene spot check](scene-spot-check.md#bg1021-on-disc-1). It ran strict on both executables, advancing the dialogue from field 260. All eight variants yielded equal guest histories and backup RAM with zero interpreted blocks. The exact donor in Enhanced mode selected all eleven ordinals. The 2560 × 1440 comparisons changed 29,665–106,992 pixels within the face bounds (1100, 309)–(1504, 645). The two early samples while native sprite coverage intersects Iris remained full-frame identical, and both builds logged the NC50 overlap guard.

Original mode, the absent donor and the altered donor each matched in 21 full RGB pairs. The altered donor changed a byte of table 12 and exercised the exact donor identity guard. For the newly registered case, an independent SPRED decoder checked eleven sampled eyes and mouths. For the seven mouths, 10,682–12,700 opaque flat donor samples per screenshot matched the output exactly, and at least 10,510 per mouth differed from the prior runtime. The four eye samples likewise match the artwork at the authored position, including a full closed-eye blink at field 202 with 24,274 exact RGB matches.

The tests were repeated on the exact SDK through patch 0170. The NC10 park and NC55 room routes preserved all previously registered ordinals, guest histories, backup RAM and eight full-size RGB pairs.

The live evidence covers this Chapter 1 disc 1 route. Gameplay on disc 2, other expressions and packaged delivery remain unverified. Local inputs, trace and RGB comparisons are under `local/work/codex-th1/nc50-live/`.
