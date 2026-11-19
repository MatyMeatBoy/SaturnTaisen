# BBG204 tactical illustration

English disc 1, episode 4. A normal Continue from the chapter-four battle save followed by dialogue advances reaches the illustration over MAP06. The CD trace reads `/SAKURA2/BBG204.BIN` at FAD 220685 during EVT06. The opaque illustration occupies native rectangle `(16, 8, 288, 144)` and is independent of the tactical ground and dialogue.

The same-number PC file `SAKURA2/BG/BBG204.SPR` contains one 576 × 320 image. The proportional crop `(0, 0, 568, 284)` aligns the sword, face and shoulder with the Saturn composition. The official PC image uses different colors. A local 1440p comparison shows the same borders and dialogue clearance.

Patch 0120 adds BBG204 to the existing native inset table. The native source mask, palette `FB7D81F5464F27B2` and presented RGB `D3B104F491C0C105` must match. The exact PC file is checked before drawing. The guest and the native tactical floor are untouched.

A strict-native development run saved the naturally reached frame 7770. At 2560 × 1440, all five replays from that state produced identical 620 guest hashes (SHA-256 `75b265799f50cc276864957c55b3d6ce022c5a43cd9379e51e01fb7bbf8e4656`) with zero interpreted blocks. With the PC file and HD enabled, samples 30, 120, 330 and 420 changed only rectangle `[416, 96)–[2144, 960)`. Samples 435, 500 and 600 matched after the illustration exited. Missing PC artwork was pixel-identical to HD disabled. Original mode was pixel-identical with and without the PC file. The existing EVE002 separately still drew its own PC image with 60 identical guest hashes. The local references, game images and captures are kept under `local/work/codex-tw2-fullscreen-bbg`. This verification covers the route and illustration above. It is not a whole-episode or package certification.
