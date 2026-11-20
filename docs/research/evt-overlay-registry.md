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
- Deep sweep, 40,000 frames with dialogue advance every 120 frames (`--advance`): all 17 entries complete with exit 0, 40,000 frames and no missing block (chapter 3 battles 1-3, chapters 4-7, chapter 8 x2, chapter 9 x2, chapter 10 x3, public 7, public 9, public Finale). Interpreted blocks were not read from the logs for this sweep; the earlier 12,000-frame runs reported 0.
- Cold start: New Game to tutorial, 297,107 frames continuous, hashes identical to the earlier segments, 0 interpreted.

Not yet done: observing the 19 inferred EVTs in play, and the remaining campaign paths (T32/T56). The sweep tooling and results stay under `local/`; they are not versioned.

## Bounded MAP04 replay on disc 1

The English disc 1 Chapter 3 second-battle checkpoint stopped in strict mode at `00206E72`. The interpreter recorded 94 previously absent variants during a 180-frame replay under ordinary camera input. All 94 complete opcode spans match the pinned 77,224-byte `/SAKURA2/EVT04.BIN` at file offsets relative to `00204000`. The registered SHA-256 is `93fb524dc7b64b1af5b576bd56fdf67d9624eea0cdf5006537ec339acb37ceaa`.

```powershell
python tools/discover_registered_overlays.py --image "local/prepared/disc1/Track 01.iso" --module EVT04_MAP04 --seed-blocks local/work/ending-aot/blocks.txt --output local/work/map04-aot
```

The example uses the 674,535-variant seed from the [ending AOT recipe](ending-bank-pairs.md#rebuild-the-observed-aot-coverage). The narrow profile checks the complete module before extracting the offset and byte-count pairs in `config/evt04-map04-aot-ranges.json`. The regular `EVT04` selection still performs eager analysis. Both selections can share a single ISO file read and output database.

The 94-variant sorted delta has SHA-256 `dde8a84b96b654777b5752187a3e9550e609d21326367d0f65c6ad501230f39e` in LF `ADDRESS UPPERCASE_HEX` form. Feeding that delta to the SDK generator emitted byte-identical sources to the private strict relink. All 180 guest hashes and SRAM matched the interpreter on the resulting 674,629-variant build, with zero interpreted blocks. This is camera-witness coverage for the retained checkpoint. Full battle coverage and package inclusion remain open. Opcode bytes, checkpoints, movies, and binaries stay local.

## Bounded MAP15 deployment and combat on disc 2

The Chapter 9 theater-defense route reads EVT15 during setup, then
EVT16 at FAD 203528. At the retained Sakura movement checkpoint, the
first 28,672 bytes of live code at `00204000` exactly match
`/SAKURA2/EVT16.BIN`. The 77,764-byte module SHA-256 is
`300a92c2cd5dd3ba8b6b57350684b47a1074142a8eb1a83d869bad0acf51ea7f`.

The first movement profile covered 68 EVT16 variants, including the old
strict miss at `00209E62`. The wider theater route adds the deployment
transition and six more recorded combat segments. A total of 591
variants are absent from the 674,629 base, with 144 complete spans in
EVT15 and 447 in EVT16. There are no unattributed variants. The combined
sorted delta SHA-256 is
`92f6185e4bb08df13843413cd48f4d72cfd165eac94ffc3831d0cb6d08474c23`.

The 675,220-variant strict build matches all 18,900 guest hashes and final
SRAM against the eight interpreter segments, with zero interpreted
blocks. Segments start from retained states and include the EVT15→EVT16
transition, deployment, movement, ordinary and special attacks, and
enemy phases through entry into turn four.

```powershell
python tools/discover_registered_overlays.py --image "local/prepared/disc2/Track 01.iso" --module EVT15_MAP15 --module EVT16_MAP15 --seed-blocks local/work/map04-aot/blocks.txt --output local/work/map15-aot
```

The profile covers the eight tested segments. Cold entry before the
retained deployment state and the rest of the battle remain open.

The [Windows v0.2.11-alpha release](https://github.com/MatyMeatBoy/SaturnTaisen/releases/tag/v0.2.11-alpha)
includes these 591 variants. Its combined 675,229-block build with patch
0193 matched all 18,900 reference guest fields and final SRAM again.
The distributed executable also passed a 120-field strict Spanish boot.
