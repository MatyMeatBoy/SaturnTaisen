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

The progress panel counts accepted matches, source-level integration and in-game validation separately. The scene-image count uses one canonical PC file per linked resource. The chapter index retains each Saturn occurrence by disc and each FILM stream by disc and offset. The NC panel counts each Saturn body package once across both discs. It reports runtime-table membership as integration and separately counts packages with a documented draw. A preparation count and a complete audit of scene appearances remain open.

## Status vocabulary (corrected 2026-11-19)

`hd`, `wired-unverified`, `excluded`, `unsupported-size`, `paired-not-wired`, `unpaired` and `unknown` are defined in the `status` block of the JSON and in `docs/SHARDS.md` ("How to read the coverage numbers"). The first version of this register reported every accepted pair that was not a documented draw as `paired-not-wired`; that counted bodies already in the runtime table, cut-outs excluded on purpose and pictures of a size the runtime does not draw, so the pool of work looked far larger than it is.

## Shared PC background files

Patch 0250 applies the existing byte-identity rule across distinct palette and
cell keys in the standard scene table. Only equal full PC SPR SHA-256 and equal
subimage indices share a file path. The generator retains all 527 Saturn keys
and redirects nine to an existing canonical PC file. All nine redirected
source and destination files were also compared byte for byte against the
local PC extraction. Guarded viewports, pans, and other compositors retain
their own rules.

The archived disc 1 chapter 7 BG2126 checkpoint ran for 56 strict fields in
each of three 2560 × 1440 profiles. The reference loaded BG2126.SPR and the
candidate loaded only BG2125.SPR. Both captures match pixel for pixel. The
candidate without a donor has 1,254,327 different pixels inside the Zoom
picture rectangle (272, 29)–(2288, 1037). Guest hashes and final SRAM match in
all three profiles. This is one natural redirected appearance. The remaining
redirected keys have table and byte-identity checks.

The chapter register records source filenames with no remaining independent
scene link in the `scene_file_aliases` field. The report removes those aliases
from the eligible inventory and counts the canonical target once. Together
with five aliases already shared by the earlier table, fourteen duplicate
filenames leave the denominator and nine leave the integrated numerator.
This changes the scene-image figure from 610/1167 to 601/1153. The number of
verified PC resources remains 152. The patch is outside v0.2.18-alpha.

## Work inventory by PC resource

The full PC census covered all 1,267 scene SPR filenames. SHA-256 of the
complete containers identifies 1,219 distinct byte sequences. Applying the
100 native-by-design exclusions leaves 1,123 eligible resources after
collapsing 44 duplicate filenames. The scene table and standard progress
report count 601 linked resources, leaving 522 to link or classify. The
existing 601 canonical paths have 1,187 recorded disc/resource links.
526 targets have more than one such link. These links are dependencies for
a resource, with separate in-game evidence kept where it exists.

Use one worker claim per PC file or exact file family. Start from the
already linked path when one exists. In the register, retain each Saturn
key and the correct PC subimage index. The byte groups reduce the work
inventory. Connecting a remaining Saturn key still requires compositor
eligibility and a route test. The inventory hash groups do not enable any
new runtime substitutions. The register assigns one `pc_identity` per exact
scene donor family. The separate `pc` field records the path selected by its
runtime row. The `pc_body_alternates` index records higher-resolution
PC donor candidates with the same Saturn body identity. The [byte-identical file catalog](../../config/hd-scene-file-duplicates.json)
records only filenames, with no source pixels or disc data.

Regenerate the file queue after each batch using the same extracted PC
edition used by the census. The CSV keeps each canonical file, its current
state, its byte-identical filenames and its known Saturn references.

```powershell
python tools/scene_file_queue.py --pc-root <private-pc-extraction> --output <private-output.csv>
python tools/scene_file_queue.py --pc-root <private-pc-extraction> --scope core --output <private-core.csv>
python tools/scene_file_queue.py --pc-root <private-pc-extraction> --scope extras --output <private-extras.csv>
```

BG1257, BG1280 and BG2247 are native decisions on both discs. The register
excludes their PC compositions from the file queue because the measured
camera does not align. This leaves 1,120 eligible files and 519 pending
at the time of this audit. The seven full-frame BBG candidates retain
their separate framing review.

### Alcance principal y extras

El inventario de v0.3.4 tiene 584 de 662 donantes principales
enlazados. Quedan 78, con una pareja parcial, siete encuadres
BBG pendientes y 70 sin clasificación definitiva. Las rutas
EVE se cuentan por su archivo donante BBG. Los 26 suelos
tácticos únicos se suman al total principal una sola vez.
Los sprites tácticos forman parte del alcance. Su integración
se cuantifica por familia cuando esté confirmado el inventario
de sustituciones, sin volver a contar los recursos de HUD.

EVENT y CG suman aparte 4 de 433 donantes integrados.
EVENT incluye animaciones de mapa como EV00S24, la figura
que se hunde en MAP02. CG incluye ilustraciones como la
recompensa de cocina BG_RYORI y también piezas de minijuego.
Que un archivo figure sin enlace indica que falta atribuirlo
o verificarlo. Para los que solo aparecen en la edición PC
se puede registrar una exclusión con evidencia.

### Equivalent decoded images

The second pass decoded 1,218 of the 1,219 byte-distinct PC files with
`tools/decode_spred.py`. Its comparison includes each image index, width,
height and full RGBA bytes in container order. It confirms 23 equivalent
groups that span multiple distinct byte signatures. The sole unresolved
file, EV19S03.SPR, remains a separate candidate. Its first bitmap entry advertises unsupported pixel format 8 and is rejected before decoding. The adjacent EV19S03A.SPR decodes three images, so it remains a distinct candidate.

For example, BG1143.SPR and BG1144.SPR have different container checksums
and the same single 576×320 image. Four corridor files BG1132/34/35/36 also
share a single 576×320 image. The work queue now has 1,095 unique resources,
584 linked and 511 pending. The 150 verified resources are unique under
the same grouping. This is a reporting and assignment change. The Saturn
palette/cell keys, loader paths, and previously reviewed camera decisions
are retained.
