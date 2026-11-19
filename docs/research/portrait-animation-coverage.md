# HD portrait and animation coverage

The audit compares the Saturn and PC atlases against the prepared HD pack. It can also reconstruct the portrait described by local states' VDP1 commands and compare it against native 320 × 224 captures. It reads inputs in place and writes reports to a new directory under `local/work`.

```powershell
python tools/audit_portrait_coverage.py --states local/work/sakura
python -m unittest discover -s tests -p test_portrait_coverage.py
```

Use `--output` with a different directory to repeat the run. Other inputs can be specified with `--project`, `--pack`, and `--disc` repeated per disc. `portrait-coverage.csv` is used to filter identities by chapter, state, or region. `portrait-coverage.json` adds the source FCEs, scores, alpha measurements, and comparisons against states and captures.

## Catalog coverage

The auditor compared the project's 304 40 × 80 Saturn atlases against the FCEs on both discs and verified the 394 80 × 160 PC atlases via SHA-256, with continuous indices from 0 to 393. It also verified the original KAO file. In the pack, it validated the binary catalog and the FNV hashes of the 382 PNG variants. When comparing their RGBA pixels against those regenerated at 1x and 2x density, the 382 variants matched. None has a pixel with partial or zero alpha where Saturn requires opacity.

Chapter 1 covers the union of identities found across the six FCEs `0100`, `0101`, `0102`, `0103`, `0108`, and `0109` on both discs.

| Scope | Saturn | HD base | HD eyes | HD mouth | Both HD strips available | PNGs verified | Pending |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Catalog | 304 | 191 | 191 | 191 | 191 | 382 | 113 |
| Chapter 1 | 123 | 81 | 81 | 81 | 81 | 162 | 42 |

Each valid atlas has 48 base rows and two 16-row strips. The "both strips" column confirms their availability in the PNGs. Their simultaneous drawing depends on the game's commands and the displayed frame. The `nearest_strip_rows` field measures the distance between color indices per placement row and serves as a hypothesis about each strip's destination.

The 191 automatic pairings respect `PC index = Saturn ID - 1`. Among the pending ones, the top visual candidate by ranking respects that rule in 102 of 113 rows, including 38 of the 42 in chapter 1. In chapter 1, the four pending entries with a different candidate are `004f`, `00ef`, `013b`, and `013c`. No pending entry got a zero distance. The index provides an additional signal for reviewing each portrait across its three regions.

Chapter 1 pending ranges in hexadecimal

```text
0013-0014 001d 0040-0041 0044-0045 0049-004a 004f 005b 0064
006b 006d-006e 007f 0088 0091-0096 0098 009b-009c 009e 00a1
00c0 00c2-00c3 00c5 00ee-00f0 00f2 00f4 013a-013c 013f 0169
```

## Saved states and Yoneda's portrait

Among the 160 available states, 79 had a portrait command at the expected position and used the expected palette. 63 unique matches were obtained against the HD catalog and 16 had no match. The 16 unmatched cases had an exact Saturn identity among the pending ones. Six states were captured with one active strip and none with two. The states `maria-face-discovery.state` and `maria-exit.state` show, respectively, the eyes and mouth of `0176` at the same relative row 16 at different moments.

Yoneda's civilian expressions `00e2–00e7` have both HD PNGs complete. Both strips of each Saturn atlas have their minimum distance at relative row 8. The eyes command of `00e2` confirms that row in `office-return-6000.state`.

| Sample | Saved command | Comparison with the capture |
| --- | --- | --- |
| `office-return-3000.state` | Base `00e3` | The 1,920 pixels match the Saturn palette colors. |
| `office-return-6000.state` | Base `00e2` and eyes at row 8, an HD match | 1,901 pixels differ from the unblended base and 1,904 from the composite of the saved commands. The 1,920 pixels match when blending the base without the eyes strip toward white. |

The 6000 sample exactly satisfies `(base_channel * 27 + 248 * 5) >> 5` per channel, with RGB555 white expanded to 248. The state describes the pending VDP1 commands. The capture shows the base portrait under blending, consistent with an offset between the saved commands and the presented image. The `PortraitPixelsVisible` guard requires equality with the unblended Saturn color and would therefore reject that portrait. The atlas, palette, and byte-level recognizer did pass the checks against the saved commands.

The report includes 42 capture/state pairs. In 36 pairs, the base matches the capture unblended. Three show exact blending toward white with weights 5, 15, and 25 over 32. The remaining three require more evidence to explain their differences. The audit validates these saved frames and atlas availability. The frequency of these dropouts during a continuous run is outside this sample.

