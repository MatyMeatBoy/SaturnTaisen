# PC asset census (counts only)

Header-level census of the PC dump's InstallShield cabinet (read-only listing of 7,116 files; no assets are copied, imported or mapped). It sizes the HD categories that were still unmeasured. Source: the owner's private `SAKURA.mdf`, listed with `local/work/pc-cab/iscab.py` (listing mode).

SPR image containers by folder:

| Folder | SPR files | HD category |
| --- | --- | --- |
| SAKURA1/BG | 716 | Scene images |
| SAKURA2/BG | 50 | Scene images |
| SAKURA2/EVENT | 235 | Scene images |
| SAKURA3/CG | 222 | Scene images |
| SAKURA1/ENDING | 13 | Scene images |
| SAKURA1/TITLE | 10 | Scene images |
| SAKURA1/ICATCH | 21 | Scene images (eyecatch) |
| SAKURA2/UNIT | 291 | Tactical mode |
| SAKURA2/MAP | 177 | Tactical mode |
| SAKURA1/MAP | 17 | Tactical mode |
| SAKURA1/ITEM | 57 | Tactical mode |
| SAKURA1/SYSTEM, SAKURA2/SYSTEM | 40 + 19 | HUD and menus |
| SAKURA1/NC, SAKURA3/NC | 147 + 19 | Large NC characters |
| SAKURA1/WALL | 25 | Decorative backgrounds (KABE, 19 themes used) |

Other content: 4,589 WAV files (4,060 voice, 458 SE, 35 BGM, 36 system) and 141 MAP DAT, 27 MAP TAB/BIN and 27 MACRO BIN tactical data files.

Scene images total 1,267 SPR files and tactical mode 542. These are candidates by file count, not approved pairs: a file can hold several images and several Saturn scenes can share one.

## Name links to Saturn files

Stem match between PC SPR names and Saturn disc files (`pc-saturn-name-links.json`; candidates, not approved pairs): SAKURA1/BG 712 of 716, SAKURA2/BG 37 of 50, SAKURA1/TITLE 10 of 10, SAKURA1/NC 147 of 147, SAKURA3/NC 19 of 19, SAKURA1/MAP 16 of 17, SAKURA1/ITEM 42 of 57, SAKURA1/ICATCH 10 of 21. No name link: SAKURA1/ENDING, SAKURA2/EVENT, SAKURA3/CG, SAKURA2/MAP, SAKURA2/UNIT and almost all SYSTEM files; those need pixel or index matching. A name link still requires decoding both images and checking the layout before it counts as matched.

### Caveat on BG name links (probe, 2026-11-18)

`/SAKURA1/BG1001.BIN` (45,120 bytes, disc 1) starts `00 01 00 01` followed by zeros and has high byte entropy (256 distinct values). It does not decode as a linear 8 bpp bitmap (widths 256/288/320), as 8x8 4 bpp cells (offsets 0, 0x20, 0x40, 0x100), or with the game's LZ (`tools/es/red_lz.py`, starts 0/4/8/16). The PC counterpart `BG1001.SPR` is a 231 KB SPRED image. Until the Saturn BG format is decoded, treat the 712 name links as unverified candidates; the name may be shared by unrelated data. Next step: find which routine loads `BG*.BIN` (trace the SH-2 program) and decode it, then compare with the PC image.

The Saturn `NC10.BIN` (104,528 bytes, all NC files share that size) starts `00 02` followed by a small table, then dense data; it does not decode as a plain bitmap or with `red_lz` at offsets 0-0x3e. Same next step: trace the loader.

### PC SPRED decoder

`tools/decode_spred.py` (ported from patch 0013) decodes any PC `.SPR` to PNG for local comparison; verified on `SAKURA1/BG/BG1001.SPR` (the theatre lobby, 576x320). The Saturn `BG1001.BIN` is not the same LZ ring format (decoded output is noise at start offsets 0-0x20). Decoded PNGs are the owner's assets: keep them under `local/`.
