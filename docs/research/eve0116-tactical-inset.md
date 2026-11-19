# EVE0116 tactical inset

The first episode shows Satan's close-up after the shrine fight on English disc 1. The VDP2 layer-5 palette is `BABF974513C7F5B4` and the opaque plate covers native (16, 8) through (303, 151). The clean Saturn RGB plate and the centre of the wide Stage01 composition both hash to `FA2D76A6FBC01DCD`. The enlarged tactical viewport can preserve the complete Saturn plate.

The corresponding PC picture is `SAKURA2/BG/BBG201.SPR`, subimage 0. A visual comparison and the 2:1 correlation fit identify the crop (0, 32, 568, 284) in the 576×320 PC image. The measured luminance signature correlation is 0.983. The runtime checks the PC file's exact length and fingerprint, and draws on the Enhanced tactical canvas only when the observed native RGB plate is opaque and matches. The destination uses the same integer scale as the tactical canvas. The native image supplies all other frames.

## In-game verification

With the 102-patch stack including RetroAchievements and IC01, the 2560×1440 run matched the earlier runtime across all 1,200 guest frame hashes with zero interpreted blocks. The changed RGB lies exactly in (416, 96) to (2144, 960), exclusive. The two captures bracketing the inset are pixel-identical. This comparison preserves the surrounding Stage01 terrain, dialogue and small portrait.

Original retained identical captures and matched all 1,200 guest hashes. Without the PC assets, the active plate matched the prior runtime and the first 700 guest hashes matched. The existing EVE202 replay still drew the same picture at 1920×1080 with all 80 guest hashes and the capture unchanged.

Private receipts and captures are in `local/work/codex-tw2-eve0116`. The witness covers the episode-1 tactical route on disc 1. Additional appearances and a visibly blended variant remain to be checked. No package change.
