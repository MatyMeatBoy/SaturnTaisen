# EVT overlay registry (T32)

The 674,182-block AOT base only covered `EVT01`, `EVT02` and `EVT06`: measured against both discs, the other 25 event overlays had only 60–220 shared positions (library code) versus ~30,000 in the three covered ones. They were the untranslated part of the campaign.

## Entry sweep (strict AOT, 12,000 frames, 674,182 executable)

| Entry | Result |
| --- | --- |
| Chapter 3 battle 1; chapters 4, 5, 6, 7; 8 ×2; 9 ×2; 10 battle 1; public 7, 9 and Finale | 12,000 frames, no missing block |
| Chapter 3 battle 2 | missing block at `00204000` (frame 6,680): `EVT04` |
| Chapter 3 battle 3 | same (6,679): `EVT05` |
| Chapter 10 battle 2 and final battle | same (6,685), disc 2: `EVT19` |

Attribution by full byte match between Low WRAM at `00204000` and the disc file (`EVT04` 77,224 B, `EVT05` 76,672 B, `EVT19` 76,596 B). With `EVT01/02/04/05/06/19`, that's six observed with the same base.

## Change

`tools/discover_registered_overlays.py` registers the 27 distinct EVTs from both discs (`EVT01` is identical on both). The three newly observed ones carry their evidence; the other 19 are listed as inferred by family. The SDK compares the block's code against memory before executing it: a wrong inference can't execute the wrong code. Local result: 674,182 → 1,357,536 candidate blocks (disc 1 +305,508, disc 2 +377,846).

Status: static, not executed. Still need to compile, repeat the sweep and walk every chapter to observe the 19 inferred ones. The full base lives under `local/`; it is not versioned.
