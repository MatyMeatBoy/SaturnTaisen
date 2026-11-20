# NC60, NC61 and NC3038 face registration

Patch 0230 registers three Chapter 9 appearances from the English disc 2 0904 route. NC60 and NC61 have identical Saturn expression bytes at offsets 65808–76431 and identical decoded PC parts for the witnessed expression group. In PC expression table 6, group 6 indexes the eye sequence 24, 25, 26, 25 and mouth ordinals 76–81. The body placement is (−16, 0) in both PC archives, so the authored positions are (40, 65) and (56, 113) relative to the body. The runtime verifies the whole Saturn and PC files for each body before using the shared group.

NC3038's three eye strips start at 24592 and its six mouth strips at 28048. Their authored PC parts 1–3 and 4–9 use positions (133, 87) and (159, 123). The earlier search placed the sampled mouth at (148, 115), leaving a visible duplicate edge. NC60's earlier matcher reused one eye part through the blink and selected a mouth from a different group. NC61 had the same mouth mismatch.

Five muted Direct3D 11 profiles per appearance reproduce 55 strict guest fields and final SRAM. Original with and without donors and Enhanced with missing or truncated donors reproduce native RGB. The 12 stable 2560 × 1440 comparisons change only the affected face regions against the earlier HD build:

| Body | Sampled face change per active capture | Independently projected flat texels matched |
| --- | ---: | ---: |
| NC3038, library entrance | 42,401 | 946 |
| NC60, library continuation | 1,553–24,743 | 1,121–1,248 |
| NC61, 0904 introduction | 28,493 | 1,121 |

NC3038 selects eye ordinals 1, 2 and 3 over the replay with mouth 4. NC60 selects eyes 24, 25 and 26 with mouth 76, and NC61 uses 24 and 76 in the stable samples. NC61 field 3 is omitted from the before/after comparison because the asynchronous donor became ready in different fields. The later NC61 blend matches native in both sampled fields. The NC71 regression reproduces 55 fields, ten RGB captures and final SRAM.

The register gains the three exact appearances. The remaining expressions and body edges outside these facial regions keep their existing presentation. Package inclusion is pending. Private assets, replays and captures remain under local/work/codex-tp3c/residual0230.
