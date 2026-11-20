# Sumire NC25 authored eyes in Chapter 1

Patch 0173 preserves the eyes already painted on the PC body for the witnessed fixed closed-eye pose. The previous renderer could place the wrong mouth image over the eyes or retain a low-resolution native eye patch. The exact recipe also places three witnessed PC mouth frames at their authored coordinates. Other expressions still use the existing matcher and native fallback.

## Asset and frame evidence

The Chapter 1 cold movie resumed from field 30,000. All 5,350 resumed guest hashes agree with fields 30,001–35,350 of the uninterrupted replay. The native VDP1 body is the 224 × 144 texture from `/SAKURA1/NC25.BIN` at `0x610`, FNV-1a `CA21D491CB7ED24F`. The file FNV-1a is `177C36A50C4CD313`. The matching PC `NC25.SPR` has FNV-1a `7D7DE6C915DE21C7` and a 440 × 320 body at ordinal 6.

The witnessed Saturn eye is a closed-eye smile at (104, 24) relative to the native body. The same expression is drawn on PC image 6. PC SPRED group 10 names eye ordinal 35, a 16 × 16 fully keyed cyan placeholder placed at (0, 0). The group links mouth ordinals 93–98. Tables 7 and 9 give the body origin (−88, 0) and mouth origin (152, 77), placing the PC mouths at (240, 77) relative to the body. The native body/face positions and the authored PC terms are specific to these assets.

| Native offset | Native FNV-1a | Dimensions | PC source |
| --- | --- | --- | --- |
| `0x8410` | `7D07BBDDE5F6F97D` | 48 × 24 | Eyes painted on body ordinal 6 |
| `0x8890` | `8D057D175FA95006` | 24 × 24 | Mouth ordinal 93 |
| `0x8AD0` | `88EDAECE4ECADBBB` | 24 × 24 | Mouth ordinal 94 |
| `0x9190` | `8AADA8C2504B9066` | 24 × 24 | Mouth ordinal 97 |

The baked-eye recipe requires the exact asset fingerprints, native texture fingerprint, dimensions and relative origin. The renderer still rejects the normal blend and intersecting-sprite cases before drawing the HD body. Direct checks reject neighboring origins one pixel up, down, left or right, altered dimensions, another texture fingerprint and a separate body's empty default recipe.

## Replay results

The 480-field strict muted A/B begins at field 34,860 of the known English disc 1 input route. All eight executions had zero interpreted blocks. Each before/after pair matched every guest hash and all final backup RAM bytes. Original mode, absent PC assets and a one-byte table-12 donor alteration produced 57 full RGB matches at 2560 × 1440. Both exact-asset runs logged the native blend fallback, and nine before/after full frames around the fade and outside the eligible pose matched exactly.

Ten Enhanced frames changed within (1168, 197)–(1504, 415) with no cyan or green key pixels introduced. Flat opaque 2 × 2 neighborhoods from the independently decoded PC body match 10,683 exact RGB pixels in the closed eyes at field 101. Of those, 9,508 were different before the patch. The three witnessed mouth images match 11,527–15,275 exact RGB pixels in their corresponding screenshots. The comparison also checks interpolated opaque edges and retains the native blend output.

All trials were repeated with the merged patch 0172 as the baseline. A separate 240-field NC11 timed-choice A/B retained the same guest history, final backup RAM and three full-frame RGB comparisons.

The verification covers the witnessed Chapter 1 disc 1 pose. Other mouth frames, disc 2 gameplay and package inclusion remain open. Local evidence is under `local/work/codex-th1/nc25-live/`.
