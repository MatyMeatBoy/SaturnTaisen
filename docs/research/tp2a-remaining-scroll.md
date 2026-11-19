# TP2a: constrained scroll fits and scenario references

These results measure the restricted whole-picture and full-height formulas in this report. The [broader affine-fit review](scroll-table.md) separately found viable fits for BG2172, BG1310 and BG2518, and a bounded overlap for BG2290 that still needs edge handling. Preserve those candidates when evaluating an SDK extension.

Method: for each Saturn BIN on the prepared discs (identical bytes on both discs for all twelve) every native 288x144 window (all positions, stride 1 or 8) is compared with the proportional PC crop of subimage 0, using the 32x16 grey signature of `tools/match_hd_all.py` and the 0.90 floor of `tools/gen_scroll_pictures.py`. Besides the table rule (PC 2x on the scroll axis, 288 of 320 rows centred) the whole-picture rule was tried, where the PC picture is the Saturn picture stretched as a whole, so the crop is `(round(at*pcw/w), 0, round(288*pcw/w), pch)` resized to 288x144. Only numbers are recorded here.

| Picture | Native / PC | Best rule | min / mean correlation (windows) | Result |
|---|---|---|---|---|
| BG2077 | 440x144 / 1024x320 | whole picture, x scale 1024/440 | 0.976 / 0.982 (153) | candidate, needs a new row style |
| BG1283 | 472x144 / 944x320 | x 2.0, full 320 rows (table rule with 288 rows: 0.877) | 0.923 / 0.941 (185) | candidate, needs a new row style |
| BG2093 | 320x144 / 592x320 | whole picture, x scale 592/320 | 0.913 / 0.920 (33) | candidate; same PC size as the BG2238 still (patch0123) |
| BG1257 | 456x144 / 1181x320 | whole picture, x 2.59 | 0.859 / 0.870 | rejected: PC composition differs |
| BG2172 | 288x280 / 576x592 | y 2.0, offset 6 | 0.878 / 0.919 | below the floor for this formula |
| BG1310 | 512x144 / 1024x320 | x 2.0, full rows | 0.818 / 0.854 | below the floor for this formula |
| BG2290 | 432x144 / 864x320 | x 2.0, full rows | 0.754 / 0.778 | below the floor for this formula |
| BG1280 | 512x144 / 1241x320 | none | 0.56 | rejected: different composition |
| BG2518 | 288x296 / 576x592 | y 2.0 | 0.459 | below the floor for this formula |
| BG2247 | 288x296 / 576x592 | y 2.0 | 0.200 | below the floor for this formula |
| BG2338 | 320x160 / no same-number PC file | n/a | n/a | not variant B; see cross-number PC pairing in [Saturn picture formats](saturn-bg-format.md) |
| BG2238 | 320x144 / 592x320 | still viewport | n/a | already has its own path (patch0123) |

The three candidates are not added to `config/hd-scroll-pictures.json` or to the C++ table: the table row only encodes the 2x rule with a centred 288-row crop. BG2077, BG1283 and BG2093 need a second row style (whole-height or whole-picture crop with a fractional scale) in the SDK, a native witness of the window and the per-frame hash comparison. None of that was built here.

## Where the scripts request them (disc scenario BINs, opcode 0x33 0x80 0x00 + number)

BG2077: 0701, 0804. BG2093 and BG2238: 0900 (BG2238 also 0902). BG1280: 0901. BG2518: 0904. BG1310: 1003. BG1257: 0403. BG2172: 0309. BG2290: 0301. BG2247 appears in many scripts (0100, 0102, 0108, 0204, 0307, 0403, 0802, 0805, 1004); BG1283 and BG2338 were not found with this opcode. The early-chapter state files were listed by name. This pass did not load states or verify a native window.
