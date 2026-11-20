# TS12 HD package gate

The active public package requires both generated layers for all ten episode cards. Each 640 × 360 surround has a transparent center and is paired with an approved Spanish lettering layer. The gate validates each layer against its provenance, rejects obsolete side strips, and pins the files at their release paths. It also validates generated backgrounds, PC background extensions, and tactical extensions from their own provenance manifests.

The final staged-tree check requires exact source hashes at these paths under `data/`.

- `config/hd-scroll-pictures.json` and `config/film-fad-map.json`.
- `preparar-juego.exe`, `herramientas/unshield.exe`, and `herramientas/xdelta3.exe`.
- `licenses/unshield-MIT.txt` and `licenses/xdelta3-Apache-2.0.txt`.

The scroll JSON describes the source scroll rows. The renderer uses a generated table compiled into the runtime. The film JSON identifies eligible clip starts. The public release rejects stray MPG, MPEG, CPK and SPR files, prepared game files, private HD resources, profiles and saves. Setup copies PC clips from the owner's edition into the private HD pack, including `MOVIE` beside an extracted installation cabinet folder.

## Gate verification

### v0.2.26-alpha

The published helper built a fresh private installation from both Japanese discs
and the extracted PC edition. All six data tracks matched their release digests,
and all 2,375 PC files matched the source by SHA-256, including 52 videos.
Preparation produced 19 background caches, 304 portraits (including 0169),
ten localized episode centers and two presentation previews. The published ZIP
passed all 166 manifest file hashes.

The packaged RecompLauncher profile's prepare command produced all four expected
CUEs. Its `--no-launcher` command started the prepared Spanish disc and rendered
240 fields. This exercises the bundled commands. A separate RecompLauncher
desktop installation was outside this test. Repeating preparation exposed a
progress regression from 98% to 97%. The source fix was retested against the
same installation and now reports 50%, 98%, 98%, 100%.

The package-art tests checked the twenty approved public card layers, staged recipe/tool paths and hashes, missing and modified files, and the rejection of stray movie data. The release-marker and synthetic setup suites exercise the existing development-state marker and private PC clip extraction. A separate clean-machine package build and preparation run remain open.

## Earlier staging evidence

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
