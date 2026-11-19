# Continuation of the first battle from the T02 handoff

The route starts from `local/work/t02/fin-multiple-turns.state` (SHA-256 `4d67dd1adc217d0a617baf1396b14ef29724663b68ee41f50552d88bef8d17b0`), with the English disc 1 and the isolated executable `local/build/sakura/sakura-episode2.exe` with 643,320 blocks. Each segment uses its own SRAM copy and eight-frame input. No states or game data were edited.

## Observed milestones

| Segment | Result |
| --- | --- |
| `kill-six` | Sumire approaches and lands a normal attack on soldier #6. The enemy is still present. |
| `sakura-special` | After the enemy phase, Sakura uses her special on #6. 95 damage points are shown at frame 1,200 and the soldier no longer appears in the scene at frame 1,600. |
| `maria-hit-eight` | Maria repositions diagonally and performs a normal attack on a soldier whose portrait shows `8 #`. The soldier is no longer visible in that camera before frame 750. |
| `inspect-map` | The minimap shows five magenta markers west of the allied units. In this capture their identities are not determined. |
| `next-west-round` | After moving Sumire and Ogami west, the enemy phase shows two additional soldiers near the ruins. At the end of that phase, a dialogue between Sakura and Ogami begins. |
| `west-dialogue` | A three-answer LIPS choice opens during battle. The replay accepts the first option and ends with Sakura's order menu open. |

Active enemies remain at this first handoff. Numeric labels change during battle, so probing a given position and defeat animations are better references for tracking each enemy.

## Handoff and reproduction

The proprietary material remains in `local/work/chapter1-victory-followup`. The starting point for the next segment is `west-dialogue/finish.state`, saved before its frame 1,439, SHA-256 `c527fab10409aa06672d93c48d355840fc7de23a696f73c42f95c3e5ced08d2b`. Use a copy of `west-dialogue/backup.bin`. The captures `maria-hit-eight/frame-000750.png`, `inspect-map/frame-000600.png`, `next-west-round/frame-000840.png` and `west-dialogue/frame-000540.png` document progress.

The accepted segments have strict tracing with zero interpreted blocks. `continuous/manifest.json` lists their order, hashes and input offsets. `continuous/input.movie` composes the 28 segments for a single-load replay from the handoff. The candidate has 24,993 frames and SHA-256 `459c3477b0c42c7c5bde109aab18a4270f937940d89fdfd2447ceb7c4c2a6750`.

The continuous replay finished with exit code 0 and zero interpreted blocks. All 24,993 hashes match the game frame by frame across segments. The final guest hash is `a8c36f754515e904` and the final RGB capture matches. The comparison was made against the segmented run in strict AOT.

## Additional round with test.2

The second route loads `west-dialogue/finish.state` with a copy of its SRAM and the isolated executable `local/build/polish-test2-final/sakura.exe`, SHA-256 `a12b26d1990cabf9c54da562e4f05a9c842c7078d1b5c8ae3fe935a426c91418`. Sakura and Ogami advance and Sumire positions next to the soldier whose portrait shows `7 #`. In `t2-seven-special-hit/frame-000600.png`, her special deals 64 damage points. The soldier is still on the map. The cursor identifies the other western soldier in `t2-maria-flank/frame-000150.png`. After finishing Maria's orders, both soldiers approach her unit. In `t2-next-enemy/frame-001600.png`, Sakura's turn returns and her order menu opens.

The test.2 handoff is `t2-next-enemy/finish.state`, SHA-256 `3089f5020b5b45ad7d40f2fd4b54faa629e0b06a0f922e2dfcf9765fa157fd1a`, along with a copy of `t2-next-enemy/backup.bin`, SHA-256 `4aa58364c1eaa4d0cee384894861caa4cde1e426aa2e43da7aa6b4e94379bc5b`. Later attempts at a Sakura attack were left as exploratory branches and are not part of the handoff.

`t2-continuous/manifest.json` records the 17 accepted segments. The composed `input.movie` has SHA-256 `b740a60d4782c68a795e53c1d61da19dd084735c24f2a3784aa6b22ffe1a242b`. The 12,454 hashes of the continuous replay match the segmented chain, with zero interpreted blocks. The final guest hash is `4bb4b0576a5b297a` and the final RGB also matches. For the RGB comparison, the last segment was repeated with a capture at its frame 1,700. Its SRAM and all its frame hashes matched. This repeat's state file differs by four bytes from the dated handoff state hashed above.

## End of battle and post-battle coverage

Sumire finishes off the soldier hit by her special. Maria eliminates the other western soldier and Sakura the first bridge soldier, both after two normal attacks. Ogami reaches the shrine soldier and finally eliminates it. After its explosion, Satan's dialogue opens. The shrine soldier's portrait shows `8 #` in `t4-sakura-bridge/frame-000650.png`, `7 #` in `t6-ogami-aim/frame-001050.png`, and `6 #` after approaching the boss in `t7-ogami-aim/frame-000500.png`.

