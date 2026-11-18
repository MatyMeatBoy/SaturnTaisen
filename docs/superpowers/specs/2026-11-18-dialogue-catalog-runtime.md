# Preloaded dialogue catalog at runtime

Scope requested by the owner: use the game scripts as preloaded internal data for the HD text, preserving the approved font/size/spacing, reveal, voices, choices, and Original. The owner's texts and dumps stay in local/ and are not published. This spec concretizes the already-requested T11 work; it does not change the framing nor add a new selection for the player.

## Evidence

Disc1 English contains 56 distinct TBL, 2,242,176 bytes, and 29,725 records with 1,190,080 bytes of text. There are 29,723 records with a maximum of 4 rows/31 columns and no unknown controls; the remaining two have a tab. The same 56 TBL are on disc2. Do not modify the tabs or prefixes without testing their meaning.

In v9 states, the BE32 word at HighWRAM 0606851C marks the start of the text: Sumire 50039 and María 50064 in 0100TBL, Iris 10507 in 0102TBL. The full tables match at LowWRAM 00224000. The interpreter cursor 060685B4 is a different piece of data and must not be confused with the text pointer. In choices, the last processed text may remain: do not attribute all options to that single record.

## Design

Prepare an immutable cache from the user's disc TBL files. Keep exact bytes to identify the revision, IDs/prefixes/offsets unreinterpreted, and ready UTF32 lines. Bound reads and budget before allocating. Do not generate or include original scripts in Git.

Capture a content witness with each framebuffer, before restoring run-ahead RAM. Only resolve a record if the full table matches and the pointer lands within its text. Do not search by ambiguous fragments nor treat a residual FILM header as a phase. The cache and the witnesses are host data, outside guest state.

The first stage prepares and verifies the link; it does not yet change the drawing. The next stage will use preloaded lines and native reveal masks, keeping the exact current glyph plates, colors, clips, and positions. Untested cases keep the existing behavior. Do not call T11 finished just because an observer exists.

## Invariants

Windows x64, C++20, and a pinned SDK. Max 16:9, integer scaling, approved Original and Zoom intact. Guest hashes and native RGB equal before/after; GUI samples equal while only the observer is being added. Catalog tied to source bytes; a table from a different translation is not accepted just because it shares IDs. No new auxiliary work in headless or in Original before HD is enabled. No RA sync or networking within this block.
