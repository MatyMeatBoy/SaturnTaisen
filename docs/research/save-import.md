# Saturn save import

Authorized requirement: import saves from various emulators via the launcher, preserve originals, and test advancement points obtained publicly. The launcher interface lets you choose or paste the file, detect the format, create a copy, activate it, and return to the usual save. Tested with real keystrokes from its test mode and then with an episode 8 load from the launcher; the originals remain intact.

First local tool:

```powershell
python tools/import_saves.py save.BUP
python tools/import_saves.py save.BUP --output local/imported.bin
```

Without `--output` it inspects; with it, it creates a new 32 KiB internal memory with the `SAKURA___*` files. It rejects an existing destination. It does not automatically merge with the active save, does not copy other games, and does not change progress or RetroAchievements data.

## Implemented formats

- BUP (`Vmem`), with declared size checked.
- Individual SAROO (`SSAVERAW`), with size and CRC checked when a CRC exists.
- Compact 32 KiB internal memory, 64-byte blocks.
- Compact 512 KiB external memory, 512-byte blocks.
- 64 KiB or 1 MiB SH-2 dumps: useful byte at odd position.

The reader detects the content, validates the block chains, and rejects cycles, overlaps, impossible sizes, and lack of space. Unrecognized machine states and formats are rejected. Still missing, among others: XML/B64/SGM, full SAROO containers, and additional geometries. Compatibility with all emulators is not claimed merely by accepting an extension.

Public samples from Mednafen, SSF, and Yabause were read from Knight0fDragon's converter repository. Several decode; others reveal formats still pending or strings that require investigation. Details are kept in `local/logs/save-format-samples.json`. Decoding a sample must not be confused with verifying that the save works inside Sakura.

## Public Sakura saves

[Bucanero's collection](https://github.com/bucanero/saturn-save-tools/tree/main/docs/sakura-wars), with credits to privateye and Pimpeaux. These are two completed saves with Sakura and Sumire endings; preserved locally. The BUP/SAROO pairs contain the same metadata and 5708 bytes of data. The first, imported into a copy for reference with English disc 2, shows episodes 8, 9, and Finale in its three slots. Loading and running those scenes in AOT are still being verified.

Provenance and hashes: `public-save-fixtures.json`. The saves are not distributed in this repository.

## Format references

- [Saturn Save Tools](https://github.com/bucanero/saturn-save-tools), `include/bup_header.h`, `include/sgm-types.h`, and `src/ss-converter.c`.
- [SS Backup RAM Parser](https://github.com/hitomi2500/ss-save-parser), SH-2 mode with interleaved bytes and allocation tables.
- [Saturn Save Converter](https://github.com/knight0fdragon/SaturnSaveConverter), per-emulator implementations and samples.

The project's converter is original code based on the documented structures; it does not run the downloaded converters.
