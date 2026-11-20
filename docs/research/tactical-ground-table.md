# Derived tactical ground keys and geometry

The inventory in config/hd-tactical-ground-table.json covers 27 Saturn map files with PC donors. The two disc copies of MAP01 share a row. Eleven rows describe existing HD grounds. Twelve candidate rows record a source-4 key, donor size and hash, and proposed world dimensions. MAP10 and MAP19 retain native ground after composition review. MAP23 needs a separate assembly method.

The runtime recognizes the ground using FNV-1a of the first 8,192 VDP2 pattern-name bytes at page 0x40000. For these maps the offline tool derives the page from the BIN. It adds 0x00600000 and slot 1's cell count (size divided by 32) to the names in slot 5, then hashes the top-left 64 columns by 32 rows as big-endian 32-bit words. MAP21 retains its individually observed key.

MAP03 has 626 square 64-pixel donor tiles on a 2,048-pixel placement plane. Its derived key 3150DAC84F35E1AE matches the natural Episode 3 disc 1 Tsukiji battle reached by saving after the sortie card and continuing from File 1 after restart. The native 2560 × 1440 control shows Sakura selected. A donor comparison is pending, including placement, seams and foreground during camera motion. Strict native replay on the tested 680541 binary stops at EVT03 00209AAC after 6690 fields; the 1440p control uses interpreter execution.

Candidate keys and dimensions are offline evidence. Runtime activation and package coverage require a separately verified draw.

Run these checks from the repository root.

```powershell
python tools/gen_tactical_ground_table.py --check
python -m unittest tests.test_gen_tactical_ground_table
```

To regenerate the table, supply --derive with --pc pointing to the donor root containing SAKURA2/MAP and --iso1 / --iso2 pointing to the prepared data tracks. The optional --inc exports candidate rows for inspection.
