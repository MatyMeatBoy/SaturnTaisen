# IC0501 intermission witness

The English Saturn disc 1 Episode 5 route reaches the intermission after Ogami locates Kanna and Sumire in the lobby. It reads IC0501.BIN at FAD 158127, then ICLOGO.BIN and the intermission resources. The CD read was recorded during a 9,800-frame muted strict replay from the preserved natural lobby checkpoint. Two native Cancel presses leave the save selector at the Save, Status and Resume menu.

IC0501.BIN is 76,672 bytes, SHA-256 `72275b7fe3f0ba7f9b725bd40a9695d91801a822fefb21f625a71931a3ed30fa`. The disc 2 file is byte-identical and its displayed composition awaits a witness. The 71,680-byte source cell span matches the preserved disc 1 state. The decoded source is 320×224. The matching 640×480 PC image is subimage 0 of `SAKURA1/ICATCH/IC0501.SPR`, SHA-256 `fd6909782802a4f42360c486c5d4ed7b433f477907805b91fe8b47b92fe0d2ce`.

## Menu, emblem and floral fade

The opened menu uses source 0 only inside the native rectangle (184,16)–(296,143), with half-open bounds. Source 4 covers the IC picture and reports page `0x44000` and palette `E9107F892185CCC8`, the shared logo palette. The displayed source-4 colors include the native signed −16 channel offset. The on-disc palette has a different fingerprint. The 2560×1440 captures at frames 20, 60 and 100 move the selection from Save through Status to Resume. At integer scale 6 the native plate bounds are (320,48)–(2240,1392). The 57,344 logical RGB samples outside (184,16)–(296,144) share FNV-1a `1F7A14C347473045` in all three captures.

A separate 340-frame replay selects Resume on the same native menu. At 1280×720 the plate retains the same protected RGB hash through sample 252, including the menu fold and the red source-2 emblem. The emblem uses the full (184,16)–(296,144) rectangle. The hash changes at 260 as the floral layer begins to mix over the IC plate and the emblem. Samples through 316 preserve that changing composition. A future HD replacement needs to follow that blend as well as protect both states of the menu rectangle.

All three bounded replays report zero interpreted blocks. Their guest hash logs contain 9,800, 120 and 340 lines. The catalog records the disc 1 appearance and its PC counterpart. Runtime substitution, disc 2 presentation, full chapter passage and packaging remain open. Evidence is retained under `local/work/codex-tw2-fullscreen-bbg/eve105-research/`.

At verification the project measured 64,798,296,250 logical bytes, above its 20 GB limit. The delivered development ZIP remained 6,315,009,692 bytes.
