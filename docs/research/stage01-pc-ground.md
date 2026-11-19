# Stage01 ground from the PC edition

Patch 0102 draws the verified PC ground in the Enhanced tactical presentation of the first battle. The owner-supplied HD pack already copies the PC SPR at the required path. The patch ships code and metadata. PC source art stays with the owner.

## Identification

Disc 1 `/SAKURA2/MAP01.BIN` has 320,128 bytes at LBA 231666 and matches the corresponding PC MAP BIN byte for byte. Its SHA-256 is `cf5ae6caf3f696f0ee8cab4ab1aa2b9af4b2d6abda129492f85b30de2450e5ec`. The PC MAP01.TAB identifies MAP01_A as ground, MAP01_B and MAP01.PRI as priority scenery, and MAP01_C1–C4 as the animated underlayer.

The visible Saturn ground is VDP2 source 4, page `0x40000`. Its pattern name fingerprint `1CAF3218B4B0F9F0` already identifies the map for the [right-side extension](pixelgen-v1.md). Source 2 carries priority scenery, source 3 carries animated water, and source 0 carries VDP1.

The loader accepts `SAKURA2/MAP/MAP01/MAP01_A.SPR` at exactly 1,786,365 bytes with FNV-1a `F7205A4FCC95F748`. The PC source SHA-256 is `5716a3b06fc3e6b049ec81467758921cf602c03fc708fc29f7c1dcfe81394d31`. Ordinal zero is 1408×960. The renderer samples one pixel from each 2×2 block into a 704×480 world grid at (0,0), using exact cyan as transparent.

## Presentation

The first matching Enhanced frame requests the asset once on a background worker when PC backgrounds are enabled and the tactical extension is present. Software composition checks the captured map signature, ground page, one-to-one line steps and supported color controls. The draw changes only opaque source-4 winners. Native sprite shadows, menu repair, priority terrain, water and other layers keep their composition. The existing strip starts at x=656 and y=24. The PC ground sampler stops before world x=656. Original uses its native presentation.

## Verification

- Seven profiles replayed 1,202 input frames from the fixed first-attack state. All guest hash logs matched. Original with and without the asset matched in RGB at passes 80, 360 and 900. Enhanced with the PC preference off, a missing asset, a truncated asset or a same-length corruption matched the Enhanced reference. The capture at pass 360 used native ground during the attack.
- A 450-frame camera-input movie ran from each of two first-battle states. Each route's Enhanced and reference runs had identical guest hashes. Each route produced ten positive captures at eight distinct origins, with changes on both sides. The capture verifier mapped every change to the exact PC sample at its current world coordinate before x=656. All protected sprite pixels matched the reference in RGB, including sprite pixels on both sides of the native rectangle. The existing integer viewport fit at ×4 in 1920×1080 and ×3 in 1440×900.
- The synthetic loader fixture covers file length, fingerprint, dimensions, cyan transparency, world sampling, and the map boundary.

The runtime comparisons use owner-provided game data in private profiles. The test builds requested strict-native mode and reported zero interpreted blocks. They also reported zero recompiled blocks, so the reported counters add no independent evidence of execution mode. This verifies a partial source-4 substitution and the sampled stretches of camera travel. Other maps, priority/water replacements, UNIT, the full battle and packaging remain open.
