# BG matching shards

Split of the 766 PC BG images so several collaborators can work in parallel. Each shard is a candidate prefix for `tools/match_bg_screenshots.py` (passing it restricts candidates and speeds ranking). Record confirmed pairs in `config/hd-scene-bg-pairs.json` and the log `bg-matching-progress.md`; take one shard per PR.

| Shard | Candidate prefixes | Images | Likely content (guess) | Confirmed |
| --- | --- | --- | --- | --- |
| A | `SAKURA1_BG10` | 100 | Theatre lobby and public areas (variants of light) | 1001, 1002, 1006, 1007, 1021 |
| B | `SAKURA1_BG11`, `SAKURA1_BG12`, `SAKURA1_BG13` | 199 | Corridors, rooms, offices (day/night variants) | 1119, 1209 |
| C | `SAKURA1_BG20`, `SAKURA1_BG21`, `SAKURA1_BG22`, `SAKURA1_BG23` | 257 | Second series (events, outdoors) | 2251 |
| D | `SAKURA1_BG25`, `SAKURA1_BG30`, `SAKURA1_BG31`, `SAKURA1_BG32`, `SAKURA1_BG35` | 92 | Later series | none |
| E | `SAKURA1_BG40`, `SAKURA1_BG41`, `SAKURA1_BG42`, `SAKURA1_BG43` | 67 | Fourth series | none |
| F | `SAKURA2_BBG`, `SAKURA2_GO_` and `SAKURA1_BG0` | 51 | Disc 2 backgrounds | none |

Counts are PC images in the shard.

## Faster capture

1. Run several headless runs in parallel, one per input movie or state (`--shot-every 125:PREFIX`), instead of one long cold run.
2. Use `--auto SEED[:FROM]` random input from a saved state in the chapter that shard belongs to, with `--unthrottled`.
3. Decode the PC images once (`tools/decode_spred.py`) and keep the signature JSON; ranking 500 screenshots takes seconds.
4. Skip frames with a dialogue box covering the scene and frames mid-fade; confirm each candidate by eye (lighting variants such as BG1119/BG1120 share structure).

Not every BG is shown in the first disc's early chapters: shards D-F need later-chapter states from the sweeps in `docs/research/evt-overlay-registry.md`.
