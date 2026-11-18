# Validation points after chapter 1

Chapter 2 already has an entry point reproducible via Continue. With the isolated binary at 614,024 blocks, strict AOT and the interpreter on the same SDK match up to frame 6,688. The former stops when entering `EVT02.BIN` at `00204000`. On English disc 2, the boot and Continue test for chapter 8 was completed up to frame 9,501, with zero interpreted blocks and zero individual instructions.

## Chapter 2 on disc 1

The SRAM copy `local/work/later-chapter-audit/episode2-test-copy.bin` was read from member `Battle Saves/Chapter 2 Battle.bkr` of `Battle_Saves.zip`. It contains the bank's compact 32 KiB SRAM container and a 5,708-byte `SAKURA___01` record. All bytes of the original member were preserved.

| Artifact | SHA-256 |
| --- | --- |
| Chapter 2 SRAM | `4c22bf1edd1437b082ccd05e12df5bbf46bdcc5c9058fa3cc869db281f043908` |
| `Battle_Saves.zip` | `cd4f151db9ab0e0cc793060f6201c5233d3cafa35a2ecc02266a648a2b955677` |
| Isolated binary `local/build/sakura/sakura-test1.exe` | `67ef0bdc41321bd19231f637070d6dd39fe6bd17df63527dffde61aa4a79cbb7` |
| English disc 1 ISO | `5b19031460c87b4773ef2cbd70ef2170bef41c1117ec8cefe27b2af1309205ec` |
| `tests/cold-load.movie` | `0a54353b4d3a3338010a1d0f033306a1c6e8855d22b978d1f8f69424541419b3` |

Beetle Saturn v1.32.1 showed three chapter-2 save slots, all marked CD-1, at frame 2,000 of `beetle-ep2`. File 1 loaded the opening dialogue over the tactical field, visible at frame 3,900. Continuing with A showed units on the map in `beetle-ep2-tactical`. This sample reaches the combat intro.

The native test uses `tests/cold-load.movie`, a single SRAM copy and disc 1. The logs `ep2-strict-anchor/frames.hash` and `ep2-reference-anchor/frames.hash` match for their first 6,688 frames. The last common hash is `3408341dbb7917d3`. Strict AOT exits with code 4 when trying to execute master block `00204000`. The interpreter continues up to the 6,701 limit, with `9a24e290a77f5d9d` at frame 6,689.

In both paths, the state saved at 6,688 contains the 76,180 contiguous bytes of `/SAKURA2/EVT02.BIN` in Low WRAM starting at `00204000`. The match is complete and already present in the states for 6,686 and 6,687. File SHA-256 `701d68ab48e67eabce1e1eb89bd4a8b790aa0f6a40ff68bbfa0600489b97c660`, LBA 221648. The prepared Japanese disc 1 contains the same bytes at LBA 251972. The exact path for this module is absent on both prepared disc 2 copies.

Full evidence stays under `local/work/later-chapter-audit`, including the exact commands, `episode2-overlay-attribution.json` and `ep2-strict-anchor/state-6688.bin` (SHA-256 `61b8cbb898f59c116509640a496ce8fb25e8b4d9d85c46d9ccef2d3533c05333`). Playback uses button presses and a normal SRAM load.

Restoring the 6,700 reference state and advancing one frame with no input, the hash matches again with the 6,701 hash from a cold boot, `673663ba1db8f5f8`. The capture `ep2-reference-6701-screenshot/shot-000001.png` shows a black screen at that sample. The `evt-family-inventory.json` inventory logs 14 EVT files per profile and 27 variants by SHA-256. Observed bases are recorded only for EVT01 and EVT02.

```powershell
python local/work/later-chapter-audit/replay_ep2_anchor.py strict local/work/later-chapter-audit/replay-strict
python local/work/later-chapter-audit/replay_ep2_anchor.py reference local/work/later-chapter-audit/replay-reference
```

Each invocation creates a fresh target with logs, hashes and boundary states. Code 4 reproduces the reference binary's failure in strict mode.

## Other entry points

