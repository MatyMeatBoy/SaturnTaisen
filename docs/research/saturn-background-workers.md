# Multi-core preparation of Saturn backgrounds

CPU preparation was separated from the loaders' texture creation/upload. Surfaces belong to the task that creates them and are destroyed after preparing the cache; textures remain on the window thread. Workers own copies of their inputs and do not access guest state, the renderer, or save games.

## Measured comparison

Same executable, resources, and quality; 19 Saturn backgrounds and 19 HD alternatives for Saturn. Three repetitions per condition in alternating order, with prior warm-up. The 38 RGBA hashes are checked against the sequential binary kept before this split. Machine: Ryzen 7 7435HS, 8 cores/16 threads, RTX 4060 Laptop.

|Workers|Empty derived cache|Prepared|Peak working set|Peak private commit|
|---:|---:|---:|---:|---:|
|1|2.102s|0.262s|23.9 MiB|17.7 MiB|
|2|1.147s|0.158s|33.2 MiB|29.7 MiB|
|4|0.676s|0.110s|54.7 MiB|53.0 MiB|
|8|0.478s|0.104s|91.1 MiB|95.7 MiB|

Memory: median of the process peaks across the three cold preparations; not VRAM nor full-game memory. Measured via GetProcessMemoryInfo. Cold cache refers only to the derived cache, without flushing the OS cache. These CPU timings exclude GPU upload, frames, and guest CD wait.

During gameplay up to four workers are used, reduced according to the number of logical processors, to leave headroom for logic/audio. Pre-preparation uses up to eight. `SATRECOMP_BACKGROUND_WORKERS=0..8` allows diagnosis and disabling. The queue is bounded by the recognized theme catalog and is released when finished. It does not retain an extra CPU copy of all backgrounds.

## Integration and validation

Enhanced mode prepares later themes' caches after loading the current scene. It only attempts enabled HD alternatives. Synchronous loading preserves decisions and the scene fallback; the speculative task only creates caches. On window close/recreate, pending work is canceled and in-progress tasks are joined before closing SDL. Decoding in progress finishes normally; its duration is bounded by the accepted input sizes.

`--prepare-saturn-backgrounds CUE CACHE_DIR` and `--prepare-pc-backgrounds ROOT CACHE_DIR` prepare the corresponding 19 unique themes without running guest code or using the renderer. The second option continues to check all owner identities.

The real test at 1280×720 compares the full image with 0 and 4 workers: exact equality; 1 against 19 valid caches at the end. Cancellation, join, isolated failure, restart, and pool limits are checked.

A test with eight producers on the same path reproduced a Windows access-denied error during replacement, because a reader could have the destination open. Publishing accepts the existing result only if it passes a full read and matches pixel-for-pixel the surface being published. If it does not match, it still returns failure. Temporaries are cleaned up and the original load remains available.

The final composition already uses Direct3D 11. This does not turn the Saturn rasterizer into a GPU path nor prove frame pacing: the first active load may still require synchronous preparation. The full campaign and the real disc swap remain pending.
