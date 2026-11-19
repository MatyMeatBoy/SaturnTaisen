# PC menu/HUD inventory for the HD mod (T23)

Machine-readable evidence: [pc-menu-hud-inventory.json](pc-menu-hud-inventory.json).

First step of T23: identify which PC menu/interface resources (`SAKURA1/SYSTEM/*.SPR`) have an equivalent candidate Saturn file, before attempting any visual substitution. `tools/audit_pc_menus.py` follows the same header-only pattern as `audit_hd_characters.py`: it does not copy pixels or art into the repository, only counts images and hashes.

## Result

```
python tools/audit_pc_menus.py --pc-root <PC extraction> --disc local/prepared/disc1/Track\ 01.iso --disc local/prepared/disc2/Track\ 01.iso --output <local report>
```

29 `.SPR` files in `SAKURA1/SYSTEM`, 572 non-empty images, 0 header errors. 20 of 29 have a candidate Saturn file by name; the other 9 (`BURO_W`, `FONT_CSL`, `JYOUKI`, `KAO`, `OP_WIN`, `R_HARI`, `SHADE_WA`, `SHADE_WB`, `TUIKA_W`) do not yet have a proposed match.

## Candidates by name (geometry and palette unverified)

| PC (`SYSTEM/*.SPR`) | Saturn candidate | Note |
| --- | --- | --- |
| `TITLE`, `SEGALOGO`, `REDLOGO`, `CAUTION`, `TL_BG0`, `TL_ROGO0` | `LOGO.SH2` | Title screen; already has its own translated text (see `traduccion-espanol.md`). |
| `OPTION`, `WINDOW`, `EXIT_W` | `SAKURA` | Options/load; matches screens already translated (`opciones()`, `carga()` in `tools/es/menus_es.py`). |
| `NOWLOAD` | `LOAD.BIN` | Dropped as a shortcut: `NOWLOAD.SPR` has a single 640x480 image (format 0x15), just as fused as Saturn's LOADING screen — the PC doesn't separate text from the background here either. `FONT_CSL.SPR` (16x32x2, name suggests a font) is the lead still to review if a dedicated font for LOADING/episode is wanted; not yet verified. |
`OMKMOV_W`, `OMKSND_W`, `KARAOKE`, `MINISAKU`, `MSTAFF` | `OMALL.DAT` | Candidates for the extra menu (T25 left it blocked for lack of a pointer table on Saturn). `KARAOKE.SPR` has 17 individual images 32px tall with variable width (192-352px) — consistent with a list of separate text labels (song titles), unlike a single fused image. This supports the Saturn extra menu (271 DTE pairs in `OMALL.DAT`) being a real list of labels and not unused data, though it does not resolve its pointer table. `OMKMOV_W`/`OMKSND_W` (500x376/480x376, several per category) look like per-tab background panels, not loose text. |
| `SISTEM`, `SIS_BG`, `SIS_BG2`, `SIS_BG3`, `SIS_ICON` | `ICATALL.DAT` | Candidates for status/intermediate, already translated on Saturn; serve as a design reference, not a blocker. |

## Next step

For each candidate with `found=true`: decode both images (PC via the native exporter `sakura.exe --export-pc-spr`, Saturn via the tools already existing in `tools/es/`), compare geometry, and check whether the PC separates text from the background in a way Saturn does not. No name match here demonstrates compatible composition, palette, or geometry — this is a list of candidates to verify, not an integration.

### Item detail sprite witness (T109)

In the chapter 1 item menu, replayed the saved options-nav state with the
English disc and the v0.2.4 reference executable
(SHA-256 1a94790eefc8492ca80499bbbd3e7517cb4db565908bcee86ae5b12f44c94b9e).
Hold Up from frame 1, release at 59 and confirm with A from 76 to 79.
The frame-180 capture shows the letter card and dialogue. All 180 frames
ran strict-native with zero interpreted blocks.

State frame 179 contains a 112×112 VDP1 command at 0xCE0, with PMOD 0x00A0,
COLR 0xC600, SRCA 0xB850, SIZE 0x0E70 and origin (-56,-88) relative to the
local coordinate. VDP1 VRAM at SRCA × 8 = 0x5C280 is byte-identical to the
12,544 picture bytes of ITEM07.BIN. CRAM byte offset 0xC00 contains the
exact 512 palette bytes, matching table fingerprint 994AF50BC61B12E6.
T108 has a 224×224 PC counterpart for this card.

