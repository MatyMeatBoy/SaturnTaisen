# Additional Chapter 1 and 3 foregrounds

Patch 0219 adds four foregrounds from retained English disc 1 replays to the existing narrative compositor. The original Saturn fixed-cell palette index zero defines the transparency boundary. PC subimage 0 uses its authored cyan key. The exact file, palette, cell, RGB and source-ownership guards remain in effect at the approved Zoom viewport.

| Foreground | Archived route | Disc FAD | Mask fit IoU | Changed pixels per active 1440p sample |
| --- | --- | ---: | ---: | ---: |
| BG4088 | Chapter 1, NC96 dialogue | 154802 | 0.957 | 132,826 |
| BG4165 | Chapter 1, sortie dialogue | 155308 | 0.939 | 280,958–854,934 |
| BG4171 | Chapter 1, victory continuation | 155354 | 0.951 | 1,207,864 |
| BG4114 | Chapter 3, opening 0301 | 155055 | 0.906 | 230,623 |

Each PC donor drew in 79 fields of its 80-field witness. All six muted Direct3D 11 profiles per foreground preserved guest hashes and final SRAM in strict native mode. All changed pixels in 20 matched 2560 × 1440 samples reproduced an independent PC projection inside the Saturn mask. Original profiles with and without donors and Enhanced profiles with missing or altered donors matched their native RGB controls.

A second BG4165 replay overlays Sakura and other VDP1 sprites. Two native layer probes identify 12,704 occupied foreground positions per sample. Those positions stay native while 262,980 visible foreground pixels per 1440p sample match the PC output. BG4114's archived opening preserves native overlaps in the same layer compositor. [Patch 0221 verifies BG3034's 651 × 326 source](bg3034-wide-cutout.md). These witnesses cover the four English disc 1 appearances. Package inclusion is pending. Private replay data is under local/work/codex-tp3c/fg-later.

## BG4370 sortie foreground

The English disc 1 sortie briefing displays the 288×144 BG4370 foreground
over BG1193. The live disc transfer at FAD 155720 identifies the Saturn
source. The visible opaque source pixels all match the composed native RGB
(13,515 of 13,515 in the registration capture). The PC donor
`SAKURA1/BG/BG4370.SPR` is 576×320, with cyan key transparency and a fitted
native-to-PC scale of 1.94 horizontally and 2.27 vertically, with offsets
−0.5 and −6 PC pixels. The image registration has 0.961 silhouette IoU.

Patch 0236 adds an exact native palette, cell and payload signature with a
pinned PC size and hash to the existing registered cutout table. The control
also loads the BG1193 backing donor. The 2560×1440 Direct3D 11 replay resumed
the natural Chapter 1 briefing from field 1959 of the archived relay. All six
profiles reproduced the same 80 strict guest hashes and final SRAM. Only
Enhanced with the exact donor drew BG4370 (79 fields). Across four captured
fields (8, 24, 40 and 60), the independent pixel comparison located 523,463
changed output pixels per field, all within eligible native-source ownership
and consistent with registered PC sampling. Missing or corrupted donor
captures matched the previous Enhanced renderer exactly. Both Original
captures matched each other exactly with and without the donor.

This verifies one physical donor in the tested disc 1 occurrence. The
disc 2 occurrence and package inclusion remain pending. Earlier evidence
where BG4370 was only resident does not verify that occurrence. BG3123 has
native blend composition in the available witness and remains native.
