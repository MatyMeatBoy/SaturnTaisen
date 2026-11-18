# Widescreen floral background — v0.1.1

## Status and authorization

The user **preliminarily** approved the second proposal generated on 2026-11-17 and then indicated they **prefer the first variant for having more flowers**. The first becomes the chosen artistic reference: keep its greater floral density while fixing the pixel finish. It is not yet the final asset nor integrated into the runtime. Keep v0.1.0 intact.

Local files, kept out of Git like the game-derived resources:

- Extracted original: `local/work/v011/layers/movie-layer5.png` (320×224).
- First proposal, now preferred by the user: `local/art/v011/floral-day/proposal-01.png`.
- Second proposal, preliminarily approved before that preference: `local/art/v011/floral-day/proposal-02-preliminary-approved.png`.

Generated via the built-in image_gen tool, with no external API configured for the project. Instruction: extend the original bitmap to 16:9, preserving the central composition, five-petal pink flowers, the diagonal green/cream/pink gradient, and the pixel pattern; no text, frames, characters, or UI. The second pass explicitly asked to preserve the original positions and avoid vector edges and paper texture.

The output still reinterprets parts of the center and its texture: the approval is of artistic direction, not a check of exact pixel preservation. Do not advertise this proposal as pixel-perfect. The production goal is a logical 416×234 canvas (exact 16:9), with the original 320×224 centered at (48,5), with verified continuity across its four seams. Do not convert to that resolution via smooth interpolation.

## Separation evidence

The renderer's plane capture shows the daytime background on NBG3, video on RBG0, and frame/emblem on VDP1. The Iris scene uses a different, nighttime floral palette, and combines character, text, and frame on VDP1. Plane separation does not imply automatic separation of every UI element.

The daytime background must not replace the nighttime variant nor appear in scenes whose composition has not been identified. The translation tools contain subtitle images: do not crop video assuming it always lacks text.

## Agreed scaling

The background uses square pixels, nearest-neighbor, and a positive integer factor. To cover a W×H output with a B×C background: `k = max(1, ceil(W/B), ceil(H/C))`; center Bk×Ck and crop only the decorative excess. This covers 16:9, 4:3, ultrawide, and arbitrary windows with no fractional scaling or distortion. The crop does not apply to video, text, or characters.

Playable content uses an independent integer factor, the largest one that lets its whole extent be shown. The background may need a larger integer to cover the window; do not shrink the content to force it to share a factor with the background. Preserve the Original option and all scenes not yet identified.

Pending: finishing the asset at logical resolution, verifying seams and palette, compositor integration, and real-output testing. This note does not record those tasks as done.