## FCE atlas attribution (TP6)

`audit_portrait_coverage.py` now writes `fce_atlases` (per `disc:file`, the identities each FCE holds) and `hd_chapter_coverage.py` uses it for the atlas-file rows of `portraits`. In the initial 112-atlas snapshot, 16 held only identities in `config/hd-portrait-recipe.json` (`hd`), 4 are empty 160-byte atlases (`excluded`), and 92 also hold `0169` (four also `00a1`), the only two identities outside the runtime recipe, so they stay `unknown` with the `uncovered` list. The 302 identities are `hd`; `00a1` (strips swapped, T45) and `0169` (different PC card design) remain T52.


## Residual portraits 00a1 and 0169

The stock 40×80 atlases agree byte-for-byte across the two prepared
discs. `00a1` occurs in `0102FCE` and `0700FCE` on each disc, and
`0169` occurs in 46 atlases per disc. Their whole-atlas FNV-1a
fingerprints are `12CC7FF05270E3C5` and `7D561BC49817D46E`.

**00a1.** The base is the same Iris expression as KAO.SPR subimage 160,
which ranks first out of 394 PC bases with the decoded native palette
`B20B13D34869E11A`. Holding the base fixed and exchanging the two
32-row PC strips reduces their RGB RMSE from 47.93 to 31.06 and from
48.07 to 33.57 on the 40×80 Saturn grid. The prepared alpha at both 1×
and 2× exactly matches the Saturn mask. Both native strips independently
best match the region starting at base row 16. The archive review
checked 438 candidate state files and found no exact active `00a1` portrait
command. The coverage register records the pairing. The swapped
strips still need a scene that exercises each of the two commands.

**0169.** The Saturn portrait shows the troupe emblem. The two
40×16 strips both equal the base region at row 16 exactly. In three
archived states, an active strip starts at row 16 and matches both
native strip payloads, so those commands reference the unchanged
base region. KAO.SPR indices 348 and 360 have the same PC base,
also identical to KAO_P.SPR subimage 24. These alternatives use the
same emblem motif with different proportions and framing. Their PC
strip data differs from the static native region. The register records
the examined PC candidates and retains Saturn artwork.

At this stage both portraits were outside the runtime recipe. The
[chapter 1 closure](#chapter-1-portrait-closure) applies the later decisions.

The measured workspace was 60,240,718,418 logical bytes with hard
links counted once and reparse points excluded, above the 20 GB cap.
The delivered development ZIP remains 6,315,009,692 bytes.


## Chapter 1 portrait closure

The reviewed recipe now prepares Iris `00a1` from KAO.SPR index 160.
It exchanges the two 32-row PC strips before applying the Saturn
alpha mask. The PC base and the native coordinates stay fixed.
At both integer densities the review pins the expected RGBA after
the reorder. The preparer also checks the original Saturn bytes and
the source KAO archive. An identity that fails its content check
retains the native portrait.

The production preparer produced 303 identities. All 604 PNG
variants for the previous 302 were byte-identical to the baseline.
The existing pack auditor checked the final 606 variants against
both discs and the 394 PC sheets, with zero validation errors.
The runtime matcher selects the 00a1 base and its two independent
row-16 strips uniquely across all 304 native atlas payloads.

Three test fixtures take the exact 00a1 index bytes and place them
in existing saved portrait-command slots. An unchanged development
runtime draws the base and, in the other two fixtures, each strip
at row 16. All 69,120 pixels in each 240×288 portrait rectangle
match the expected prepared composition at 2560×1440. Guest
hashes match with the pack enabled and disabled throughout the
40-frame base and two 12-frame strip replays. Early Enhanced
captures show each strip active, with every changed pixel confined
to the verified portrait rectangle. The strip controls in Original
match in RGB with the pack present and absent, and
each run reports zero interpreted blocks. These fixtures verify
the three draw paths. The natural 00a1 chapter scene remains
to be observed.

The owner decision keeps the Saturn emblem `0169` by design.
There are 303 HD identities and one native choice. Coverage now
closes the six chapter-1 FCE atlas entries. Across both discs,
108 nonempty atlas entries contain prepared identities and any
explicit native choices. The four empty atlas entries remain
excluded. No release package was built.

At block close the workspace measured 62,111,789,211 logical bytes
with hard links counted once and reparse points excluded, above the
20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.
