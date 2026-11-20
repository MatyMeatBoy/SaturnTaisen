# MAP05 tiled ground from the PC edition

The Chapter 3 third-battle Continue route reads MAP05.BIN from FAD 232479 on English Saturn disc 1. The Saturn and PC map files both contain 335,808 bytes and have SHA-256 `59e60cb1754564908151f74835a6c926c2b49eb517bdbc1ea2e4482f22ab2601`. The PC map table identifies MAP05_A.SPR as Ground. The SPR is 2,361,801 bytes with FNV-1a `F3F7198CA32391D8` and SHA-256 `d3e2478a8d327fc46ee3478688d7c159d3439fa3d7e79ab22fb74931b9ccf3a0`.

Patch 0153 gives the existing placement assembler a per-map tile size. MAP05 puts 46 distinct 256 × 256 tiles in a 2048 × 2048 plane. Even rows and columns provide the 1024 × 1024 world sampler. Enhanced selects the donor by source-4 pattern-name FNV-1a `A18A5122F7C18729` on VDP2 page `0x40000`. The compositor applies the native color offset and changes only eligible top-source-4 pixels within the integer-scaled center. Empty, transparent and keyed positions keep the native pixels.

## Verification

Seven muted, 180-frame interpreter replays start from the preserved MAP05 continuation. They match all guest hashes and SRAM bytes. The guest hash log SHA-256 is `0d5ae8edec7d4628d5ad670707347883d0c322a8327dd057a17736c8678b435c`. Enhanced with a valid donor draws HD. Enhanced with a missing, same-length corrupt or disabled donor matches the earlier runtime in RGB at all four captures. Original with and without the donor matches in RGB.

The camera remained at (263, 149) in the sampled window. At 2560 × 1440, every changed pixel agrees with the independent PC placement decode and the Saturn color offset (−4, −4, −4). The changes remain within the 1920 × 1344 integer-scaled center.

| Frame | Changed pixels |
| ---: | ---: |
| 24 | 1,654,020 |
| 74 | 1,654,380 |
| 122 | 1,657,404 |
| 168 | 1,654,848 |

The local strict-native build matched the earlier runtime in all 1,200 opening guest hashes, final capture and SRAM. The separate strict-native MAP04 comparison passed with matching 180 guest hashes, four 1440p captures and SRAM. Both regressions reported zero interpreted blocks. Strict execution of the MAP05 fixture stops at untranslated master SH-2 entry `00205ED4`. A moving camera, complete battle and packaging remain open.

Private comparison inputs and receipts are under `local/work/codex-th1/map05-triage/`.
