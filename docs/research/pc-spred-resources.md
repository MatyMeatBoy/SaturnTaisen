# PC resources: first verified decoding

Owner-supplied Japanese PC media, inspected locally on 2026-11-17. The user confirmed that PC text should reuse and adapt the existing English Saturn translation, retaining its credits.

The InstallShield cabinets were extracted without running the installer, game executable or legacy drivers. The game resource group contains 2,059 `.SPR` files. `tools/audit_pc_sprites.py` records their identities, image-table dimensions and formats in a local manifest; it does not establish correspondence with Saturn resources.

The header inventory identifies 69,174 nonempty image entries: 69,168 use format `0x15`, six use `0x04`. One file, `SAKURA2/EVENT/MAP19/EV19S03.SPR`, fails the current image-extent rule. This may be a format variation; it has not been established that the source file is damaged. Reject it until its layout is understood.

## Native decoding proof

The independently implemented bounded decoder in the dependency patch stack supports the observed compressed RGB555 stream and indexed image paths. Synthetic tests cover raw and compressed red/blue pixels, truncation and invalid extents. The native diagnostic command is:

```
sakura.exe --export-pc-spr INPUT.SPR LOCAL_OUTPUT_DIRECTORY
```

It operates without starting Saturn or requiring a Saturn disc. This initial diagnostic writes RGB PNGs; it does not preserve transparency or reconstruct animation/composition metadata. It is not a production HD-pack importer.

Locally decoded and visually inspected examples:

| Resource | Dimensions | Finding |
| --- | --- | --- |
| SAKURA1/WALL/KABE0100.SPR, entry 0 | 640×480 | Correct day floral motif and colors; Saturn KABE00 is 320×224, so direct replacement requires framing decisions. |
| SAKURA1/BG/BG0000.SPR, entry 0 | 576×320 | Flat cyan resource; dimensions alone do not imply useful scene detail. |
| SAKURA1/NC/NC10.SPR, entry 0 | 326×320 | Sakura body with green exterior and blank facial region. Other entries contain expression parts; this requires composition and transparency rules. |

NC10 exports 94 nonempty image entries successfully. Do not treat its body image as a complete standalone portrait or the green exterior as a verified alpha mask. Establish keyed colors, anchors, expression selection and animation timing from executable/data evidence before integration.

## Research provenance and limits

The public [Sakura Taisen PSP translation tools](https://github.com/snake7594/sakura-taisen-1-2-psp-korean) provide primary format research for SPRED headers, palettes and the ring-buffer compression. PC observations above were checked against the owner's files; PSP behavior is not assumed to prove every PC composition rule. No code from that project was incorporated into the decoder.

PC script mapping, English reinsertion, playable PC compatibility and the full Saturn HD resource compositor remain pending. No extracted original artwork or full scripts are included in the repository.

## Additional inspection

All19 native PC WALL KABE resources decode successfully; every one contains a640×480 image. The exceptional EV19S03 image chunk contains readable authoring/export comments and bitmap names where the usual entry table is expected. Its layout remains unsupported; this observation does not justify bypassing bounds checks.

The historical [Iwakura PC project announcement](https://iwakuraproductions.wordpress.com/2014/09/01/the-sakura-wars-pc-fan-translation-project/) documents English reinsertion in2014 and names cj_iwakura, EsperKnight and Nezumi. It does not provide a verified reinsertion tool for this Japanese dump, nor establish current PC compatibility.

## Experimental background integration after v0.1.5

The development runtime accepts `--pc-assets EXTRACTED_PC_RESOURCE_ROOT`. The supplied Japanese PC KABE resources can supply the corresponding decorative theme in enhanced Saturn scenes. Each source must match its recorded size and FNV64 identity before SPRED decoding; unknown or modified files fall back to Saturn. This is an accidental-mismatch guard, not cryptographic authentication. The initial English font option stays independent.

Generated PC masters are normalized onto 864×486, using only colors observed in the matching native 640×480 PC image. The generated art is still preliminary and does not preserve the original center bit-for-bit. Rendering uses integer cover and carries the same native color offsets during fades. Disabling PC HD backgrounds selects the Saturn background.

`--prepare-pc-backgrounds ROOT CACHE_DIRECTORY` validates and caches the 19 unique native PC decorative sources without starting the game. All 19 succeeded locally. An interactive night scene was inspected; tests confirm that disabled or modified-source PC data selects the same Saturn exterior pixels as the fallback. This is not a PC game executable path, HD character/video replacement or PC text translation. The public launcher import flow for PC media is still pending. These additions are subsequent development and are not in the immutable v0.1.5 package.

## PC executable follow-up

Read-only LLVM inspection identifies ADVcore.exe as PE32/i386. Visible imports include DirectDrawCreate, DirectInputCreateA and dynamic GetProcAddress; the visible table is not evidence of the complete game API or font renderer. No CreateFont/TextOut API names were found in this static image. PC script storage and executable compatibility remain unresolved. No installer, game executable or legacy driver has been executed during this resource work.

The [DxWnd project discussion](https://sourceforge.net/p/dxwnd/discussion/general/thread/379615954b/) records developer observations of ADVcore spawning copies and helper DLLs in temporary folders. This is evidence from another installation, not confirmation for this dump, but future PC launch supervision must account for child processes rather than assuming the original PID owns the final game window. The [official chronology](https://sakura-taisen.com/archives/game/nenpyou/index.html) distinguishes the original PC and later DVD editions; media timestamps alone do not identify the commercial release date.

## Windows PC asset roots (patch 0212)

The Windows C runtime passes narrow command-line arguments in its code page. A folder containing U+00F1 supplied byte F1 to a UTF-8 filesystem conversion, which aborted the runtime. The PC asset argument now uses the Unicode Windows command line, each filesystem consumer decodes the stored UTF-8 consistently, and MPEG decoding opens the native path for both demux cursors.

The complete 676,369-variant Windows candidate 8232f966863a restored MAP12 HD with asset roots containing U+00F1 and U+685C. Each matched the ASCII baseline over 110 strict fields and four 2560x1440 captures. Missing, modified and disabled donors matched the Saturn fallback, and Original matched with and without the donor. A natural MOVIE004 run from the U+685C root matched the ASCII baseline across 3,750 strict fields, SRAM and six captures across the native cut. Local replay evidence is in `local/work/codex-th1/utf8-assets-probe`. Package verification remains pending.
