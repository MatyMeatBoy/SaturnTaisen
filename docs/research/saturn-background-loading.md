# Saturn background loading and its HD mod

Priority confirmed by the user: finish Saturn first; PC execution and translation are left for later. PC resources used by the Saturn HD mod are within scope for this work.

## Reproducible comparison

Base 77b43c6, SDK pinned by config/dependencies.json. Tool `tools/benchmark_backgrounds.py`, Clang 23.1.3, optimization O3 and SDL software renderer. The same loaders used by the Saturn presentation are invoked. Inputs: 19 unique Saturn backgrounds and 19 HD pack alternatives. Originals 90/91 are identical and are not counted twice.

Baseline/change binaries, input/output hashes, and per-resource logs were kept. Three repetitions per condition, alternating order. Cold cache means an empty derived-background cache; the OS cache was not flushed. A concurrent run with the test suite was kept for correctness and excluded from the timing figures.

| Preparation of the 38-background set | Before | Change |
| --- | ---: | ---: |
| Median, empty derived cache |5.284s|1.911s|
| Median, prepared derived cache |0.279s|0.280s|

The 38 results are pixel-identical across all comparisons. These are component timings, not a full boot measurement, game frames, or CD wait times. The hot cache shows no overall improvement in this comparison.

## Verified changes

- Binary cache of prepared surfaces, with dimensions, defined byte order, version, exact size, and data checksum. Truncated, altered, or incorrectly-dimensioned files are rejected and regenerated. Temporary writes are published by replacement, preserving the previous file on failure.
- Migration of existing PNG caches. The original content and generated masters are not modified.
- Accelerated nearest-color search, preserving exactly the RGB metric and the first color on ties. Checked against exhaustive search for palettes of up to 1693 colors.
- Bounded reading of the master PNG and dimension check before decoding. Hashing and decoding use the same bytes read, avoiding mixed revisions if the file changes during loading.
- Test with a real night scene: a corrupted cache is regenerated, restores its bytes, and preserves the displayed background.

The final representation uses 8-bit palette or RGB555 when it exactly reproduces every color, with RGBA as a fallback. The set occupies 16,145,238 bytes versus 39,312,064 for direct RGBA. DEFLATE reduces it to 5,368,794 bytes, but raises the hot median from 0.251 to 0.290 seconds and preparation from 1.920 to 2.059 seconds: it stays disabled by default. Reading supports the previous cache version and rejects extra or truncated data. Numeric results and limits in `saturn-background-loading.json`; detailed evidence is local under local/work/background-bench and local/logs.

The OptiPort methodology was checked against 9673006504bf6712b320da70965bc3f65f2dd41a. Guest CD commands and timings were not changed.

## Final comparison and limits for the next stage

The independent final comparison, three alternated repetitions with 38 identical images, records 5.128 → 1.960 seconds with an empty derived cache, and 0.268 → 0.274 seconds prepared. No overall hot-cache improvement is demonstrated. The 64 tests pass; they include format round-trips, backward compatibility, corruption, and regeneration in a real scene. Results in `saturn-background-compression.json`.

An observation of the night scene at 1280×720 with Direct3D 11 records 55.374/5.277 ms of CPU to load the Saturn background cold/hot, and 61.309/12.559 ms for HD. Includes upload calls, but not GPU wait or frame-pacing proof. Work remains to avoid the first-use cost.

The observed system has a Ryzen 7 7435HS (8 cores, 16 threads) and an RTX 4060 Laptop. SDL compositing already uses Direct3D 11; Saturn rasterization remains on the CPU. Preparing independent resources is a candidate for bounded parallelism. Window-renderer textures must be created/used on their thread; CPU preparation must be separated before introducing workers. The SH-2s are not parallelized without preserving their shared memory and timing.
