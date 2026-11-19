# BBG full-frame pictures (TP2b)

Scope: the seven disc 2 battle pictures that `config/hd-chapter-coverage.json` lists as `unsupported-size`: BBG238-BBG243 and BBG300. (The queue row said eight; the inventory in `config/hd-wide-bg-plan.json` has seven BBG entries, all variant C, 320x224 Saturn and 640x480 PC.)

## Why the scroll-table rule does not apply

`tools/gen_scroll_pictures.py` handles a 288x144 window sliding over a larger variant-B picture whose PC art is exactly 2x. These pictures are variant C: a full 320x224 frame, no scroll axis. The scene-picture path in the runtime also draws only inside the 288x144 Zoom window, mapping the whole PC image onto it, so it cannot place a 640x480 image against a 320x224 layer. A new draw path would need an exact native frame match plus a PC crop, and each picture needs a valid crop first.

## Geometry check (offline, no game)

Both sides decoded with `tools/decode_saturn_bg.py` and `tools/decode_spred.py` (Saturn from `local/prepared/disc2`, PC from the local CAB extraction). Contact sheet, Saturn next to PC:

| Picture | Saturn | PC | Finding |
|---|---|---|---|
| BBG238 | Sakura, tight close-up, face fills the frame | Sakura, different pose (hand at chin), wider framing, kimono visible | different composition, no proportional crop |
| BBG239 | Sumire close-up | Sumire, hand at mouth, shoulders visible, different head angle | different composition |
| BBG240 | blond, red glove, close-up | same character, wider, jacket visible, other expression | different composition |
| BBG241 | purple braid and glasses, close-up | same character, hand at chin, costume visible | different composition |
| BBG242 | brown spiky hair, close-up | same character, fist visible, wider | different composition |
| BBG243 | blond with bow, close-up | same character, wider, teddy bear clearly visible | different composition |
| BBG300 | blue gradient, dark top-right | blue gradient, dark top-right | same gradient, but 8 bpp banding vs 24 bpp; best crop (0,32,640,480) has mean RGB difference about 11-14 levels, full-frame crop about 17, squash about 14-16: no unique crop |

For the six portraits the PC art is a redrawn, wider-framed version of the same character, not the Saturn picture at 2x. A scale-and-offset search of PC sub-rectangles with the Saturn aspect (40-100 % of the width) reached only 0.74-0.95 on a coarse grey signature dominated by the white background, and the eye check shows the poses differ, so no crop reproduces the Saturn framing. This is the same situation as BG2252, which stays native because the PC composition differs.

## Decision

- BBG238-BBG243: keep the Saturn picture (status stays `unsupported-size`; reason now also "PC composition differs"). Replacing it would change the framing, not just the resolution. If the owner prefers the wider PC portrait, the pairing is already in `config/hd-scene-bg-review.json` and what is missing is a full-frame draw path in the runtime (T105c), not data.
- BBG300: plain gradient, nothing to gain at 1440p, no unique crop. Stays native.
- No state reaches any of the seven pictures in the local set, so no in-game capture was possible; no SDK patch, no table row and no regeneration of `docs/HD_PROGRESS.md` or `config/hd-chapter-coverage.json` were needed (no status changed).

## Not verified

Where in the game each picture is shown (which event or battle intro), and whether it is shown full-frame or under the Zoom window. That needs a replay that reaches disc 2 battle intros (TH-series attribution).
