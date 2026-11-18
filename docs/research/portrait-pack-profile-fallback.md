# HD portrait pack selection

The runtime first evaluates the catalog at `user/mods/hd-portraits`. If that candidate fails, it evaluates `hd-resources/portraits` as the bundled catalog. It publishes the path and data only after validating the candidate. With a verified original KAO, it keeps the personal mod's priority. With prepared resources, the receipt must match the source, the identity count, and the selected manifest's fingerprint. If both candidates fail, the native portrait is kept.

Before the change, the runtime tried the bundled catalog only when the personal manifest could not be read. A personal manifest that could be read and then failed when compared against the receipt left the game without HD portraits. The synthetic test reproduces two causes, a stale identity count and the same count with a different manifest. It also covers the empty profile, the malformed manifest, the profile that matches the receipt, and the case where both catalogs are invalid.

With `SATRECOMP_HD_STATS=1`, the log indicates whether the profile or the bundled catalog was rejected and gives the reason. Validation of each PNG when preloading or displaying it keeps its behavior.

## Verification

- The synthetic test failed with the previous header. With the change, both late rejections select the four variants of the bundled catalog.
- A direct fixture was compiled with Clang, SDL, and the SDK reader. In a test with the owner's original KAO, the one-identity personal mod kept priority over a two-identity catalog.
- With the catalog of 191 as the profile input and the prepared pack of 201 as the bundled input, the read-only fixture logged `prepared count mismatch`, `records=201 source=prepared`, and `portrait preload: variants=402 failed=0`. This test exercised the real PNGs. Path selection was verified afterward in the integrated build described below.
- The v0.2.0-test.2 ZIP was published before this change and keeps its content.

## Integrated build and parity

Patch 0047 on top of the registered tree 0001..0046. Candidate 674,023 blocks, SHA256 `cdedbb966ea5222d55898c50c7b89303fd53eb23c2ed19f3a391308f54f07897`. It was compared against the test.2 runtime across four profiles: catalog 191, catalog 201 with a different fingerprint, empty profile, and a valid copy of catalog 201.

Eight runs of 90 frames at 2560×1440. The two stale profiles went from 0 to 402 preloaded variants with no failures. The 90 hashes per case and three native RGB captures per case matched; all finished with zero instructions interpreted. In both corrected cases, the only GUI difference versus test.2 was the portrait, within `[404,644) × [1090,1378)`. The empty and valid profiles kept the identical GUI. The four new profiles showed exactly the same GUI as the empty profile with 201.

Private evidence: local/work/portrait-fallback-runtime/result.json and its logs/captures. The composite-tree validation and two portrait fixtures passed. The shared CMake recovered its usual output after compiling the isolated candidate. The deferred failure of a PNG after accepting the catalog remains outside this fix; per-image-file fallback is not promised. The change is tested in development, not included in test.2.
