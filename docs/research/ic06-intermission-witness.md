# IC06 intermission on disc 2

The natural English Chapter 9 continuation from the underground storage
briefing loads all 38 sectors of IC06.BIN at FAD 135034 and reaches the
Save, Status and Resume menu. The exact ISO file SHA-256 is
`dad3910df4e73285f08592c7e1f8794a74bd6338c379b1252181d16d9cb4c747`.
The two Down presses and A resume into 0902.BIN, read at FAD 109436.
The IC06 file number is independent of the chapter number.

The source-4 plate uses its own palette `FEBAEA7B6E7CAC67`. The native
picture decoded using that palette matches all 57,344 RGB pixels outside
the menu/emblem rectangle (184,16)–(296,144). Their unshifted FNV-1a is
`0F85EDA8CE4B247D`. The PC donor is IC0600.SPR subimage 0, 640×480,
179,506 bytes, FNV-1a `D6AEB7F7E04B94DA`. The compositor applies the
same 640×448 registration as the two previously verified plates.
The table binds each plate to its disc and palette before checking its
native RGB. The other disc's IC06 remains on its previous path.

Eight 430-field strict replays at 1440p match guest hashes and SRAM.
Fifteen opaque screenshots in each Enhanced layout verify all 2,064,384
pixels outside the protected rectangle inside the native viewport
against an independent decode and integer-scale projection. The menu and
everything outside the viewport match exactly. Wrong-size, missing or
altered resources keep the native path, and the sampled missing and
same-length altered controls match the stock RGB. Original matches all
sampled baselines.

The 350-field exit replay includes fourteen more changed samples in the
same viewport, preserving the menu rectangle along the transition and
returning to identical RGB by sample 325. The disc 1 IC03 entrance and
IC0501 exit regression pairs match all 1,080 guest hashes, 26 complete
captured RGB pairs and final SRAM. The witness is for this English disc
2 route. New package inclusion and other appearances remain open.
Private replays are under `local/work/codex-th1/ic06-live/`.
