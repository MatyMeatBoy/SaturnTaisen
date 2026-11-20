# Offline crop measurements for size-mismatched pictures

The coverage register has 19 `unsupported-size` entries across 13 distinct pictures. The six SAKURA1 BG files are byte-identical between the prepared English discs. The seven SAKURA2 BBG files are on disc 2. The measurements use one copy of each picture.

Run `python tools/measure_size_candidates.py --prepared <prepared-disc-root> --pc <extracted-pc-root> --out <json-output>` with NumPy and Pillow installed. The search samples a finite grid of independent X and Y scales. For each scale, it compares integer positions in a reduced grayscale image using normalized correlation. The selected crop is then rescored using the scroll generator's grayscale signature. Pan samples use a four-pixel stride and always include the final offset. When the stride lands on that endpoint, the sweep counts it again. `config/hd-size-candidates.json` records the scores, candidate full-frame boxes and sampled offsets below 0.90. These scores describe the sampled crops. They do not establish an upper bound for other transforms, prove geometric registration, or demonstrate an in-game draw.

| Picture | Saturn size | Sampled signature minimum / mean | Finding |
|---|---|---|---|
| BG1257 | 456 × 144 | 0.863 / 0.879 | Every sampled offset falls below 0.90. |
| BG1280 | 512 × 144 | 0.796 / 0.852 | Some sampled offsets fall below 0.90. |
| BG2093 | 320 × 144 | 0.951 / 0.967 | The isolated picture aligns. The witnessed dream retains its native composite. |
| BG2247 | 288 × 296 | 0.376 / 0.549 | The [witnessed theatre pan](bg2247-native-pan.md) retains the Saturn perspective. |
| BG2290 | 432 × 144 | 0.877 / 0.972 | Offsets 0, 4 and 8 fall below 0.90. A minimum supported offset and the proposed end clamp still need review across the actual viewport range. |
| BG2338 | 320 × 160 | 0.943 | The whole-picture candidate uses BG2238.SPR. It has no pan window or in-game crop witness. |
| BBG238 | 320 × 224 | 0.987 | High grayscale score, with a different pose and framing. |
| BBG239 | 320 × 224 | 0.848 | The candidate falls below the floor. |
| BBG240 | 320 × 224 | 0.985 | High grayscale score, with a different pose and framing. |
| BBG241 | 320 × 224 | 0.926 | High grayscale score, with a different pose and framing. |
| BBG242 | 320 × 224 | 0.915 | High grayscale score, with a different pose and framing. |
| BBG243 | 320 × 224 | 0.989 | High grayscale score, with a different pose and framing. |
| BBG300 | 320 × 224 | 1.000 | Broad gradient agreement gives no unique registration. |

The [BG2093 dream witness](bg2093-dream-transition.md) records per-line origins and a changing blend with a second source on disc 2. The offline fit measures the isolated art. A separate disc-1 appearance with a compatible composition remains unwitnessed. The [full-frame BBG review](bbg-full-frame.md) compared poses and framing directly. Its native disposition still applies.

The offline sweep requires no SDK change. A compatible live composition and a rebuilt replay are still required before activating a new substitution.
