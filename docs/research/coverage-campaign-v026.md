# Coverage campaign on v0.2.6 (chapter 1 start, 4 seeds)

`tools/coverage_campaign.py` with the v0.2.6 runtime, the Enhanced title state and `tests/chapter1-title-new-game.movie`, seeds 11-14, 20,000 frames from frame 6,000 (random input `--auto`). The runtime traced these draws:

- Bodies: NC10, NC11, NC50, NC3250 (NC10, NC50 and NC3250 are new in the register).
- Scene pictures: BG1001, BG1006, BG1209, BG2159, BG2250, BG2251 (all new in the register).
- Clip: MOVIE001.

This is a draw trace, not a visual review: framing of each item is still to be checked by eye. The register marks them `verified_in_game` (drawn by the runtime) only.

Second run (seeds 21-26, 30,000 frames from 4,000): adds body NC25 and scene picture BG1045; the rest repeats the first run.