The menu before selection can retain the texture and palette with no active
112×112 command. Patch 0090 requires the approved command and matching whole
texture and palette fingerprints. It tracks actual VDP1 writes on each
framebuffer and checks the card against VDP2 scanout. Zero-indexed texels,
pixels covered by later commands, and pixels won by other layers stay native.
Unsupported blends, clipped draw targets, missing art, and Original mode use
the native presentation. The 38 approved Saturn texture and palette pairs
were identical on both prepared discs. All 38 paired PC subimages decoded to
opaque 224×224 pictures with the SHA-256 recorded by T108. The runtime table
can be regenerated with this command.

```text
python tools/gen_item_table.py config/hd-item-map.json item_card_table.h --textures config/hd-item-texture-fingerprints.json
```

#### Runtime evidence

The letter was replayed from `options-nav.state` using the inputs above.
At 1920×1080 the approved viewport placed it at (680,104), scaled from 112×112
to 560×560. All 287,325 destination pixels belonging to visible card texels
matched the PC source. The 26,275 other pixels inside the rectangle and the
entire surrounding frame matched the same runtime with the PC file absent.
Preselection captures also matched.

A second letter replay and the Jean-Paul replay both start from the legitimate
`leave-dressing.state` (SHA-256 `4784c3eb1643676b39abb0b0bcc01092a782e5fefedf5d728a8041d70a4b4d62`),
the point after collecting the bear and leaving the dressing room. Both re-enter
by holding Down on frames 20–25, pressing A on 45–52, and opening inventory with
Start on 700–707. The remaining inputs and observed results are:

| Case | Input after opening inventory | Frame 1000 |
| --- | --- | --- |
| ITEM07 with cursor | Up+Left 810–827, Left 828–841, A 890–897, Right 930–954 | HD color replaces 280,575 destination pixels. All 171 cursor-covered native texels and 1,051 transparent texels retain their original RGB blocks. No RGB difference extends past the card rectangle. |
| ITEM12, excluded bear | Up+Left 810–827, A 890–897 | Fully native. Active command 0x5C0 uses the same geometry and mode as ITEM07. Texture FNV `2E3976D6862A7486`, palette FNV `235B09AEB829FB4C`. The PC asset is an icon-only match. |

Strict-native windowed runs compared all 190 guest hashes of the first letter
route and all 1,010 guest hashes of each dressing-room route. Across the relevant
runs, the Original viewport and ITEM12 Enhanced viewport matched the previous
runtime pixel for pixel, and the ITEM07 asset-absent Enhanced viewport matched
it as well. Every run reported zero interpreted blocks. The other 37 approved
cards have offline evidence and still need direct in-game witnesses. There was
no release package change.

## T110 offline geometry and palette review

Decoded all nine previously unmatched files and checked their SHA-256 hashes
against the inventory. They contain 430 images. The PC images use SPRED
format 0x15 (compressed RGB555), with cyan-keyed transparency where relevant.
For candidate discovery, compared grouped dimensions and downsampled,
chroma-keyed PC images with RGB reconstructions of saved VDP1 commands. Read
the saved `RAMCTL`, `SPCTL` and `CRAOFB` to resolve the native CRAM banks.
Appearance scores served as search hints. Each proposed correspondence
received a visual check against the actual native and PC textures.

