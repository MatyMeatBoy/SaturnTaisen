# THD21: routes to the menu screens and what each one draws

Answers the open question of PR #709 (which layer draws each menu when it is open) for the screens reachable from the title with normal
inputs. Runtime: `sakura-full2` (stack of PR #691, AOT, copied with its `art/`), hidden window, `--unthrottled`, fresh cold boot of disc 1
(and disc 2 for one case), 1280x720 captures read by eye after each short stretch. Every run ended strict-native with 0 interpreted
blocks. Inputs are `tests/*.movie` lines (`frame buttons buttons2`; frame counted from power-on). Bits confirmed in these runs: Start 0800,
A 0400 (confirm), down 2000, right 8000. Hold each press at least 5 frames (8 for cursors) and leave 40-100 frames between moves.
Machine data: [config/hd-menu-state-evidence.json](../../config/hd-menu-state-evidence.json), written by `tools/menu_state_probe.py`
(palette fingerprints are FNV-1a 64 of the CRAM bytes the sprite command points at; VDP2 registers read from the state).

## Routes

Fresh backup RAM gives a two-entry Program menu (New Game, Options). The Continue entry and the load screens need a backup with saves:
the case "save" below uses the chapter-sweep seed `bank-3-battle-1` on disc 1 and `bank-10-battle-1` on disc 2 (local, never committed).

| Case | Frame | Input | What is seen |
| --- | --- | --- | --- |
| title | 0-650 | none | black, translation credits, pink intro text, opening film |
| title | 650 | Start | skips the film; the title logo builds up (1100-1800) and settles with the copyright lines, "Press Start Button" blinks |
| program | 2200 | Start | Program frame opens: New Game, (Continue), Options |
| options | 2320 | down | cursor on Options |
| options | 2420 | A | Options panel: Cursor Speed, Sound, Voice, Controls, Exit; cursor on Cursor Speed |
| options-controls | 2600, 2650, 2700 | down x3 (8 frames each) | cursor on Controls |
| options-controls | 2800 | A | blue binding panel: A Ok, B Cancel, C Ok, X Y Z L R No Setting, Exit |
| program (save) | 2699 | down | cursor on Continue |
| load | 2899 | A | "Data to load": three files, CD-1 disc icons, console icon, Copy and Del buttons; file 1 selected |
| load (disc 2) | same | same | the icons read CD-2 and the files "Finale / Final Judgement" |
| load-confirm | 4198 | A | adds the "Load?" line with Yes and No, Yes selected |
| loading | 6197 | A | fade to black, then the LOADING screen with the rail of Japanese title tiles (visible at 6400) |
| copy-select | 3400, 3450, 3500, 3560 | down x4 (8 frames each) | cursor on file 3, then Copy/Del row |
| copy-select | 3640 | right | Copy highlighted; one more right highlights Del |
| delete-select | 3720 | A on Del | header changes to "Data to delete", file 1 selected |

## What draws each screen

| Screen | Layer | Detail |
| --- | --- | --- |
| title | VDP1 sprites over VDP2 NBG3 (the pink floral backdrop) | logo pieces are 8-bit sprites (112x136, 96x96, 152x56, 64x80 twice, 24x24) that share one 256-colour palette (fingerprint DC1F1B06C3693D3E); the copyright line is a 4-bit 168x24 sprite |
| program | same | one 208x152 frame sprite (palette EB0E8FBCD10F6A6A) plus 16x16 tiles with two 16-colour palettes (A34A4A3675D9F164 selected-off, D5E6859F7CCE70F2 selected) |
| options | same | one 288x144 frame sprite (texture 3B1D76464A70DBA4, palette 809F8438D9925B74) plus about 50 16x16 and 8x16 text/rail tiles |
| options-controls | same | adds the blue panel pieces (more sprites, same two tile palettes) |
| load, copy, delete, confirm | same | 288x184 body (texture 621BD33F6CF0DACA), 176x24 header, 144x32 or 144x24 prompt, four 40x40 disc/console icons with palette 52C0DBB1EA90290A; text drawn as 16x16 tiles |
| loading | VDP2 only: NBG0, NBG1, NBG2, NBG3 on, no sprite, colour offset on | no VDP1 witness; any HD substitute would need a VDP2 layer recogniser |

So every menu frame that is open to HD is a VDP1 sprite with a stable texture hash and a palette fingerprint: the per-screen texture
and palette are in the JSON. The title logo pieces and the disc icons (palette 52C0DBB1EA90290A) can be keyed the same way as
FONT_CSL and the object cards.

## Not reached

* The extra (omake) menu (KARAOKE, OMKMOV_W, OMKSND_W, MINISAKU, MSTAFF): the title offers no entry on a save without the unlock; it needs
  a backup with the extra content unlocked. Missing: that backup (owner of the saves).
* SEGALOGO, REDLOGO and CAUTION: the Saturn boot of this disc shows black, the translation credits and the intro text only; those PC
  screens have no native counterpart in a cold boot. NOWLOAD corresponds to the LOADING screen above (VDP2 only).
* JYOUKI (steam) and the save-slot screen with game data written from inside a chapter (Save): not reached here.

## Pairing against the PC SYSTEM files (follow-up, offline)

The PC `SAKURA1/SYSTEM/**/*.SPR` files (SISTEM, OPTION, WINDOW, SIS_ICON, ICON, ... 287 images without KAO) are now extracted from the
private MDF into `local/work/pc-cab/out-system` (read-only, never committed). `python tools/hd_system_menu_pairs.py` decodes them with
`tools/decode_spred.py`, decodes the 165 distinct VDP1 textures of the eight saved menu states (title, program, options, controls, load,
confirm, load disc 2, loading) with their CRAM bank, and pairs by 32x32 luminance plus gradient signature (lower of the two
correlations, firm at 0.90 with a 0.05 margin and a compatible aspect). Data: `config/hd-system-menu-pairs.json` (names, sizes, hashes,
scores; no pixels).

Result: 5 firm pairs, all exactly 2x and all already wired by shipped patches (SISTEM 11 = 0205, 12 = 0209, 1 and 4 = 0206, 2 = 0213),
so the measurement independently confirms those patches and yields **no new group connectable by a table row**. 2 ambiguous: the 208x152
Program frame against OP_WIN 0 (0.81, kept native by decision) and one 40x40 console/disc icon against SIS_ICON 1 (0.78; the other
three 40x40 icons score 0.73-0.74 against a runner-up within 0.01-0.02: SIS_ICON is a family of near-identical emblems, they need the
palette of each disc slot, not content). 158 Saturn textures have no counterpart: the 288x184 load body and the title logo pieces
(new PC art or baked Japanese lettering), and the 16x16 and 8x16 text tiles (the translated text is drawn from tiles, no PC picture). Of
the PC side, 280 images have no Saturn witness in these states: reasons per file are in the JSON (keep native R_HARI, SHADE_WA/WB, OP_WIN,
HARI/LIPS; no Saturn draw for SEGALOGO, REDLOGO, CAUTION, TITLE, TL_*, NOWLOAD (VDP2 only), the extra menu and JYOUKI).

## Not done in this PR

No runtime patch: nothing firm and unwired was found, so nothing was built or replayed. Missing states, owner of the saves: the extra
menu (needs an unlocked backup), a save-slot screen with game data, and the discs 3 and 4 slot emblems. The three coverage deltas are
zero (attributed 0, integrated 0, verified 0).
