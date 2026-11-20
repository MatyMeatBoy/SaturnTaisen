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
| ITEM12, bear before patch 0147 | Up+Left 810–827, A 890–897 | Fully native. Active command 0x5C0 uses the same geometry and mode as ITEM07. Texture FNV `2E3976D6862A7486`, palette FNV `235B09AEB829FB4C`. The earlier audit selected the 72×72 menu icon. |

Strict-native windowed runs compared all 190 guest hashes of the first letter
route and all 1,010 guest hashes of each dressing-room route. Across the relevant
runs, the Original viewport and ITEM12 Enhanced viewport matched the previous
runtime pixel for pixel, and the ITEM07 asset-absent Enhanced viewport matched
it as well. Every run reported zero interpreted blocks. The other 37 approved
cards have offline evidence and still need direct in-game witnesses. There was
no release package change.


### ITEM03, ITEM12 and ITEM27

The original item ranking allowed 72×72 menu icons to outrank complete item cards. A reverse search limited to full 224×224 cards found Maria’s photograph (`ITEM03`), Iris’s teddy bear (`ITEM12`) and Ogami’s photograph (`ITEM27`). Each PC file has a complete same-number picture, with one opaque image at index 0 and the same border and key geometry as the previously verified letter card. The two prepared discs have byte-identical 112×112 pictures and 512-byte palettes for each item.

| Card | Native texture FNV-1a | Native palette FNV-1a | PC file |
| --- | --- | --- | --- |
| ITEM03 | `987FF4B5CDFCC8F7` | `303817C07D8AD3EA` | `ITEM03.SPR` |
| ITEM12 | `2E3976D6862A7486` | `235B09AEB829FB4C` | `ITEM12.SPR` |
| ITEM27 | `69495E754C680B31` | `61BE6F092AD8446C` | `ITEM27.SPR` |

The existing item-card draw path matches the exact texture and palette and uses the presented VDP1 write mask. Patch 0147 adds three generated table rows. The review pins the complete PC file SHA-256 for each approved card.

An English disc 1 resume of the archived bear-card route verified ITEM12 at 2560×1440. The destination was (888,141), 784×784. All 549,927 visible card pixels match the selected PC image at the existing integer scale. Exactly 549,736 pixels differ from the native capture, all inside the card. Every pixel outside the native card mask is preserved. The missing, disabled and previous-renderer Enhanced captures match, as do both Original captures. The six runs have identical SRAM and 80 identical guest hashes (SHA-256 `aefc784b2fefa2f9f9eac5a2373d9c80feeded9767258eaa178c35fa4f99295a`), with zero interpreted blocks. The 190-frame ITEM07 control and 1,200-frame opening also match the previous renderer in guest hashes, SRAM and the sampled captures.

ITEM03 and ITEM27 are checked offline. Their natural display and package inclusion for all three cards remain open. Private captures and receipts are under `local/work/codex-th1/hud-item-candidates/`.

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

## T110b CD-1 emblem in the load menu

The English disc 1 **Data to load** screen uses a 40×40 VDP1 CD-1 emblem at native (24, 64). The matching donor is subimage 2 of `SAKURA1/SYSTEM/SIS_ICON.SPR` at 80×80. Its alpha mask exactly matches the doubled Saturn silhouette, and 627 native texels have different colors within the corresponding 2×2 PC blocks.

Enhanced identifies the emblem by its VDP1 command geometry, indexed texture and CRAM palette, then checks its actual framebuffer writes and scanout ownership. The native draw uses a ratio-zero VDP2 interpolation, with 31/32 sprite RGB and 1/32 lower-layer RGB. The replacement applies the same per-channel calculation using the lower RGB verified at scanout. Other effects and missing or altered PC data retain native rendering.

The 2560×1440 comparison replayed the same settings, PC data and guest inputs on the candidate and its prior runtime. An independent reconstruction using the captured VDP1 and VDP2 layers matched the entire output frame. Only pixels inside the CD-1 emblem changed. Original mode, a missing or altered donor, and disabled PC backgrounds retained their native pixels. All profiles matched all 25 guest frame hashes with zero interpreted blocks. The existing FONT_CSL inventory brackets were active and matched the prior runtime pixel for pixel at 2560×1440 with all 61 guest hashes equal.

SIS_ICON subimage 1 also matches the System RAM icon's silhouette. Its 2×2 blocks are all uniform, and the candidate keeps that icon native. Private captures and receipts are in `local/work/codex-tw5-next`. Other menu layouts, palette variants and disc 2 remain open. No package change.

