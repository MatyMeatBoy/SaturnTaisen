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

[The ending bank map](../../config/hd-ending-bank-map.json) stores the four GE pairs and records 6, 7, 8 and 11 from each heroine bank. The color and sepia photographs have distinct palette and cell keys, each repeated across all six native banks. Their corresponding PC subimages are 6 and 7. The 28 entries represent seven inventory files and include the repeated photograph records. The catalog classifies all seven banks as `paired-not-wired`.

The GE pictures are whole-screen variants. The runtime needs the ending viewport, fade and overlay behavior before selecting one by its native key. The four small heroine records are art components with separate bounds. The small illustrations need per-record layout evidence. The close-ups and final illustrations have distinct redraws.

PC subimages 0, 1 and 9 depict a different view of the theatre exterior. The PC mark at subimage 11 has different geometry and lettering. The native exterior records and the native ending mark, including localized Fin variants, remain the display sources.

The comparison uses `decode_saturn_bg.py`'s row-major tile decode and `decode_spred.py`, with 32×16 grayscale signatures to rank PC candidates. The four GE variants and the two group photographs were reviewed side by side. The private full-file SHA checks, decoded contact sheets and per-record scores are in `local/work/codex-th1/tp3c-cg`.

## Route-specific portraits

Each of the six heroine banks pairs Saturn record 8 with PC subimage 8 and Saturn record 11 with PC subimage 10. All twelve matches rank first within their respective PC SPR and agree in character and composition. The catalog pins each 320×160 native record and its 640×320 PC donor. The PC redraws shift the background mullions, and the Sakura close-up changes the mouth. The native compositions remain in use.

The English disc 2 Sakura route displays record 11 at credits frame 2,880 and record 8 at frame 3,360. Both fill the same rectangle as the group photos, `(0,16,320,176)` in half-open bounds. Each capture matches all 51,200 native pixels. Those captures establish the layout for the two Sakura records. The other routes and the four GE variants still need composition witnesses.

## Observed Sakura ending on English disc 2

The archived `SakuraTaisen/Data/SaveData/Mednafen/GameCompleted.bkr` seed (SHA-256 `e981b37dd8f9111cbc1a6e9c3c564b6610978dbdc9ced59b73acbec1da9b1674`) provides a direct route. From the title select Continue, load slot 1 (`Finale / Final Judgement`), and advance the post-victory dialogue and Sakura epilogue with normal controller input. The run reaches the animated ending through ordinary game transitions. The separately unlocked Long Day menu is available from this seed.

The interpreter state at the aperture contains the complete 407,908-byte `SA_CG.BIN` at Low WRAM `00204000`. Its first 38,400 cell bytes are at VDP2 VRAM offset `0x8040`, and all 512 palette bytes match at CRAM offset `0x200`. The complete English disc-2 `ENDING.BIN` (178,968 bytes) is present at High WRAM `06080000`.

| Interpreter capture | Ending picture and observed composition | Exact native RGB match |
| --- | --- | --- |
| `ending-bank3`, frame 5,200 | `SA_CG` record 0 through a black-surround aperture. Source rectangle (57, 0, 264, 120), destination (57, 24, 264, 144). | 24,840 pixels |
| `ending-cg-live`, frame 1,440 | Unobstructed `SA_CG` record 1. Source rectangle (0, 0, 320, 120), destination (0, 24, 320, 144). | 38,400 pixels |

Rectangles use half-open bounds. The pixel comparison expands each native RGB555 channel with a left shift of three. Intermediate captures show separate character insets over the full-width theatre strip and separate credits text. A full-screen substitution cannot preserve these layers. The already-cataloged PC exterior art also uses a different framing. The two observed exterior records retain the original draw. The GE variants still need a live composition witness.

The earlier strict build (`sakura.exe` SHA-256 `38bed813262e937e7cfe328b8ab2e3ec35aef280e4996675558465ccfbde300f`) completes a 20,164-frame cold replay from this seed through theatre narration before the CG bank loads. Resuming the exact aperture state under strict AOT then stops at master PC `06080104`, which is file offset `0x104` of the byte-matched `ENDING.BIN` at `06080000`. The earlier static model used `00204000` as an inferred candidate origin. The observed high-WRAM placement and execution site are recorded in the [ending module analysis](ending-module-analysis.json). The state, input movies, captured frames and hashes remain in `local/work/codex-th1`.

## Verified color and sepia group photos

