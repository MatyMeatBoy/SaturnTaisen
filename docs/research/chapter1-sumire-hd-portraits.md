# Second batch of chapter 1 HD portraits

Three Sumire expressions were reviewed. Mouth and eye differences distinguish the two close poses `0040` and `0041`. `0045` shows the open mouth. Comparing the base's outfit allowed ruling out PC alternatives 90, 91 and 95, which share the strips and wear a different variant.

| Saturn ID | PC candidate | Base RMSE | First strip | Second strip | Observed in-game |
| --- | ---: | ---: | ---: | ---: | --- |
| `0040` | 63 | 0.058700 | 0.057460 | 0.056257 | First strip at Y=16 |
| `0041` | 64 | 0.058665 | 0.057952 | 0.056752 | First strip at Y=16 |
| `0045` | 68 | 0.059924 | 0.059211 | 0.056777 | Base |

The analysis compared the 40×80 Saturn grid against an area reduction of the 80×160 PC atlas. In all three regions of each portrait, the error was lower with `dx=0` and `dy=0` than when shifting by one native pixel. The Saturn mask was preserved exactly with 3,200 opaque pixels at 1× and 12,800 at 2×, with no gaps. The second strip and both strips together are still pending in-game observation. `0095` still has two close candidates with no conclusive evidence to pick one. `0169` still has composition and strip differences that require further review.

## Reproduction

The [review registry](../../config/hd-portrait-reviewed.json) pins the KAO file, the three Saturn atlases, the PC pixels, and each prepared variant via hashes. The same command applies these three reviews and the two for Sakura to the owner's original project and exports to a new folder.

```powershell
python tools/apply_reviewed_hd_portraits.py --output-project local/work/chapter1-hd-196/project.json --export
```

The checkpoint audit counted 196/304 global identities and 86/123 in chapter 1, with 392 variants and zero errors. 108 remain pending in the catalog and 37 in chapter 1. The prepared private package preserves the 19 backgrounds byte for byte and has an SHA-256 receipt `7db33b3dbf185870f7077a695f27ba420927641e112573dbab963746184dfd02`. Delivered packages are kept.

## Execution test

Build v0.2.0-test.1 reproduced each state for 180 frames at 2560×1440 with the 193 and 196 packages. The comparison obtained 180 matching guest hashes and three identical native RGB captures per identity. The GUI difference at frame 8 was limited to the portrait rectangle `[404,644) × [996,1284)`. The runtime logged density 2 and zero interpreted blocks across the six runs. The states, captures and per-run hash reports remain in the owner's private space.
