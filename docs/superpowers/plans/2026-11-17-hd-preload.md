# Optional HD preload

Option on the launcher's HD MOD card and Display settings. Disabled by default. When enabled, available backgrounds and enabled HD portrait variants are loaded before the first frame is ready. Visible bar and counter in the title; the launcher keeps its wait until confirming the first frame. CPU/renderer stay on the window thread; it does not change the guest CD's timing.

Backgrounds keep their validated cache and their SDL upload on the main thread. Portraits verify size/hash/dimensions before decoding; preload keeps both densities in memory, max 394 pairs (~25MiB of pixels). Without preload, only one atlas stays active. A failed resource keeps the original fallback. PC backgrounds are skipped if disabled. Memory is freed on window close/recreate.

Evidence: identical scene between normal and preloaded loading. Isolated test with the full pack available: 38/38 backgrounds, 382 variants of 191 portraits, 0 errors. Real tests at 720p, 900p, 1080p, 1440p, 2160p and ultrawide 3440 before removing ultrawide support; changes limited to the portrait. A corrupt PNG or missing manifest keeps the exact original capture. This does not equal the full NC body pack nor validation of the whole campaign.