The Sakura ending displays records 6 and 7 at `(0,16,320,176)`. Frame 1,560 of the final credits continuation matches all 51,200 color pixels. Frame 2,400 matches all 51,200 sepia pixels. Each checkpoint retains the exact complete `SA_CG.BIN` in Low WRAM. The color tiles and palette match VDP2 VRAM `0x8040` and CRAM `0x200`. The sepia tiles and palette match VRAM `0x40040` and CRAM `0x400`. Each 640×320 PC photo decodes byte-identically from all six heroine counterparts. The renderer pins the size and hash of `END_SA.SPR` and selects subimages 6 or 7.

The Enhanced draw keeps the integer-scaled native frame and replaces the opaque photo rectangle after matching its captured palette bank, owner for every pixel, and full native RGB signature. Credits outside the rectangle keep their original pixels. The exact match also leaves intermediate fades, the separate localized `Fin`, and Original mode on their native paths.

The 2560×1440 A/B comparison changes exactly `(320,144,2240,1104)` for both photos. Every pixel in that rectangle matches the selected PC subimage at 3× nearest-neighbour scale. Original and missing-donor comparisons are exact. Seven transition captures confirm the change stays inside that rectangle, with four intermediate captures pixel-identical. Each of the five configurations per photo produces the same 135 guest hashes. The 920-frame transition A/B and the 1,200-frame disc-1 opening parity are also exact in guest hashes.

A private build appended 353 variants observed on this path and checked each variant's opcode bytes against the English disc-2 `ENDING.BIN` at `06080000`. Strict sections of 5,305 frames from the Sakura epilogue into the aperture and 18,605 frames from the aperture through `Fin` match the interpreter's guest hashes and SRAM. Six aperture-to-Fin pictures match exactly. These bounded sections verify the ending renderer with the private AOT candidate. The registry recipe below reproduces the tested addition. An isolated standard build is verified below. Shared runtime rollout and release packaging remain open. Private inputs, states, and captures remain under `local/work/codex-th1`.

## Rebuild the observed AOT coverage

Generate a local candidate database from the prepared English disc 2 data track and a local seed database:

```powershell
python tools/discover_registered_overlays.py --image "local/prepared/disc2/Track 01.iso" --module ENDING_DISC2_EN --seed-blocks local/work/sakura/blocks.txt --output local/work/ending-aot
```

The registry resolves `/SAKURA1/ENDING.BIN` from the ISO directory and checks its full size and SHA-256 before reading the 353 observed file offset and byte count pairs in `config/ending-aot-ranges.json`. Every emitted address is the observed High WRAM base `06080000` plus its file offset. This entry skips eager block discovery. The offsets and lengths are versioned. The opcode bytes, merged database, and build outputs remain local. Disc 1's distinct module is rejected.

Use the output `blocks.txt` as the seed for the existing SDK recompilation and build, with `--max-function-blocks 1` and a configured address range that includes `06080000` (the regular `06002000-08000000` range does). Keep the old seed and build separately. On the witnessed 674,182-variant seed, the merged count is 674,535. The LF-formatted sorted delta (`ADDRESS UPPERCASE_HEX` plus newline per entry) has SHA-256 `db6c0ee54437160f0ca8634ae6749917c8045d1732c8aa8e58364191d6a1939d`.

The public recipe recovered the same 353 variants and generated byte-identical C++ for the private strict candidate. Both natural photo checkpoints passed again in the combined renderer build. A 290-frame resume on localized `Fin` matched the interpreter in all guest hashes, two RGB captures, and SRAM. The scope is the observed English disc 2 Sakura ending. Other routes, a fresh campaign completion, and packaging are separate work.

### Build through the standard entry point

The ending registry feeds the standard `tools/build_runtime.py recompile` flow through its normal `local/work/sakura/blocks.txt` input. In a separate source layout, put the registry's merged database at that path and keep the original seed in its own location. Use a fresh SDK checkout with `core.autocrlf=false` on Windows so dependency validation sees the pinned bytes. From that layout, run:

```powershell
python tools/build_runtime.py recompile --toolchain C:/msys64/clang64
```

The normal recompile command validates the dependency patch stack, generates the native blocks, and links `local/build/sakura/sakura.exe`. The isolated trial used project commit `127c5ca` and the 674,535-variant merged seed. The trial kept its own SDK, block order, generated code, object files, and executable.

