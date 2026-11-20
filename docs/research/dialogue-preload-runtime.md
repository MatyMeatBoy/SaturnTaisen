# Native dialogue preload and witness

Patch0048 prepares an immutable disc catalog before drawing HD text. It preserves ID, index, offset, prefixes and original bytes; it precompiles the CP1252 lines without correcting the prose or the translations. Patch0049 uses views of those lines for verified narrative. The extracted content stays under `local/`. Candidate patch0050 extends the loan to verified LIPS groups, preserving proof of their current glyphs and plates.

## Identification

Across five private states, High WRAM BE32 `0x0606851C` points to the text of the current record. The full table sits at Low WRAM `0x00224000`. The witness requires both 1 MiB banks and a byte-for-byte match of the whole table, not just the record or its ID. It rejects altered tables, ambiguous matches and pointers outside the text. The position of the NUL terminator is valid. Do not attribute semantics to the prefixes without additional evidence.

| Sample | Table | ID | Index | Prefix offset |
| --- | --- | --- | --- | --- |
| Sumire | 0100TBL.BIN | 50039 | 473 | 32930 |
| Maria | 0100TBL.BIN | 50064 | 498 | 34408 |
| Iris | 0102TBL.BIN | 10507 | 546 | 34608 |
| Two-option LIPS | 0102TBL.BIN | 10250 | 284 | 21420 |
| Three-option LIPS | 0102TBL.BIN | 10035 | 63 | 11110 |

In LIPS, a pointer identifies a processed record, not the full set of options. The pointer can also persist after the dialogue disappears: it isn't enough on its own to decide that a page should be shown. The subsequent visual integration must verify the glyphs and their reveal mask from the same framebuffer.

## Limits and lifecycle

The reader rejects the declared size before allocating or reading; an incomplete read leaves the output empty. The catalog supports at most 128 tables, 8 MiB of source and 65,535 records; each TBL parser supports up to 4 MiB. It is sealed before being published via `shared_ptr<const DialoguePreload>`. Duplicate names and additions after sealing are rejected.

The 56 English TBLs contain 29,725 records and 2,242,176 source bytes. 29,723 records can be prepared as up to four 31-column lines. The other two keep their tabs and are flagged as not preparable; they are not truncated or replaced with spaces. The tables are identical between the two English discs checked.

Preparation is triggered once, with verified English atlas, Enhanced and HD text. It is also consulted when switching modes in the menu. Original, headless and the active GPU backend do not prepare the catalog; returning to Original or native text does not look up a record per frame. The observed path is the project's default software path.

The machine callback captures the witness alongside the pixels under `fbMutex`; SDL copies both together. This avoids querying RAM already restored after run-ahead. It is not serialized with the guest. `SATRECOMP_DIALOGUE_TRACE` reports one preparation per session and changes to the displayed record, identified by the framebuffer serial.

## Evidence and limits

The synthetic read test failed for lack of the API and then passed with a valid file, oversized file, missing file and partial read. The catalog fixture passed with Clang and covers limits, sealing, CP1252, controls, geometry and pointers. A private program read the full corpus and the five samples; altering the last byte of each table invalidated the witness.

Development build of 674,023 blocks: SHA256 `191e2e0a701bc0624727ea09fd06ba4caf836ecf4f824cca451bd09172907bf2`. The integrated comparison uses candidate patch0047 as reference, without modifying the delivered packages. Private results in `local/work/dialogue-preload-runtime/result.json`, with logs, hashes and captures per profile. Fourteen runs covered Sumire, Maria, Iris, two/three-option LIPS, Original and Iris with run-ahead2. Each pair matched on 60 hashes, three native RGB captures and one GUI capture at 1440p: 420 hashes compared, 21 native pairs and seven GUI pairs. All ended with zero interpreted blocks. Each Enhanced run logged a single preload and the expected record; Original did not preload. The preparation times from these runs do not demonstrate an improvement in the game's load performance.

## Visual consumption of preloaded lines

Patch0049 compares each observed tile against the expected byte of the record from the same framebuffer. A row only takes the catalog's view if its cells match and no letters are missing before the last visible cell; space gaps are valid. The view ends at that last cell, so it never advances letters. The sealed catalog belongs to Port for the whole session; moving the draw list leaves no references to temporary strings.

The measured command grid starts at x=64, with advance 8 and rows 160/172/184/196. The ink clip keeps x=56: these are distinct limits. A real test detected that the prototype with origin 56 stayed on fallback; besides comparing images, the tests require `catalog=1` traces. Inspection of the corpus's 263 rows of 31 characters found a trailing space on all of them. The ink guard still rejects content that falls outside the tested interior.

Candidate 674,182/patch0049 has SHA256 `377cb29b9e05d2f70d8a97c838e0cd9ccc511046ff690da54953b60dac5a0ba7`. It was compared against host0048 of the post-battle candidate e7dd1c0…, preserving the guest code. The seven initial cases checked 420 hashes, 21 native RGB pairs and seven GUI pairs at 1440p. They include Original, run-ahead2 and the two existing choices; the latter do not demonstrate LIPS text sourced from the catalog.

