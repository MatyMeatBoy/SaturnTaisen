# T21 — reproducible AOT coverage for overlays

Scope approved in the queue: automate the K001–K019 expansion that fixed Sumire, without modifying disks or the shared base used by Claude.

1. Add synthetic tests for exact family identification, bounds/alignment/base, duplicate variants, preservation of previous candidates, and rejection of incomplete data.
2. Implement `tools/discover_battle_overlays.py`: read prepared ISOs, validate overlays, deduplicate by SHA, reuse `static_program.discover`, merge candidates while preserving variants, and emit a base/manifest in a new private directory. The SDK can be explicitly specified to work in an isolated worktree.
3. Reproduce from the private base prior to the fix with the four available profiles. Compare the resulting set with the current 614,024 candidates, without promoting it or regenerating the shared executable. Log inputs, hashes, and bounds; candidates do not equate to executed coverage.
4. Review, open PR T21, and integrate with the updated queue. Workers document verifiable points for later chapters and separately review T10.