### T110c CD-2 emblem in the load menu

The English disc 2 title replay opened **Data to load** with two Chapter 8 slots and one Chapter 7 slot. The top CD-2 emblem uses the same 40×40 Saturn command and position (24,64) as the verified CD-1 call. Its complete texture fingerprint is `9AF2CC56D5CAEB11` and palette fingerprint is `52C0DBB1EA90290A`. The corresponding pink CD-2 subimage is 3 of the existing pinned `SIS_ICON.SPR`. The 80×80 alpha silhouette matches the doubled Saturn indices.

Patch 0146 uses the previous VDP1 ownership and VDP2 blend checks. Each exact emblem has its own decoded cache entry. The renderer keeps the lower slots on the native path. At 2560×1440, the independent 31/32 PC and 1/32 background reconstruction reproduced the entire result, with 1,122 native-owned texels in the tested draw and preserved pixels outside the emblem. All seven 30-frame runs shared the same strict guest hash log. Original, disabled, missing and corrupt-donor controls passed. The existing disc 1 HD emblem retained identical output and guest hashes. Other slot positions, other variants and package inclusion remain open.


## Load menu selection arrows

The English **Data to load** screen on both Saturn discs uses two 8×16 arrows at native (224,62) and (280,62). Both commands use mode `0080`, color bank `02C0` and the exact 32-byte palette fingerprint `809F8438D9925B74`. The packed texture fingerprints are `C22BF33F44463864` and `FF02AF0F7DEB043C`, respectively. The PC equivalents are subimages 8 and 9 of `SAKURA1/SYSTEM/SISTEM.SPR`. Each is 16×32. Their cyan-keyed masks match all 512 pixels of their doubled Saturn silhouettes.

Patch 0150 extends the existing bracket ownership tracker to the exact two-arrow layout. It requires both recorded commands and valid scanout before using the 285,236-byte PC file pinned by FNV-1a `0DBC9A3C989D369B`. Each owned arrow pixel must satisfy the native VDP2 ratio-zero blend, with the sprite weighted 31/32 and the underlying layer 5 weighted 1/32. The HD draw repeats that blend for each PC subpixel. Occluders, transparent holes, slot labels and the middle of the selector retain the composed Saturn pixels.

The 2560×1440 replay resumed the genuine English load menu on each disc. All 2,772 changed pixels in each arrow match independently decoded PC art blended over the corresponding archived VDP2 layer. Changes stay within (1664,420)–(1712,516) and (2000,420)–(2048,516) in half-open bounds. Missing and same-size altered donor files preserve the native arrows. Both Original captures match, as do the two disabled captures and the previous renderer’s Enhanced capture without the replacement.

Each group of eight controls produces 60 identical guest hashes, identical SRAM and zero interpreted blocks. The guest SHA-256 is `4667bdada71e2e83b4a67f9dc1be1840a06795e079b5aab4daa6767762d839e2` for disc 1 and `539d5621003d529c2abc486f5e9b5a50a39eb9c68b1910245905e4725f5e594b` for disc 2. The active FONT_CSL inventory bracket comparison matches the prior runtime in all 61 guest frames and the 1440p capture. A 1,200-frame opening comparison also matches.

Private inputs, states and controls remain under `local/work/codex-th1/load-arrows/`. Package inclusion remains open.

## HD measure of the menu/HUD category (TW5)

The register (`config/hd-chapter-coverage.json`, category `menus-hud`) now carries the runtime-drawn menu/HUD pictures, and `tools/build_hd_progress.py` takes the `hud-menus` integrated count from it. The map is explicit in `tools/hd_chapter_coverage.py` (`SYSTEM_HUD_DRAWS`, `SYSTEM_HUD_EXCLUDED`; item cards come from the same selection as `tools/gen_item_table.py`). A picture counts once per PC image, whatever the disc.

Denominator: 572 SYSTEM images, minus the 394 KAO faces (portrait atlas, counted under portraits), plus the 51 distinct PC item pictures of `config/hd-item-map.json` = 229. Integrated: 55.

