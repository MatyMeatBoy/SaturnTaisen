# Resource and scene index

The private index at `local/work/scene-index` gathers the resources from the two prepared English discs and the documented execution observations.

```powershell
python tools/build_scene_index.py
python -m unittest discover -s tests -p test_scene_index.py
```

- `resource-inventory.json` and `resource-inventory.csv` identify the 3,570 ISO filesystem entries, 1,785 per disc. Each entry keeps disc, ISO path, LBA, size, SHA-256, and the video streams identified within the file.
- `scene-index.json` and `scene-index.csv` include 166 candidates derived from resources and nine execution observations. The candidates comprise 112 dialogue tables and 54 video streams.
- `manifest.json` records the disc hashes, the manifest and the source JSONL, the counts, and the tag vocabulary.

The six visible labels are **video**, **dialogue**, **choice**, **map**, **battle**, and **menu**. Their exchange IDs are `video`, `dialogo`, `eleccion`, `mapa`, `combate`, and `menu`. A transition observation may have a null label. `certainty` distinguishes observations from inferences, with evidence per row. The index inventories the files from both discs. Execution coverage is limited to the nine annotated samples.

## Videos and relation to text

The reader validates the FILM, FDSC, and STAB structures for Cinepak, including each sample's length within the file. It identified four streams in standalone CPK files and 50 streams within `/SAKURA4`, 31 on disc 1 and 19 on disc 2. Each stream keeps the relative offset, dimensions, sample count, and SHA-256 of its extent. File recognition provides a video candidate. The presence of text and the advance conditions for these clips remain unknown.

`dialogue_table` and `associated_record_keys` link the 59,450 record keys to their exact tables, identified by disc, path, and hash. `record_association=table_inventory` explains the scope of that link. Determining which entries appear during a given video or visit requires observing that path. The index avoids associating resources by prefix or numbering.

## Use in Zoom and translation

`runtime_layout` keeps the observed layout when it appears in the evidence. `zoom_eligibility=validated_for_observation` is limited to that sample's framing. Unknown rows keep `fallback_layout=native`. A null `wait_for_text` leaves the decision on automatic advance pending.

The translator can use `associated_record_keys` to locate the corresponding rows in `local/work/spanish-translation`, which also contains their aliases across discs. The index exports metadata and pointers to the local evidence. Image, video, and script files remain in their private locations.

## Importing observations from the later sweep

```powershell
python tools/build_scene_index.py --observations local/work/later-chapter-audit/chapter-sweep/observed-scene-resources.json --output local/work/scene-index-later
```

The optional argument adds 17 observations from the sweep described in [AOT sweep of later-episode saves](chapter-sweep.md). The new destination contains 26 observations in total. Without the argument, the generator produces the nine base observations.

Nine Continue selections are recorded with the `menu` label, and eight scenes with visible dialogue with the `dialogo` label. The episode for both phases comes from the observed slot. The case of a lock before any dialogue is shown keeps only the selection. Each ID includes disc, case, and phase. The manifest records the name and SHA-256 of the imported report. Screenshot paths are relative to the report's directory, and the importer validates the format of their hashes.

The `resident_table_inventory` link requires a full match declared in RAM and verification of disc, ISO path, size, LBA, and SHA-256 against the inventory. The catalog keys correspond to the records of that resident table. The test leaves the use of each record in the observed frame pending. Zoom eligibility remains unknown for the imported rows, and the fallback stays native.
