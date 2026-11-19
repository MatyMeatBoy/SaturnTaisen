# AOT sweep of later-episode saves

The isolated executable `local/build/sakura/sakura-episode2.exe` with 643,320 blocks was used. Its SHA-256 is `a5fabd38b0b2fd80d877482903d9d5537c2c7920f9ad36042d4ca1075fcb0e2e`. Each test starts with a copied SRAM, boot of the indicated English disc, and Continue via inputs. The game's menu was checked to identify the episode and disc of each save. The bank and its sources are described in [Post-episode-1 validation points](later-chapter-validation.md).

The run files are under `local/work/later-chapter-audit/chapter-sweep`. Each folder contains the input derived from `tests/cold-load.movie`, run parameters, slot-selection capture, hashes, and runtime log. `seeds.json` identifies the hash of each SRAM copy and the bank member when applicable. `provenance.json` keeps the hashes of the two discs, the bank, and the executable.

## Verified points

| Observed selection | Strict AOT segment | Post-Continue evidence |
| --- | --- | --- |
| Episode 3, File 1, CD‑1 | 12,000 frames, zero interpreted blocks | Opening dialogue and episode 3 title at the end. Folder `bank-3-battle-1-strict`. |
| Episode 4, File 1, CD‑1 | 6,678 complete frames. Exits with code 4 when entering `00204000`. | Load menu confirmed. Folder `bank-4-battle-strict`. |
| Episode 5, File 1, CD‑1 | 12,000 frames, zero interpreted blocks | Opening dialogue after Continue. Folder `bank-5-battle-strict`. |
| Episode 6, File 1, CD‑1 | 12,000 frames, zero interpreted blocks | Opening dialogue after Continue. Folder `bank-6-battle-strict`. |
| Episode 7, File 1, CD‑1 | 12,000 frames, zero interpreted blocks | Episode title at 10,500 and dialogue at 12,000. Folder `bank-7-battle-strict`. |
| Episode 8, File 1, CD‑2 | 12,000 frames, zero interpreted blocks | New Year narration and subsequent dialogue. Folder `bank-8-battle-1-strict`. |
| Episode 9, File 2, CD‑2 | 12,000 frames, zero interpreted blocks | Post-load dialogue in the 7,500 and 12,000 captures. Folder `public-9-strict`. |
| Finale, File 1, CD‑2 | 12,000 frames, zero interpreted blocks | Initial dialogue. The bank member's name declares chapter 10. Folder `bank-10-battle-1-strict`. |
| Finale, File 3, CD‑2 | 12,000 frames, zero interpreted blocks | Another Finale dialogue. Folder `public-finale-strict`. |

Eight routes each completed 12,000 frames, 96,000 in total, with zero interpreted frames and zero individual instructions. `final-state-matches.json` keeps the hashes and the files that match in RAM. `observed-scene-resources.json` links the `menu` and `dialogue` tags with the disc, the episode shown by Continue, the observed capture, and the run state. Zoom suitability remains unknown, and the indicated fallback is native.

The narrative scripts in the following table match byte for byte from `00204000` in the saved states. For each family, the dialogue table from `00224000` and the portrait atlas from `00251000` also match. All three files are under `/SAKURA1` and their correspondence is documented by RAM residency.

| Observed episode | Disc | BIN / TBL / FCE family |
| --- | --- | --- |
| 3 | CD‑1 | `0301` |
| 5 | CD‑1 | `0501` |
| 6 | CD‑1 | `0601` |
| 7 | CD‑1 | `0700` |
| 8 | CD‑2 | `0801` |
| 9 | CD‑2 | `0900` |
| Finale, File 1 | CD‑2 | `1001` |
| Finale, File 3 | CD‑2 | `1004` |

## Episode 4's initial lock

The interpreter on the same binary completes 6,692 frames. Its first 6,678 hashes match AOT, including `3879c325e99c165a` at the last common frame. The interpreter's states from 6,677 to 6,680 contain the **77,716 bytes** of `/SAKURA2/EVT06.BIN` at `00204000`. This file, at LBA 221800 on English disc 1, has SHA-256 `3214506d26f1b9fbec18190e993acf4ef5502532522790d7a327efe7125c89e5`. The RAM comparison is exact across the four states.

