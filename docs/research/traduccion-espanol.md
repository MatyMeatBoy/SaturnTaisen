# Spanish translation (T25)

First goal: all menus and chapter 1. The tools live in `tools/es/`; the script, the batches, the reconstructed Japanese, and the generated files remain in `local/work/guion-es` and are never pushed. `SAKURA_OWNER_ROOT` points to the copy that contains `local/` (same convention as the runtime tests).

## Translation method

1. **Reconstructed Japanese**: the Japanese tables `NNNNTBL.BIN` store 16-bit codes (`0` end, `0x0A0D` line break, `c` = glyph `c-1` from `NNNNKNJ.BIN`, 16×16 at 4 bpp). Glyphs are identified by MD5 and transcribed once by hand; `tools/es/japones.py` regenerates the script aligned with the English version (same IDs and record count). Chapter 1: 3,971 records, 1.2% uncertain glyphs. Battles (`SAKURA2/M##MES.BIN` + `.FNT`) use the same scheme.
2. **English v2.1** as the reference adaptation, human-reviewed.
3. **Spanish**: neutral (ustedes, no voseo); slight Spain-leaning turn of phrase only if it improves the idiom. Steps: batch translation (~330 unique texts in script order), line-by-line review Japanese → English → Spanish, term and register unification in the private style guide, validation (`tools/es/validar_lote.py`). In chapter 1, the Japanese-based review changed between 25% and 70% of lines per batch and fixed English errors (休演日 = day with no performance, 大将 = army general, 人を呼びますわよ = "I'll call someone", Kohran's Osaka dialect, the 舞台/部隊 pun resolved with "company").
4. **Per-chapter batch extraction**: `tools/es/lotes.py --tables 02XX... --out capitulo2/lotes` generates a chapter's batches from the already-existing English dialogue catalog (`local/work/dialogue-catalog-worker/dialogue.jsonl`, covering the whole game), filtering out the `NNNNTBL:idx` markers (not translated, resolved by the engine at runtime). `tools/es/validar_lote.py loteNN --capitulo capitulo2` validates any chapter, not just the first.

## Dialogue and battle

- English-patch fonts: full CP1252 with accents (dialogue 16×16; battle 8×12, 255 glyphs). No need to draw glyphs.
- Limit: 30 characters × 4 lines. Automatic wrapping; only LIPS and choice menus carry explicit line breaks.
- `tools/es/tablas.py`: header `>II`, entries `>II` (id, offset), record `>HH` + CP1252 text, even, ending in `00 00`, lip-sync vowel footer intact. Reproduces the 56 English tables byte for byte.
- `tools/es/combate.py`: text in 16-bit CP1252 words, line break `0x0A0D`; reproduces the 13 tables byte for byte.
- `tools/es/iso.py`: copies the prepared English ISO and moves all `*TBL.BIN` and `*MES.BIN` files to fixed 128 KiB slots at the end; the other files are replaced in place with the same size. LBAs don't change between builds, so savestates from a Spanish ISO remain valid. The game locates files via the ISO directory (the English patch already rebuilt the image).
- A savestate contains the already-loaded table: to see new text you must start from a state prior to that load.

## Menus

Custom LZ compression (SH-2 routine `0x0600A164`), implemented in `tools/es/red_lz.py` and verified against all known streams. When reinserting, a stream can only occupy its original length plus the zero padding that already followed it: palettes or tables usually sit behind it.

| Screen | Data | Placement |
| --- | --- | --- |
| Title (Program) | `LOGO.SH2`+0xFF20, 16×16 4 bpp tiles | Piece groups `x,-8,16,16,char` in `LOGO.SH2`+0x6086 (pointers at +0x6234, counters `08 05 08 07 07 08`); each piece points to any tile. |
| Title labels | 8 bpp frame `LOGO.SH2`+0x10808; "Press Start" 4 bpp at `+0x25410`+81760 | Painted: recomposed with the letters from the English patch itself (d = flipped b; s drawn the same). |
| Interlude | `ICATALL.DAT`+0x2800 | Fixed-length tile lists (5, 5, 6) in `SAKURA`+0x5F5C8. |
| Options and controls | `SAKURA`+0x5B320 and +0x59878; frame +0x5AE38 | Piece tables in `SAKURA` (~0x59C70–0x5ACB0): each Spanish word is drawn on the same tiles as the English one. |
| Load/save | 8×16 pair font (DTE) `SAKURA`+0x5C654, 144 tiles | Base-1 tile strings ending in 0 at `SAKURA`+0x5A09E..0x5A34A, almost all with a pointer (`0x0605xxxx`, loaded at 0x06004000). Buttons use fixed ids: Copy [90,4,95], Del [102,41], Yes [34,6], No [95,133,95]. |
| Status (stats) | `ICATALL.DAT`+0x13800, 48 tiles (16×16 4 bpp) | Tiles 0-16: character names (not translated). 17-18 High, 20-21 Spirits!, 22-24 Normal, 25-26 Mood, 27-29 Terrible, 30-31 Atk, 32-33 Def, 34-35 Mov; the rest are `+ - 0-9`. |
| Load frame (File/System RAM) | `SAKURA`+0x5E190..0x5EB4C (288×184, 4 bpp) painted labels, not tiles | "File 1/2/3" in boxes (196,y,60,16) with y=40/80/120; "System RAM" at (2,162,108,16); same `rotulos.replace_text` as the "Options" tab. |
| Battle bar (the 13 scenarios: WKL01, 02-11, 21, 22) | `SAKURA2/WKL##.BIN`, block 0 of the "battle menu" section, uncompressed 4 bpp sprites, 28 pieces of 16/24×16px | Address computed per file with the `WklBattleMenuExtractor` algorithm (`local/research/noahsteam-repo/SakuraTaisen/SakuraTaisen.cpp`): u32 at `+0xE8` → block table → 16-byte image headers of block 0 (offset/offset_prev/width/height). 25 words (the last 3 are icons, untouched); CENTURY.TTF font at 9pt (the 15pt one used on other screens doesn't fit these cells), binarized to 2 tones (ink index 3, border 1). Verified byte for byte: the same algorithm reproduces the offset found by hand for WKL01 (`0x339A8`), and all 13 headers give the same width/height per sprite with identical English content. |

Menu text rules: same typeface as English (Century for the serif, condensed Georgia Bold for the title); four ink levels [1, 5, 9, 13] so every string fits; if a word needs to be compressed below 85%, its abbreviation is used ("Cancel.", "Habl.", "Cop.", "Bor.").

## HD text with Spanish

Resolved by construction, with no code changes: `local/deps/satrecomp/port/glyph_text.h` (`DecodeCodepoint`) recognizes the whole CP1252 range (32-126 and 128-255, with the 0x80-0x9F punctuation table that includes `…`=0x85), not just ASCII — so á/é/í/ó/ú/ñ/¿/¡ get the same HD treatment as any English letter. The condition is that the glyph atlas matches the `KnownEnglishAtlas` fingerprint (0xA6A05DFF441E0C60); the Spanish patch never replaces the `NNNNKNJ.BIN` files (font), only `TBL`/`MES` tables and menu strips — confirmed in `tools/es/iso.py::build`, which only replaces what it explicitly receives. The font arrives intact, byte for byte identical to the English patch.

## Tests

- `tests/test_es_herramientas.py`: round-trip LZ, synthetic tables and battle data, and exact reconstruction of every table on the owner's disc if available.
- `tests/test_es_output_safety.py`: tests ISO bounds, atomic writes, and preservation of discs, states, and input profiles with synthetic data.
- `tools/es/parchear_estado.py`: applies the Spanish data to an English savestate's RAM/VRAM to review a menu in seconds; it does not replace a real boot.
- Verified in the runtime (strict AOT, 0 interpreted): prologue and the meeting with Sakura in Spanish from the Spanish ISO, chapter 1 battle in Spanish, title and loading screen from cold boot; interlude and options via patched states.

## Spanish mode in the launcher

Already works without touching code: `tools/es/construir_disco_es.py` generates `local/prepared/disc1-es` and `tools/es/perfil_es.py` creates a separate profile (`local/profiles/espanol`, a copy of the base profile with `[game] disc=` pointing to the Spanish disc) and the local shortcut "Jugar en español.bat". Verified with the `v0.2-ch1-preview` build: the launcher boots the Spanish disc and the title shows "Pulsa Start".

The command-line tools store discs, test states, and profiles under `SAKURA_OWNER_ROOT/local`. The builder verifies the ISO in a temporary file before publishing the image. Repeating profile creation only updates `[game] disc` in the launcher's INI, keeping the profile's settings and saves. The Windows shortcut uses UTF-8 and supports paths with spaces and Unicode characters; for automated, time-bounded playbacks, run the runtime directly with `--disc`, `--settings`, and `--backup`.

Proposed integrated launcher option (dependency, requires coordinating SDK ownership):

- "Language: English / Español" selector on the disc card; saved to `launcher.ini` (`[game] language=es`).
- With `es`, `find_nearby` first tries `local/prepared/disc1-es/game.cue`, `game/disc1-es/game.cue`, and `disc1-es/game.cue`; if none exists, the selector appears disabled with the text "Falta el disco en español (tools/es/construir_disco_es.py)".
- `check_disc` accepts the Spanish disc: the game code is identical to the English one; only tables, menus, and the main program change, in data zones.
- Saves: the format doesn't change; sharing or separating folders is the owner's decision (the separate profile from `perfil_es.py` keeps them apart).
- The public release never includes the Spanish disc: it is a local owner output, just like the prepared English disc.

## Pending

Episode label (`TITLE1.BIN`) and LOADING screen, extra menu (`OMALL.DAT`), HD text review with Spanish, and the language option in the launcher. Chapters 2–10 follow the same method for the script.

**Japanese available**: the raw dump of the Japanese disc (.cue/.bin) is indeed on the owner's machine; it was prepared with `tools/prepare_discs.py --original` into `local/prepared/japanese-disc1` and `-disc2`. Japanese-based review is no longer blocked.

**Chapter 2**: 1,775 unique texts (6 batches, `0201TBL.BIN`-`0206TBL.BIN`) translated and validated. 125 new glyphs transcribed (`glifos_nuevos.py`), `japones.json` rebuilt (2,692 records, 1.3% uncertain, matching chapter 1's 1.2% with `japones.py`). Japanese → English → Spanish review: batch01 fully reviewed line by line (2 real corrections); batches 02-06 only had an automatic sweep for numeric divergences, no human read yet. The script lives only in `local/work/guion-es/capitulo2` (never pushed) with its own `ESTADO.md`; do not treat it as finished until that review is complete.

**Chapter 3**: in progress, 3 of 7 batches (990 of 2,060 texts) translated and validated from English, no Japanese-based review yet.

Investigated and shelved for now (don't retry without what's missing):

- **Episode / LOADING**: `draw_vdp2_screen` (see `decodificar.py`) confirms these are VDP2 screens of 8×8 8-bpp cells with a 40×28 map — not tile text strips. The "LOADING"/"Episode N: ..." label is hand-painted, in the same style as the background (petals, the 「サクラ大戦」 watermark); redrawing it with a TTF font would clash with the art, and the label's cells might be shared with the background (unverified), risking corruption of other screen areas. Missing: confirm which cells belong exclusively to the label before touching anything, or obtain hand-painted art in the same style.
- **OMALL.DAT**: the 271 DTE pair tiles (`omake_textos_1000`/`_79000`) have no pointer table within the file itself — the LZ streams at 0x0/0x3000/0x3800, once decoded, are frame graphics (nibble patterns typical of borders), not index lists. The table referencing those pairs (equivalent to `SAKURA`+0x5A09E..0x5A34A from `carga()`) lives in another file at a load address that isn't documented. Starting point to pick this back up: `local/deps/satrecomp/tools/sh2dis.py` (SH-2 disassembler already included in the repo) on `SAKURA` loaded at `0x06004000` — the string `"OMALL.DAT"` lives at `SAKURA`+0xFD60 (address `0x06013D60`), referenced from the literal pool at 4 points (`0xFE88`, `0xFFA4`, `0x10074`, `0x10174`). The first one (`0x06013DFE`) loads that address into `r5` right before a call to `0x06008AF4`; a few instructions below there's a call to `0x0600704C` with `r4=0x060E0000` (possible destination buffer in work RAM) and `r5=0x25F00C00` (possible VDP1 VRAM). Those two calls still need to be traced (they are library routines reused in several places, not specific to OMALL) to confirm which one reads the file and where its pointer table ends up, before the extra menu can be translated.
  Additional data point: `local/research/noahsteam-repo/SakuraTaisen/SakuraTaisen.cpp` (tools from the English translation team, source for `docs/research/sakura-engine-notes.md`) extracts `OMAKE01-03/11-13.BIN` as full-screen images (same as `TITLE#.BIN`/`LOAD.BIN`, tile offset 0x1380), and **does not mention `OMALL.DAT` or any extra menu text at all** — the reference English patch didn't translate this menu either. It isn't just low priority per `AGENTS.md`: there is also no precedent that it has ever been solved.
