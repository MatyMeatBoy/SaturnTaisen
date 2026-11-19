# BG2093 in the Chapter 9 dream transition

English Saturn disc 2 reads `BG2093.BIN` at FAD 124938 for 25 sectors during the `0900` dream. The next image read is BG2238 at FAD 127528. The muted 7,200-frame strict-native replay matches the archived Chapter 9 guest hashes, ending at `52b7bd37d69c650f`. A short relay from archived frame 6500 matches the same 320 hashes around the transition. The 2560 × 1440 presentation probe also retains the native layout.

The 320 × 144 BG2093 tile data resides at VDP2 VRAM `0x34800` with its exact palette at CRAM `0x200`, fingerprint `65D40E5ACD068572`. It supplies NBG0 (source 2) at page `0x40000`, through the 288 × 144 picture viewport at (16, 8). NBG2 (source 4) supplies the upper green plate from page `0x44000`.

| Resume checkpoint | NBG0 rows at native X 7 / 8 / 9 | NBG2 color calculation | Exact pixels in the reconstructed 288 × 144 viewport |
| --- | --- | --- | ---: |
| 6644 | 51 / 49 / 44 | Ratio 10 | 41,472 |
| 6676 | 42 / 50 / 52 | Ratio 21 | 41,472 |
| 6692 | 42 / 50 / 52 | Ratio 24 | 41,472 |
| 6708 | 50 / 42 / 52 | Ratio 19 | 41,472 |
| 6772 | 0 / 144 / 0 | Disabled, NBG2 opaque | 41,472 |

For each checkpoint the layer dump and the screen capture come from the same first rendered frame after loading. Each row of the isolated lower source matches exactly one of the indicated Saturn picture origins. At the four blended frames, the native viewport equals the integer color mix of the two captured sources. At 6772 the lower source still matches the exact BG2093 crop at native X 8, and the opaque upper source supplies the entire visible viewport.

The reviewed 592 × 320 PC pair and the [offline crop fit](scroll-table.md#remaining-ten-offline-alignment-measurements-not-wired) describe the isolated BG2093 image. The witnessed effect needs a per-line origin and a changing second-source blend, so one viewport crop cannot preserve the composite. The catalog records the disc 2 appearance and keeps BG2093 on the native path. BG2238's verified still remains a separate case. This route gives no BG2338 read.

Replay commands, state receipts, layer dumps and comparison counts are local under `local/work/codex-scroll-remainder/`.
