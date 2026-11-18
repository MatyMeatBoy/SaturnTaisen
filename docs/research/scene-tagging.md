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
