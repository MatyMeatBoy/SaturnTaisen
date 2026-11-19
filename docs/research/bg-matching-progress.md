# BG scene-image matching: running log

Goal: pair the 766 PC BG images (`SAKURA1/BG`, `SAKURA2/BG`) with the Saturn scenes, by comparing game screenshots against decoded PC images (`tools/decode_spred.py`, `tools/match_bg_screenshots.py`). Counts only; images stay under `local/`.

Signature: 32x20 luminance of the scene area (x 5-95 %, y 4-66 % of the frame), z-scored correlation against all 766 decoded BG images (`tobytes` grayscale). Candidates need a visual confirmation; a margin under 0.05 is ambiguous.

## Confirmed pairs (visually checked)

| PC image | Scene | Notes |
| --- | --- | --- |
| `SAKURA1/BG1119` | Chapter 1 corridor, day | `BG1120` is the night variant (lights lit) |
| `SAKURA1/BG1209` | Letter with seals | Saturn frame mid-fade; PC image is the full-brightness version |
| `SAKURA1/BG2251` | Cherry-blossom avenue | |
| `SAKURA1/BG1001` | Theatre lobby, front doors | |
| `SAKURA1/BG1002` | Theatre lobby with visitors (variant) | Actors in the PC image |
| `SAKURA1/BG1006` | Lobby, staircase and desk | |
| `SAKURA1/BG1007` | Theatre lobby with crowd (variant) | |
| `SAKURA1/BG1021` | Lobby staircase, green carpet | |
| `SAKURA1/BG1116` | Corridor with windows and door | |
| `SAKURA1/BG2039` | Group photo (academy cadets) | |
| `SAKURA1/BG1075` | Library, green curtains | |
| `SAKURA1/BG1120` | Corridor at night (lamps lit, dark window) | Night variant of `BG1119` |

Rejected: `SAKURA1/BG2173` for the episode title card (false positive, no matching structure).

## Pass 1: cold New Game, continuous run

- Source: the 297,107-frame cold run (inputs of `local/work/rb-full/input.movie`), one screenshot every 250 frames (about 1,190 frames), strict native mode.
- Status when written: running; 875 screenshots ranked (93 strong, 13 distinct candidates, 12 confirmed). After it ends: rank all screenshots, confirm candidates visually, and update this table and the scene-images counter in `config/hd-progress.json`.
- Count so far: 12 of 1,267 scene images matched, 0 integrated.

## Shard B review (T77, 2026-11-19)

Shard B = `SAKURA1/BG11xx`, `BG12xx`, `BG13xx`: 200 decoded pictures (138 `content`, 60 `number`, 2 `missing`). 53 `number` pairs were already reviewed; the 7 remaining were compared by eye on a contact sheet (Saturn decode left, PC picture right) and all confirmed as the same scene: BG1207 (blossom picnic), BG1257 (ruined buildings), BG1280 (battle scroll), BG1282 (breaking wave), BG1283 (ruined street), BG1285 (burning street), BG1310 (large wave). Correlation is low (-0.27 to 0.47) because the Saturn decodes of BG1257, BG1283, BG1285 and BG1310 show band/strip artefacts (decoder layout, see `docs/research/saturn-bg-format.md`), so the match rests on composition, not pixels. Added to `eye_confirmed_number_tier`. `config/hd-scene-bg-pairs.json` is unchanged: it records screenshot-confirmed pairs with an evidence frame and none was taken.

## Shard A review (T76, 2026-11-19)

Shard A = `SAKURA1/BG10xx`: 99 decoded Saturn pictures, 65 tier `content` and 34 tier `number` in `config/hd-scene-bg-map.json`. All 34 `number` pairs were already confirmed by eye in `config/hd-scene-bg-review.json` (contact sheets, Saturn next to PC), so nothing is left to review at that tier and no new pair was added. Re-checked by a contact-sheet script that no `number` pair of the shard is missing from the confirmed or rejected lists. Not done: a side-by-side check of the 59 shard-A `content` pairs above correlation 0.905 (only the 96 lowest correlations of the whole set were reviewed side by side); the Saturn side was checked for baked-in English text.