| Source | Declared or observed chapter | Test path |
| --- | --- | --- |
| `Battle_Saves.zip` | The 16 names declare battles in chapters 1 through 10. The names are selection hints. Chapter 2 was observed in the game. | Check the slot and disc indicated by Continue before fixing each path. |
| `disc2Start.bkr` | Menu observed in Beetle. File 1, chapter 7 CD-1. File 2, chapter 6 CD-1. File 3, chapter 8 CD-2. | File 3 loaded chapter 8's intro on English disc 2. File 1 triggered the CD-1 switch prompt. |
| Public import from privateye | Menu observed. File 1, chapter 8 CD-2. File 2, chapter 9 CD-2. File 3, Finale CD-2. | Chapter 8 loaded under strict AOT for 9,501 frames on the 614,024-block binary. SRAM SHA-256 `1b3457dc6b2f0f5d3aefd1e69873ca7126720be75253554551219d77acb8c5f2`. |
| Public import from Pimpeaux | Menu observed. File 1, chapter 8 CD-2. File 2, chapter 7 CD-1. File 3, Finale CD-2. | File 3's historical path loaded Finale with zero interpreted blocks per `public-save-fixtures.json`. The state and replay are kept under `local/work/sakura`. |

The bank is at `local/research/noahsteam-repo/SakuraTaisen/Data/SaveData` from checkout `10aefa40c555c2b1135b5836434c2315135b5306`. `disc2Start.bkr` and `bkramDisc2Start.bin` have different containers with the same save-record SHA-256. The English disc 2 data track has SHA-256 `fb813e8fe15caf03887321a5ceacb32d5d8822801fba460af726a59a6753770b`.

The private inventory `inventory.json` logs the bank and the review of name/format candidates under `local/work` and `local/profiles`. Of 639 candidate files, 579 decoded a Sakura record, grouped into ten container hashes. Copies with the same hash are listed together. Historical chapter 8 and Finale states were verified by v9 state signature and by comparing each native/interpreter pair. In those pairs, the only differences fall within the documented host pointer.

## Follow-up test

1. Verify hashes and copy SRAM to a fresh test profile per run. Use the disc indicated by the game's slot and Continue. Keep the `movie` and the state immediately before each milestone.
2. Compare strict AOT and the interpreter on the same binary with the same `movie`. Log the first missing block, its PC and the contents of Low/High WRAM in states on both sides of the failure. Identify the module on disc by byte match.
3. After extending a path, replay from the original SRAM and replay file. Log the new stretch up to the next milestone and keep the hash comparison.

The paths start from advanced saves. Verification covers entry into chapter 2, reproducibility of the first missing block, and chapter 8's load. Battles, endings and continuous transition between discs are still to be walked.

## EVT02 fix verified on a local candidate

The registry in `tools/discover_registered_overlays.py` fixes EVT02 to the version and base attributed by the full match in RAM. It rejects versions with a different size/hash; it does not assume every EVT is placed at that address. New candidates are generated in a private directory and keep earlier variants for the same CPU address.

29,296 candidates were added to the existing 614,024, reaching 643,320. The isolated build recompiled 75 generated objects and reused the remaining 1,535 whose sources were identical. It did not replace the shared executable used for the Spanish tests nor modify its active base. The objects/steps and hashes are in the private manifest under `local/work/episode2-candidate`; the [public report](episode2-aot-fix.json) contains only metadata and results.

Before the change, the regression from state 6688 fails with exit 4 at 00204000. After it, the candidate passes 1,200 frames from the same state: all hashes and the final RGB match the interpreter, with zero interpreted blocks under AOT. The test from the original boot and SRAM also completes **9,501 frames**, all matching the interpreter, with identical final RGB and zero interpreted blocks. The last hash is `332fc7fa22f639e9`; the capture shows the combat's opening dialogue. This closes the observed loading blocker, not the whole battle.

v0.2.0-test.1 remains unmodified and still contains that chapter-2 blocker. The fix is verified on a local candidate, not in a new release. The build used for this result keeps the presentation from before the T10 prototype, isolating the code expansion from the visual changes that are tested separately.

```powershell
python tools/discover_registered_overlays.py `
  --image "local/prepared/disc1/Track 01.iso" --module EVT02 `
  --seed-blocks local/work/sakura/blocks.txt `
  --output local/work/episode2-aot
```

The result is a candidate base: coordinate its AOT regeneration in its own directory before promoting it. For the regression, `tests/test_later_chapter_runtime.py` uses the private fixtures; `SAKURA_OWNER_ROOT` and `SAKURA_LATER_TEST_EXE` let you point to the owner's workspace and the isolated binary from a worktree. `SAKURA_LATER_COLD=1` enables the long comparison from SRAM; without that variable, the 1,200-frame boundary is tested.