The build exited 0 after generating 674,535 native blocks with zero skipped. Its executable SHA-256 is `b08616243a4a89d14088b85cbdc5a6b9cdad56ce95c4b474d541088a320adba8`. Strict replay of both natural photo checkpoints verified the 2560×1440 replacement rectangle and exact Original and missing-donor fallbacks. A 290-frame `Fin` continuation matched the interpreter in guest hashes, both RGB captures, and SRAM. The disc-1 opening matched all 1,200 guest hashes and the title capture. The shared executable and release package are separate from this isolated build.

## Exact 0183 candidate verification

The IC06 development candidate at project commit `a3722eb` has executable
SHA-256 `d29a9f17ecf980d96e2673166c20985d7960a6a0ac191233ffd79baa60c26c0a`.
Its response file links the 353 ending blocks in table 1686 and the 94
later EVT04 blocks in table 1687. Executable extraction returned 674,629
unique address-and-byte rows. All 353 expected rows from the pinned English
disc 2 `ENDING.BIN` and `config/ending-aot-ranges.json` are present.

| Replay | Archived checkpoint | Length | Matched against archived interpreter |
| --- | --- | ---: | --- |
| Epilogue into aperture | `ending-bank2/end.state` | 5,305 frames | Every guest hash, SRAM, two native RGB captures |
| Aperture through Fin | `ending-bank3/end.state` | 18,605 frames | Every guest hash, SRAM, six native RGB captures including the visible Fin at frame 18,000 |

Both strict runs reported zero interpreted blocks. Their guest hash logs
have SHA-256 `218e67cedc3cf58931fdc51fd28f5a47e9f20328de11c2fa6f531617d05e4fc7`
and `0572b894e3187fd79be001a2ff16ff32046ed395cccdff1767c70c970b6edb71`,
respectively. A cold English disc 1 opening also matched all 1,200 hashes
and the native title capture against the archived strict baseline. The two
English disc 2 group photographs passed the 135-frame Enhanced, Original
and missing-donor controls at 1440p. Donor changes were confined to
`(320,144)–(2240,1104)` on both photographs, and all five modes per photo
matched in guest hashes.

For AOT membership, run the following from the project root with the
retained local candidate and prepared English disc 2. This checks the PE
executable's linked rows, with no compilation.

```powershell
$trial = Join-Path $PWD 'local/work/ending-0183-reproduction'
New-Item -ItemType Directory -Force $trial | Out-Null
$env:TAISEN_ENDING_LINKED_ROWS = Join-Path $trial 'linked-blocks.txt'
$candidate = Join-Path $PWD 'local/work/codex-th1/ic06-live/candidate.exe'
python tools/extract_blocks_from_exe.py $candidate $env:TAISEN_ENDING_LINKED_ROWS
@'
import hashlib, json, os, sys
from pathlib import Path
sys.path.insert(0, "tools")
from decode_saturn_bg import Iso
disc = Iso("local/prepared/disc2/Track 01.iso")
data = disc.content(disc.find("SAKURA1/ENDING.BIN"))
assert len(data) == 178968
assert hashlib.sha256(data).hexdigest() == "f85eff4cef05796bcbaedb29099795dcc9ebd61bf24d81d8fb819899eb4b1553"
ranges = json.loads(Path("config/ending-aot-ranges.json").read_text())
expected = {f"{0x06080000 + offset:08X} {data[offset:offset+size].hex().upper()}"
            for offset, size in ranges}
linked = set(Path(os.environ["TAISEN_ENDING_LINKED_ROWS"]).read_text().splitlines())
assert len(linked) == 674629 and len(expected) == 353 and expected <= linked
print("353 linked English disc 2 ending variants")
'@ | python -
```

For the replay, use a fresh output directory and copy the corresponding
checkpoint's `backup.bin` there before starting. All inputs below are
under `local/work/codex-th1/final-battle-probes`. Use
`ending-aot-entry-observe/input.movie` for the entry checkpoint and
`ending-aot-full-observe/input.movie` for the aperture checkpoint. Each
movie's directory also holds the interpreter hash log, final SRAM and
native RGB references.

