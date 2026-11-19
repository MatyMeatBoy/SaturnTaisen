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
| Battle bar (the 13 scenarios: WKL01, 02-11, 21, 22) | `SAKURA2/WKL##.BIN`, block 0 of the "battle menu" section, uncompressed 4 bpp sprites, 28 pieces of 16/24×16px | Address computed per file with the `WklBattleMenuExtractor` algorithm (`local/research/noahsteam-repo/SakuraTaisen/SakuraTaisen.cpp`): u32 at `+0xE8` → block table → 16-byte image headers of block 0 (offset/offset_prev/width/height). All 28 pieces are words (no icons; `*` = highlighted variant, fill index 12 instead of 1). They are composed with the bar's own condensed pixel font (letters read from the English sprites; 1 px strokes, 1 empty column between letters, 4-connected 1 px outline index 3; P/F/u/q/`.` derived): `pixel_word` in `tools/es/menus_es.py` reproduces 26 of the 28 English sprites pixel for pixel (only the two 16 px `Spcl` differ; they use another hand-drawn S). The earlier CENTURY.TTF 9 pt binarised redraw was unreadable. Verified byte for byte: the same algorithm reproduces the offset found by hand for WKL01 (`0x339A8`), and all 13 headers give the same width/height per sprite with identical English content. |

Menu text rules: same typeface as English (Century for the serif, condensed Georgia Bold for the title); four ink levels [1, 5, 9, 13] so every string fits; if a word needs to be compressed below 85%, its abbreviation is used ("Cancel.", "Habl.", "Cop.", "Bor.").

## HD text with Spanish

Resolved by construction, with no code changes: `local/deps/satrecomp/port/glyph_text.h` (`DecodeCodepoint`) recognizes the whole CP1252 range (32-126 and 128-255, with the 0x80-0x9F punctuation table that includes `…`=0x85), not just ASCII — so á/é/í/ó/ú/ñ/¿/¡ get the same HD treatment as any English letter. The condition is that the glyph atlas matches the `KnownEnglishAtlas` fingerprint (0xA6A05DFF441E0C60); the Spanish patch never replaces the `NNNNKNJ.BIN` files (font), only `TBL`/`MES` tables and menu strips — confirmed in `tools/es/iso.py::build`, which only replaces what it explicitly receives. The font arrives intact, byte for byte identical to the English patch.

## Tests

- `tests/test_es_herramientas.py`: round-trip LZ, synthetic tables and battle data, and exact reconstruction of every table on the owner's disc if available.
- `tests/test_es_output_safety.py`: tests ISO bounds, atomic writes, and preservation of discs, states, and input profiles with synthetic data.
- `tools/es/parchear_estado.py`: applies the Spanish data to an English savestate's RAM/VRAM to review a menu in seconds; it does not replace a real boot.
- Verified in the runtime (strict AOT, 0 interpreted): prologue and the meeting with Sakura in Spanish from the Spanish ISO, chapter 1 battle in Spanish, title and loading screen from cold boot; interlude and options via patched states.

## Spanish in the launcher (v0.2.2-alpha)

The player never builds a disc by hand. The release ships the language as **layers of differences** in `parches/`, and `preparar-juego.exe` (`tools/taisen_setup.py`) applies them on the player's PC:

| Layer | From → to | Size (disc 1 + 2) |
| --- | --- | --- |
| Inglés v0.1 Taisen | original Japanese data track → English base | 4.0 + 4.1 MB |
| Español v0.1 Taisen | English base → Spanish | 0.58 + 0.58 MB |
| Subtitled videos (optional) | original `/SAKURA4` → the subtitled container, in place | 101 + 123 MB |

