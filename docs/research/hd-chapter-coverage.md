# HD coverage by chapter

[Chapter coverage JSON](../../config/hd-chapter-coverage.json) combines the two-disc scene index, the portrait audit and the reviewed replacement catalogs. The chapter rows follow the Continue-screen evidence in [the chapter sweep](chapter-sweep.md). Chapters 6 and 7 were observed on disc 1. Chapters 8 through 10 were observed on disc 2.

An asset can have an HD replacement and still lack an attributed chapter. The "association" field distinguishes assets seen on screen, files found resident in RAM, and candidates inferred from episode title numbering or portrait atlas membership. A portrait found in an atlas is eligible to appear in that chapter. Individual appearances still need a trace. The unassigned section preserves disc inventory entries whose chapter remains unknown. Empty category lists flag gaps in chapter evidence, and no counts here certify a full chapter or change a release package.

The replacement status follows the compiled scene table generator, the portrait recipe, film FAD mappings and the documented NC draws. The 45 eligible disc/FAD starts correspond to 44 distinct movies because MOVIE015 occurs on both discs. Alternate film cuts keep their Saturn picture and audio. The stage 01 extension is listed as evidence of the first tactical map; the generated side art does not replace the whole map.

To regenerate, build the enriched scene index as documented in [Scene tagging](scene-tagging.md) and run the [portrait audit](portrait-animation-coverage.md). Pass the resulting directory and report:

```powershell
python tools/hd_chapter_coverage.py --index local/work/scene-index-later --portrait-audit local/work/portrait-coverage-worker/portrait-coverage.json
python tools/hd_chapter_coverage.py --index local/work/scene-index-later --portrait-audit local/work/portrait-coverage-worker/portrait-coverage.json --check
python tools/build_hd_progress.py --check
python -m unittest discover -s tests -p "test_hd*.py"
```

The progress panel counts accepted matches, source-level integration and in-game validation separately. Its updated scene-image count uses distinct PC filenames, while the chapter index lists Saturn files by disc and FILM streams by disc and offset. The NC panel uses Saturn body packages as its unit and counts six integrated bodies with documented draws. A measured preparation count or a complete in-game verification count is still pending in these updated categories.

## Status vocabulary (corrected 2026-11-19)

`hd`, `wired-unverified`, `excluded`, `unsupported-size`, `paired-not-wired`, `unpaired` and `unknown` are defined in the `status` block of the JSON and in `docs/SHARDS.md` ("How to read the coverage numbers"). The first version of this register reported every accepted pair that was not a documented draw as `paired-not-wired`; that counted bodies already in the runtime table, cut-outs excluded on purpose and pictures of a size the runtime does not draw, so the pool of work looked far larger than it is.
