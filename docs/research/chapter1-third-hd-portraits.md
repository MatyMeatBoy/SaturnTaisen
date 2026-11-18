# Third batch of chapter 1 HD portraits

The review compared the base and both strips per identity and outfit. Sakura `001d` wears a scarf, Maria `0064` has a dark collar, and `006d/006e` share the light collar with different expressions. Iris `0096` keeps the eyes open, the round mouth, and the same outfit as her Saturn atlas.

| Saturn ID | PC candidate | Evidence |
| --- | ---: | --- |
| `001d` | 28 | Base and both strips verified on atlas |
| `0064` | 99 | Base and both strips verified on atlas. Base observed before the first battle |
| `006d` | 108 | Base and both strips verified on atlas |
| `006e` | 109 | Base and both strips verified on atlas |
| `0096` | 149 | Base and both strips verified on atlas |

All three regions of each atlas got their best alignment at zero offset versus one-native-pixel offsets. Strip agreement decreased when they were swapped. Both densities preserved the full Saturn mask, with 3,200 opaque pixels at 1× and 12,800 at 2×, with no gaps. Iris's color differences are kept as part of the PC art. `0093`, `0095`, `00a1`, `00c2` and `0169` are left out of this batch.

The [review registry](../../config/hd-portrait-reviewed.json) pins the KAO and the native atlas hashes, the PC pixels, and both prepared variants. Reproducing from the initial 191-portrait project applies the ten approved pairings and exports a new project. The reproduction obtained the same 404 candidate files, with an SHA-256 manifest `b3ee89d7bea42ed2d50df70389059c9f8d4c2adba5a94dedf8d0d4c718ea0a25`.

```powershell
python tools/apply_reviewed_hd_portraits.py --output-project local/work/chapter1-hd-201/project.json --export
```

The checkpoint reaches 201/304 global identities and 91/123 for chapter 1. The audit verified 402 variants, with zero errors, and leaves 103 pending in the catalog, 32 in chapter 1. The 19 backgrounds from the 196 checkpoint match byte for byte with the ones prepared alongside the 201 portraits. The private package receipt has SHA-256 `e1fb09fed81cfd4450ee2b3f4058178f48086a7fb2f5904b1da1e64b70b5be7b`.

Build v0.2.0-test.1 showed Maria's `0064` base at 2560×1440 and density 2. Comparing the 196 and 201 packages matched all 180 game hashes and three native RGB captures. The GUI difference at frame 8 stayed within the portrait rectangle `[404,644) × [996,1284)`. Both runs logged zero interpreted blocks. Maria's strips and the other four portraits await in-game verification.
