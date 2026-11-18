# Static coverage expansion

`tools/static_program.py` uses the SH-2 definitions from the pinned dependency. It extracts the first regular file from the ISO9660 root and its load address from the Saturn header, without extracting assets to paths chosen by the image. It checks the bounds of each extent and the little/big-endian copies of the directory fields. It also supports binary images with an explicit base.

The analysis follows calls and direct branches, call returns, and aligned pointers that point inside the program. It recognizes the `MOVA / MOV.W / ADD / JMP` switch pattern, with the bound obtained from an unsigned `CMP/HI` comparison and its exclusion branch. It includes the variant that places the index copy in the delay slot. It does not guess the end of a table by walking neighboring data.

The first pointer-based expansion added 4,209 candidates to the set that had been obtained by playing. The continuation found an entry missing at `0x0601AB1A`; code analysis identified a relative-offset table. The recognizer was tested first on a synthetic program that failed, then on the real case. Other observed patterns and targets were incorporated through instrumented discovery, without introducing an SH-2 fallback interpreter in production.

The `static-program-analysis.json` report records hashes and counts for the four initial programs: two discs, English translation, and original Japanese. The initial expansion gathered 16,767 variants. The later exhaustive analysis preserves all decodable prefixes from aligned addresses: the set of initial programs gathered 253,159 variants, with no grouped functions. This includes alternate entries and candidates that were not run: the number does not equal percentage of the game completed.

## Execution evidence

- The 18,001-frame continuation from the theater state matches frame-by-frame between interpreter and AOT with 12,943 variants. Local report `post-theater-parity.json`.
- After expanding to the four programs, the 4,200 boot frames preserve the hashes of the previous reference interpreter. The runtime accepts the rules of the 16,767 blocks, with no incompatibility warnings.
- María's inspection allows moving the cursor, observing different zones, and selecting the mouth to continue the conversation. The 4,201-frame route then reaches the dialogue with Yoneda under strict AOT.
- 31 Python tests pass, including truncated ISO extraction, calls/pointers, branches, bounded relative tables, and invalid delay slots. A ResourceWarning from the upstream generator's definition reader is preserved; it is not a test failure.

The states are only local research instruments with the same runtime and the same image. They do not substitute for validating the game's save or its identity across profiles. Other routes, battle, minigames, sound contrasted against reference, and a real disc swap remain pending.

The exhaustive set also preserves the 47-instruction prefix when the next jump needs its delay slot. With 253,159 variants, the 4,200-frame boot preserves the previous hashes, and a 12,001-frame continuation from the sales booth runs under strict AOT up to the original options menu. The 12,001 hashes of that continuation match the interpreter; the reference was repeated after applying the CD cache patch. Navigation with 30-frame inputs allows selecting Exit and leaving to the items menu.

Patch 0007 invalidates the sector cache when the disc reader is reinstalled. A synthetic test first reproduces the stale sector and then verifies the content of the new medium at the same FAD. It does not equal a validated campaign transition.

The continuous replay `tests/chapter1-free-movement.movie` completes 119,781 frames from boot without loading states and without interpreting SH-2. The first 30,000 hashes match the previous reference. The states at frames 30,000, 47,999, and 119,780 match their research segments except for the host sound RAM pointer stored inside `sound::Dsp`, which the loader restores from the current machine. The field's size and offset were checked against the runtime's compiler. This route reaches an event in a hallway; it does not include battle.

The analysis also added candidates from `/SAKURA1/ENDING.BIN`, with inferred base `0x00204000`. The initial attribution of Continue to that module was corrected: its first 64 bytes match those of LOGO.SH2, but the function bodies observed at `0x0020528E` and `0x00208A02` correspond to `/SAKURA1/LOGO.SH2`. The common table alone does not identify the loaded module. Its two disc variants (identical between English and Japanese on each disc) were added to the set, which now contains 307,553 variants and zero grouped functions. `ending-module-analysis.json` records sizes, addresses, hashes, and the difference between observed and inferred address.

The `tests/cold-load.movie` test selects Continue, file 1, and Load/Yes from boot. With a previously saved own memory card, its 9,098 frames match between interpreter, AOT, and AOT replay. Opening the executable directly, without environment variables, also produces the same 9,098 hashes, zero interpretation, and zero bound host calls. The final state matches the segmented run except for the restored sound host pointer. The source memory card preserves its SHA-256. This verifies this save/load of episode 1, without extending the claim to other points nor to the disc transition.

The incremental manifest was initialized on the 253,163 blocks already compiled without rewriting any C++; adding the module preserved the previous files and wrote 138 of the resulting 769 files. Five synthetic tests cover identity with the first generation, stability against lower addresses and same-address variants, and rejection of duplicate or incompatible manifests. The eight patches were also applied to a clean checkout of the pinned commit: the thirteen modified files match the local dependency.

The route that opens a disc 1 save from disc 2 shows an original prompt asking to swap the disc and restart. The body of `0x00205E9C` matches LOGO.SH2 at offset `0x1E9C`, not ENDING.BIN. Native execution correctly halted when that variant was missing; the interpreter was used to identify it. The automatic transition is not yet implemented.

The later expansion with LOGO.SH2 from the four profiles gathers 406,725 native variants, with no grouped functions nor skipped blocks. The route that loads a disc 1 save from disc 2 now completes 9,098 frames under AOT and shows the original disc-swap prompt. Its state at frame 9,000 matches the reference except for the sound host pointer. The 31 tests still pass; both Japanese discs also pass their 1,800-frame boots with the default configuration.
