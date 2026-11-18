# Chapter 1: ongoing battle validation

The entire chapter has not been verified yet. The previous continuous run reaches a hallway; the following segments start from local states for research and do not complete that route.

The orders tutorial was completed and a normal Sakura attack was verified: attack effect, enemy disappearance, and return to the remaining actions. tests/battle-first-attack.movie reproduces that attack from the fixed local scene. tests/test_battle_progression.py compares 1,200 frame hashes and the final image between strict AOT and the interpreter of the same SDK: they match. AOT runs zero interpreted blocks. This is a CPU-path comparison, not an independent reference for the whole hardware.

Defense, turn change, enemy-phase camera, and María's movement with confirm/cancel were also observed. Original backups and the movies/logs/states under local/work/chapter1-progression are preserved. No segment forces HP, victory, or mission variables. The inputs cover several fields so the SMPC probe can observe them; a single-frame transition may not be sampled by the game.

Battle victory, episode ending, continuous composition without state loads, and native save/load of the ending are still missing. These partial milestones are not turned into a claim of a complete chapter.


## Continuous turns and Sumire's lock

`tests/battle-multiple-turns.movie` runs 23,443 frames from a local fixture after Sakura's first attack, with a single initial load and no intermediate loads. The guest hash and final RGB pixels match the last probe in the chain. Binary cd4407e ran zero interpreted blocks. This validates composition and progression of those turns; it still does not include victory nor the route from New Game. The fixture's SHA and scope are in chapter1-continuous-battle.json.

Next, Sumire's normal attack reproduces a strict AOT exit, code 4, at 060783FC. The instrumented reference run attributes the bytes to `/SAKURA2/K002.BIN`, offset 03FC, base 06078000, SHA256 8ce336483ca256b87e0d96eb1575afca07959a42e7ce48eccbde67684253cbcb. The reference completes the attack and eliminates one of the enemies. This failure affects the v0.1.2 binary; its ZIP and tag are kept immutable. The static candidate expansion is verified before declaring the lock fixed.

In development, 33,696 AOT candidates were added for the 18 unique variants of the K001–K019 family, reaching 614,024 static blocks. The regressions for Sakura's attack (1,200 frames) and Sumire's (1,800 frames) matched the reference in every guest hash and final RGB, with zero interpreted instructions in AOT. Evidence prior to presentation work: `local/logs/sumire-fixed-parity.log`. The fix does not modify the already-delivered ZIPs and still does not certify victory nor a complete chapter.

## Relay toward victory

2026-11-18 rerun on the current local build: `tests/battle-multiple-turns.movie` from the fixture `chapter1-multiple-turns.state` (SHA-256 87f69986…) completes the 23,443 frames with 0 interpreted blocks. The last frame shows a unit's orders menu (Move/Atk/Def/Info/End). A local relay state, `local/work/t02/fin-multiple-turns.state` (SHA-256 4d67dd1adc217d0a617baf1396b14ef29724663b68ee41f50552d88bef8d17b0), was saved at frame 23,400 to record the remaining turns (T02a). It was not compared against the reference in this rerun, nor was the number of remaining enemies counted.