```powershell
$saved = Join-Path $PWD 'local/work/codex-th1/final-battle-probes'
$disc = Join-Path $PWD 'local/prepared/disc2/game.cue'
$dlls = Join-Path $PWD 'local/releases/SaturnTaisen-v0.2.10-alpha-win64/data'
$env:PATH = "$dlls;$env:PATH"
$env:SATRECOMP_STRICT_NATIVE = '1'
foreach ($replay in @(
    @{ Seed = 'ending-bank2'; Ref = 'ending-aot-entry-observe'; Count = 5305; Interval = 2400 },
    @{ Seed = 'ending-bank3'; Ref = 'ending-aot-full-observe'; Count = 18605; Interval = 3000 }
)) {
    $seed = Join-Path $saved $replay.Seed
    $ref = Join-Path $saved $replay.Ref
    $out = Join-Path $trial $replay.Seed
    New-Item -ItemType Directory $out | Out-Null
    Copy-Item -LiteralPath "$seed/backup.bin" -Destination "$out/backup.bin"
    Push-Location $out
    try {
        & $candidate --headless --unthrottled --mute --stats --disc $disc `
          --frames $replay.Count --state-load "0:$seed/end.state" `
          --movie "$ref/input.movie" --backup "$out/backup.bin" `
          --hash-log "$out/frames.hash" --shot-every "$($replay.Interval):$out/shot-" `
          *> "$out/run.log"
        if ($LASTEXITCODE -ne 0) { throw "Strict replay failed" }
    } finally { Pop-Location }
    foreach ($file in @('frames.hash', 'backup.bin')) {
        if ((Get-FileHash "$out/$file").Hash -ne (Get-FileHash "$ref/$file").Hash) {
            throw "Replay mismatch in $file"
        }
    }
    Select-String -Path "$out/run.log" -Pattern 'interpreted 0 \('
}
```

Compare the matching `shot-*.png` files as decoded RGB. Private verification
records are in `local/work/codex-ending-0183`. This evidence covers the
specified 0183 candidate, these English checkpoints and the opening check.
Other heroine endings, a complete campaign and package inclusion remain
open.

## Composition model and wiring status per bank (TP3c pattern audit)

How the game composes an ending, from the documented captures: the backdrop is a VDP2 bitmap layer fed from one `*_CG.BIN` record (palette in CRAM, 8-bit cells in VRAM). The sepia and color group photographs use two different layers and palette banks (CRAM `0x200` and `0x400`) at the same `(0,16,320,176)` rectangle. Credit text, character insets and the localized `Fin` are separate layers drawn over or around that rectangle. The theatre strip records (0, 1, 9) occupy `(0,24,320,144)` or a black-surround aperture and are shared with moving insets. So only the record that fills an opaque, unobstructed rectangle can be replaced; patch 0137 already does that with the recogniser pattern of the scene pictures (palette fingerprint, layer ownership, native RGB signature, native fallback).

Measured from `config/hd-ending-bank-map.json` and patch 0137: the seven banks hold 76 records (4 GE + 6 x 12). Records 6 and 7 are byte-identical in the six heroine banks (same palette and cell fingerprints `A19A0B84409A3AB8`/`FCAFB7040FA7C5ED` and `BD98B23C7D99D3DD`/`F660240773226223`), so the single table of patch 0137 already covers 12 of the 72 heroine records with two keys and one donor (`END_SA.SPR`, subimages 6 and 7, donors decode identically in all six `END_*.SPR`). Records 8 and 11 are specific to each heroine. The initial audit kept their native presentation because the PC redraws change the framing and details. Records 0-5, 9 and 10 are strips, insets, petals and the Fin mark with different PC geometry. The four GE records are whole-screen variants with no composition witness.

That audit moved the six disc 2 banks away from a blanket `paired-not-wired`: disc 2 SA is `hd` (records 6 and 7 verified), disc 2 AI/KA/KO/MA/SU are `wired-unverified` (same keys, no replay of that route), disc 1 banks and GE stay `paired-not-wired` with a specific reason. The generator derives the keys from patch 0137, so the status cannot drift from the runtime.

The earlier pattern audit used the then-current 353-variant registry and had no accessible alternate route checkpoint.

What is missing and who does it:
- Owner (discs, natural play): continuation replays of the Kanna, Maria, Iris and Kohran endings through their unique photos.
- Owner or integration desk: a GE (theatre) ending witness with viewport and fade evidence; then a generated GE table keyed by the four palette fingerprints.
- Integration desk: a disc-1 decision (distinct ENDING module, no witness) and package inclusion.

## Natural Sumire ending and unique PC photographs

