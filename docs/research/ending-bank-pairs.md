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

Measured from `config/hd-ending-bank-map.json` and patch 0137: the seven banks hold 76 records (4 GE + 6 x 12). Records 6 and 7 are byte-identical in the six heroine banks (same palette and cell fingerprints `A19A0B84409A3AB8`/`FCAFB7040FA7C5ED` and `BD98B23C7D99D3DD`/`F660240773226223`), so the single table of patch 0137 already covers 12 of the 72 heroine records with two keys and one donor (`END_SA.SPR`, subimages 6 and 7, donors decode identically in all six `END_*.SPR`). Records 8 and 11 (route-specific) stay native by decision (the PC redraws the mullions and the Sakura mouth). Records 0-5, 9 and 10 are strips, insets, petals and the Fin mark with different PC geometry. The four GE records are whole-screen variants with no composition witness.

The register now reflects this instead of a blanket `paired-not-wired`: disc 2 SA is `hd` (records 6 and 7 verified), disc 2 AI/KA/KO/MA/SU are `wired-unverified` (same keys, no replay of that route), disc 1 banks and GE stay `paired-not-wired` with a specific reason. The generator derives the keys from patch 0137, so the status cannot drift from the runtime.

No state, input movie or save on this machine reaches any ending (the private `local/work/codex-th1` evidence is not present here; only the Sakura and Sumire backup RAMs exist, and the ending blocks need the 353-variant AOT build of patch 0183's candidate). Nothing was built or replayed in this shard; no runtime patch was added, because a table-only refactor would add no coverage.

What is missing and who does it:
- Owner (discs, natural play): continuation replays of the Kaede, Sumire (Sumire backup RAM exists), Maria, Iris and Kohran endings through the group photos with the 0183 candidate, to move five `wired-unverified` entries to `hd`.
- Owner or integration desk: a GE (theatre) ending witness with viewport and fade evidence; then a generated GE table keyed by the four palette fingerprints.
- Integration desk: a disc-1 decision (distinct ENDING module, no witness) and package inclusion.
