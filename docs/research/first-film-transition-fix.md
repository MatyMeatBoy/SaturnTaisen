# First video: clean background before and after

Patch0046 removes, in Enhanced, the empty footer and image shadow from the verified phases of New Game. The active video keeps the 288x144 crop and its maximum integer scale from patch0038. Original is unchanged.

## Identity and phase

Program 0100.BIN is 15404 bytes and FNV64 `5DA24532C9356735`. It is read once via the simple name used by DiscFiles; other files are rejected. Each phase witness compares the full module against Low WRAM at 00204000 and reads the BE32 cursor from High WRAM 060685B4. The exact observed list is 00204006, 00204462, 00204ED8, 00204EDE, 00204EE4 and 00204EE6. The sequence and samples are described in [the cursor research](first-film-script-phase.md); these values are not a general identification of the SDK nor of all its opcodes.

The witness is captured in the framebuffer callback, under its same mutex and before restoring RAM after run-ahead. It is copied alongside the presented pixels. It is host metadata and does not enter guest state nor modify the script.

Hiding also requires a 320x224 frame with no image layers 1/2/4, visible floral background, and only layers 0/3 within known zones. Drawable VDP1 commands must be absent or exclusively the known footer/badge by mode, geometry and texture hash. The badge bank C400 or 4400 is accepted during its fade, and two identical footer copies on exit. Any unknown figure, glyph, texture or drawable command keeps normal rendering. The episode card uses layer 4 and is explicitly rejected even if cursor 00204EE6 persists.

## Continuous verification

Playback from title-final.state, with no intermediate divergent state loads, up to 6201 frames. The final candidate SHA256 is `453e1a6ae4679f654d27534c718edd7e5b817f97f8048a14178422dcbd1a1af1` (614024 blocks).

- All 6201 hashes match Original and the archived path; six native RGB captures match and there are zero interpreted blocks.
- Background only: steps 707..879 and 5938..6067, with no intermediate return to the novel group. Captures 806/807/820/830/831 and 5938/5939/5960/5988/5989 were reviewed.
- Enlarged video: 880..5937. The image uses the 288x144 area and does not include the empty text box.
- Step 6068: the episode card keeps its native content. That transition and the full title petal effect remain pending separately.
- The fixtures verify accepted/rejected cursors, altered module, truncated buffers, presence of image/actor outside the footer, and unknown commands. The failure was observed before implementing the fix.

The optional SATRECOMP_MOVIE_PHASE_TRACE traces number the cursor and layout changes to narrow single-frame defects. States, images and receipts are kept under local/work/first-film-phase-approved and the owner's earlier audits. The patch is tested on this path and is not yet included in a new ZIP. It does not demonstrate the full intro nor the campaign.