The English disc 2 archived Finale slot reaches Sumire by ordinary inputs.
Load `local/work/later-chapter-audit/chapter-sweep/public-finale-strict/state-11999.bin`
with its SRAM. Advance with mask `0400` for eight fields every 70 fields
from field 120. The 27,000-field relay ends before the ending dispatch.
Its unmodified selector is 2 at Saturn address `002003A6`. The dispatch
at `060802F0` chooses `SU_CG.BIN`; the complete bank at `00204000` from
continuation field 3000 matches the source at FAD 148297 byte for byte.

The prior strict runtime stopped at master SH-2 PC `06080318`. The 23,000-field
interpreter continuation uses the same input pattern from relay field 0 and
shows the localized Fin at field 22200. Seven additional block variants match
the English disc 2 ENDING module exactly. The combined strict registry has
360 module variants and reproduces the continuation's guest hashes, SRAM
and all 38 native RGB captures. The checkpoint, shifted input and reference output are
kept under `local/work/codex-witness-441-review/sumire-ending`.

| Saturn record | Continuation field | CRAM and VRAM offsets | PC subimage | PC crop (x, y, w, h) |
| --- | --- | --- | --- | --- |
| 11 | 19200 | `0x200`, `0x8040` | `END_SU.SPR` 10 | (10,0,616,320) |
| 8 | 19800 | `0x400`, `0x40040` | `END_SU.SPR` 8 | (68,28,522,282) |

Both records match all 51,200 native pixels in the half-open rectangle
(0,16) to (320,176). The PC crops align the faces and theatre mullions
to the Saturn framing. Patch 0189 uses the original palette, full RGB
signature and full layer ownership to select each donor. At 1440p
the rendered rectangle is (320,144) to (2240,1104). The 90-field strict
Enhanced and Original pairs agree in guest hashes and SRAM for each
record. Enhanced changes only the photograph rectangle. Original matches
exactly when the donor is present or absent. All 1,843,200 pixels inside
the enhanced rectangle in each steady comparison match the independently
cropped and nearest-scaled PC source. A continuous 2,201-field Enhanced
comparison matches guest hashes and SRAM. The 13 sampled fades and
surrounding pictures remain pixel-exact. The four fully opaque Sumire
samples change only within the photograph rectangle.

Records 6 and 7 continue to use the canonical END_SA asset. Their decoded
640×320 RGBA pixels are byte-identical in all six heroine PC files, so
these shared photographs contribute one donor. The two unique Sumire
pictures use the verified physical END_SU file. Other routes and release
package inclusion remain open.

## Controlled Kanna ending photographs

The fixture comes from the natural English disc 2 Sumire relay state at
field 27,000. It changes the 16-bit value at Low WRAM address `002003A6`
from 2 to 4, changing one serialized byte at offset `0x1003E3`.
The original game dispatches from `0608030C` to the Kanna arm at
`06080350`, then loads the complete `KA_CG.BIN` from FAD 136797 at
`00204000`. The fixture reuses the same input movie and SRAM as the
Sumire continuation. Its recipe, reference and hashes are retained under
`local/work/codex-witness-441-review/sumire-ending/kanna-controlled`.

The 22,500-field strict comparison matches the interpreter's guest hashes,
all 37 native RGB captures and final SRAM through Fin. The two additional opcode variants
match the English disc 2 ENDING module at offsets `0x350` and `0x364`.
The added photographs use the existing Enhanced opaque layer, palette and
RGB checks. Each native record matches all 51,200 pixels at (0,16) to (320,176).

| Saturn record | Continuation field | CRAM and VRAM offsets | PC subimage | PC crop (x, y, w, h) |
| --- | --- | --- | --- | --- |
| 11 | 18600 | `0x200`, `0x8040` | `END_KA.SPR` 10 | (16,0,620,320) |
| 8 | 19200 | `0x400`, `0x40040` | `END_KA.SPR` 8 | (34,0,584,300) |

At 1440p, the changes are confined to (320,144) to (2240,1104), all
1,843,200 pixels within each steady donor capture match an independent
crop and resample, and Original and the sampled fades match the native
captures. At the group-photo entry, the native image is visible at sampled
field 600 and the registered image is visible by field 605 in the onset
replay. The donor loads asynchronously. Both photos use the verified
physical END_KA file.
The canonical group photographs continue to use END_SA once.

This evidence covers a controlled authored dispatch. Natural Kanna route
verification and package inclusion remain open.

## Controlled Iris and Kohran theatre insets

