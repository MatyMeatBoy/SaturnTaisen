# BG scene-image matching: running log

Goal: pair the 766 PC BG images (`SAKURA1/BG`, `SAKURA2/BG`) with the Saturn scenes, by comparing game screenshots against decoded PC images (`tools/decode_spred.py`, `tools/match_bg_screenshots.py`). Counts only; images stay under `local/`.

Signature: 32x20 luminance of the scene area (x 5-95 %, y 4-66 % of the frame), z-scored correlation against all 766 decoded BG images (`tobytes` grayscale). Candidates need a visual confirmation; a margin under 0.05 is ambiguous.

## Confirmed pairs (visually checked)

| PC image | Scene | Notes |
| --- | --- | --- |
| `SAKURA1/BG1119` | Chapter 1 corridor, day | `BG1120` is the night variant (lights lit) |
| `SAKURA1/BG1209` | Letter with seals | Saturn frame mid-fade; PC image is the full-brightness version |

Rejected: `SAKURA1/BG2173` for the episode title card (false positive, no matching structure).

## Pass 1: cold New Game, continuous run

- Source: the 297,107-frame cold run (inputs of `local/work/rb-full/input.movie`), one screenshot every 250 frames (about 1,190 frames), strict native mode.
- Status when written: running; 35 screenshots captured. After it ends: rank all screenshots, confirm candidates visually, and update this table and the scene-images counter in `config/hd-progress.json`.
- Count so far: 2 of 1,267 scene images matched, 0 integrated.
