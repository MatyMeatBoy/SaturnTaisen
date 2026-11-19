# EVE202 tactical inset

Disc 1 shows EVE202 on VDP2 layer 5 during the episode-2 tactical encounter. The opaque picture fills native (16, 8, 288, 144), over the map and above the dialogue panel. Windows of 1280 × 720 and 1920 × 1080 place the inset at (208, 48, 864, 432) and (384, 124, 1152, 576), respectively.

Patch 0097 uses the Enhanced HD backgrounds setting on this presentation path. It requires the EVE202 palette in the captured frame, the exact top-source footprint and the opaque native RGB fingerprint. The RGB fingerprint makes the runtime fall back to native when the appearance differs. The worker verifies the PC file size and fingerprint, then crops BBG202.SPR subimage 0 at (0, 20, 564, 282). This keeps the 2:1 ratio of the Saturn inset. The texture uses nearest-neighbour scaling and the approved integer canvas fit. The native composition supplies the rest of the frame.

## Verification

- In the two-window A/B, each pair matched all 80 guest hashes, with zero interpreted blocks. HD differences occupied the inset exactly. Original, missing PC assets and the EVE0101 control produced identical RGB with the setting enabled and disabled.
- Entry from the episode-2 cold Continue checkpoint at frame 6250 matched 1,242 guest hashes across HD enabled, disabled and the v0.2.5-alpha reference. Twenty-four capture pairs at 1280 × 720 show the native map through capture 1139, the native EVE202 image at 1140, and the HD inset active by 1150.
- Exit from the EVE202 checkpoint with the chapter-2 intro movie delayed 100 frames matched 130 guest hashes across the same three variants. Eighteen capture pairs at 1280 × 720 show active HD through 105. The native inset is visible at 106, followed by the map at 107. The enabled and disabled outputs match from capture 106 onwards.
- Entry and exit had zero interpreted blocks. Frames outside the inset matched across all captured comparisons. Both boundaries are cuts. A naturally blended EVE frame remains untested.

With patches 0095 and 0097 applied together, an exit smoke test matched 134 guest hashes and reproduced the five sampled captures, with zero interpreted blocks. The HD inset was active at capture 105 and the enabled and disabled captures matched from 106.

The private replay scripts, receipts, state fingerprints and screenshots are in `local/work/codex-tw2`. This validates EVE202 on the observed disc-1 path. EVE0101 has different framing. IC01 recognition was confirmed under the Save/Status/Resume menu and still needs its own HD placement. Additional EVE, IC, disc-2 behavior and release packaging remain open.

## 1440p verification

The merged runtime with patches 0136 and 0137 and the observed ending AOT variants replayed the same disc-1 exit at 2560 × 1440 in Zoom. Enhanced with the isolated BBG202 donor, Enhanced with HD backgrounds disabled, Enhanced with the donor missing, and both Original controls produced the same 132 guest hashes. All five runs reported zero interpreted blocks. The guest hash log SHA-256 is `db81952e43de30d01d6d16ab8b043b4afc875cad86ebb44229dd19935ab0dc67`.

The active inset at (416, 96) has size 1728 × 864. At capture 105, each of its 1,492,992 RGB pixels matches the independently decoded PC crop at (0, 20) with size 564 × 282 after nearest-neighbour scaling. Differences from the Zoom control stay within that inset at captures 80 and 100–105. At capture 106 and later sampled frames, the gameplay output is pixel-identical to the control. The missing-donor pair and the Original pair are pixel-identical in all 12 samples.

The coverage register records this runtime witness for disc 1. The pictures, receipts, and replay commands are retained under `local/work/codex-tch2-scenes/`.
