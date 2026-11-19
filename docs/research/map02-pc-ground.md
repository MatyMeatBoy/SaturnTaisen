# MAP02 ground from the PC edition

The continuous English Saturn disc 1 route loads `MAP02.BIN` at FAD 231973. The 336,640-byte PC `MAP02.BIN` is byte-identical to Saturn, SHA-256 `f2bc29c87209a2bb1ab28b0664e3be1140b2245632005e03f35d84e1b8015611`. The PC table identifies `MAP02_A.SPR` as the ground. It contains one 2048×2048 image, 5,829,484 bytes, FNV-1a `437AE98D69D62C17`, SHA-256 `82b49a84a91c5982e5f22d0f18c5ebb2cf613a19ddeb19c36eb7a03ad00e5983`.

The Enhanced renderer uses the existing ground compositor. It identifies VDP2 source 4 at page `0x40000` by its 8,192-byte pattern-name fingerprint `25FF56EB6965E424`. The map uses the Saturn camera coordinates on a 1024×1024 ground grid, sampled at even coordinates in the PC image. The source-4 tint follows the native registers. Cyan, transparent and out-of-bounds samples retain the native source. The presentation keeps the current integer fit, and applies the ground only in the native centre. Units, priority scenery, shadows, and unsupported blend cases use their existing render paths. The register classifies this under tactical maps.

## Verification

The first active grid and Kohran's turn were tested with English disc 1 at 2560×1440 and 1920×1080. On each 60-frame test, guest hashes matched and zero blocks were interpreted. Original matched in RGB with the donor present and absent. At 1080p a same-length donor with one byte changed gave the same RGB capture as the missing donor. Enhanced differences stayed within the 320×224 integer-scaled centre.

Two 180-frame D-pad replays reproduced the same guest hashes with the donor present and absent. An exact comparison of changed logical pixels at the following captures used the PC ground coordinates from the recorded Saturn VDP2 state, including the native tint. All changed samples matched.

| Route | Native camera origins | Changed samples, in capture order |
| --- | --- | --- |
| First active grid | (632,656), (704,656), (704,581), (704,581) | 33,704 / 35,828 / 45,004 / 44,996 |
| Kohran's turn | (584,704), (669,704), (669,629), (669,629) | 41,737 / 45,309 / 46,338 / 46,370 |

The updated runtime repeated the same 28,491-frame continuous Episode 2 route through Kohran's turn, with zero interpreted blocks and identical guest hash log SHA-256 `12cae74f096b5a5bff308994efce70ec40cef1525e9de663686e256903d136cf`. That headless replay verifies guest execution. The windowed comparisons above verify the host drawing.

The previous and updated renderers matched 60 guest hashes and the 1440p RGB capture on MAP01 in strict mode and on MAP21 in interpreter mode. The standard AOT build stops on both binaries at the same untranslated EVT21 block `00205C38`; MAP21's earlier strict proof used its independent overlay.

At verification the project occupied 63,790,174,764 logical bytes, above its 20 GB limit. The delivered development ZIP remained 6,315,009,692 bytes.

Local scripts, input, hashes and captures are under `local/work/codex-tw2-fullscreen-bbg/chapter2-attribution/` in the `map02-1440p`, `map02-1080p`, and `map02-motion-states` trials. Package and full chapter exit verification remain open.
