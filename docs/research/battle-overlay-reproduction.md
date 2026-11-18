# Reproduction of the battle AOT expansion

`tools/discover_battle_overlays.py` replaces the private trial that expanded the K001–K019 family after the Sumire lock at 060783FC. It does not modify discs, the active discovery base, nor executables. It reads a seed base and emits a candidate and its manifest in a new private directory.

The project's static analyzer and the pinned SDK are reused. Modules must belong exactly to the known family, have bounded size/alignment, and absolute pointers that support the observed base 06078000. The analyzer cannot emit bytes or addresses outside the module. Identical modules are deduplicated, but distinct variants are preserved at the same CPU address, as are all provenance profiles. This generates candidates; it does not certify that every entry is executed code.

## Reproduced result

Starting from the private pre-fix seed of 580,328 entries, 18 unique modules and 33,696 new candidates were recovered: **614,024 entries**, exactly the same set used by the test.1 build. No entry was missing or extra. The [manifest](battle-overlay-reproduction.json) keeps hashes, profiles, and counts; the code bytes stay in `local/work`, outside Git.

The shared executable was neither regenerated nor replaced for this check. Sumire's fix and its AOT/interpreter parity were already documented in [chapter 1 progress](chapter1-battle-progress.md). This reproduction removes a dependency on private scripts by rebuilding that fix; it does not prove the full campaign nor resolve new modules from other chapters.

## Usage

Example from the root of a checkout with both own images prepared:

```powershell
python tools/discover_battle_overlays.py `
  --disc "disc1=local/prepared/disc1/Track 01.iso" `
  --disc "disc2=local/prepared/disc2/Track 01.iso" `
  --seed-blocks local/work/sakura/blocks-before-k-family.txt `
  --output local/work/battle-overlay-reproduction
```

For a worktree without its own SDK, `--sdk-root` can point to the existing dependency, and the image/seed arguments can be absolute paths. The SDK must have the pinned commit. The recorded trial also included the two available Japanese profiles to cross-check variants. The manifest distinguishes the images actually included in each run.

The output is not automatically promoted. Compare the set, review the manifest, and coordinate regeneration/compilation before replacing `blocks.txt`. Never do this while another collaborator is using that base or compiling. The CLI rejects existing destinations and destinations outside `local/work`.

Tests: `python -m unittest discover -s tests -p test_battle_overlay_discovery.py -v`. They cover family selection, sizes, pointers, variants, rejection of invalid candidates, and validation of the seed without modifying it.
