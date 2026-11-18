# HD matching tool and Saturn application

Authorized scope: a program to match most assets and fit them into the recomp, adapting to resolutions; text review within its box. Runs on the existing development branch, with no agents and without altering v0.1.5.

## Contracts

- Original inputs are read-only. Matching project, previews, and derivatives live under local/. No proprietary sprites uploaded.
- Normalized image comparison for analysis; game output uses grids and integer scales. Coordinates/anchors stored in native units.
- Density variants 1 and 2: if the viewport scale is odd, variant 1 is used; if divisible by 2, variant 2 may be used. The set's maximum size is preserved and no fractional presentation factor is introduced.
- Proposals by visual distance and margin over the second candidate. Ties/conflicting identities require review. Similarity is not presented as a probability of correctness.
- Local GUI to compare, pick a candidate, adjust anchors, and export. Export produces a JSON project and an INI manifest with native identities and prepared files; atomic publishing.
- Runtime: only replace identified textures with complete/usable resources. Validate dimensions, versions, paths, checksums, and known PC origin. Fallback to the original on any failure. Renderer resources only on their thread.

## Tasks

1. Text: validate real ink against the interior 56,160–304,208; avoid partial substitution of the last letter and crop the enhanced text to the projected interior. Test edges and scales 720p/1080p/4K/ultrawide; test a real scene.
2. Core matching in tools/hd_matching.py: prepare a native FCE catalog using the palette of a validated local state and a PC catalog of images from the existing decoder; ranking, margins, hashes, and integer variants. Synthetic tests for identity, ambiguity, anchors, alpha, and scales.
3. Interface in tools/hd_matcher_ui.py and tools/match_hd_assets.py: per-resource review, next pending, keyboard, persistence, and export of accepted results. Loopback-only server; images under local catalog. Local BAT to open it.
4. First consumer: narrative portraits 40×48 and patches 40×16 identified by native bytes, palette, and mode. Joint application of known pieces; don't half-replace a portrait. Validation in a real scene and menu options.
5. Extend the same pipeline to NC bodies once their parts/anchors are verified; don't interpret table differences as equivalent indices.

## Initial evidence

The portrait from Iris's scene matches by bytes with native identity FCE 0x0015. Its capture palette reproduces the original colors and its best PC candidate is 20. Across 304 portraits, visual ranking 20×40 returns hypothesis ID−1 as the top option in 293 cases and within the top 5 in 304. With threshold 0.06 and margin 0.008, 194 cases are preselected and all of them agree with that hypothesis. This is evidence for prioritizing review, not artistic verification of every pair.

Ruling: start applying this to portraits, whose native format and link to a real texture are already demonstrated, while the matcher accepts PNG catalogs for other resources. Full bodies are not declared integrated just because the catalog exists.


## Verified progress

The HD font now keeps a uniform transform across the whole typeface, referenced to the original's uppercase height. The native 8-pixel advance is kept; narrow letters are not individually widened. It is cropped to the dialogue interior and the glyphs' real ink is checked. The original-text option remains available.

The catalog holds 304 native identities and 394 PC candidates. After discarding conflicting proposals, 191 remain preselected and 113 pending. These are not 191 approved artistic comparisons.

Local usage: `python tools/match_hd_assets.py --serve --open`. Lets you compare, adjust native offsets, accept/skip, and export. The pack only uses the owner's local resources and validates identity, dimensions, and hashes. Density variants 1/2 preserve integer scaling. NC bodies still need their format and anchors verified.

First real scene: replacing portrait 0x0015 at 1280×720 changes exclusively the rectangle (202,498)–(322,642) relative to the capture without HD. The rest of the scene stays identical. Expressions are identified by bytes, including patches with transparency; ambiguous matches keep the original. This evidence does not validate the whole campaign or every expression.

Correct native build and 24 correct frontend/matching tests. Still pending: full set validation, artistic review, and additional resolution/expression tests.
