# Scene picture spot check (TP9)

One in ten of the connected scene pictures, checked by eye. Names, status and verdicts only; no pixels are committed.

## Selection rule (reproducible)

Set: every `scene-pictures` entry of `config/hd-chapter-coverage.json` whose status is `hd` or `wired-unverified` (no entry has the second status today), de-duplicated by `disc:path` (59 rows, 58 distinct pictures). Sort the 58 names as strings and take positions 10, 20, 30, 40 and 50 (every 10th). That gives 5 pictures.

## Verdicts

Two levels were tried. "In game" means the runtime drew the PC picture and a capture of it was compared with the native Saturn capture of the same scene. "Pair" means the decoded Saturn picture (`tools/decode_saturn_bg.py`) was compared by eye, side by side, with the decoded PC picture the table maps it to (`tools/decode_spred.py`); this checks the pairing data, not the runtime draw.

| # | Picture | Chapter | In game | Pair (offline, contact sheet) |
|---|---|---|---|---|
| 10 | `1:/SAKURA1/BG1022.BIN` | 3 | not reachable: no saved state or movie beyond chapter 2 in `local/work` | OK |
| 20 | `1:/SAKURA1/BG1193.BIN` | 1 | not reachable (see below) | OK |
| 30 | `1:/SAKURA1/BG2039.BIN` | 1 | not reachable (see below) | OK |
| 40 | `1:/SAKURA1/BG2533.BIN` | 5 | not reachable: chapter 5 has no saved state; wide 512 px picture, PC shows the cropped pan | OK (same scene, the PC picture is the cropped pan) |
| 50 | `2:/SAKURA1/BG1072.BIN` | 9 | not reachable: no disc 2 state in `local/work` | OK (same room; the PC tint is lighter than the Saturn palette) |

Wrong pictures: 0, so no neighbour review was triggered.

## Numbers

- Reached in game with a PC-versus-native capture: 0 of 5. Not reachable: 5 of 5 (100 percent of the sample; 5 of 58 pictures were sampled).
- Error rate of what was reached in game: undefined (nothing reached).
- Pair level: 5 checked, 0 wrong (0 percent; with n=5 the 95 percent upper bound is about 45 percent, so this does not certify the other 53).

## Why the in-game check failed

BG2039 (frames 143,040-143,100) and BG1193 (253,260-253,320) lie on the chapter 1 cold route, which the input movie `local/work/rb-full/input.movie` (297,107 frames) reaches from a cold start. Headless runs with a copy of an existing build at `local/build/sakura-tp9run/` and `--pc-assets local/work/pc-cab/out-bg` with `pc_hd_backgrounds=0` did not draw any PC scene picture: no `scene picture:` trace line appeared and a PC capture was pixel-identical to the native one, in a state saved at frame 143,070 and in the cold route at frame 8,850 (BG1209, which the coverage report records as drawn). The build of 2026-11-18 predates the PC scene draw; the later builds tried either crashed at startup (t118) or ran no recompiled blocks (t116, t120). The frame 143,070 capture also shows a bedroom, not a group photo, so the guest-frame bracket in `hd-chapter-1.md` is the callback frame, not necessarily the frame where the picture is on screen. This needs a working Enhanced build; the owner or the integration desk should repeat it with the build used for `coverage_campaign.py`.

## Not verified

The runtime draw of all five, the 1440p result, chapters 3, 5 and 9 in game, and the other 53 pictures.
