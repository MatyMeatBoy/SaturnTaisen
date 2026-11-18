# Entry point for contributors

SaturnTaisen project (formerly SaturnTaisenFirst). Before changing code, read:

1. [Pending items and current status](docs/PENDIENTES.md).
2. [Handoff and working method](docs/HANDOFF.md).
3. The research document for the area you are about to touch.

Saturn has priority; playable PC/PC translation are left for later. PC assets do serve the Saturn HD mod. Maximum 16:9, integer scaling, Original mode preserved. Do not move the approved Zoom framing again without a new request.

Dumps, BIOS, save states, original images, and reference compositions stay in `local/`. Do not add them to Git or to the public release. Extracted script text is different: only the original, untranslated Japanese text pulled from the discs must never be committed or released; translated/derived script text (English extraction, Spanish fan translation, etc.) may be published, including in public releases, since the game has no official English or Spanish release. The authorized personal ZIP is a separate local delivery. Keep the packages already delivered.

The dependency is modified in `local/deps/satrecomp`, but its changes are recorded as patches in this repo. Do not run `build_runtime.py` while there are unrecorded dependency changes: it validates the composite tree and must reject differences. Coordinate file ownership and builds with the active collaborator before working on them. Do not restore or clean up someone else's changes to make a test pass.

When closing a block, update pending items and evidence; distinguish implemented, tested, and included in a package. A saved state, a screenshot, or an approved suite do not certify complete chapters/campaigns.

## Mandatory workspace hygiene

- Maximum of two existing worktrees: main repository and one auxiliary copy. Reuse the available auxiliary one; do not create another while it is busy. Check `git worktree list --porcelain` before starting.
- When merging a PR, remove its worktree once it is clean, contains no unique local data, and its HEAD is preserved in Git. Use `git worktree remove` without `--force`, followed by `git worktree prune`. Never delete someone else's changes to free up a copy.
- Keep the project below 20,000,000,000 bytes and the development ZIP below 10,000,000,000 bytes. Measure and record the size when closing each block; remove regenerable intermediates before duplicating them.
- Keep a current runtime and a known previous reference, which may be archived compressed by verifying the CRC and SHA of the restored executable. Keep the AOT bases and their commands to regenerate sources/objects; remove generated trees and caches from closed trials.
- Share graphics assets between tests; each trial uses independent absolute profiles and outputs. Keep initial/final states, inputs, reports, and screenshots of relevant limits; do not accumulate full copies of assets or hundreds of default states.
- Dumps, BIOS, scripts, art sources, useful saves, and packages already delivered are kept. A duplicate extraction is removed only after verifying its manifest and the archive that allows it to be recovered. Delivered ZIPs are immutable.
- Cleanup is selective and documented: do not use `git clean -xfd`, indiscriminate recursive deletions, or restorations of someone else's changes. The personal ZIP being uploaded is not modified to incorporate later changes.
