# Scene spot check (1 in every 10)

Owner request (2026-11-19): shards connect pictures without checking each one, so the integration desk samples them. The list is every 10th distinct PC picture of the %d marked `hd` in `config/hd-chapter-coverage.json`, in sorted order (%d pictures). Verify each by drawing it in game (the picture over the Saturn scene, framing, no wrong picture) and report in a PR: OK, wrong picture (give the right one), or not reachable. Pictures already `verified_in_game` need no new work. Regenerate the list when the register changes a lot; the sample is meant to estimate the error rate, so a wrong match found here means checking its neighbours (same palette family, same shard worker).

| # | PC picture | Saturn picture (first seen) | Already seen in game |
|---|---|---|---|
| 1 | SAKURA1/BG/BG1001.SPR | 2:/SAKURA1/BG1001.BIN | no |
| 2 | SAKURA1/BG/BG1011.SPR | 2:/SAKURA1/BG1011.BIN | no |
| 3 | SAKURA1/BG/BG1021.SPR | 2:/SAKURA1/BG1021.BIN | no |
| 4 | SAKURA1/BG/BG1031.SPR | 1:/SAKURA1/BG1031.BIN | no |
| 5 | SAKURA1/BG/BG1041.SPR | 1:/SAKURA1/BG1041.BIN | no |
| 6 | SAKURA1/BG/BG1051.SPR | 1:/SAKURA1/BG1051.BIN | no |
| 7 | SAKURA1/BG/BG1061.SPR | 1:/SAKURA1/BG1061.BIN | no |
| 8 | SAKURA1/BG/BG1071.SPR | 1:/SAKURA1/BG1071.BIN | no |
| 9 | SAKURA1/BG/BG1081.SPR | 1:/SAKURA1/BG1081.BIN | no |
| 10 | SAKURA1/BG/BG1091.SPR | 1:/SAKURA1/BG1091.BIN | no |
| 11 | SAKURA1/BG/BG1101.SPR | 1:/SAKURA1/BG1101.BIN | no |
| 12 | SAKURA1/BG/BG1111.SPR | 1:/SAKURA1/BG1111.BIN | no |
| 13 | SAKURA1/BG/BG1123.SPR | 1:/SAKURA1/BG1123.BIN | no |
| 14 | SAKURA1/BG/BG1148.SPR | 1:/SAKURA1/BG1148.BIN | no |
| 15 | SAKURA1/BG/BG1167.SPR | 1:/SAKURA1/BG1167.BIN | no |
| 16 | SAKURA1/BG/BG1177.SPR | 1:/SAKURA1/BG1177.BIN | no |
| 17 | SAKURA1/BG/BG1194.SPR | 1:/SAKURA1/BG1194.BIN | no |
| 18 | SAKURA1/BG/BG1209.SPR | 2:/SAKURA1/BG1209.BIN | no |
| 19 | SAKURA1/BG/BG1225.SPR | 1:/SAKURA1/BG1225.BIN | no |
| 20 | SAKURA1/BG/BG1235.SPR | 1:/SAKURA1/BG1235.BIN | no |
| 21 | SAKURA1/BG/BG1245.SPR | 1:/SAKURA1/BG1245.BIN | no |
| 22 | SAKURA1/BG/BG1266.SPR | 1:/SAKURA1/BG1266.BIN | no |
| 23 | SAKURA1/BG/BG1291.SPR | 1:/SAKURA1/BG1291.BIN | no |
| 24 | SAKURA1/BG/BG1301.SPR | 1:/SAKURA1/BG1301.BIN | no |
| 25 | SAKURA1/BG/BG1315.SPR | 1:/SAKURA1/BG1315.BIN | no |
| 26 | SAKURA1/BG/BG1326.SPR | 1:/SAKURA1/BG1326.BIN | no |
| 27 | SAKURA1/BG/BG1342.SPR | 1:/SAKURA1/BG1342.BIN | no |
| 28 | SAKURA1/BG/BG1353.SPR | 1:/SAKURA1/BG1353.BIN | no |
| 29 | SAKURA1/BG/BG2015.SPR | 1:/SAKURA1/BG2015.BIN | no |
| 30 | SAKURA1/BG/BG2028.SPR | 1:/SAKURA1/BG2028.BIN | no |
| 31 | SAKURA1/BG/BG2041.SPR | 1:/SAKURA1/BG2041.BIN | no |
| 32 | SAKURA1/BG/BG2053.SPR | 1:/SAKURA1/BG2053.BIN | no |
| 33 | SAKURA1/BG/BG2064.SPR | 1:/SAKURA1/BG2064.BIN | no |
| 34 | SAKURA1/BG/BG2075.SPR | 1:/SAKURA1/BG2075.BIN | no |
| 35 | SAKURA1/BG/BG2086.SPR | 1:/SAKURA1/BG2086.BIN | no |
| 36 | SAKURA1/BG/BG2099.SPR | 1:/SAKURA1/BG2099.BIN | no |
| 37 | SAKURA1/BG/BG2120.SPR | 1:/SAKURA1/BG2120.BIN | no |
| 38 | SAKURA1/BG/BG2133.SPR | 1:/SAKURA1/BG2133.BIN | no |
| 39 | SAKURA1/BG/BG2145.SPR | 1:/SAKURA1/BG2145.BIN | no |
| 40 | SAKURA1/BG/BG2156.SPR | 1:/SAKURA1/BG2156.BIN | no |
| 41 | SAKURA1/BG/BG2166.SPR | 1:/SAKURA1/BG2166.BIN | no |
| 42 | SAKURA1/BG/BG2200.SPR | 1:/SAKURA1/BG2200.BIN | no |
| 43 | SAKURA1/BG/BG2212.SPR | 1:/SAKURA1/BG2212.BIN | no |
| 44 | SAKURA1/BG/BG2222.SPR | 1:/SAKURA1/BG2222.BIN | no |
| 45 | SAKURA1/BG/BG2235.SPR | 1:/SAKURA1/BG2235.BIN | no |
| 46 | SAKURA1/BG/BG2250.SPR | 2:/SAKURA1/BG2250.BIN | no |
| 47 | SAKURA1/BG/BG2272.SPR | 1:/SAKURA1/BG2272.BIN | no |
| 48 | SAKURA1/BG/BG2283.SPR | 1:/SAKURA1/BG2283.BIN | no |
| 49 | SAKURA1/BG/BG2294.SPR | 1:/SAKURA1/BG2294.BIN | no |
| 50 | SAKURA1/BG/BG2520.SPR | 1:/SAKURA1/BG2520.BIN | no |
| 51 | SAKURA1/BG/BG2530.SPR | 1:/SAKURA1/BG2530.BIN | no |
| 52 | SAKURA2/BG/BBG107.SPR | 2:/SAKURA2/BBG107.BIN | no |
| 53 | SAKURA2/BG/BBG211.SPR | 2:/SAKURA2/BBG211.BIN | no |
| 54 | SAKURA2/BG/BBG249.SPR | 2:/SAKURA2/BBG249.BIN | no |