- The English base is the English translation v2.1 repackaged for this port: identical to it except that `/SAKURA4` (the FILM video container) keeps the original bytes. With the video layer the prepared disc is byte for byte the v2.1 one.
- The Spanish layer is encoded between images whose `/SAKURA4` extent is zero-filled and the video bytes are copied back afterwards, so it applies to an English disc with either container. A player's own English v2.1 disc is therefore a valid starting point, and a later release can rebuild only the Spanish disc from the English one already prepared.
- A disc is identified by the SHA-256 of its data track, whatever its container (`.cue` with one or two files, a single `.bin`/`.img`, a plain `.iso`, a folder or a `.zip`). `parches/parches.json` pins every input and output; a step whose hash differs stops with a message.
- `tools/build_taisen_patches.py` regenerates the layers from the owner's prepared discs (`local/prepared/japanese-discN`, `discN`, `discN-es`) and verifies each by decoding it again. The owner pipeline below (`construir_todo.py`) still produces those reference discs.
- Language is a switch on the launcher's home page (Español / English): it points `launcher.ini` at `game/disc1-es` or `game/disc1` and takes effect at once. `tools/es/perfil_es.py` and the "Jugar en español" shortcut remain only as owner conveniences.
- The public release still never includes a disc: the layers contain differences only and are useless without the player's own discs.

## All chapters, both discs

