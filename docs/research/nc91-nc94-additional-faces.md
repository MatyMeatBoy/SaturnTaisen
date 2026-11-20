# Additional NC91 and NC94 face groups

Patch 0226 registers two further Chapter 8 appearances on the archived English disc 2 Iris route. The Saturn NC91 ambush uses the fixed-eye group at offsets 56080 and 57872. NC94's deployment uses its second eyes and mouth group at offsets 46096 and 51472. The active native textures match the respective disc file at those offsets, and the PC expression tables give the matching ordinal groups and authored positions.

| Appearance | Registered PC ordinals | Live selections | Flat donor texels matched per 1440p sample |
| --- | --- | --- | ---: |
| NC91 ambush | Eye 7, mouths 20–25 | 7 and 20 | 3,504 |
| NC94 deployment | Eyes 4–6, mouths 14–19 | 4, 5, 6 and 14 | 3,166–3,274 |

Both use eye position (137, 81) and mouth position (158, 155) in their own PC body image. The prior heuristic retained the native eye and mouth rectangles over both PC bodies. The new draws remove those rectangular joins. Each of the five 2560 × 1440 samples per appearance changes only the eye and mouth region against the prior build. The body outline retains its existing registration.

Five 55-field muted strict Direct3D 11 arms per appearance match their guest hashes and final SRAM. Original, missing and truncated donor profiles reproduce native RGB. The NC94 deployment also matches all 55 archived hashes in a separate replay with the exact input suffix. The first NC91 group from patch 0225 preserves all ten RGB samples, 55 guest fields and final SRAM. Other groups retain the existing path. The register credits NC94's sampled appearance and retains the earlier NC91 witness. Package inclusion is pending. Private evidence stays under local/work/codex-tp3c/residual0226.