| Piece | PC images | Patch / table | State |
| --- | --- | --- | --- |
| Inventory item cards | 41 `SAKURA1/ITEM/ITEMnn.SPR` (of 51 candidate pictures) | 0090, `item_card_table.h` | drawn; ten candidate pictures remain open |
| Inventory brackets | FONT_CSL 2 of 2 | 0093, `system_brackets.h` | drawn (idle/hover/confirm) |
| CD-1 and CD-2 load emblems | SIS_ICON 2 of 10 (subimages 2 and 3) | 0112 and 0146, `load_disc_icon.h` | verified for the top load slot; subimage 1 (System RAM icon) kept native |
| Load menu selection arrows | SISTEM subimages 8 and 9 (of 45) | 0150, `system_brackets.h` | verified in the English load menu on both discs |
| Save confirmation frame | TUIKA_W subimage 0 | 0197, border strips | verified in the English disc 1 save confirmation |
| Load-menu banner and control | SISTEM subimages 1 and 4 | 0206, rail masks | English discs 1 and 2 and Spanish disc 1 load menu |
| Options and System frames | SISTEM subimages 11 and 14 | 0205, rail masks | English and Spanish disc 1 Options and English System |
| Timed LIPS and dialogue frames | WINDOW subimages 0 and 1 | 0202, rail masks | English disc 1 Sakura choice and dialogue |
| Long Day choice frame | WINDOW subimage 2 | 0198, rail mask | English disc 2 room choice |
| KAO | 394, excluded here | portrait pack | counted in portraits |

Open (174 images), per SYSTEM file: BURO_W 2, CAUTION 8, EXIT_W 1, JYOUKI 19 (steam, no native witness), KARAOKE 17, MINISAKU 1, MSTAFF 1, NOWLOAD 1, OMKMOV_W 7, OMKSND_W 5, OP_WIN 1 (keep native), OPTION 4, R_HARI 7 (keep native), REDLOGO 1, SEGALOGO 1, SHADE_WA 1, SHADE_WB 1 (keep native), SIS_BG 1, SIS_BG2 1, SIS_BG3 1, SIS_ICON 8, SISTEM 39, TITLE 29, TL_BG0 1, TL_ROGO0 1, TUIKA_W 2 (needs layout), WINDOW 3; plus ten item pictures. Already drawn from other categories and not counted here: IC01 (patch 0107, ICATCH, scene-images), the battle insets (0125/0134, SAKURA2/BG, scene-images). The Spanish CARGANDO lettering (0117) is generated text, with no PC image. The tactical category lists ITEM files in its own unit; that category is not measured yet, so check for overlap when it is.

## TW5 wiring audit: which open families the existing mechanisms can reach

Patches 0090, 0093 and 0112 all recognise their Saturn picture from a **witnessed VDP1 draw call**: a saved state where the menu is open gives the command geometry, the texture bytes (FNV of the unpacked indices) and the CRAM bank, and the renderer then tracks the actual framebuffer writes and VDP2 scanout. Data alone (a table row) is enough only when the new picture goes through a call that is already witnessed and guarded. The original audit checked 187 open images against that rule, using the exports in `local/work/audit-pc-menus` and the earlier search (`local/work/codex-tw5-next/search.py`, which ranked every SYSTEM image against every VDP1 command in all saved states and found only the emblem and the brackets). That audit predated the CD-2 emblem and the three full cards above. Wiring the following blind would be a guess on geometry or on the Saturn texture identity, so each family lists what it needs.

