# Screen backgrounds

Generated with built-in ImageGen using the PixelGen v1 workflow. Original reference layers remain local. `provenance.json` pins the selected files; the normal release accepts only these named generated assets.

OPENING and TITLE continue their native cherry-branch backgrounds. STATUS continues the lavender status-screen backdrop. PAUSE01 contains only the mint-green backdrop, blossom silhouettes and flowers; the character, logo and menu come from the player's native IC01 resource, never from a generated replacement.

The runtime normalizes OPENING, TITLE and STATUS to416×234 in their verified native palettes. PAUSE01 uses800×450, aligned with the original320×224 rectangle at240,113 and the same integer display scale. The player resource supplies the protected center and an eight-pixel palette-normalized join. This permits wider framing while preserving original artwork, menu geometry and fades.

Prompt summary for STATUS: continue the exact muted lavender/purple gradient and diagonal silhouetted cherry branches into16:9, with native pixel clusters and ordered dithering; no text, logos, characters or border. Prompt summary for PAUSE01: extend the mint/ivory paper and pink blossoms, then remove all generated characters and lettering so only a background texture remains.

LOADING is a provisional generated blue-violet tiled logo backdrop. The animated native column is preserved. Its tile phase at the protected-center join still needs visual refinement before a release claims seamless loading transitions.

The generated-only tactical strip is tracked separately in `assets/generated/tactical-extensions`; owner reference composites remain local. It is not part of this generated-screen allowlist.