From the same pre-dispatch checkpoint used by the Kanna proof, set the
authored ending selector at Low WRAM `002003A6` to 5 (Iris) or 6 (Kohran).
Each fixture changes one serialized byte at `0x1003E3`. The original game
loads the corresponding `AI_CG.BIN` or `KO_CG.BIN`. The source bank matches
the Low WRAM copy byte for byte. The bounded 4,800-field strict runs reach
the theatre insets and match the interpreter's guest hashes, 96 native
RGB captures and SRAM for each route. The four added AOT ranges match the English disc 2 ENDING module
at `0x36C`, `0x380`, `0x388` and `0x39C`.

Both insets display record 5 at (16,96) to (104,200), with PC subimage 5
at 176×208. All 9,152 steady native pixels match the per-channel rule
(31 × foreground + lower) divided by 32 with integer truncation. The
lower input is the Saturn theatre through the top 48 rows and black
through the last 56. The replacement requires the exact palette, winning
NBG3 layer, mixed RGB, lower input and 31/32 coefficient. Native draws
continue through the moving theatre transition and fades.

At 1440p the rectangle is (416,624) to (944,1248). The strict Enhanced
and Original A/B tests verify the inset and guest hashes with the donor
present and absent. All 329,472 pixels match an independent PC blend in
each steady capture. The two 651-field fade comparisons retain exact guest
hashes and SRAM, and all 14 sampled nonsteady frames remain pixel-exact.
Original and the protected surround remain exact.
The separate physical END_AI and END_KO files each add one donor. The
shared photographs continue to use END_SA. The larger redraws remain
native. The natural Iris and Kohran routes and package inclusion remain
open. Private receipts are retained under
`local/work/codex-witness-441-review/sumire-ending`.

## Controlled general ending playback

A private English disc 2 Sakura state taken at the theatre aperture holds
`0x81` in the completion word at `06003050`. The ending routine masks that
word with `0x3F` and enters the general branch when all six bits are set.
Changing the single serialized byte from `0x81` to `0xBF` in a copy of
that state exercises the original branch and loader. The control from
the unmodified Sakura route does not take this branch.

The old strict build stops at `06080710` after 18,105 fields. An
interpreter continuation from field 18,000 issues a 150-sector read at
FAD 134315 and loads the complete `GE_CG.BIN` at `00204000`. The four
decoded Saturn records match all 71,680 native pixels in the following
continuation samples.

| Record | Fields |
| --- | --- |
| Theatre | 450, 600 |
| Cast | 2,700, 2,850 |
| Cast with logo | 3,000 |
| Cast with logo and final mark | 3,150, 3,300 |

The English disc 2 ENDING registry adds 84 observed block variants. All
84 match bytes in the pinned module, taking the registry from 366 to 450.
The linked 677,461-block build reproduced all 3,300 guest fields, all 22
native RGB samples and final SRAM with zero interpreted blocks. Evidence
is retained in `local/work/codex-th1/tp3c-cg`.

This is a controlled reproduction of the original branch. A natural
six-route completion, HD composition and package inclusion remain open.

## General ending HD composition

Patch 0233 identifies the four general ending plates by their exact
palette and cell fingerprints and checks their winning VDP2 layers.
It draws the PC donor inside the Saturn rectangle at the current
integer fit. The theatre uses a 600 × 440 crop at (24,16). The three
cast plates use the centered 640 × 448 crop at (0,16). The registered
theatre crop keeps the arch and aisle close to Saturn. The cast crops
keep the cast, logo and final mark in their original positions.

The independently drawn native characters remain over the theatre.
The HD background uses the VDP2 color offset during the opening
fade and the original 32-step color calculation weights during the
theatre-to-cast and logo-to-final-mark dissolves. The PC bank is
decoded once in a background task after the first plate is identified.

The controlled English disc 2 route matches all 3,300 guest fields and
final SRAM across the Enhanced and Original profiles. Twenty 1440p
samples with the donor absent match the previous runtime. Original
captures match with and without the donor. Enhanced changes are
confined to the viewport (320,48)–(2240,1392). At 1080p, eight
normal and fade samples draw within (320,92)–(1600,988), with the
lead-in sample unchanged. Independently decoded PC colors agree with
all changed native-center samples in the theatre, character overlays,
cast variants and both measured dissolves.

The coverage register credits the physical donor once. The proof is
from a controlled save, and package inclusion and the natural
six-route completion remain open. Private receipts and renders are
under `local/work/codex-th1/tp3c-cg/ge-render`.

