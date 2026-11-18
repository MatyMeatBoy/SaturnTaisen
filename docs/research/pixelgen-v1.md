# PixelGen v1 — decorative extensions

Name confirmed by the user. Flow: generate with scene context, keep the original outside the approved zone, normalize to the native grid and compatible palette, review the seam at real size, and integrate at map coordinates. Offset and scale follow the map/camera; units, effects, and HUD composite on top. It does not add playable tiles or change collisions.

First approved asset: first battle's garden, right-side extension. The spurious water strip and the void are omitted; grass, wall, and cherry trees are continued. The first generation redrew the center and was discarded as a full substitution. Separate right-side context was generated and only x814-895 of the 940x448 diagnostic capture was incorporated. Pixels x0-813 remain original. Source, variants, and the hash manifest are in local/art/tactics/stage01; preview-16x9-v2.png is the approved composition. It contains data derived from the owner's media and stays out of Git.

Design limit: 16:9 maximum, ultrawide discarded. The full reference composition and its inputs remain local.

## Native anchoring of the first battle

Later calibration against the full VDP2 map: the reference capture has 940x448 output pixels, corresponding to 438x224 native pixels. Its map origin is 277,24, with 8825 local pattern matches versus fewer than 923 for the alternative scales tested. Therefore, it does not hold to treat both axes as a uniform x2 upscale.

The approved 814-895 strip is exported alone as 39x224 native pixels and anchored at 656,24. The native map ends at column 655; the extension begins outside it. `tools/export_tactical_extension.py` validates hash, dimensions, and the approved rectangle before producing the strip and its manifest, excluding all original context. The initial 41x224 export with origin 655,48 was provisional and has since been replaced before delivering a ZIP.

The consumer uses per-line scroll and the same integer as the scene. The renderer preserves the original center and rasterizes separately the sprites that cross the old boundary, with framebuffer and clip exclusive to the host. Unknown units and effects retain priority over the extension. Eight identified frames of the right-edge decorative water particles are filtered only in that region and in presentation; guest logic and its framebuffer remain intact. The camera during combat and the full chapter playthrough are still being verified.

Research: the SDK draws additional VDP2 on the GPU path, but hides the sides if it does not detect 3D ground. A temporary test removed that condition and revealed a real map beyond the native rectangle, along with spurious boundaries and content that require per-scenario handling. The original condition was restored; that test is not enabled in production. Primary reference: [SDK renderer](https://github.com/tmcleroy/satrecomp/blob/67a5fd456609f702817c08164e77e1420dc91138/video/renderer.cpp).
