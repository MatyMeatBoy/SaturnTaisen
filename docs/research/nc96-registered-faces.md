# NC96 face placement in Chapter 1

Patch 0179 uses the eye and mouth positions authored in the PC character asset. The previous placement search put the eye strips 17 PC pixels below the authored origin. The moved strips duplicated parts of the bangs and obscured the pupils with a rectangular skin patch. The old mouth origin was seven PC pixels too low, leaving a second nose and chin edge. The authored positions join the eyes and mouth to the existing HD body.

## Asset identity and correspondence

The Saturn body is a 144 × 144 VDP1 bitmap at offset `0x610` of `/SAKURA1/NC96.BIN`, texture FNV-1a `3054475EEEA3AADB`. The whole Saturn asset has FNV-1a `0B3929452D595C6D`. The PC donor `SAKURA1/NC/NC96.SPR` has FNV-1a `65D5B1D476AB6D80` and a 272 × 320 body at ordinal 0.

The first three 56 × 24 eyes start at `0x5710`. Six 16 × 16 mouths follow from `0x66D0` to the end of the file at `0x6CD0`. Their shapes and order match the three eye and six mouth ordinals in the PC asset. Table 7 places the body at (8, 0). Tables 8 and 9 place the eyes at (40, 25) and the mouths at (120, 105), yielding the positions below relative to the body.

| Saturn offset | Texture FNV-1a | PC ordinal | PC body position |
| --- | --- | --- | --- |
| `0x5710` | `6436E9A5EFA4F819` | 1 | (32, 25) |
| `0x5C50` | `B4D3AB09FFBE32CE` | 2 | (32, 25) |
| `0x6190` | `E812BFFF5E1E39AA` | 3 | (32, 25) |
| `0x66D0` | `6304A98F9EAC61B6` | 4 | (112, 105) |
| `0x67D0` | `0883CB37C8589682` | 5 | (112, 105) |
| `0x68D0` | `695A53E3B21B4217` | 6 | (112, 105) |
| `0x69D0` | `251212E9E24DC22F` | 7 | (112, 105) |
| `0x6AD0` | `E0669AE9ECD23F0C` | 8 | (112, 105) |
| `0x6BD0` | `774478D4F636261C` | 9 | (112, 105) |

## Replay results

The strict 31,016-field continuation from `after-options-3000.state` matches all uninterrupted game hashes from global fields 74,995–106,010. The focused scene replay resumes from global field 105,540 and completes 470 fields with the recorded inputs. Paired guest histories and final backup RAM match in all four configurations, with zero interpreted blocks. The runtime traces all nine registered parts in the exact-asset Enhanced run.

The sampled Enhanced changes stay within (1055, 175)–(1504, 604) at 2560 × 1440, right and bottom exclusive. Each build logs the native NC96 blend guard, and all 17 samples before the HD face becomes visible match in full RGB. Original, absent-donor and altered-donor runs match all 36 paired screenshots exactly. The altered donor flips an unused table 12 byte to test the exact registration identity while preserving decoded artwork.

Independent comparisons against the decoded PC images found 34,994 and 31,660 exact flat opaque RGB matches for two visibly sampled eye poses. The closed and open mouths had 36,212 and 34,363 exact matches, including more than 13,000 per mouth that differed from the previous placement. The surrounding picture, dialogue, torso and Zoom geometry remain pixel-identical.

The exact live proof is for the English first disc route on the stack through 0178. Later appearances and package inclusion remain open. Local state, hashes and captures are under `local/work/codex-th1/nc96-live/`.