## Controlled Maria ending photographs

The English disc 2 fixture changes the heroine selector at `002003A6`
from 2 to 3 in a private copy of the natural Sumire checkpoint. The
game takes its original Maria dispatch and loads the complete native
`MA_CG.BIN`. It draws both unique photographs as full, unobscured
320 × 160 rectangles at (0,16).

| Saturn record | CRAM / VRAM | PC subimage | PC crop (x, y, w, h) |
| --- | --- | --- | --- |
| 11 | `0x200` / `0x8040` | 10 | (0,0,640,320) |
| 8 | `0x400` / `0x40040` | 8 | (48,48,540,270) |

Patch 0239 uses the existing ending photograph compositor. The
independently decoded donor matches every sample in the 1,843,200-pixel
rectangle at 1440p. Surrounding pixels stay native. Six steady captures
show the corresponding HD photo. The sampled transitions, Original mode,
and missing and truncated PC files match the native controls. The five
profiles match all 1,160 guest fields and final SRAM.

The two observed dispatch variants at ENDING offsets `0x334` and
`0x348` match the pinned module bytes. The linked 677,643-variant
runtime matches all 22,500 guest fields, 37 native RGB captures and
final SRAM against the interpreter. No interpreted blocks were needed.
The private receipts are under `local/work/codex-th1/tp3c-cg/maria-hd`.

The coverage register credits the physical Maria donor once. The
canonical shared cast photos still use END_SA. The native Maria route
and package inclusion remain open.

## Natural Sumire finale under the 1,411,614-block AOT build (THD08)

PR #600 left an isolated strict AOT build (`sakura-end2.exe`, SHA-256 `155b255d79fe95ec16f1ff9a24e9670472e1e457a2d780eaa40d9780b6a0b34b`, 1,411,614 blocks, whole-module `ENDING_DISC2_EN_FULL`). Its public Finale case stopped at 45,000 frames before the credits. This run extends the same cold route to the end of the ending and the return to the title.

Command (English disc 2, the `public-finale` backup, confirm mask `0400` held 4 fields every 75 fields: the old movie to frame 44,929, then the same cadence from 45,000):

```powershell
python tools/chapter_loads.py --exe local/build/sakura-ending/sakura-ending.exe --disc 2 --backup local/work/end2/run-public-finale/backup.bin --movie local/work/ending/finale-125k.movie --frames 125000 --interval 500 --out local/work/ending/run-cold-125k
```

`--disc 1` already gives a different frame hash at frame 3,000, so the case needs `--disc 2`. Result: exit 0, 125,000 frames, 125,000 frame hashes, `interpreted 0 (0.00%)`, blocks found this run 0. Frame-hash log SHA-256 `bd0b5197d24b33eb54cb3113453faff707c3d4fd053328ca43f4bb1b04141413`; extended movie SHA-256 `78183af17e9999e9b2939e0e4d474243890097745eb45984d3e45dd716a7c66b`; the first 44,929 frames use the previous movie, and the guest hashes of the first 45,000 frames equal those of the 45,000-frame run. The `art/` folder was beside the executable; the guest does not depend on it.

Loads of the final stretch (`first_loads` of `loads.json`; frames are the trace estimate, states are the first saved state at or after it):

| Cold frame | File | State | State SHA-256 |
| ---: | --- | --- | --- |
| 43,244 | `ADVSE10` | 43,499 | `d185d753…e7244e7` |
| 43,430 | `ENDING.BIN`, `SU_CG.BIN`, `SU_SPR.BIN` (same Play Disc burst) | 43,499 | `d185d753a31dd5e4e39eea2254aaed454a774ac63165d25d5153dce37e7244e7` |
| 43,616 | `OTOMEADP.DAT` | 43,999 | `361b632af00068ce0225da62327ee7aaea418b36be8e29b66e080b25c2be4da0` |
| 62,942 | `VCEADV` | | |
| 63,871 | `LOGO.SH2` (reset to the title) | | |
| 64,057 and every ~8,500 fields after | `ADVSND`, `TITLESE`, `ADVBGM01`, `SAKURA4`, `OPSAKURA.CPK` (title and attract loop) | | |

