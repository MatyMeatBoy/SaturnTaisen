# Witness routes (TW7)

Seeds, frames, scene names and state SHA-256 only; states live in `local/work/witness/` and are never committed. Produced with `tools/witness_sweep.py` (see its docstring): headless runtime copy `local/build/sakura-witness/sakura-witness.exe` (copy of the 2026-11-19 `sakura-ic-base.exe` build), strict native, `--auto SEED:0` from a state, a checkpoint state every N frames, and the CD block `Play Disc` commands mapped to ISO files (FAD = LBA + 150).

## Method and limits

1. Start states: `python tools/chapter_jump.py CASE --exe local/build/sakura-witness/sakura-witness.exe --frames 8000 --state-at 7999 --out local/work/witness/jump-CASE` for the 16 chapter-sweep seeds ([scene-jump](scene-jump.md)). 12 reached frame 8000 with zero untranslated blocks; `bank-3-battle-2`, `bank-3-battle-3`, `bank-10-battle-2` and `bank-10-final-battle` stop at frames 6679-6685 with `untranslated master 00204000` in this build (the same lock as the chapter-sweep episode 4 item), so they have no state.
2. Sweep: `python tools/witness_sweep.py --exe local/build/sakura-witness/sakura-witness.exe --disc D --state local/work/witness/jump-CASE/state-7999.bin --backup local/work/witness/jump-CASE/backup.bin --seeds 1 --frames 9000 --interval 500 --out local/work/witness/sweep-CASE` (`long-*` rows: seeds 2-5, 20000 frames, interval 1000, for public-7, public-9, public-finale).
3. A scene here is a **disc load**, not proof it was displayed: preloads can read a file before it is shown. The frame is estimated from the buffered hash log (early by up to a few dozen frames); the state is the first checkpoint at or after estimate + 60 frames. Confirm visually or with `scene picture:` traces (`tools/coverage_campaign.py --state STATE`) before using a state as a witness.
4. `--auto` random input never finished a battle: **no IC, ENDING, CG or EVE file was loaded in any of the 12 sweeps and 3 long sweeps** (12 x 9000 + 12 x 20000 frames). Only BG loads and, from `bank-4-battle`, BBG204/EVT06/MAP06 (the known chapter 4 lock).

## Reached scenes

| start | disc | run | scenes loaded (BG unless noted) |
|---|---|---|---|
| bank-10-battle-1 | 2 | sweep | BG1160, BG1292, BG1293, BG2020, BG2023, BG2244, BG2245, BG2246, BG3020, BG4055 |
| bank-4-battle | 1 | sweep | BBG204, EVT06, MAP06 |
| bank-5-battle | 1 | sweep | BG1031, BG1243, BG2058, BG2132, BG2133, BG2156, BG2533, BG3132, BG3133 |
| bank-6-battle | 1 | sweep | BG1003, BG1008, BG1021, BG1025, BG2156, BG4059 |
| bank-7-battle | 1 | sweep | BG1266, BG1267, BG1268, BG2014, BG2019, BG2126, BG2160 |
| bank-8-battle-1 | 2 | sweep | BG1050, BG2159, BG4187 |
| bank-8-battle-2 | 2 | sweep | BG1001 |
| bank-9-battle-1 | 2 | sweep | BG1076, BG2017, BG2018, BG2031, BG2091, BG2092, BG2093, BG2100, BG2156, BG2160, BG2236, BG2238, BG3091 |
| bank-9-battle-2 | 2 | sweep | BG1143, BG1160, BG1184, BG2021, BG2160, BG4055 |
| public-7 | 1 | sweep | BG1266, BG1267, BG1268, BG2014, BG2019, BG2126, BG2160 |
| public-9 | 2 | sweep | BG1076, BG2017, BG2018, BG2031, BG2091, BG2092, BG2093, BG2100, BG2156, BG2160, BG2236, BG2238, BG3091 |
| public-finale | 2 | sweep | BG2025, BG2026, BG2284, BG2285, BG2286, BG3026 |
| public-7 | 1 | long | BG1178, BG1181, BG1266, BG1267, BG1268, BG2014, BG2019, BG2080, BG2126, BG2160, BG4017 |
| public-9 | 2 | long | BG1060, BG1062, BG1076, BG1175, BG1176, BG1280, BG2017, BG2018, BG2031, BG2091, BG2092, BG2093, BG2097, BG2098, BG2100, BG2110, BG2156, BG2160, BG2236, BG2238, BG3091, BG3097 |
| public-finale | 2 | long | BG2025, BG2026, BG2046, BG2057, BG2162, BG2163, BG2164, BG2165, BG2166, BG2167, BG2247, BG2284, BG2285, BG2286, BG2287, BG2288, BG3026, BG3046, BG3163, BG3164, BG3165 |

## Targets

| scene | reached | where (first) |
|---|---|---|
| BG2077 | no | - |
| BG1283 | no | - |
| BG2093 | yes (disc load) | sweep-bank-9-battle-1 seed 1, frame ~5308, state frame 5499, state SHA-256 `c5eee3d9670b8b2edb932b8db18976881e2bccc446cf9a09a2f1893e8f63c702` |
| BG2290 | no | - |
| any IC02..IC1006 | no | - |
| ENDING / CG | no | - |

## Notes on unverified scenes

BG2093 (disc 2, Chapter 9 dream) is already verified by [bg2093-dream-transition](bg2093-dream-transition.md); the state above is only a quicker entry point. The other BG names in the table were not checked against `wired-unverified` or `paired-not-wired` rows (not verified); each can be reproduced with its row command above and the state of the `summary.json`.

## Next (not done)

- IC and ending files need a scripted route: finish the battle (tactical input movies such as `local/work/t30-chapter2-followup`) or enter the post-battle script; the random autopilot does not. A run from `rb-full/final.state` (disc 1) was not made.
- A runtime scene trace carrying the frame number (the CD trace has none) would remove the frame estimate; needs a runtime change, outside this PR.
- A build where `00204000` is translated would recover the four locked seeds.