| Family (open images) | What the PC images are | Why it is not wired | What it needs |
|---|---|---|---|
| SIS_ICON 9 | 80x80 disc icons: CD-1..CD-4 in pink (subimages 2, 3, 6, 7) and blue (4, 5, 8, 9), System RAM, cartridge | Same call as 0112 (40x40, mode 0x00A0 bank 0x0600), but `kLoadDiscIcon` is one row keyed by the disc 1 texture and CRAM fingerprints and by position (24,64). The Saturn textures and CRAM of CD-2 are unknown: the only witness is the disc 1 load menu. The Saturn has two discs, so CD-3 and CD-4 never appear. System RAM stays native (uniform 2x2 blocks, shading only). | A disc 2 load-menu state (texture FNV, CRAM FNV, position) and one for any selected/blue variant, then a second table row and a table-driven entry instead of the single `kLoadDiscIcon`. Best next step: 2 to 4 images. |
| SISTEM 43, SIS_BG/BG2/BG3 3, OPTION 4, WINDOW 6, EXIT_W 1, BURO_W 2, TUIKA_W 3 | Window frames and tab panels with blank interiors (nine-slice style, a few baked Japanese tabs such as the Option tab), many at ratios such as 2.25x | No saved state shows any of them as a VDP1 texture; the search found no match. The Saturn probably draws frames from VDP2 cells or as scaled polygons, which the texture-fingerprint path cannot see. The first TUIKA_W band (576x48) against a 256x24 native band is 2.25x by 2x. | Runtime witnesses per menu (which layer draws the frame, VDP1 or VDP2, command list), then per-panel geometry and a frame-and-interior compositor. This is a new mechanism, not a table row. |
| TITLE 29, SEGALOGO, REDLOGO, TL_BG0, TL_ROGO0, CAUTION 8, NOWLOAD | Title emblem pieces, copyright lines, PC-only prompts ("Click Left Mouse Button"), 640x480 logo and caution screens with Japanese text baked in | The Saturn title is built from LOGO.SH2 16x16 tile piece groups with translated labels, so the PC pieces are not 1:1 textures. The full screens are 640x480 against a 320x224 Saturn picture (2.14x vertically, not an integer), and the screen map correlation for OMAKE02 against REDLOGO is 0.29. CAUTION and NOWLOAD are PC-specific or fused with Japanese text. | A per-screen path like the IC01 one (0107: layer ownership hash and custom geometry) with a witnessed frame for each logo screen, and a decision on baked Japanese text versus the translated native text. |
| KARAOKE 17, OMKMOV_W 7, OMKSND_W 5, MINISAKU 1, MSTAFF 1 | Extra-menu labels and per-tab panels | The Saturn extra menu has no pointer table (T25) and no witnessed draw call; OMAKE11/12/13 against WALL/SIS_BG3 are only 0.71 to 0.74 correlation candidates (SIS_BG3 ties with WALL/OMAKE1). | A saved extra-menu state, an eye check of the three OMAKE pairs, then the screen-picture path of the IC01 type. |
| JYOUKI 19 | Steam animation | No native steam sequence identified. | A frame sequence where the steam is on screen. |
| R_HARI 7, SHADE_WB 1, OP_WIN 1, SHADE_WA 1 | Clock hand with face, dialogue shadow, program frame, scene shadow | Kept native on purpose (aspect, colour, baked Japanese labels) or no same native texture. | Nothing unless the keep-native decision changes. |
| Ten item pictures | Nine compact icon subimages and the full ITEM09 flower card | The card path requires a full-card counterpart. | Native icon command evidence or an ITEM09 full-card pair. |

Nothing was built or replayed for this change (documentation and register notes only), so the opening-film hashes are untouched by construction.

## HD save confirmation frame

The English disc 1 victory continuation reaches the `Save Complete!`
confirmation through normal save inputs. The retained state and SRAM are
under `local/work/chapter1-victory-followup/corridor-bridge/continuous-native`.
The saved VDP1 command uses mode `0080`, color bank `02C0`, and a 256×24
picture at (32,184). All 1,680 native border pixels match the independently
decoded palette and texture after the Saturn RGB offset of −16.

PC `SAKURA1/SYSTEM/TUIKA_W.SPR` subimage 0 measures 576×48. The corner strips
use the native 2× geometry, and the intervening straight rows are uniform,
allowing them to fit the 256×24 viewport. Patch 0197 checks the captured VDP1
command, palette, winning layer and composed RGB before drawing the four
border strips. The separate game label and interior retain their Saturn pixels.

At 1440p, all 60,480 border pixels match the independent PC decode and offset.
Four captures of the active confirmation preserve the entire label, interior
and surround pixel for pixel. Two captures after dismissal match the native
screen. Six 110-field strict profiles match guest hashes and SRAM, including
Original and the absent, corrupt and disabled donor controls. Verification
covers the replayed confirmation on English disc 1. Package inclusion and
other TUIKA_W subimages remain open.

## HD Long Day room choice frame

The natural English disc 2 Long Day room menu displays the two-option
room choice after the archived continuation in
`local/work/codex-th1/final-battle-probes/longday-hall`. The size field
describes a 256×88 source. The centered VDP1 scaled sprite renders an
inclusive (32,40) to (288,128) rectangle of 257×89 native pixels.
The texture walk reproduces all 2,806 native gold rail pixels using
the witnessed palette.

Patch 0198 selects WINDOW.SPR subimage 2 and maps its 2× source through
the same VDP1 geometry. The texture preserves native pixels outside
the authored gold rails and where the donor is keyed. The draw requires
the matching command, palette, winning layer and composed native inks.

