# TS12 HD package gate

The public package validates the generated-art provenance in all four art
folders. Each episode must have a left and right 39 × 224 RGBA strip, and the
two strips must declare the same palette fingerprint. The package manifest
records the hashes of the approved art and language layers at their exact
release paths. The gate rejects stray PC movies and SPR images, prepared
game files, profiles and saves.

For a PC edition supplied as an extracted cabinet folder, setup reads
`MOVIE` beside the cabinets and writes the clips directly to the private HD
pack. The old helper moved the whole input folder into its temporary working
directory, which could delete the player’s clips when setup cleaned up. A
synthetic cabinet extraction reproduces the fault and checks both the input
clip and the resulting private copy.

## Validation

- `python -B -m unittest discover -s tests -p test_package_art.py -v`
- `python -B -m unittest discover -s tests -p test_taisen_setup.py -v`
- Staged locally with `tools/package_release.py` in directory mode using the
  existing v0.2.4-alpha runtime and a freshly frozen `preparar-juego.exe`.
  The staged manifest listed 132 files, plus the manifest itself.
  Verified 65 generated PNGs by manifest hash: 20 backgrounds, 19 PC
  background extensions, 25 screen images including all 20 episode sides,
  and one tactical extension.
- Ran `preparar-juego.exe prepare` with explicit fresh home, game and HD
  destinations, both original Japanese Saturn discs, and an extracted PC
  edition with `MOVIE`. The subprocess used a Windows-only `PATH` and an
  isolated temporary directory on the test host. Checked all six disc images
  against `parches/parches.json`, including the English and Spanish variants
  with the optional subtitle layers. The prepared pack had 19 background
  caches, 302 portraits and 2,375 PC files. Its inventory matched the source
  files byte for byte, including all 52 clips and the 50 distinct clips named
  in the FILM map.

The staging test used an existing runtime to exercise preparation. Runtime
movie playback, cabinet extraction with a real disc copy and a separate
Windows installation were outside the staging test. No delivery archive was
created or published.

After removing both runs' regenerable disc and HD copies and the staging
tree, the workspace measured 45,835,825,716 bytes with hard links counted
once. This exceeds the existing 20,000,000,000-byte workspace limit. The
development ZIP measured 6,315,009,692 bytes. Trial logs, receipts and
presentation captures were kept locally.
