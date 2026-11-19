# Coverage campaign on v0.2.6 (chapter 1 start, 4 seeds)

`tools/coverage_campaign.py` with the v0.2.6 runtime, the Enhanced title state and `tests/chapter1-title-new-game.movie`, seeds 11-14, 20,000 frames from frame 6,000 (random input `--auto`). The runtime traced these draws:

- Bodies: NC10, NC11, NC50, NC3250 (NC10, NC50 and NC3250 are new in the register).
- Scene pictures: BG1001, BG1006, BG1209, BG2159, BG2250, BG2251 (all new in the register).
- Clip: MOVIE001.

All six scene pictures logged `usable=1`. BG1006 appeared in seeds 12 and 14.
The other five appeared in all four seeds.

The register uses `verified_in_game` for the runtime draw trace. BG1209
has a separate visual comparison below.

### BG1209 letter at 1440p

The retained Chapter 1 letter snapshot `d1-frio-dialogo/final.state` from the
prepared Spanish disc 1 replays directly with the matching backup seed
and no inputs. Both
Enhanced Zoom profiles used the v0.2.6 campaign executable with SHA-256
`6fcd9aba866a1f3c14c706b8c1a9edc4b40ad4f5a555daa2454c9a59a9269482`.
The HD profile could see only BG1209.SPR. The control used an empty PC
asset directory and kept the Saturn presentation of the letter. The
prepared English and Spanish disc 1 copies have identical BG1209.BIN bytes.

All 60 guest state hashes matched byte for byte (log SHA-256
`e44ae33172694f23bab2b5ec93a419239c68831ec49743db12c6c9bc5dfb5d52`),
with zero reported interpreted blocks. In the 2560×1440 captures at
20, 40 and 58, the RGB differences fit the picture extent
(272,29)–(2288,1037), right and bottom exclusive. The letter edges and
seal align with the Saturn picture, and the Spanish dialogue and
surrounding presentation remain pixel-identical. The other five campaign
scenes retain trace evidence.

Second run (seeds 21-26, 30,000 frames from 4,000): adds body NC25 and scene picture BG1045 (trace evidence only).