The state `t6-ogami-hit-plateau/finish.state` is saved after the first attack on the shrine soldier, SHA-256 `fcf8823074ed494ff7844a691a94529fba91d20bcc8a89db21005a9a186e8d0f`. `t6-continuous/manifest.json` records 38,757 hashes equal to those of the segments from the `t2-next-enemy` handoff. The final guest hash is `0195ee86c16a4f32`, the final RGB matches, and there were zero interpreted blocks.

All four allies attack Satan in successive rounds. At the end of the first round in which all four attack, an 80-point recovery of the boss is observed. In the next round, Maria's last attack empties its bar and removes it from the board. `t10-maria-hit-boss/frame-001100.png` shows the final damage, `frame-001320.png` its absence, and `frame-002200.png` the farewell scene. Ogami confirms the group protected the capital in `t10-after-boss/frame-000600.png`. The battle's resolution and the start of the team's farewell were observed. The sequence had not yet reached the save menu in test.2.

`t10-continuous/manifest.json` records the replay from `t6-ogami-hit-plateau` to `t10-after-boss`. The 55,038 hashes match those of the segmented route, with zero interpreted blocks. The final RGB matches and the last guest hash is `3d464a2e532559dc`.

The `t10-curtain` route reproduces the lockup at the start of the final pose. It loads `t10-after-boss/finish.state` SHA-256 `e43d120faf07392b36932ad42ca73df298a56d217e990c18b9d665a09dfd1c7a` and a copy of its SRAM with the same footprint as the previous handoff. Its input movie has SHA-256 `518aab4a47f686646764515acb44e87ec6b46854aa371f59d91dc651786d8cd0`. Test.2 completes 495 hashes up to `84d329001596f4de` and ends with exit code 4 upon reaching the un-recompiled block `06002042` on the main SH-2. `t10-curtain-boundary/finish.state` is saved right before the failure frame and has SHA-256 `b71e1c0c53ea4843c684e2c988b0f33b13467f8902787342d5835053cc90f364`.

In the state right before the failure, High WRAM contains a fragment of `/SAKURA` at `06002000`. That program's routine `06005C58` copies 119 words from `060535D8` to the destination. That is 238 bytes from offset `0x4F5D8` of the file, SHA-256 `2be6e6b0c337ca1e36dc67c4649ca04b67c3fa6ba72a6c6f1f0411672bbc182e`.

The trace up to reaching `06002042` shows another copy between save and execution. Routine `06032B00` copies 103 words from `0604BB14` to the same destination. The call at `06032AC2` enters `06002020` and the instruction at `06002028` jumps to `06002042`. The 206 bytes executed in `[06002000,060020CE)` match the file `/SAKURA2/0SLG.BIN` from disc 1 at offset `0x47B14`. SHA-256 of the fragment `c8f547b446ef793c22fad73f63a8d7c4632abce683cda4d794ab120fd87bee6e`. The same bytes are in `/SAKURA2/SLG.BIN` at that offset. The first build that only recorded the `/SAKURA` fragment reproduced the same error because the code comparison discarded that variant at the moment of the jump. The exact RAM and arrival trace remain in `local/work/postbattle-miss-diagnostic`.

The reference run with `--cpu free` and `SATRECOMP_NO_BLOCKS=1` from the pre-failure state completes 1,200 frames. Its input movie shifts the remaining events to frame 0 of the handoff and has SHA-256 `abd1094cd2320aa5767c138f73c9cf27f390b4e36f31c701d208220b36ef0e3d`. The log confirms the main SH-2 executes `06002042` and continues through the copied routine. In `t10-curtain-free-reference/frame-000360.png` the intermission menu appears, `frame-000720.png` confirms the save selection, and `frame-001200.png` shows `Save Complete!`. The last guest hash is `c99aea4e279c6dbb` and the SHA-256 of the resulting SRAM copy is `6d96f3daa07711500e1b8d2d7cbe1e69ac8bc285e83124271597347a9e4e03df`. This route proves the save in the interpreted reference. Coverage in AOT is verified with the later candidate.

The static comparison finds the same 238 bytes of `/SAKURA` in the English, Spanish and Japanese disc 1 at `0x4F5D8`, and in English and Japanese disc 2 at `0x4F5E8`. All five programs have the 119-word copy routine to destination `06002000`. The same 206 bytes of `/SAKURA2/0SLG.BIN` and `/SAKURA2/SLG.BIN` appear at `0x47B14` in all five images. The earlier interactive run was tested with the English disc 1.