Seven 190-field strict replays at 1440p match the stock runtime in guest
hashes and SRAM. The highlighted option changes under normal controller
input. An independent decode reconstructs every output pixel in six
captures, with 100,926 changed RGB pixels in each. The choice label,
selection bar, translucent interior, portrait and background remain
exact. Original and the absent, corrupt and disabled donor profiles
match the corresponding native RGB. This evidence covers the English
disc 2 room choice. Other WINDOW variants and package inclusion remain
open.

## HD timed LIPS and dialogue window rails

Patch 0202 extends the guarded WINDOW renderer to PC images 0 and 1. A natural English disc 1 Sakura timed LIPS continuation draws both frames together. The 272 × 120 timed LIPS source maps to Saturn's inclusive 273 × 121 rectangle at (24,16). The 304 × 64 dialogue source retains its exact native placement at (8,152). The masks select 3,194 and 1,214 native rail pixels respectively. The existing disc 2 room-choice layout shares the renderer.

The exact command, indexed source, active palette, winning sprite layer and composed native colors qualify the overlay. The existing timer, timer lettering, center ornament, localized choices, selection, portrait and dialogue stay on the native composition. The donor's keyed samples preserve the native image.

The English disc 1 replay ran 75 strict fields for each of seven profiles. Guest hashes and final SRAM matched. Independent RGB reconstruction matched every pixel in six 1440p captures. Both donors were visible at fields 8, 12 and 16, and dialogue alone at 24, 40 and 60 after the timed choice closed. Original with and without the donor matched. The missing, corrupt and disabled donor profiles matched stock Enhanced. The separate English disc 2 Long Day route matched stock guest hashes, final SRAM and all three sampled captures with WINDOW image 2 active.

Local proof and commands are in `local/work/codex-witness-441-review/hud/window01-ab/receipt.json`, `local/work/codex-witness-441-review/replay-window01.py`, and `local/work/codex-witness-441-review/verify-window01.py`. Package inclusion remains open.

## HD Options and System panel rails

Patch 0205 uses SISTEM images 11 and 14 on the disc 1 Options and System panels. The PC images register at exactly 2× to the verified 288 × 144 and 112 × 88 VDP1 frames. The two localized Options textures share an identical mask. The exact source, palette, command placement, winning layer and composed native colors guard each draw.

The Options mask keeps the right-side arrows and the white option wells native. System keeps the interior native. Both panels retain the whole footer containing the localized label. The overlays use the native 320 × 224 placement and existing integer scale.

Strict 1440p A/B replays on English Options, Spanish Options and English System matched all guest hashes and final SRAM for 56 fields per route. Independent PC decode and native color reconstruction matched every pixel of twelve captures, including Options navigation. Original, missing, damaged and disabled donors matched their native controls. Another 760-field replay preserved the restored Iris/Ogami HD poses and matched seven RGB captures.

Local receipts are `local/work/codex-witness-441-review/hud/system-ab/receipt.json` and `local/work/codex-witness-441-review/hud/system-combo-regression/receipt.json`. Package inclusion remains open.

## HD load menu banner and control rails

Patch 0206 uses SISTEM images 1 and 4 on the Saturn load menu. The 352 × 48 banner and 288 × 64 control art register at 2× to the native 176 × 24 and 144 × 32 commands at (16,24) and (160,178). The masks include 1,200 and 1,328 authored rail pixels. They preserve the banner text, both button wells, the file rows, existing arrows and CD emblems.

The exact scaled sprite geometry, indexed source, palette and load-arrow layout identify the panels. Each native rail must match the winning sprite and the 31:1 interpolation with its captured lower VDP2 layer. The replacement uses the same interpolation and updates its texture when the lower colors change.

Three natural 1440p replays on English discs 1 and 2 and Spanish disc 1 matched 56 strict guest fields and final SRAM each. Independent reconstruction matched all twelve RGB captures, with 91,008 changed pixels per capture. Original and the missing, corrupted and disabled donor controls matched. The separate release crosscheck kept both Iris/Ogami HD poses, WINDOW timed LIPS and dialogue, and the Long Day room choice exact.

Local receipts are in `local/work/codex-witness-441-review/hud/load-rails-ab/receipt.json` and `local/work/codex-witness-441-review/hud/load-rails-release-gate/receipt.json`. Package inclusion remains open.