| PC file | Decoded contents | Native evidence and decision |
|---|---|---|
| `BURO_W` | Two 208x384 tabbed bromide panels | No native equivalent established in the saved-state sample. |
| `FONT_CSL` | Two 16x32 arrow cursors | Left and right 8x16 sprites in the same menu state at (64,108) and (104,108). Command mode 0x0080, colour 0xA2D0, with 16 CRAM words at byte 0x5A0. The active grey entries are 6 and 9. Only new direct candidate at 2x on both axes. |
| `JYOUKI` | 19 cyan-keyed steam frames, up to 80x64 | No native steam sequence identified. The closest colour candidate was an unrelated small battle sprite. |
| `KAO` | 394 portrait atlases at 80x160 | The existing portrait recipe already pairs these with Saturn FCE sprites. The native portrait base is 40x48, with 40x16 eye or mouth strips on the witness route. Reuse that pipeline. |
| `OP_WIN` | One 416x304 program frame and background | Program menu in `continue-probe`: 208x152 at (56,40), bank 0x0500 and 256 CRAM words at 0xA00. Despite exact 2x dimensions, the PC plate bakes Japanese labels into the art. Keep the localized native frame. |
| `R_HARI` | Seven 32x44 variants of the clock hand with clock-face pixels | The LIPS witness in `prebattle-3000` uses an 8x16 indexed sprite at (160,32), mode 0x00A0, colour 0xC500. Its exact bytes occur at `VDP1.BIN` offset 74,624. The stored CRAM colours include 0x8000, 0xBE34 and 0x952B. The PC tile includes the surrounding white clock face and uses a different aspect ratio. Keep the native hand and timing. |
| `SHADE_WA` | One 576x320 right-and-bottom shadow edge | Serves as a reference for the scene-picture shadow. No same native texture established. |
| `SHADE_WB` | One 608x128 dialogue shadow | The 304x64 native witness at (8,152), from `VDP1.BIN` offset 32,640, is the gold frame and its CRAM values are coloured. The PC candidate is black and its mask differs. Keep the native effect. |
| `TUIKA_W` | Three blank bands, 576x48, 576x80 and 384x80 | First band resembles a native 256x24 additional menu band at (32,184), colour 0x02C0 and 16 CRAM words at 0x580. Ratios are 2.25x and 2x. An unmodified draw would change width or height. The second and third entries had no visually verified native match. |

The [offline review table](../../config/hd-system-hud-review.json) lists
all candidates, their PC source identities, and the command and CRAM
fingerprints used to distinguish the six observed textures. The runtime
acceptance for the confirmed inventory layout is documented below.

Separately, `WALL1.BIN` at 320x224 matches the floral composition of
`SAKURA1/WALL/KABE0100.SPR` subimage 0 at 640x480. The whole-image grey
signature correlation was 0.99594 and the flower positions agree by eye.
The file hashes and native palette fingerprint 0x48291F6F1C8A4707 agree
with the existing KABE00 and KABE0100 provenance. Width scales at 2x and
height at 15/7, so keep the existing backdrop path and avoid a raw stretch.
There is no new direct replacement for this backdrop in T110.


## T110a inventory brackets in game

Patch 0093 draws the two 16×32 PC FONT_CSL glyphs over the four 8×16 native
brackets. It requires the complete group of scaled VDP1 commands at native
x=64, 104, 128 and 168, y=108. The VDP1 texture fingerprints and inclusive
corners identify the glyphs. VDP2 scanout supplies each bracket's mode-1 CRAM
bank and indices 6 and 9. The idle bank is 0x5A0 and the hover and confirmation
bank is 0x5E0. The inventory label and hand cursor use their native paths.

The rasterizer follows actual framebuffer writes. A later opaque writer keeps
its native pixels, even when it writes the same color as the bracket. The
overlay covers only texels still owned by a bracket at scanout. Effects,
incomplete or changed groups, other palette banks, and unavailable or
unrecognized PC assets fall back to Saturn. The verified gray and pink shades
are reused at twice the native density within the existing integer-scaled
viewport. The verified states do not establish a disabled-button palette.

| Disc 1 replay | Captured frames |
| --- | --- |
| English idle | 60 |
| English Option and Return hover | 62 and 104 |
| English Option confirm and exit | 68 and 92 |
| English Return confirm and exit | 113 and 140 |
| English hand over the left Option bracket | 76 |
| Spanish idle after leaving Options | 115 |

Seven private replays at 1920×1080 each compared the asset-present and
asset-absent viewports in Original, Enhanced Set, and Enhanced
Zoom. Each of the 656 guest frame hashes matched the other profiles for its
input route, with zero interpreted blocks across all 43 runs including the
altered-asset control. Every Original capture matched pixel for pixel. The
Enhanced changes stayed inside the four verified glyph rectangles, including
at hand overlap. Exit captures and the altered-asset control matched the
asset-absent viewport pixel for pixel. No release package was made.