An interpreted continuation from the save selects `Resume` in `t10-resume-free-reference/frame-000840.png` and shows the hanami epilogue in `frame-001800.png`. It completes 1,800 hashes and preserves the footprint of the saved SRAM. The movie has SHA-256 `0e900c1c0a2add2dbe819be90f624d98fa9cc694d3a50b367cd7b66c012c698c` and its final guest hash is `3cbd8ffb97c0500b`.

## Verified AOT fix

`tools/discover_registered_overlays.py` registers `MAIN_RELOCATED` and `SLG_RELOCATED`. Each registration validates the size and SHA256 of the full file before extracting the copied fragment. The analyzer only admits PCs and bytes within that fragment; it preserves distinct variants at the same address. A synthetic test covers boundaries, alignment, tampering outside the fragment, and provenance. Derived data stays in `local/`.

From the 674,023-block base, both registrations produce 674,182: 159 additional candidates. The direct reproduction matches byte for byte with the two-step expansion; final base SHA256 `eeb6cf3a498d2ca5434b036f5dc5aca3d3379b19406230ce2df7c3a484c668ae`. This proves reproducible generation; execution is tested separately.

Local reproduction, with a destination that does not yet exist:

```powershell
python tools/discover_registered_overlays.py --image "D:/01Claude/Sakurawars/local/prepared/disc1/Track 01.iso" --module MAIN_RELOCATED --module SLG_RELOCATED --seed-blocks local/work/episode4-aot/blocks.txt --sdk-root D:/01Claude/Sakurawars/local/deps/satrecomp --output local/work/postbattle-aot-reproduction
```

The isolated candidate `local/build/postbattle-slg-candidate/sakura.exe`, SHA256 `e7dd1c007e0b7610485f4fe98dd0bb2de4f47411e0cbc3cec835e8758fd120ec`, preserves the patch0048 host. The earlier objects were hash-verified during incremental linking and the owner's executable was not replaced. The first standalone variant, candidate 674,110, is kept as a failed reproduction; the diagnostic was compiled outside the SDK and is not part of the approved candidate.

Candidate 674,182 passed the 1,200 frames from the boundary to `Save Complete!`, and then 1,800 more from its own saved state to hanami. All 3,000 hashes matched the interpreted references. Ten RGB pairs matched on save and five on Resume, and the resulting SRAM was identical to the reference in both phases. All candidate runs logged zero interpreted blocks. Private evidence: `local/work/postbattle-fixed-validation/result.json` and its `save`/`resume` subfolders.

## Continuous reproduction after LIPS

With the 674,182-block candidate, `west-dialogue/finish.state` was loaded once and the composed movie was replayed without loading intermediate states. The full route completes the battle, saves at the intermission, and selects `Resume` through to the hanami epilogue. The 109,740 guest hashes matched the segmented reference and zero interpreted blocks were logged. The last guest hash was `3cbd8ffb97c0500b`. The final RGB and the resulting SRAM matched the reference.

The movie has SHA-256 `3e7db4e78a2c498d892864fa850bc363bc5faa769bbfe8c525ab842249732693` and the resulting SRAM has SHA-256 `6d96f3daa07711500e1b8d2d7cbe1e69ac8bc285e83124271597347a9e4e03df`. The verification record is kept in `local/work/chapter1-victory-followup/t10-save-resume-native-full/verification.json`.