- `tools/es/volcar_todo.py --disc 1|2` replaces every `NNNNTBL.BIN` (and every `M##MES.BIN` that has batches) of a prepared English disc. Translations are looked up per chapter (first two digits of the table id) by English text. `capituloN/overrides.jsonl` (`{"id": "TTTT-iiii", "es": "..."}`) translates one record regardless of its English text: needed where identical English hides different Japanese speakers or registers (`yes, sir` said with はっ/はい, polite vs plain, Kansai). Batches without a `.out.jsonl` are skipped with a warning.
- `tools/es/construir_todo.py --disc N` = `volcar_todo` + (disc 1) `menus_es` + `iso.py`, output `local/prepared/discN-es`. The disc-2 `SAKURA` program (392,024 bytes vs 391,712) and `LOGO.SH2` differ from disc 1, so `tools/es/menus_disco2.py` does not reuse the offsets: it takes every range the disc-1 menu patch changed and finds the same original bytes (with context) in the disc-2 file; the `SAKURA` data is shifted by 0x138 and the one patch that writes absolute pointers (load/save string table) moves them by the same amount. `ICATALL.DAT`, `OMALL.DAT`, `TITLE1.BIN`, `LOAD.BIN` and `WKL01.BIN` are byte-identical on both discs and reuse the disc-1 Spanish files; the 13 disc-2-only battle bars (`WKL12-20`, `WKL23-26`) are redrawn with the disc-1 routine. All 7 `SAKURA` ranges and 5 `LOGO.SH2` ranges resolved uniquely. Verified byte-wise only; the disc-2 menus still need an in-game look.
- Fixed slots keep every LBA stable across rebuilds, so savestates from a Spanish build stay valid. Battle batches use `capituloN/lotes/lote90` (N = the M## scenario number).

## Review lessons (what the full pass taught)

These rules come from reviewing all ten chapters against the reconstructed Japanese; the script itself stays private.

- **Japanese is the authority.** English adds or drops honorifics (`ma'am`, `sir`, `Chief`) and flattens speaker and register. Speaker, tú/usted, gender and tone are decided from the Japanese (`tools/es/leer_japones.py TABLE FROM TO [disc]`, with romaji for reviewers who do not read it); a per-character style table is only a starting point. A bulk pass that applied the table without reading the Japanese had to be redone for Ayame (she addresses Ogami as 大神くん with commands like しなさい, i.e. familiar), Sakura and the staff.
- **Terms are decided by context and Japanese, not by the English word.** 帝国歌劇団 (the theater company) and 帝国華撃団 (the military unit) are both "Assault Troupe" in English; Spanish keeps them apart ("de Ópera" / "de Asalto"). "Revista" reads as a magazine in Spanish and is not used.
- **Identical English can hide different Japanese.** Batches deduplicate by English text, so `tools/es/dedup_riesgo.py` lists the groups whose Japanese differs in register or speaker; those are resolved with per-record overrides (see above).
- **Jokes are recreated, not translated.** Puns, misunderstandings and dialect jokes are re-built in Spanish with the scene context (e.g. a mix-up between two similar words becomes an equivalent Spanish pair); a literal rendering that no longer makes a joke is treated as an error.
- **Mechanical checks** (`tools/es/auditar_todo.py`): missing/duplicate ids, altered markers, `\n` literal, non-CP1252 characters, unopened `¿`/`¡`, vosotros/voseo, lost digits. `tools/es/verificar_iso_es.py N` re-reads a built disc and checks every table against the English one (same record ids, markers intact, share of changed texts).
- **Neutral Spanish** (`ustedes`, no voseo, no regionalisms from Spain or Latin America) with character voices kept constant; Spanish text is longer than English, so the 30×4 limit forces condensing without losing sense or tone.

## Pending

Episode label (`TITLE1.BIN`) and LOADING screen, the extra menu (`OMALL.DAT`), video subtitles in Spanish, HD text review with Spanish beyond chapter 1, and in-game play of chapters 3–6, 9 and 10 (verified on the built image only). The launcher language option is done (v0.2.2-alpha).

**Japanese available**: the raw dump of the Japanese disc (.cue/.bin) is indeed on the owner's machine; it was prepared with `tools/prepare_discs.py --original` into `local/prepared/japanese-disc1` and `-disc2`. Japanese-based review is no longer blocked.

**Chapter 2**: 1,775 unique texts (6 batches, `0201TBL.BIN`-`0206TBL.BIN`) translated and validated. 125 new glyphs transcribed (`glifos_nuevos.py`), `japones.json` rebuilt (2,692 records, 1.3% uncertain, matching chapter 1's 1.2% with `japones.py`). Japanese → English → Spanish review: batch01 fully reviewed line by line (2 real corrections); batches 02-06 only had an automatic sweep for numeric divergences, no human read yet. The script lives only in `local/work/guion-es/capitulo2` (never pushed) with its own `ESTADO.md`; do not treat it as finished until that review is complete.

**Chapter 3**: in progress, 3 of 7 batches (990 of 2,060 texts) translated and validated from English, no Japanese-based review yet.

Investigated and shelved for now (don't retry without what's missing):

- **Episode / LOADING**: `draw_vdp2_screen` (see `decodificar.py`) confirms these are VDP2 screens of 8×8 8-bpp cells with a 40×28 map — not tile text strips. The "LOADING"/"Episode N: ..." label is hand-painted, in the same style as the background (petals, the 「サクラ大戦」 watermark); redrawing it with a TTF font would clash with the art, and the label's cells might be shared with the background (unverified), risking corruption of other screen areas. Missing: confirm which cells belong exclusively to the label before touching anything, or obtain hand-painted art in the same style.
- **OMALL.DAT**: the 271 DTE pair tiles (`omake_textos_1000`/`_79000`) have no pointer table within the file itself — the LZ streams at 0x0/0x3000/0x3800, once decoded, are frame graphics (nibble patterns typical of borders), not index lists. The table referencing those pairs (equivalent to `SAKURA`+0x5A09E..0x5A34A from `carga()`) lives in another file at a load address that isn't documented. Starting point to pick this back up: `local/deps/satrecomp/tools/sh2dis.py` (SH-2 disassembler already included in the repo) on `SAKURA` loaded at `0x06004000` — the string `"OMALL.DAT"` lives at `SAKURA`+0xFD60 (address `0x06013D60`), referenced from the literal pool at 4 points (`0xFE88`, `0xFFA4`, `0x10074`, `0x10174`). The first one (`0x06013DFE`) loads that address into `r5` right before a call to `0x06008AF4`; a few instructions below there's a call to `0x0600704C` with `r4=0x060E0000` (possible destination buffer in work RAM) and `r5=0x25F00C00` (possible VDP1 VRAM). Those two calls still need to be traced (they are library routines reused in several places, not specific to OMALL) to confirm which one reads the file and where its pointer table ends up, before the extra menu can be translated.
  Additional data point: `local/research/noahsteam-repo/SakuraTaisen/SakuraTaisen.cpp` (tools from the English translation team, source for `docs/research/sakura-engine-notes.md`) extracts `OMAKE01-03/11-13.BIN` as full-screen images (same as `TITLE#.BIN`/`LOAD.BIN`, tile offset 0x1380), and **does not mention `OMALL.DAT` or any extra menu text at all** — the reference English patch didn't translate this menu either. It isn't just low priority per `AGENTS.md`: there is also no precedent that it has ever been solved.

## Episode title cards (draft, 2026-11-19)

`SAKURA1/TITLE1..10.BIN` are the episode cards (320x224, English lettering painted in; layout in [saturn-bg-format.md](saturn-bg-format.md)). `tools/es/portadas_es.py` drafts them in Spanish: it finds the lettering as the palette indices used only inside the text zone, fills the sky behind it by diffusion, draws the Spanish lines in the card's own fill and outline colours (Arial Rounded Bold; the original lettering is a different, hand-made face) and rewrites only the cells under the text to the nearest palette colour, so each file keeps its size, palette and cell table (`tests/test_portadas_es.py`). Output goes to `local/work/guion-es/builds/es-portadas` (never to Git: it derives from game art) and `construir_todo.py --disc 1 --portadas` puts the ten files into the Spanish disc.

Known limits: some cards keep a faint smudge where the English lettering was, the outline colours of cards 3, 4 and 9 are a best guess, and the Spanish titles are drafts to review (they follow `CARGA_ES` in `menus_es.py` where it has them). The owner asked for generative art for these cards, so this is a fallback to compare against, off by default, and the launcher's language layers do not include it yet.

## LOADING scroll (draft, 2026-11-19)

`SAKURA1/LOAD.BIN` is a 320x224 picture with the dark logo pattern and a vertical brush-lettered scroll ("LOADING") in a double red frame (x 131-187, y 8-215). `tools/es/carga_es.py` clears the frame interior and draws "CARGANDO" one letter per row in Ink Free, white with a soft edge, rewriting only the cells under the interior to the nearest palette colour (size, palette and cell table are kept; `tests/test_portadas_es.py`). Output next to the episode cards in `local/work/guion-es/builds/es-portadas/SAKURA1/LOAD.BIN`; `construir_todo.py --disc 1 --portadas` puts it on the disc. It is a draft of the lettering (thinner and tidier than the original brush strokes), off by default, and not in the language layers yet.

## Episode cards and LOADING in the Spanish layer (2026-11-19)

The drafted Spanish episode cards (`tools/es/portadas_es.py`) and the "CARGANDO" scroll (`tools/es/carga_es.py`) are now part of the Spanish disc 1: it was rebuilt with `python -X utf8 tools/es/construir_todo.py --disc 1 --portadas` (3 minutes; the eleven files keep their size, palette and cell table) and the layers were regenerated with `tools/build_taisen_patches.py` (7 minutes with xdelta3; the English layers and the Spanish disc-2 layer came out byte-identical, only `parches/espanol-v0.1-disc1.xdelta` changed, 584,930 to 676,258 bytes, and `parches.json` has its new checksums). The setup helper therefore builds Spanish discs with the cards and the scroll; the 16:9 widening of the cards works on them as on the English ones (same layer and fingerprints).

They are program-made drafts (Arial Rounded Bold and Ink Free, not the hand-made lettering); the owner asked for generative art, which would replace them (rebuild the discs and the layers as above). `--portadas` stays an option of `construir_todo.py`; regenerate the layers whenever the cards change. The video layers (`videos-*.xdelta`, over 100 MB) were rebuilt unchanged and are release assets, not in Git.

### Spanish draft cards in game (T107a)

The ten TITLE files in the prepared Spanish disc 1 are byte-identical to the
drafts from portadas_es.py and differ from the English files in their picture
cells. verificar_portadas.py reported OK for all ten: each keeps its size,
palette, cell table and fingerprint.

Replayed chapter1-title-new-game.movie from intro-enhanced/title-final.state
on the Spanish disc, in separate hidden profiles at 1920×1080. The runtime
SHA-256 was cc7fa58737c37075efaea76a72cbe390454d21847ebadf1ca1b030e75ac046c2.
Original and Enhanced produced 6,400 identical per-frame guest hashes and zero
interpreted blocks. At screenshot pass 6200 the Spanish Episode 1 lettering is
visible in both modes, and Enhanced fills the surrounding window from the card
edges. The draft still shows banding on the right edge and retains its draft
lettering. The other nine cards were verified on disc only. This run used an
existing executable and disc, and did not create a package.
