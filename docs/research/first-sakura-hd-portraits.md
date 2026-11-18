# First HD portraits of Sakura

The review approved Saturn identities `0013` and `0014` with PC atlases 18 and 19. The matching numbers helped locate the candidates. The approval was based on the expression, the pink outfit, the position of the features, and comparison of the atlas's three regions.

| Saturn identity | PC atlas | Base RMSE | First strip | Second strip |
| --- | ---: | ---: | ---: | ---: |
| `0013` | 18 | 0.058240 | 0.047862 | 0.043342 |
| `0014` | 19 | 0.057876 | 0.047865 | 0.042901 |

The scores compare the 40×80 Saturn grid against an area-reduced 80×160 PC atlas for the analysis. Swapping 18 and 19 worsens all three regions for each identity. Gray-outfit atlases 54 and 55 share the corresponding strips, with a visible difference in the base outfit. Shifting either approved candidate by one pixel on any axis worsened the regional fit. The variants keep the framing with `dx=0` and `dy=0`, integer densities 1× and 2×, and the exact Saturn mask of 3,200 and 12,800 opaque pixels respectively.

## Preparation and playback

The [review registry](../../config/hd-portrait-reviewed.json) fixes the KAO file hashes, the Saturn atlases, and the RGBA PC pixels, both raw and prepared. The tool verifies the registry, copies the images and indices from the source project, and publishes a new project. If export is requested, the pack is created inside the new project.

```powershell
python tools/apply_reviewed_hd_portraits.py --output-project local/work/sakura-hd-193/project.json --export
```

In a separate checkout, `SAKURA_OWNER_ROOT` can be set and an absolute output path used under its `local/work`. The command uses the existing exporter and leaves the original project ready for other review flows. `match_hd_assets.py --workspace local/work/sakura-hd-193` opens the project with the `--serve` option. The private 193-portrait checkpoint keeps the 19 prepared backgrounds; the delivered v0.1.2 package is still documented with 191 portraits.

## Execution evidence

Build v0.2.0-test.1 recognized `0013` and `0014` in native chapter 1 states at 2560×1440, density 2. 420 frames per identity were compared against the 191 and 193 packs. The game's hashes and six native RGB samples matched. The GUI changes on frame 8 fell within the portrait box, in the half-open rectangle (404, 996) to (644, 1284). Both trials ended with zero interpreted blocks.

The run observed the base of both portraits. The PNG review verified the presence, fit and mask of both strips. Substitution during blinking, mouth movement, and their combination remains to be observed. The checkpoint covers 193/304 global identities and 83/123 from chapter 1, with 386 valid variants and 111 identities still pending in the catalog.

The prepared pack's fingerprint is `24286afce17baeb43d0744b0f4b8171c8d044af02462d660ff71da2272d287b5`. Captures, states and the local validation receipt are kept outside Git.
