# Identifying LIPS groups by script cursor

Two private states from English disc 1 v2.1 let us associate the visible LIPS panel with a single record from `/SAKURA1/0102TBL.BIN`. Each record contains all the options in order, separated by CR. Matches of individual phrases against other records of the same table do not identify the panel.

| Private state | BE32 cursor at `0x060685B4` | Command offset in `0102.BIN` | Decimal ID and TBL record index | TBL offset and prefix | Native rows Y and cells |
|---|---|---|---|---|---|
| `prebattle-3000.state` | `0x002068CE` | `0x28C5` | 20008, index 285 | `0x53CC`, `00000000` | 62: 17, 94: 30 |
| `resume-chapter-6000.state` | `0x002051F2` | `0x11E9` | 20002, index 64 | `0x2BB0`, `00000000` | 54: 20, 78: 25, 102: 23 |

The comparison verified both full files in each state's Low WRAM. `/SAKURA1/0102.BIN` occupies 26,646 bytes from `0x00204000` (SHA-256 `0d7fe995a3c488ef4989791068b8b1e97259087ad26cea8150638caaf3e77f4e`). `/SAKURA1/0102TBL.BIN` resides from `0x00224000` (SHA-256 `7b08f9cd054200f17153db7a6690624b364bff31125a583ae1b689a23a2b2ae2`).

In both samples, the command starts nine bytes before the cursor. The initial bytes are `2E 80 00` followed by the BE16 ID. The translation team's [FindDialogOrder classifier](https://github.com/NoahSteam/RomHackingTools/blob/10aefa40c555c2b1135b5836434c2315135b5306/SakuraTaisen/SakuraTaisen.cpp#L2287-L2305) recognizes `2E 80 00` and `17 80 00` as LIPS. The second form remains unvalidated at runtime. The narrative pointer `0x0606851C` points to a different record in both states.

Inspection of the VDP1 commands verified one clock per panel, centered rows, eight-pixel spacing, and 115 glyph tiles matching byte for byte the English atlas slots for those options. Both states show the first option selected. The local verifier `local/work/dialogue-preload-worker/lips-group-verify.py` generates `lips-group-witnesses.json` with the hashes and geometry; the states and game text stay local.

## Intended runtime use

Prepare an index bounded by script identity, command offset and record ID. On the presented frame, resolve the group using the cursor and the verified resident script and table. Confirm the record's rows against the full panel and tiles before lending its text. The current clock, position, color and ink-ownership checks remain necessary. If any check fails, keep the current glyph-based reconstruction.

Still to check: the meaning of the command's final four bytes, the distance to the cursor for other branches or opcodes, the coordinates of other panels, combat LIPS, and disc 2. This study does not modify the SDK nor integrate preloaded text for choices.