`bank-4-battle-reference/state-6678.bin` preserves the boundary, SHA-256 `42ab8d52f4b844bd45ae80ca799b98a7732e84f8e0814164a4b89a1f718cba14`. Restoring this state under strict AOT with a copied SRAM and no inputs produces the same exit code 4 at the first frame again. The command is in `bank-4-strict-from-boundary/boundary-replay.json`. The matching routes and logs appear in `checkpoint-state-matches.json`.

## EVT inventory

`evt-pointer-metadata.json` gathers 27 files by content across the four prepared profiles. Each candidate logs SHA-256, ISO locations, and 32-bit aligned words that would point within their own range if loaded at `00204000`. This signal offers inspection candidates. The RAM-verified base is distinguished with `base_observed`.

EVT06's match at the boundary state adds an observed base to those of EVT01 and EVT02. The initial pointer sweep was saved before the EVT06 test, and its match report preserves the later evidence.

A 12,000-frame route certifies the milestone shown in the capture. The save labels name the destination proposed by the bank, and the game may start at the episode's prologue. The intermediate and final segments of each chapter are still to be run.

## EVT06's later fix

The registered entry from `discover_registered_overlays.py` adds EVT06 only after fully attributing its bytes to 00204000. From the 643,320-candidate base, 30,703 are added, yielding **674,023**. The isolated base and binary remain private; the shared seed and executable are not replaced.

The previous binary fails the regression from state 6678 with code 4. The candidate passes 1,200 frames from that state, with all hashes and the final RGB matching the interpreter. It also preserves the episode 2 regression. The route from the original SRAM and `tests/chapter4-load.movie` completes **12,000 frames** with zero interpreted blocks, all hashes matching the interpreter, and identical final RGB. The first 6,678 hashes also match the pre-fix run. The last hash is `c8f0bd57666eb8e9`, and the capture shows the tactical field with the units.

The [fix report](episode4-aot-fix.json) keeps hashes and bounds. The private verifier had a formatting error in the PNG name after comparing hashes; it was fixed and the existing image was verified under its real name, without altering or re-running the game's data. Both game processes ended with code 0. This result closes the observed load lock, not the victory nor the entire chapter. The published test.1 version is not modified.

## Episode 4 second tactical overlay

The disc-1 Episode 4 route starts from the same copied backup RAM and `tests/chapter4-load.movie` as the EVT06 proof. After frame 12,000, the trial pulses A for seven frames every 105 frames to advance the dialogue. The cold strict-native development runtime completes 15,859 frames and stops at master SH-2 PC `00204000`. Its final guest hash is `03e4768050826a51`. A relay from frame 14,000 reproduces the stop at relay frame 1,859, with the same guest hash.

The disc trace reads `EVT21.BIN` at FAD 222176 and then loads MAP21, WKL21 and UNIT21. The interpreter boundary state contains all 75,364 bytes of EVT21 at low WRAM `00204000`. The file SHA-256 is `ee4180e542c543a6af6d68cea487f788695c757e72ee060a8c973017df104afc`. All 55 newly executed candidate variants recorded through relay frame 1,960 belong to the statically analysed EVT21 extension.

On a private 674,182-block base, the registered overlay adds 21,488 distinct variants. To regenerate the database from the matching discs and a private base, run:

```powershell
python tools/discover_registered_overlays.py --image "local/prepared/disc1/Track 01.iso" --module EVT21 --seed-blocks local/work/sakura/blocks.txt --output local/work/evt21
```

The isolated build linked all 21,488 additional native variants. It completed the 4,000-frame relay with zero interpreted blocks. All guest hashes and 13 RGB captures matched the interpreter run, including the new tactical field. The final guest hash was `4c2c58f80ad1ee27`. The runtime SHA-256 was `c28c9747b4af062fbb4661f8a45f32ab520b105e3c081efe37ae24d6c5036886`.

Private recovery commands and test receipts are in `local/work/codex-tw2-later-eve`. This is the validated EVT21 entry and follow-up segment. Full chapter completion and inclusion in a package remain open.
