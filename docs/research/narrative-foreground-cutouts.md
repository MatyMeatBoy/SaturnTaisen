# Registered narrative foreground cut-outs

The Chapter 5 English disc-1 prologue reads BG3132 at FAD 153744 and BG3133 at FAD 153767. Both are exact 288 × 144 fixed-cell backgrounds on NBG2, source 4, above BG2132 and BG2133 on source 2. The archive and isolated layers account for all native viewport pixels. At the two checkpoints, all 18,112 and 16,593 non-key foreground pixels match final native RGB.

Patch 0210 adds BG3132.SPR and BG3133.SPR, preserving the existing Zoom framing. The runtime verifies the source palette, cells and file, then registers official PC art to a 2× grid. Sampled native/PC silhouettes have intersection over union of 0.931 and 0.954. The draw requires current foreground ownership and agreement with the exact Saturn RGB at each pixel. The backing scene, one native pixel at the cyan edge, PC key and cropped areas, other overlays and color-calculated pixels retain their prior rendering.

| Foreground | Strict archived fields per variant | Draws | Active 1440p samples | Changed pixels per active sample |
| --- | ---: | ---: | ---: | ---: |
| BG3132 | 16 | 15 | 5 | 799,817 |
| BG3133 | 320 | 197 | 5 | 738,460 |

Six Direct3D 11 profiles per scene matched the archived guest histories and final SRAM with zero interpreted blocks. The shorter BG3132 replay starts at the stable field-4799 checkpoint. The BG3133 relay includes the preceding scene and verified four unchanged pre-draw samples. Both Enhanced comparisons held the backing donor fixed. Missing, one-byte-corrupt and Original comparisons were pixel-identical to their baselines. Every changed RGB in the active 2560 × 1440 samples matched the independently decoded PC donor exactly and lay within the verified native foreground. The final combined stack also reproduced 56 strict disc-2 Load fields on the line-reuse path and 110 MAP12 fields with a non-ASCII PC asset path, with matching final SRAM and four exact 1440p captures each.

The Chapter 3 BG3123 silhouette fits its counterpart at 0.945, but only 10 of its 7,447 opaque source pixels agree with final RGB at the witnessed frame because color calculation is active. It remains native pending exact mix transport. BG4055 needs a separate registration study. The whole-plate fit scores 0.760 and misaligns individual characters. The two Chapter 5 donor files are distinct and only their English disc-1 occurrences were verified. Public package inclusion is pending. Private replays, captures and build commands stay under local/work/codex-tp3c/fg313x.
