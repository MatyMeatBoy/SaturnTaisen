# LIPS choices from preloaded data

Continues T11 within the approved scope of preloaded HD text. Evidence: [LIPS cursor](../../research/lips-script-cursor.md). Does not modify the script, timing, inputs, positions, or delivered ZIPs.

## Design and limits

Prepare an immutable index of complete `2E8000` commands and their options record. Each group occupies one record with CR breaks. Capture its witness alongside the framebuffer, with a full match of the resident script and TBL and a BE32 cursor at 060685B4. The narrative pointer does not identify the options.

The helper accepts explicit limits and rejects ambiguous references. The host's first activation is pinned to 0102.BIN/26646 bytes/FNV0CE1CF29E7390A98, the observed source. Do not generalize to 178000, battle, or other scripts without evidence. Absence of a witness keeps the previous path.

The substitution is atomic per panel: clock, rows, centering, banks, ink, and current plates remain mandatory. Only if all options match their tiles/bytes and the full record do we borrow views from the sealed catalog. Do not reconstruct strings for the prepared group; keep the existing reconstruction as fallback.

## Work

- [x] ChoicePreload helper and bounded index; RED/GREEN tests for cursor, revisions, ambiguous cases, and limits.
- [x] Pure helper for option rows/tiles and tests for two/three rows, centering, CP1252, and bounds.
- [x] Full-panel fixture: borrowing of all rows, atomic fallback on a wrong record, and ink ownership intact.
- [x] Wire up preparation, capture under fbMutex, and copy alongside pixels; keep Original/headless/GPU outside the new work.
- [x] Capture patch0050 and validate the SDK tree before building into an isolated output.
- [x] Compare two/three-option panels, selection, confirmation, and expiry; identical hashes/RGB and effective catalog trace. Keep the caveats and the lack of testing on other branches.
- [x] Review, pendings, and evidence; integration via PR34. Test.3 remains unchanged.

## Ongoing verification

Three fixtures pass against the composite SDK0001..0050, re-validated with no differences. Candidate 674,182 has SHA256 `df68e9dbe2c7d9efe273e0e716c504774ba5c5f5f0826abc783a2e3d6bffcbd3`. Twelve run pairs match on 3,240 hashes and 102 RGB pairs, including Original, native text, Zoom, the set, and run-ahead 2. The traces verify 11 preloaded commands and real consumption of groups 20008/20002. Private evidence: `local/work/choice-preload-runtime/result.json`.

The first trial started from panels already confirmed and closing. Earlier seeds were obtained through normal inputs, without changing the guest or the clock. The private verifier `choice-input-probe/verify.py` passes for two/three rows: Down moves the highlight to the second row at 30; A dismisses the panel before 150 and opens the corresponding answer at 170; the neutral control keeps the panel at 150 and expires with a different answer at 450. Frontend inspection confirmed that the `moviePlay.empty()` guard does cover the controller write; no SDL input fixes were needed.

The additional comparison from those seeds now also passes for three options: six profiles, 2,100 hashes, and 59 identical RGB pairs, 0 interpreted. The equivalent two-option suite also passes: another 2,100 hashes and 59 RGB pairs. The three suites together total 24 run pairs, 7,440 hashes, and 220 matching RGB pairs, with zero interpreted. Independent review of the helpers/panel and three fixtures with no blockers.