After the Fin the game returns to the title screen and loops its attract opening until frame 125,000. No other `*_CG.BIN` bank, FILM stream or credits stream is loaded: the credits and the Fin are drawn by `ENDING.BIN` itself. The other heroine banks and `GE_CG.BIN` stay unreachable on this route (the general ending needs all six completion bits, and the other routes need their own save). All 60 files of the run that are register resources are already attributed (`SU_CG.BIN` and the chapter 10 scene pictures, bodies and `1004FCE` of PR #600) or are `LOAD.BIN` (`unassigned`, loaded by the title). This route therefore adds no new attributed row.

Timeline of the ending, measured from the saved state 43,999 of that cold run with native captures (frame `N` is `N` fields after loading it): staff credit pages to about +12,700, the colour group photograph with credit text over it from about +12,850, unobstructed from about +13,150 to +13,400, a fade, sepia group photograph from about +13,650 to +13,900, two route close-ups of Sumire from +14,000 to +14,800, the theatre exterior from +14,850, the copyright line at about +15,700 and the localized `Fin` visible by +16,000 (cold frame about 60,000). The photograph is a stable full rectangle only in the two windows above; with the credit text over the colour photograph before +13,150 the exact-signature draw would stay native.

### Does the Enhanced draw run on this route?

Not with this executable. `sakura-end2.exe` has no ending presentation code: the checked-out source tree it was linked from (`local/deps/satrecomp-end2`) accepts a reverse apply of the stack only up to about patch 0084, and the binary holds no `ending photo` string (patches 0137, 0189, 0192, 0194, 0233, 0239 add the ending draws). Four 2560x1440 pairs (Enhanced with the donor pack, Enhanced without it, Original) from the saved states at +13,249, +13,799, +14,299 and +14,719 give Enhanced equal to the missing-donor capture in all four (0 pixels differ) and the same guest hashes in all three configurations, strict, 0 interpreted. That is the executable, not the donors: the same states with a full-stack executable draw.

A full-stack development executable of the same day (`sakura-thd01.exe`, SHA-256 prefix `f2fcb44a037b1427`, full presentation stack with 0137 but without the `END_SU` rows of 0189, no ENDING blocks, run with the interpreter `SATRECOMP_NO_BLOCKS=1`) loads the same states. With the donor pack `SAKURA1/ENDING/END_SA.SPR` (2,988,213 bytes, FNV `44DC7D66456C8105`):

| State and frames | Picture | Enhanced differs from missing donor | Inside the (320,144)-(2240,1104) rectangle | Outside |
| --- | --- | ---: | --- | --- |
| +12,999, 250 fields (+13,249) | colour group photograph (record 6) | 1,792,224 px, all inside the rectangle | equals `END_SA` subimage 6 at 3x nearest, 100% | Enhanced equals missing donor |
| +13,499, 300 fields (+13,799) | sepia group photograph (record 7) | 1,755,558 px, all inside the rectangle | equals `END_SA` subimage 7 at 3x nearest, 100% | Enhanced equals missing donor |

A sweep every 50 fields (1280x720) shows the draw at +13,149 to +13,399 and +13,649 to +13,799 and no difference at +13,449 to +13,599 (the fade). The guest hash logs of Enhanced, missing donor and Original are identical in each pair, and equal to the strict AOT hash logs of the same segments (`5b4b17dd58b4da0d` and `c9ab75af77d67651`, first 16 hex digits of the SHA-256 of the hash log), so the 1,411,614-block build and the interpreter agree on the route. The two close-ups of Sumire (records 8 and 11, patch 0189) are not drawn by that executable (no `END_SU` in it), so the Sumire-only pictures are not re-witnessed here.

These pictures are the shared END_SA photographs already `hd` and verified (see above). Nothing here changes a register row: the disc 2 `SU_CG.BIN` row stays `hd`, `observed`, chapter 10; the seven disc 1 rows stay `paired-not-wired` (this route is disc 2); no `wired-unverified` ending row is left in `config/hd-chapter-coverage.json`.

### What is missing and who

- Integration desk: link one executable with the full patch stack (through 0245) and the 1,411,614-block ENDING-complete registry (PR #600). That would show the Enhanced draw of all four photographs and the zero-interpreted hash parity in a single strict run. It needs a clean build of the generated blocks, which is hours, so it was not done here.
- Owner (discs, natural play): Kanna, Maria, Iris and Kohran continuation replays, and the six-route general ending, as listed above. The Sumire route does not load their banks.
- Fixtures, states, movies and captures stay under `local/work/ending`.
