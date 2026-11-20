# Iris NC56 face placement in Chapter 1

Patch 0176 makes the NC56 eyes and mouth use the positions authored in the PC resource. The previous mouth alignment search placed the closed mouth 8 pixels to the right and 9 pixels down in the 288 × 320 body. The open mouth was 11 pixels to the right and 15 pixels down. At 1440p, this left a displaced patch of skin and hair over Iris's face. The fixed positions follow the PC expression group and remove that displacement.

## Authored expression group

The native VDP1 body is the 136 × 144 texture at `0x610` of `/SAKURA1/NC56.BIN`, FNV-1a `BA10FBEE653BA644`. The exact resource FNV-1a is `AC0E7FA242BB31C5` across both prepared English and Spanish discs. The PC asset is `SAKURA1/NC/NC56.SPR`, FNV-1a `9EF3AC7440EC0E6E`, with a 288 × 320 body at ordinal 6.

The native file ends at `0x6610`, immediately after three 48 × 24 eyes and six 16 × 16 mouths. This fills the entire payload after the body. The PC resource decodes only group 12's three eyes (38–40) and six mouths (107–112) alongside the body. Table 6 preserves each group's order, and tables 8 and 9 give eye origin (96, 89) and mouth origin (104, 129). Subtracting the table 7 body origin (−8, 0) gives the placements below. Native texture shape and decoded PC expression agree throughout the bank.

| Native offset | Texture FNV-1a | PC ordinal | Position | In the live command trace |
| --- | --- | --- | --- | --- |
| `0x5290` | `B4C0E575B90E4717` | 38 | (104, 89) | Yes |
| `0x5710` | `7B98A3444970D9AF` | 39 | (104, 89) | Yes, during native blend |
| `0x5B90` | `36E282B6B181C89B` | 40 | (104, 89) | Yes, during native blend |
| `0x6010` | `EF7095F8C1726F8E` | 107 | (112, 129) | Yes |
| `0x6110` | `94D0394CC5913B7B` | 108 | (112, 129) | Yes |
| `0x6210` | `DBFC67B257182027` | 109 | (112, 129) | Offline correspondence |
| `0x6310` | `BF20288CEB038675` | 110 | (112, 129) | Offline correspondence |
| `0x6410` | `A9DD22C9049C2A3D` | 111 | (112, 129) | Offline correspondence |
| `0x6510` | `F60E1447A705F2F9` | 112 | (112, 129) | Offline correspondence |

## Replay evidence

The 11,100-field strict continuation from `chapter1-continuous-47999.state` agrees with the uninterrupted disc 1 guest history at fields 48,000–59,099. The second resume uses the resulting field 58,279 checkpoint and reaches the NC56 draw naturally. Across the eight 820-field variants and two 380-field dialogue-hold runs, each pair had identical guest histories and final backup RAM, with zero interpreted blocks.

The 2560 × 1440 Enhanced captures change up to 46,625 pixels, all within the face rectangle (1131, 317)–(1445, 626). The preceding NC56 blend uses the native output and the sampled fade pixels remain identical. Original, absent and altered-donor controls match all 54 full-frame samples. The altered donor changes a byte of table 12 outside the image decoder and retains the previous placement path.

The independently decoded PC mouth images match all 12,182 and 11,266 checked flat opaque samples for the closed and open poses. Of 18,780 opaque bilinear neighborhoods per mouth, all but one and two samples respectively are within one per-channel RGB value. The visible eye matches 16,016 exact flat opaque samples. In the hold variant the registered closed mouth remains visible through sampled field 355.

The live certificate is for the English disc 1 route. Four additional mouth phases are covered by offline resource correspondence. Package inclusion is pending. Evidence is under `local/work/codex-th1/nc56-live/`.
