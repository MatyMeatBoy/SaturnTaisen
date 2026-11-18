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
