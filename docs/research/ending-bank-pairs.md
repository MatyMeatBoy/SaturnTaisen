# Ending picture banks and PC counterparts

TP3c covers the seven `/SAKURA1/*_CG.BIN` ending banks. Both prepared English Saturn discs contain byte-identical copies of each bank. The PC files are `SAKURA1/ENDING/END_AI.SPR`, `END_GE.SPR`, `END_KA.SPR`, `END_KO.SPR`, `END_MA.SPR`, `END_SA.SPR` and `END_SU.SPR`.

A bank contains individual palettes, cell maps and 8-bit tile data. The current scene table accepts individual scene rectangles. The bank needs record selection and ending composition before it can use these PC subimages.

## Saturn layout

Each record starts with 256 big-endian RGB555 palette words followed by an identity table of big-endian 32-bit entries. Each entry equals twice the tile index. The tile data uses 8×8, 8-bit cells. General ending records start with tile zero. Heroine ending records start with tile one, so their stored tile data includes one unused 64-byte tile before the first visible cell. Splitting each bank at these record lengths consumes the entire file.

`GE_CG.BIN` is 306,688 bytes. Its four 76,672-byte records start at `0x0`, `0x12B80`, `0x25700` and `0x38280`. Each decodes to 320×224. PC `END_GE.SPR` subimages 0–3 match the four stages of the theatre and cast illustration. They include the scene's successive logo and final-mark variants.

Each heroine bank is 407,908 bytes and follows this layout.

| Record | Byte offset | Native size | Visible role in the decoded art |
| --- | --- | --- | --- |
| 0 | `0x00000` | 320×120 | Sepia theatre exterior |
| 1 | `0x0A1A0` | 320×120 | Color theatre exterior |
| 2 | `0x14340` | 112×120 | Small character illustration |
| 3 | `0x17D48` | 136×80 | Small character illustration |
| 4 | `0x1ACB0` | 88×80 | Small character illustration |
| 5 | `0x1CC28` | 88×104 | Small character illustration |
| 6 | `0x1F464` | 320×160 | Color cast photograph |
| 7 | `0x2CB24` | 320×160 | Sepia cast photograph |
| 8 | `0x3A1E4` | 320×160 | Route-specific close-up |
| 9 | `0x478A4` | 320×160 | Sepia theatre exterior with petals |
| 10 | `0x54F64` | 64×64 | Ending mark |
| 11 | `0x562A4` | 320×160 | Route-specific final illustration |

## Confirmed donor records and composition

[The ending bank map](../../config/hd-ending-bank-map.json) stores the four GE pairs and records 6 and 7 from each heroine bank. The color and sepia photographs have distinct palette and cell keys, each repeated across all six native banks. Their corresponding PC subimages are 6 and 7. The 16 entries represent seven inventory files and include the repeated photograph records. The catalog classifies all seven banks as `paired-not-wired`.

The GE pictures are whole-screen variants. The runtime needs the ending viewport, fade and overlay behavior before selecting one by its native key. The four small heroine records are art components with separate bounds. The remaining close-ups have corresponding motifs and different crops. Both groups need their native framing and layer evidence before replacement.

PC subimages 0, 1 and 9 depict a different view of the theatre exterior. The PC mark at subimage 11 has different geometry and lettering. The native exterior records and the native ending mark, including localized Fin variants, remain the display sources.

The comparison uses `decode_saturn_bg.py`'s row-major tile decode and `decode_spred.py`, with 32×16 grayscale signatures to rank PC candidates. The four GE variants and the two group photographs were reviewed side by side. The private full-file SHA checks, decoded contact sheets and per-record scores are in `local/work/codex-th1/tp3c-cg`.

## Observed Sakura ending on English disc 2

The archived `SakuraTaisen/Data/SaveData/Mednafen/GameCompleted.bkr` seed (SHA-256 `e981b37dd8f9111cbc1a6e9c3c564b6610978dbdc9ced59b73acbec1da9b1674`) provides a direct route. From the title select Continue, load slot 1 (`Finale / Final Judgement`), and advance the post-victory dialogue and Sakura epilogue with normal controller input. The run reaches the animated ending through ordinary game transitions. The separately unlocked Long Day menu is available from this seed.

The interpreter state at the aperture contains the complete 407,908-byte `SA_CG.BIN` at Low WRAM `00204000`. Its first 38,400 cell bytes are at VDP2 VRAM offset `0x8040`, and all 512 palette bytes match at CRAM offset `0x200`. The complete English disc-2 `ENDING.BIN` (178,968 bytes) is present at High WRAM `06080000`.

| Interpreter capture | Ending picture and observed composition | Exact native RGB match |
| --- | --- | --- |
| `ending-bank3`, frame 5,200 | `SA_CG` record 0 through a black-surround aperture. Source rectangle (57, 0, 264, 120), destination (57, 24, 264, 144). | 24,840 pixels |
| `ending-cg-live`, frame 1,440 | Unobstructed `SA_CG` record 1. Source rectangle (0, 0, 320, 120), destination (0, 24, 320, 144). | 38,400 pixels |

Rectangles use half-open bounds. The pixel comparison expands each native RGB555 channel with a left shift of three. Intermediate captures show separate character insets over the full-width theatre strip and separate credits text. A full-screen substitution cannot preserve these layers. The already-cataloged PC exterior art also uses a different framing. The two observed exterior records retain the original draw, and wiring for the group photographs and GE variants remains open.

The current strict build (`sakura.exe` SHA-256 `38bed813262e937e7cfe328b8ab2e3ec35aef280e4996675558465ccfbde300f`) completes a 20,164-frame cold replay from this seed through theatre narration before the CG bank loads. Resuming the exact aperture state under strict AOT then stops at master PC `06080104`, which is file offset `0x104` of the byte-matched `ENDING.BIN` at `06080000`. The earlier static model used `00204000` as an inferred candidate origin. The observed high-WRAM placement and execution site are recorded in the [ending module analysis](ending-module-analysis.json). The state, input movies, captured frames and hashes remain in `local/work/codex-th1`.
