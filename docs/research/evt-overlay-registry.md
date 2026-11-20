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


## Bounded MAP12 opening and first enemy phase on disc 2

The natural English disc-2 Chapter 8 continuation from IC08 reads
38 sectors of EVT12 at FAD 203377, then 151 sectors of MAP12 at
FAD 219422. The initial sparse runtime stops at master SH-2 address
`00205FB0`. The first 71,692 live bytes at `00204000` match the
`/SAKURA2/EVT12.BIN` source in the retained MAP12 checkpoints.
The complete 75,984-byte module has SHA-256
`0d7a561da50c9a209157bf61b645b49b0ef37c70c5db409e8f8a1ea4cf02f11d`.

Five recorded interpreter segments match the archived guest hashes
and final SRAM. They yield 468 variants absent from the 674,638-block
reference. Every complete instruction span matches the pinned disc
module, including the opening strict miss. The canonical sorted
variant delta has SHA-256
`04bc31de45b19b6c846a0950bdf34a5bb5946895bbbbd5b71cfa6c7f20422ae6`.

| Recorded continuation | Matching strict guest fields |
| --- | ---: |
| IC08 exit to MAP12 briefing | 3,600 |
| Briefing through deployment | 2,520 |
| Opening navigation preview | 540 |
| Kohran's first-turn reposition | 4,200 |
| First enemy phase | 4,800 |
| Total | 15,660 |

The strict 0193 candidate with the delta matches all five sets of
guest hashes and final SRAM with zero interpreted blocks. Its SHA-256
is `c0acc9fb441dd1375acb5adb05896cf8166b3c54e142dced10c47c55c2b759a9`.
The narrow profile regenerates the exact variants from the pinned
disc and the public offset/length pairs.

The same candidate runs a strict 320-field Direct3D 11 donor/empty
pair at 2560×1440. Guest hashes and final SRAM match. The five captures
per variant match the corresponding portable outputs pixel for pixel.


```powershell
python tools/discover_registered_overlays.py --image "local/prepared/disc2/Track 01.iso" --module EVT12_MAP12 --seed-blocks local/work/map04-aot/blocks.txt --output local/work/map12-aot
```

These retained segments bound the proof. A fresh campaign route,
remaining turns and package inclusion stay open. Inputs, states and
binary evidence are private under `local/work/codex-th1/map-bulk-live/`.

## Chapter 8 rematch: EVT13 camera coverage

Two natural English disc 2 segments reach MAP13 after retreating through the shrine gate. The runtime reads EVT13 at FAD 203415 and MAP13 at FAD 219573. The first 71,692 bytes at `00204000` match the pinned 75,280-byte EVT13 module in both retained camera states.

The two interpreter recordings match all 4,380 reference guest fields and final SRAM. The observed range profile records 195 new spans whose complete bytes match EVT13. It excludes the 925 remaining spans from the multi-module entrance segment. The combined strict candidate verifies the 540-field camera segment against the interpreter with identical guest hashes and final SRAM and zero interpreted blocks. The complete MAP13 entrance remains open for strict replay, and this profile is not in the published package.

```powershell
python tools/discover_registered_overlays.py --image "local/prepared/disc2/Track 01.iso" --module EVT13_MAP13 --seed-blocks local/work/sakura/blocks.txt --output local/work/evt13-map13-aot
```

## Iris and Ogami combo during the MAP13 rematch

The English disc 2 replay loads `/SAKURA2/GATTAI.BIN` at FAD 212474. All 38,908 bytes match High WRAM at `060F0000` in six retained states around the combo. The strict miss at `060F0490` is inside that module. The interpreter trace contributes 472 new complete GATTAI spans and one six-byte return span at `00205BC8`, independently pinned to EVT13. The combined strict build reproduces all 1,800 guest fields and final SRAM with zero interpreted blocks.

This covers the witnessed Iris combo and return to the MAP13 battlefield. The full battle and other heroine combos remain open. No public package contains the new variants yet.

```powershell
python tools/discover_registered_overlays.py --image "local/prepared/disc2/Track 01.iso" --module EVT13_MAP13 --module GATTAI_SD2_IRIS --seed-blocks local/work/sakura/blocks.txt --output local/work/map13-combo-aot
```

## Chapter 8 MAP14 deployment and combat

Three retained MAP14 states contain 71,692 byte-identical leading bytes of the pinned EVT14 module at 00204000. A stock build reproduces a strict-native miss at 0020A4C4. The four reference segments recorded 426 unique new complete code spans, all matching the pinned 77,656-byte EVT14 and none from another module. The exact linked executable contains 676,795 variants. The new observed range profile rebuilds the linked row set byte-for-byte from the owner's disc and the previous 676,369-variant seed.

```powershell
python tools/discover_registered_overlays.py --image "local/prepared/disc2/Track 01.iso" --module EVT14_MAP14 --seed-blocks local/work/sakura/blocks.txt --output local/work/map14-aot
```

The sample covers 2,400 strict fields from deployment via File 1, 900 of motion, 1,200 of enemy camera and 300 of targeting, with zero interpreted blocks, exact portable guest hashes and matching SRAM. Further battles and alternate branches are outside this receipt.

### MAP14 enemy turns and attacks through turn five

The initial EVT14 profile stopped strict-native execution in five later
natural English disc 2 replays. The first misses were at 0020A38E,
00204968, 002049A0, 00204914 and 00204DDC. The portable recordings
matched the retained guest hashes and final SRAM.

| Segment | Strict-native fields after the update |
| --- | ---: |
| Enemy approach and turn | 4,500 |
| Iris attack and following movement | 1,800 |
| Kohran attack in turn two | 1,080 |
| Sakura attack in turn four | 1,500 |
| Kohran attack in turn five | 1,500 |

The five segments record 71 additional complete spans. Every byte
matches the pinned English disc 2 EVT14 module. The updated registry
reproduces all 497 observed EVT14 variants from the previous
676,369-variant seed. The linked executable (53c5576f017e9dada21499677f36d6435e845b0c6c3e337849d8257b14eea33c)
contains exactly the regenerated 676,866 address-and-byte variants.

All 10,380 strict fields and final SRAM matched the portable references
with zero interpreted blocks. The local replays and build recipe are in
`local/work/codex-th1/map14-late-aot`. This verifies the five listed
segments. The updated profile shipped in [v0.2.15-alpha](../releases/v0.2.15-alpha.md). The remainder of the battle is open.

### MAP14 turn-ten Boar attack and Cover

The natural English disc 2 replay from the Kanna targeting checkpoint
includes the enemy approach, Boar's fire attack and Iris covered by
Ogami. The previous strict runtime stopped at 00204708.

The expanded profile adds 511 complete variants whose bytes match the
pinned EVT14 module. All 3,600 strict guest fields and final SRAM match
the retained portable recording. The regenerated 1,008 EVT14 variants
and the 676,369-variant seed match the 677,377 linked variants exactly.
The executable SHA-256 is `0303ee0f7a29c66c18afeae24ef70848120ebe56cfa9aa0ae3a3de6b4325df36`.

The same executable reproduced the NC3285 and NC3286 controls from
patch 0224, including 110 strict fields, SRAM and ten 1440p captures.
The replay and private build evidence are under
`local/work/codex-th1/map14-boss-aot`. Later turns and package inclusion
are pending.