The later [full cold replay](#full-cold-chapter-1-replay) joins those handoffs from New Game. The already-delivered test.2 ZIP precedes this candidate.

## Continue from a cold boot

The 674,182-block candidate was restarted with a copy of the SRAM produced by the battle save. `tests/cold-load.movie` opens Continue, selects slot 1, and confirms the load. The hanami epilogue screen appears at frame 7,000. The 9,500-frame replay starts without loading emulator states. All guest hashes match and 19 RGB captures match between strict AOT and the interpreted reference of the same executable. The SRAM copy keeps its initial SHA-256 and the candidate logs zero interpreted blocks. The last guest hash is `d74aa82a82d17894`.

The private report is at `local/work/chapter1-victory-followup/t10-cold-continue/comparison.json`. The later [full cold replay](#full-cold-chapter-1-replay) verifies both profiles and their restarts.

## From the corridor to the night-time save

From `stairs-scan.state`, progress continues through the corridor's LIPS choice, the return to Yoneda's office, and Sakura's dialogue before the intermission. The game was saved to slot 1 with normal inputs and `Save Complete!` was observed. This segment uses its own SRAM copy and the 674,182-block candidate.

A single initial load replays the 29,597 hashes of the four segments. For the same 29,597 frames, the interpreted reference matches in hashes, final RGB, and saved SRAM. The AOT candidate logged zero interpreted blocks. The last guest hash is `f5282806f43e9908`. The movie has SHA-256 `34df861ba09b6ba1899d4708ce44e3cb31abe4acd7ee5404f247683bc0288596` and the saved SRAM has SHA-256 `2e96cc84378141ecc42d37c1ba1d71976974f6984ce85c791b68d9b95390801c`. The private evidence is at `local/work/chapter1-victory-followup/corridor-bridge/verification.json`.

The corridor anchor corresponds to frame 119,780 of the earlier New-Game replay, per the historical state comparison, except for the sound RAM pointer that the loader restores. The later [full cold replay](#full-cold-chapter-1-replay) verifies this join.

## From the night-time save to the battle tutorial

From the night-time save, the `Resume` command returns control to the theater. The round goes through the library, the ground floor, and the dressing room. After returning Jean-Paul to Iris, Ogami ends the round. The morning exit leads to a second intermission and a save to slot 1 before the battle. On resuming, the route reaches target selection after Maria's instructions.

With a single initial load of the night-time save state, the 674,182-block candidate replays the 147,730 guest hashes of the 21 segments. The final RGB and the saved SRAM match, with zero interpreted blocks. The last guest hash is `f26cfda21efe6e60`. The movie has SHA-256 `0e8cd95c6802a3ad702794cf25299366fd468a82cb5b8088da73ea8640aa5fef` and the resulting SRAM, `5c71f7178690356219a0c800e1206412ad059de11dd9981873472c15e83868d0`. In the battle-entry segment, 5,400 hashes, nine RGB captures and the SRAM also match between strict AOT and the interpreted reference.

The private evidence is at `local/work/chapter1-victory-followup/corridor-bridge/continuous-night-to-tutorial/verification.json`. The new tutorial's handoff reaches an interface similar to that of the historical state, with RGB and guest RAM differences. The [full cold replay](#full-cold-chapter-1-replay) below records the completed route.

## Full cold Chapter 1 replay

The English disc 1 route now runs from a cold New Game through the first battle, the postbattle save, and Resume to the hanami epilogue. The 511,978-frame input movie uses ordinary controls and starts both runs with a fresh profile and SRAM. The first guest hash agrees with a separate cold frame-zero reference with blank SRAM. The route joins the corridor at frame 119,780, the overnight save at 149,376, the corrected battle tutorial at 297,105 and the verified bridge approach at 324,603. From the later tactical handoff at 459,334, Maria and Sakura defeat the shrine guard. Ogami survives the fourth enemy phase by using Heal and defeats Satan in round five. The route overwrites slot 1 and selects Resume.

| Verification | Native headless | Enhanced SDL |
| --- | --- | --- |
| New Game to hanami | 511,978 frames | 511,978 frames |
| Fresh launch and Continue from the SRAM written by that run | 9,500 frames | 9,500 frames |
| Interpreted blocks | 0 | 0 |

Both full hash logs were identical and matched the verified segment references. Both fresh Continue runs matched the same 9,500 guest hashes, reached hanami, and preserved the completed SRAM. The full Enhanced profile used a 1280×720 window with PC backgrounds and verified portrait replacement enabled. It preloaded 38 backgrounds and 604 portrait variants. The native comparison reproduced the final hanami RGB from its final state and matched the segment reference. The Enhanced captures show the opening, corridor, prebattle save, tutorial, shrine, farewell, postbattle Save Complete and epilogue. The terminal emulator state files differ in four bytes at offsets 4,217,313–4,217,316.

- Runtime SHA-256: `d7db281302bef15e84f227bb191bb830406a330efc4f5c2515fa5bf209e1c360` (674,182 recompiled blocks).
- Full input movie SHA-256: `091b157c76066ee44131c2102ea64aa0a7c7c0713dc1066e0ac637e640762c1c`.
- Full guest hash log SHA-256: `d5eabf510c933aa7896c26e4d4614426c9bc28b257266583baec44d1afeec9b8`.
- Chapter SRAM SHA-256: `473e662f04143fb15de6f4d92ad73f5a7c405f78a055d203fcc47a8fddf95876`.
- Cold Continue movie SHA-256: `0a54353b4d3a3338010a1d0f033306a1c6e8855d22b978d1f8f69424541419b3`.
- Cold Continue guest hash log SHA-256: `5dde4196767eea71d70366355d6063bdf4344cba0adc7369e37921c1af7d6776`.

Private commands and evidence live under `local/work/codex-th1`. `run-earned-route.ps1 -Mode native` and `-Mode hd` run the full movie. `compare-earned-route.py` checks the logs, the guest hash rows and the postbattle SRAM. `run-earned-continue.ps1` starts a fresh process from each actual battery save. The full-run comparison and the separate Continue reports are under `earned-route/`. The plan records the segment boundaries and the expected hashes.

This closes the replay requirement for one English disc 1 path on the pinned runtime. Chapter 1 asset attribution and unresolved HD replacements remain under TH1, and package validation remains under T26. The replay evidence stays local and the released packages are unchanged.
