# Chapter 10 NC3286 body and face

The English disc 2 ending route starts from the archived Mednafen GameCompleted save. The 8999-field checkpoint identifies NC3286 by its byte-exact 288 × 144 VDP1 body texture, FNV-1a `EDEB190DB6BE8263`, and the disc palette. The original input suffix reproduces all 55 archived guest hashes in each of five muted Direct3D 11 profiles. Final SRAM matches. Original with and without the PC donor and Enhanced with a truncated or missing donor produce identical corresponding native RGB.

At fields 3, 8, 16 and 36, the installed donor changes 1,631,402 to 1,631,513 pixels at 2560 × 1440. A mask rebuilt from the live Saturn command list, exact texture bytes and matching palette contains every changed pixel. It covers 33,355 opaque positions and includes two witnessed eye textures. The field-52 blend stays pixel-identical to native and logs the body blend guard. This verifies the sampled draw and blend fallback on disc 2. Other occurrences remain open.

The same route's field-13799 NC3057 checkpoint exercises the existing PC body clip with four active face strips. The HD result has visible rectangular seams around the faces. The v0.2.14-alpha executable, SHA-256 `8232F966863A8872B19B5121996AC448EB5F8DC8641AA452449471F5ED5D5665`, reproduces all 55 archived guest hashes, final SRAM and five RGB samples per arm exactly against the current test executable. The seam is present in both versions. The [patch 0222 witness](nc3057-ending-faces.md) verifies the corrected face draw separately. Private files and commands are under local/work/codex-tp3c/residual0222.

## Exact face placement in patch 0224

English disc 2 Chapter 10 checkpoints show two wounded poses, NC3285 and NC3286. Each Saturn file stores three eye strips and six mouth strips after the body. Their hashes and dimensions now select the corresponding PC ordinal. The PC expression tables give the authored top-left coordinates for eyes and mouth. The previous heuristic moved the NC3285 eye and mouth 11 and 10 source texels horizontally. For the first NC3286 expression it moved the eye and mouth six and eight texels vertically. Those placements produced visible joins where the eye region crosses the headpiece.

| Pose | PC eye position | PC mouth position | Active 1440p samples | Changed pixels versus previous HD per active sample | Independently projected flat texels per active sample |
| --- | --- | --- | ---: | ---: | ---: |
| NC3285 | (159, 83) | (236, 161) | 5 | 90,810 | 6,028 |
| NC3286 | (219, 13) | (207, 112) | 4 | 154,018–154,259 | 10,784–10,884 |

For each body, five muted 55-field strict-native arms agree on guest hashes and SRAM. NC3286 also matches the archived input suffix. Each active 2560 × 1440 sample agrees with the independently projected donor at every sampled flat texel. The previous-versus-corrected differences stay within the face regions, and all changes from native stay within the 37,185-position NC3285 and 33,355-position NC3286 silhouette masks. The broad body silhouette and its visible edge differences are outside this face repair. Original, missing and truncated donors match their RGB controls. The field-52 NC3286 blend remains pixel-identical to native.

The live logs confirm NC3285 eye and mouth ordinals 1 and 4, and NC3286 eye ordinals 1, 2 and 3 with mouth ordinal 4. NC3058 reproduces its earlier 55 guest fields, ten RGB captures and final SRAM. The verification covers these appearances. Package inclusion remains pending. Private evidence and commands are under local/work/codex-tp3c/residual0224.
