# Petals, flash and the first New Game film

Presentation audit with `sakura-test1.exe` at 614,024 blocks, SHA-256 `67ef0bdc41321bd19231f637070d6dd39fe6bd17df63527dffde61aa4a79cbb7`. English disc 1 and a copy of the test.1 version's art were used in each isolated profile. Captures and states stay under `local/work/intro-petals-audit`. The test window is 1280 × 720. Window steps are numbered from one.

## Opening and title

| Playback | Evidence |
| --- | --- |
| From `intro2399.state` with no input | The opening fades to black before entering the title. In `title-petal-fine`, small petals appear at 3990 and a giant petal at 4026. The native frame appears at exactly steps 4027–4037 and disappears at 4038. |
| From `intro1799.state` with `chapter1-opening-skip.movie` | The opening fades to black after Start and the title reappears. `skip-fine` contains the same frame at sampled steps 726, 728, 730, 732 and 734. |

The title keeps palette fingerprint `91E480C617AD7F6C`. VDP2 layer 5 keeps 71,680-pixel coverage in the probes. The title's visible area shrinks as it gets covered by VDP1 layer 0. Its mask covers 17,928 pixels at probe 3990, the full 71,680 at probes 4026 to 4036, and 19,283 when the title returns at 4037. Background selection requires at least 1,000 visible pixels of its layer. When that effective coverage disappears, the layout switches to `native` and draws the host's frame.

The petals reach VDP1 in a dynamic 320 × 224 texture. The normal command at VRAM `00100` uses source `3A800`, coordinates (0, 0), mode `00A8` and color `0000`. The texture from sample 4032 has SHA-256 `0620c6da882b0e2d29a6eb5c1fe88abb94e7d8c4b52179e273b327b9fb0cb`. The `/SAKURA1/LOGO.SH2` module matches fully in Low WRAM at `00204000` during samples 3990, 4026, 4032 and 4038. It is 243,200 bytes, LBA 160804, SHA-256 `0745216059e495e7ba45faf1657bc045317579186bc539802d35b9567cb483ca`. The texture's hash changes during the effect and its full bytes were not found as a static module region.

Native image 4032 has ranges R=229–232, G=212–215 and B=228–230. Image 4038 has 69,298 white pixels out of 71,680 and keeps faint title details. A detector for uniform black or white leaves part of the flash out. The dynamic texture ends at the native frame's edge. The audit identifies the loss of framing and the effect's origin. Petal continuity in the outer strips remains to be implemented.

## New Game and the narrative film

The continuous `new-game-film` path uses `title-final.state` and `tests/chapter1-title-new-game.movie`. It logs 6,300 frames under strict AOT with zero interpreted blocks.

| Phase | Sample and source |
| --- | --- |
| Program closing | Step 268 with native frame. Sampled steps 272–292 are full-screen black. |
| Loading | Probes 400 and 650 with `anchored-menu`. Layer 4 occupies 71,680 pixels, palette `74EA8ADC9B0340CC` from `LOAD.BIN`. |
| Before the film | Step 736 shows the darkened KABE00 background, the empty footer and a rectangular image shadow. The probe has layer 1 absent, layer 0 at 1,214 pixels and layer 3 with content from Y=12. At 840 the corner badge appears, still without layer 1. |
| Active film | Probes 880, 920, 1200 and 5700 show 41,472 layer-1 pixels at (16, 8) to (303, 151), a native region of 288 × 144. Step 1132 shows the city skyline and keeps the badge and empty footer. |
| Film exit | The white image at sampled steps 5704–5884 still belongs to the film frame. At 5920 the fade to KABE00 is visible. Steps 5956, 5992 and 6028 show flowers with the empty footer. At probe 6000 there is no longer layer 1, layer 0 returns to 1,214 pixels and layer 3 sits below Y=160. At 6064 the footer disappears. From 6100 onward the episode title appears, a separate transition. |

The layout reports `movie` while showing the skyline with the footer. The bbox returned by `AnalyzePresentation` spans the image and footer layers, and the `movieOnly` branch extracts that bbox from the native framebuffer. In the active samples, the combined bbox runs from (9, 8) to (314, 219). That's where the footer sits within the film crop. The separately traced layer 1 delimits the 288 × 144 video crop.

The footer uses a VDP1 command, mode `00A0`, color `C500`, at (8, 152), 304 × 64. The badge uses mode `00A0`, color `C400`, at (16, 160), 40 × 48. The sampled states between 736 and 6000 lack the 16 × 16 glyphs with colors `C510` or `C570`. Layer 3 provides the fill and shadows, and layer 5 keeps KABE00, palette `48291F6F1C8A4707`. The 15,404 bytes of `0100.BIN` and the 54,018 of `0100TBL.BIN` match fully at `00204000` and `00224000` in the samples across the whole stretch.

The first narrative film sits inside `/SAKURA4` at offset 23,695,360, with 21,714,028 bytes, 2,354 STAB samples and a 288 × 144 image. SHA-256 `610cb5c5538896968c457937d7101783dfe20d073ae58c0f948ee9ed1eb5dd02`. Its first 128 bytes are present in High WRAM `06080000` during the active probes and also at 6000, where the header of the next stream is already present at `060B0000`. The resident header serves to identify the asset, and the visible layer 1 provides evidence of the image being played. The empty footer in any given scene requires keeping its native behavior. The pre- and post-film samples belong to the observed transition of `0100.BIN`.

The extracted states were used for point probes. Attempting to resume long sequences from samples 840 and 5700 produced hashes different from the continuous playback, so the steps and visual sequence were taken from the continuous path.

## PC candidate

The local ffprobe inventoried 52 MPEGs. `MOVIE000.MPG` is a visual candidate for the opening, MPEG-1 at 576 × 288, MP2 audio, duration 85.942856 s. SHA-256 `8fb04101f255ac257e027d18d5d324d115b47ef1eb14b9bada64ab70aa25dd10`. PC samples at approximately 10.125 and 30.25 s show the same shots as Saturn captures 1200 and 2400. Saturn sample 1800 had no close match in the sampling. The comparison identifies shared material and leaves the full edit, sync and subtitles to be measured. The PC video is still outside the runtime.
