# Chapter 2 — orders and first battle rounds

A proprietary episode 2 save, loaded via Continue from disc 1, reaches battle and allows executing orders, going through the first enemy phase, and returning to the allied turn. The strict candidate ran every segment with no interpreted blocks. The chapter is still in progress.

| Observed milestone | Private evidence in `local/work/t30-chapter2-followup` |
|---|---|
| Continue shows the episode 2 introduction | `cold-native/frame-009501.png` |
| Maria confirms a move and ends up in a new position | `first-move/frame-000600.png` |
| Sakura performs Defend and the shield is visible | `sakura-defense/frame-000120.png` |
| The allied phase completes and the enemies move and fire | `fifth-end-order/frame-000180.png`, `fifth-end-order/frame-000540.png`, `enemy-turn/frame-000600.png` |
| Maria gets her turn back, selects Musket #7, and confirms an attack | `enemy-turn/frame-001800.png`, `maria-second-aim/frame-000180.png`, `maria-confirm-hit/frame-000180.png` |
| The attack deals 68 damage and the health bar drops | `maria-confirm-hit/frame-000180.png`; SHA-256 `85c4846c77bdcb14082a58471b78c18e7adb1cf22e07b1c2f12d573ec2a889ef` |
| Maria fires again after the second enemy phase. Musket #7 loses its remaining health, explodes, and disappears from the field | `maria-elimination/frame-000420.png`, `frame-000540.png` and `frame-000780.png` |
| A tactical LIPS opens with three options. The second is selected, its answer appears, and Kohran receives orders again | `round-two-kohran-ranged/frame-000060.png` and `frame-000300.png`, `kohran-turn-ready/frame-000300.png` |

The private segment `first-defense` keeps its original name. The order observed in that segment is Info → Advice. Effective defense was tested in `sakura-defense`. Maria's first attack grid only proves order selection; the hit was observed after the enemy phase.

## Per-segment comparison

Isolated 674,182-block binary, patch 0050, SHA-256 `df68e9dbe2c7d9efe273e0e716c504774ba5c5f5f0826abc783a2e3d6bffcbd3`. Strict AOT was compared against the interpreter of the same SDK, in Original presentation and with the same initial states, SRAM, and input movies. The comparisons cover guest hashes, RGB samples, and final SRAM bytes.

| Segment | Frames compared | RGB pairs |
|---|---:|---:|
| Continue from cold boot | 9,501 | 1 |
| Battle introduction | 3,600 | 6 |
| Cancel, cursor, and first move | 960 | 16 |
| Advice, grids, handoff, and Defend | 3,300 | 55 |
| Dialogue, end orders, enemy phase, and Maria's attack | 8,580 | 143 |
| Second allied turn, tactical LIPS, and Kohran's grid | 2,580 | 43 |
| Second enemy phase and Musket #7's elimination | 4,620 | 77 |
| Per-segment total | 33,141 | 341 |

All pairs matched and the SRAM kept SHA-256 `4c22bf1edd1437b082ccd05e12df5bbf46bdcc5c9058fa3cc869db281f043908`. Reports are kept in `cold-result.json`, `intro/cold-result.json`, `orders-result.json`, `tactical-interactions-result.json`, `enemy-turn-result.json`, `second-allied-turn-result.json`, and `third-round-result.json`. Each handoff keeps its movie, final state, SRAM, and hashes.

The most advanced handoff in this comparison is `maria-elimination/finish.state` (SHA-256 `f1084a893b337712195d700b110855138e6f20b00104bd108742c7100302ca01`) with the SRAM from the same directory. Still pending: defeating all target units, the victory, and exiting the battle. This comparison evaluates the route in Original presentation and uses the interpreter of the same SDK as the reference.
