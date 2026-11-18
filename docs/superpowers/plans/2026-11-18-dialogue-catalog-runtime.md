# Runtime dialogue catalog — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Prepare the script text once and link it to the native framebuffer before replacing the dynamic line reconstruction.

**Architecture:** Immutable cache keyed by exact content, with a witness captured alongside the framebuffer. Bounded reading precedes parsing; rendering keeps its current logic until the observer tests are complete.

**Tech Stack:** C++20, existing discFileReader, existing TBLparser, SDL, and private Clang/fixture tests.

**Spec:** ../specs/2026-11-18-dialogue-catalog-runtime.md

## Global Constraints

- Only the user's private resources; no script or dump goes to Git.
- Windows x64; C++20; SDK/patches registered before build_runtime.
- Approved Original and Zoom framings stay intact, 16:9 max, integer scaling.
- Do not alter guest bytes, timers, inputs, or text rules.
- Every SDK change is captured in a patch and validated as a composite tree.

## Review Focus

- Table partially overwritten during a load: must not produce a valid witness.
- Pointer outside the text, or a different table revision: do not infer a record by ID.
- Uninterpreted controls or geometry outside 4×31: keep the data and flag the visual preparation as unsupported.
- Mode change in the selector, or pause: load once and do not introduce per-frame disk work.
- Frame shown after run-ahead or a state load: use framebuffer metadata, never RAM restored afterward.

### Task 1: Pure, bounded cache

**Files:** SDKport/dialogue_preload.h; tests/test_dialogue_preload.cpp.

**Interfaces:** namespace port, DialogueWitness{bool valid; uint32_t table,record,offset;}, PreloadedDialogueLine{uint32_t rawOffset; std::u32string text;}, PreloadedDialogueRecord{id,index,offset,prefix0,prefix1,raw,array4lines,lineCount,simple}, PreloadedDialogueTable{name,fingerprint,bytes,records}. DialoguePreload::Add(string,span<const uint8_t>), Seal(), Sealed(), TableCount(), RecordCount(), ReadyCount(), SourceBytes(), Tables(), Get(witness), Locate(low,high), all observers const. Add returns bool; Locate returns DialogueWitness; Get returns const PreloadedDialogueRecord*.

- [x] RED test for a valid table/CP1252/line breaks/prefixes and flagged record.
- [x] Implement with the existing parser, 128 tables, 8MiB of source bytes, 65,535 global records; prevent Add after Seal and duplicate names. Do not silently truncate data.
- [x] Precompile up to 4 rows/31 columns; keep the full raw data and mark simple=false for unsupported controls. Tab remains uninterpreted.
- [x] Locate requires both 1MiB banks, exact table at low+0x24000, and a BE32 pointer at high+0x6851C. Validate text after the 4-byte prefix and up to/including NUL; reject ambiguous results.
- [x] GREEN tests for bounds, altered revision, invalid pointers, truncated table, end of string, and Seal; save evidence.

### Task 2: Integrated reading and capture

**Files:** SDKport/disc_files.h/.cpp, port/port.h, port/main.cpp, port/frontend_sdl.cpp; reading fixture.

**Interfaces:** DiscFiles::ReadBounded(name,data,maxBytes), Port::PrepareDialogueCatalog(knownAtlas), shared_ptr<const DialoguePreload> and fbDialogue; copy to shownDialogue under fbMutex. Preparation only with the verified English atlas, enhancedPresentation, and HDtext.

- [x] RED test for ReadBounded: size above the limit is rejected before reading and leaves data empty; valid read and partial failure both checked.
- [x] Read TBL with the remaining budget, compile and seal before publishing the catalog. Log counters/timing under SATRECOMP_DIALOGUE_TRACE; no new technical UI.
- [x] Capture Locate() in the framebuffer's own callback and copy the witness alongside softwareShown. Do not serialize it with guest state.
- [x] Real-catalog test 56/29,725, 29,723 preparable; 2 controls preserved. Test of known Sumire/María/Iris samples and choices, and rejection during loading.
- [x] Compare hashes/RGB and GUI before/after, with Original having no new preload. Verify a single preparation per session/mode change, not one per frame.
- [x] Capture patch0048, validate the composite tree, and review before integrating. Do not declare T11 complete.

### Task 3: Rendering from preloaded lines

**Files:** frontend/UiTextLine and a separate reveal-mask helper; coordinate ownership before editing.

- [x] Test the mask/expected cell against the atlas and commands from the same framebuffer, without advancing letters or erasing unknown glyphs.
- [x] Use views into immutable lines and the already precooked font; keep approved positions, plates, color, and clip.
- [x] Repeat reveal, advance, 4 rows, fades, and portrait entries/exits; measure coverage and fallback. Choices require separately identifying their full set.
- [x] Update pendings/evidence and close only the tested cases, without modifying test.2.

Task 3 evidence: patch0049, candidate 377cb29…; 14 cases/2,280 hashes/104 matching RGB pairs. Narrative with origin 64, clip 56 intact, and effective catalog traces. T11 remains partial: per-set choices and overall coverage still pending.
