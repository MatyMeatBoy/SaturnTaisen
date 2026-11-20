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

Patch0195 uses the registered 592 × 320 PC plate as the lower source in Enhanced mode. It checks both native page and palette identities and the BG2093 tile payload, then recovers each row origin by matching the isolated lower pixels. Consecutive checkpoints also contain rows at X 6 and X 10, so the lookup covers the full 0–32 crop range and requires one exact match per row. Before drawing it checks the entire visible viewport against a reconstruction using the live upper pixels and hardware blend ratio. Unsupported mixtures and fully opaque upper frames use the native rendering. BG2238's verified still remains a separate case. This route gives no BG2338 read.

Six 320-field Direct3D 11 runs at 2560 × 1440 reproduced the archived guest-frame hashes and matched final SRAM. They covered the previous pinned runtime, the exact candidate with a valid, missing, or one-byte-corrupted donor, and Original with or without the donor. The native controls matched across 22 sampled frames. The valid donor produced 148 guarded draws and changed pixels strictly inside the picture viewport, including all 11 consecutive samples at replay fields 140–150. Independent projection matched the complete 2,032,128-pixel picture area to within one RGB level per channel at eight blended samples and matched both opaque-upper samples exactly. The original native viewport reconstruction matched all 41,472 pixels at each of those ten checkpoints.

A separate donor/missing replay resized 2560 × 1440 → 1920 × 1080 → 2560 × 1440 and quick-saved and reloaded during the effect. Guest hashes and final SRAM matched, and all five samples kept the effect inside the viewport at the requested sizes. SDL device-loss recovery is covered by explicit texture cleanup and was inspected in code without injecting device loss.

In a serial baseline/donor/donor/baseline run without screenshots, dream fields 130–215 measured 10.18–10.36 ms median and 11.28–11.68 ms p95 at baseline versus 11.52–11.85 ms median and 12.46–14.35 ms p95 with the donor. None of those dream fields exceeded 16.67 ms. Ordinary fields 25–70 and 285–315 measured 9.31–9.98 ms median at baseline versus 9.98–11.20 ms median with the candidate, with zero and two fields over budget per run, respectively. This single-host sample includes ordinary-frame variability and does not establish a cost on slower systems.

Replay commands, state receipts, layer dumps and comparison counts are local under `local/work/codex-scroll-remainder/bg2093-0195/`.
