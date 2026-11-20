# Derived tactical ground keys and geometry

The inventory in config/hd-tactical-ground-table.json covers 27 Saturn map files with PC donors. The two disc copies of MAP01 share a row. Twelve rows describe existing HD grounds. Eleven candidate rows record a source-4 key, donor size and hash, and proposed world dimensions. MAP10 and MAP19 retain native ground after composition review. MAP23 needs a separate assembly method.

The runtime recognizes the ground using FNV-1a of the first 8,192 VDP2 pattern-name bytes at page 0x40000. For these maps the offline tool derives the page from the BIN. It adds 0x00600000 and slot 1's cell count (size divided by 32) to the names in slot 5, then hashes the top-left 64 columns by 32 rows as big-endian 32-bit words. MAP21 retains its individually observed key.

## MAP03 at 1440p

MAP03 has 626 square 64-pixel donor tiles on a 2,048-pixel placement plane. Its derived key 3150DAC84F35E1AE matches the natural Episode 3 disc 1 Tsukiji battle reached by saving after the sortie card and continuing from File 1 after restart. Patch 0262 binds that key to the PC ground with the existing source-4 sampler.

Six 180-field replays at 2560 × 1440 matched all guest hashes and save memory. At four camera samples, the donor changed between 1,900,800 and 1,930,680 pixels, all inside (320,48)–(2240,1392). Original matched pixel for pixel with and without the donor. Missing, truncated and disabled donor controls matched. The three recovered camera origins agreed with the registered atlas.

The first visual checks used the portable interpreter fallback. Strict replay stopped at EVT03 address 00209894 both with and without the ground. A relink with 76 observed EVT03 variants then passed 180 strict fields without interpreted blocks. Guest hashes, save memory and the four 1440p samples matched the portable runs. The checks start from a natural playable checkpoint. Cold entry and the rest of the battle remain open.

The v0.2.27 candidate contains the MAP03 patch and this observed AOT set. Its executable SHA-256 is `dd7965fd137544711356d3923ae7308ecfd5a1fe5de3bac53b7b98736c15bf72`. To reproduce the exact set on the owner machine, use the retained `local/work/codex-th1/map03-691/map03-v026/record.py` and `build-aot.py`. The builder checks each observed variant against EVT03 before linking and keeps its response file and verification receipts in the same directory.

### Cold EVT03 deployment

The `EVT03_MAP03` build registry now pins the union of 805 exact
offset/length ranges for the cold deployment and moving-camera route.
The owner disc provided every instruction byte. The new executable
adds 729 entries over v0.2.27, including the alternate entry at 0020AD24.
It completed 12,000 strict fields from power-on Continue → File 1
through selectable Sakura in MAP03. The interpreter replay matched
every guest hash, final SRAM and the final PNG. The strict endpoint
still has VDP2 key 3150DAC84F35E1AE. The tested executable is
`cb632a30be34033922760f90465d2f8baf28ad832f56b7a454a33dae3ac3ba0f`.
Receipts and rebuild commands stay in
`local/work/codex-th1/map03-691/map03-v027-cold`. The same
12,000-field test passed on the combined
[v0.2.28-alpha](../releases/v0.2.28-alpha.md) binary. The remaining
battle is pending.

Candidate keys and dimensions are offline evidence. Runtime activation and package coverage require a separately verified draw.

Run these checks from the repository root.

```powershell
python tools/gen_tactical_ground_table.py --check
python -m unittest tests.test_gen_tactical_ground_table
```

To regenerate the table, supply --derive with --pc pointing to the donor root containing SAKURA2/MAP and --iso1 / --iso2 pointing to the prepared data tracks. The optional --inc exports candidate rows for inspection.
