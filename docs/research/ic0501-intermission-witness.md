# IC0501 intermission witness

The English Saturn disc 1 Episode 5 route reaches the intermission after Ogami locates Kanna and Sumire in the lobby. It reads IC0501.BIN at FAD 158127, then ICLOGO.BIN and the intermission resources. The CD read was recorded during a 9,800-frame muted strict replay from the preserved natural lobby checkpoint. Two native Cancel presses leave the save selector at the Save, Status and Resume menu.

IC0501.BIN is 76,672 bytes, SHA-256 `72275b7fe3f0ba7f9b725bd40a9695d91801a822fefb21f625a71931a3ed30fa`. The disc 2 file is byte-identical and its displayed composition awaits a witness. The 71,680-byte source cell span matches the preserved disc 1 state. The decoded source is 320×224. The matching 640×480 PC image is subimage 0 of `SAKURA1/ICATCH/IC0501.SPR`, SHA-256 `fd6909782802a4f42360c486c5d4ed7b433f477907805b91fe8b47b92fe0d2ce`.

## Menu, emblem and floral fade

The opened menu uses source 0 only inside the native rectangle (184,16)–(296,143), with half-open bounds. Source 4 covers the IC picture and reports page `0x44000` and palette `E9107F892185CCC8`, the shared logo palette. The displayed source-4 colors include the native signed −16 channel offset. The on-disc palette has a different fingerprint. The 2560×1440 captures at frames 20, 60 and 100 move the selection from Save through Status to Resume. At integer scale 6 the native plate bounds are (320,48)–(2240,1392). The 57,344 logical RGB samples outside (184,16)–(296,144) share FNV-1a `1F7A14C347473045` in all three captures.

A separate 340-frame replay selects Resume on the same native menu. At 1280×720 the plate retains the same protected RGB hash through sample 252, including the menu fold and the red source-2 emblem. The emblem uses the full (184,16)–(296,144) rectangle. The hash changes at 260 as the floral layer begins to mix over the IC plate and the emblem. Samples through 316 preserve that changing composition. A future HD replacement needs to follow that blend as well as protect both states of the menu rectangle.

All three bounded replays report zero interpreted blocks. Their guest hash logs contain 9,800, 120 and 340 lines. The catalog records the disc 1 appearance and its PC counterpart. Disc 2 presentation, full chapter passage and packaging remain open. Evidence is retained under `local/work/codex-tw2-fullscreen-bbg/eve105-research/`.

At verification the project measured 64,798,296,250 logical bytes, above its 20 GB limit. The delivered development ZIP remained 6,315,009,692 bytes.

## Enhanced presentation

Patch 0144 verifies the English disc 1 intermission at 2560×1440. The full 640×480 PC plate is registered to the native 320×224 viewport. The replacement keeps (184,16)–(296,144) half-open for the native menu and emblem. The palette check is paired with an exact fingerprint of the visible native source-4 plate outside that rectangle. The entrance has no offset (RGB fingerprint `A5E3498BEDDC1305`), and the exit applies −16 to each channel (`1F7A14C347473045`). During a blend the compositor also reconstructs the native pixel from both source samples and the Saturn's 1/32 weights before accepting the plate.

When the wide floral compositor is active, only its intermission input changes. Its KABE40 entrance or KABE41 exit pixels, signed offset, weight and viewport remain in use. The stock native path uses the same verified VDP2 source samples and weights. Its texture is limited to 640×448, with an opaque-frame cache and a transparent menu rectangle. Missing or invalid PC art keeps the same composition, and Original bypasses the replacement.

The paired 705-frame entrance replay starts within the retained natural lobby-to-intermission route, before the reveal. Eight 1440p captures include the first visible reveal, the emblem and the menu. The paired 340-frame exit replay covers Save, Status and Resume, the emblem, the floral fade and the return to the existing renderer. The two runs preserve all 1,045 guest hashes, with zero interpreted blocks. Every tested capture preserves the menu/emblem rectangle and all pixels outside the viewport. By exit sample 332 the full frame is identical. Independent pixel reconstruction checks 2,064,384 screen pixels per wide sample for entrance weights 7/32 and 19/32 and exit weights 31/32, 27/32, 18/32 and 3/32. The native compositor's unblended and blended tests independently check 229,376 donor samples per frame. The missing PC asset, corrupt PC asset, Original mode and IC01 regression controls reproduce their corresponding stock captures and guest hashes.

The original media, saves, probe scripts, frame hashes and captures are retained locally under `local/work/codex-ic0501/`. The released packages were not rebuilt.
