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

PC script mapping, English reinsertion, playable PC compatibility and the Saturn HD resource compositor remain pending. No extracted original artwork or full scripts are included in the repository.

## Additional inspection

All19 native PC WALL KABE resources decode successfully; every one contains a640×480 image. The exceptional EV19S03 image chunk contains readable authoring/export comments and bitmap names where the usual entry table is expected. Its layout remains unsupported; this observation does not justify bypassing bounds checks.

The historical [Iwakura PC project announcement](https://iwakuraproductions.wordpress.com/2014/09/01/the-sakura-wars-pc-fan-translation-project/) documents English reinsertion in2014 and names cj_iwakura, EsperKnight and Nezumi. It does not provide a verified reinsertion tool for this2006 Japanese dump, nor establish current PC compatibility.
