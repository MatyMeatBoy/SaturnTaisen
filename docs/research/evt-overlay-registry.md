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

## Compiled runtime results

The 27 EVTs were compiled into the AOT base (1,357,536 blocks, rebuilt incrementally with `recomp.py --append-order`). Strict native mode (`SATRECOMP_STRICT_NATIVE=1`, exit code 4 on a missing block):

- The four entries that failed (chapter 3 battles 2 and 3, chapter 10 battle 2 and final battle) now pass 12,000 frames.
- Deep sweep, 40,000 frames with dialogue advance every 120 frames (`--advance`): 15 of 17 entries complete with exit 0, 0 interpreted and no missing block (chapter 3 battles 1-3, chapters 4-7, chapter 8 x2, chapter 9 x2, chapter 10 x3, public 7). `public-9` and `public-finale` were still running when this was written.
- Cold start: New Game to tutorial, 297,107 frames continuous, hashes identical to the earlier segments, 0 interpreted.

Not yet done: observing the 19 inferred EVTs in play, and the remaining campaign paths (T32/T56). The sweep tooling and results stay under `local/`; they are not versioned.