Six other cases checked 960 hashes and 50 native RGB/GUI pairs: partial reveal of four rows, full page, second-row continuation, four-row library, office sample and B-advance during a voice line. The traces verified effective catalog use, including at y=196 and from a single visible letter. The 1,380 hashes and 78 RGB pairs from both suites matched, with zero interpreted blocks. Private evidence: `local/work/dialogue-render-runtime-v2/result.json` and `local/work/dialogue-render-dynamic/result.json`.

The map→floral/novel transition added 900 hashes and 26 identical RGB pairs (17 GUI and nine native), sampling entry/fade between 400 and 550 and the dialogue afterward. The trace also confirmed catalog consumption. Evidence: `local/work/dialogue-render-map-fade/result.json`. Total across the three suites: 14 cases, 2,280 hashes and 104 RGB pairs, all matching the reference with zero interpreted blocks.

Pending: identify the complete choice sets, test LIPS expiry and extend coverage by route/chapter, transitions and fonts from other translations. Neither the full catalog nor these samples prove that all HD text is resolved. Not included in v0.2.0-test.2.

## Preloaded LIPS groups candidate

Patch0050 indexes the full `2E8000` commands of the observed script0102.BIN. The witness requires cursor 060685B4, the full resident script and the full table, associated to the same framebuffer under `fbMutex`. Size 26646 and FNV64 fingerprint `0CE1CF29E7390A98` are fixed; other sources and the 178000 command are not enabled by inference. The index supports 128 scripts, 128 KiB per script, 8 MiB total and 65,535 commands, rejecting ambiguities. In this script, 11 commands are prepared; that does not equal 11 choices actually played.

The panel takes catalog views only when all its rows agree — centering, tiles, ink, clock and plate ownership. A mismatch returns the whole group to its own strings. The input logic, the clock and the position of the options are not changed. The lifetime of the views is tied to the Port's sealed catalog.

Three fixtures pass against the real dependency, and the composite stack 0001..0050 matches the SDK. The general Python suite passes 167 tests with 88 skipped due to their local requirements; the three fixtures above were run explicitly against the shared dependency, without skipping them.

Twelve run pairs of candidate 674,182 (`df68e9db…`) against patch0049 (`377cb29b…`) compare 3,240 hashes and 102 identical RGB pairs, with 0 interpreted blocks. They include two/three-row panels in Zoom/ensemble, native text, Original and run-ahead2. The trace shows consumption of groups 20008/20002. Private evidence: `local/work/choice-preload-runtime/result.json`.

The first trial did not demonstrate interaction: its seeds had the selection fixed and still showed the panel during closing. The movie SDL guard was reviewed and does confirm it prevents overwriting the played inputs. Earlier seeds were sought via normal inputs, without modifying the guest or the clock. The private verifier `local/work/choice-input-probe/verify.py` passes for two and three rows: at frame 30, Down moves the selected bank C570 from the first to the second row; without confirming, it keeps that selection at 150; with A, the panel is already absent at 150. Confirmation opens another response at serial 170, and the neutral control expires at 450.

| Group | Response on confirming second option | Response on expiring without confirming |
| --- | --- | --- |
| 20008, two rows | 10269 | 10281 |
| 20002, three rows | 10054 | 10061 |

The controls log catalog consumption and 0 interpreted blocks. Private anchors: `two-anchor/f1176.state` SHA256 `a9b64760e87a7f574e397dd881e1c41a7972cd2633b2c2c26ff0dd3b5c762bb8` and `earlier/f0336.state` SHA256 `61a3de6ad685849fb729728f7a8816f33abc1831d850510a9a71485dfef150da`, under `local/work/choice-input-probe`. Their movies, states, fonts and text are not published. Review of the helpers and panel found no blockers. The additional cross-host comparison from those anchors passes for all six profiles of each group: 4,200 hashes and 118 identical RGB pairs, including selection, confirmation and natural expiry. Private evidence: `choice-preload-active-runtime/result.json` and `choice-preload-active-two-runtime/result.json`, under `local/work`. Added to the first suite, that's 24 run pairs, 7,440 hashes and 220 identical RGB pairs, with zero interpreted blocks. Candidate not yet included in test.3; the delivered packages remain immutable. Other choices, scripts, chapters and localizations are still pending.

## HD narrative ink index

Patch 0158 uses the verified native glyph band to index each ink pixel's
first dialogue row and the latest sprite owner within that row. The existing
glyph bounds check guarantees both array indices. The ordered glyph columns,
cross-row collision detection, saved-under plate verification, and selection
of the native ink colour follow the existing rules.

Two private builds used the same 0157 base, AOT objects and display settings.
Strict replays compared the office with a state reload at frame 250
(500 frames), the three-choice LIPS route (260), and the Spanish park dialogue
at 2560×1440 (400). All 1,160 guest hashes and 11 sampled RGB pairs matched.
Both builds reported zero interpreted blocks and the same VDP2 reuse counters.
The text-layout, glyph-plate, dialogue-preload and choice-text tests passed.

Three unthrottled alternating runs per build gave these medians of the
per-run HD text scan times, in milliseconds. Window captures were disabled
for the timed runs.

| Replay | Mean before | Mean after | P95 before | P95 after |
| --- | ---: | ---: | ---: | ---: |
| Office | 1.118 | 0.305 | 1.749 | 0.407 |
| Spanish park | 0.283 | 0.108 | 0.841 | 0.220 |

The measurement covers the HD text scan, including frames with little text.
The reported other-PC flicker and release packaging remain unverified.
