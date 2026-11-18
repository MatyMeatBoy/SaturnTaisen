# Chapter1 playable validation

Immediate goal: demonstrate a reproducible path from New Game to the end of episode1, in-game save, and Continue, before claiming the chapter is complete. Keep Saturn as the priority and do not confuse visual improvements with validated progression.

1. Inventory the existing continuous path of 119,781 frames: it reaches the corridor and does not include a battle. Record story anchors, choices, and access to combat.
2. From a local combat state, advance controls and turns to verify movement/attack, victory, and exit. Use backup copies and deterministic movies; keep the commands and hashes. Save states make investigation easier and do not count as a continuous path from the start.
3. If an AOT block is missing, reproduce it and attribute it to a real module; statically generate the needed candidates without enabling the interpreter in production. Compare the segment against the reference whenever there is doubt about semantics/state.
4. Compose a continuous playthrough from boot, with no jumps via save states. Save a native save at the end of the episode, restart, and load it with Continue. Verify two repeats with no interpreted fallback.
5. Document passed tests, pending alternate routes, and campaign/disc status separately. Add a regression for each fixed lockup, with no tests that merely repeat the implementation.

Out of scope for this test: HD bodies, PixelGen on the map, and panoramic battle must not change logic or collisions; investigate the relative HUD after a reproducible progress baseline. Chapter1 is not considered verified until reaching 4.


## Continuation after v0.1.2

1. Reproduce Sumire's normal attack from an immutable local fixture and pin its public movie with no original data. v0.1.2 stops at strict AOT at 060783FC.
2. Attribute the block by its bytes to K002.BIN (offset 03FC, base 06078000), statically extend the module, and check siblings of the K family via their own pointers; do not confuse candidates with executed coverage.
3. Recompile incrementally and compare 1,800 hashes and final AOT/reference RGB for Sumire; repeat Sakura's previous attack.
4. tools/stitch_battle_replay.py composes the probes with a frames-1 offset, because the state is saved before executing that frame. Reject modified source, held input, and boundary events. Four synthetic tests precede its real use.
5. Run the composed movie with no intermediate loads and compare its final state/frame against the segmented path. The current path starts after the first attack; it still does not demonstrate New Game→end of episode.
