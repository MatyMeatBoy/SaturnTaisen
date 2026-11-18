# HD font proportions

Scaling each glyph independently to its native ink box widened narrow letters and distorted their proportions. Now the whole font receives a uniform transform, computed from the reference advance and cap height. The game's eight-pixel advance and a shared baseline are preserved.

Detection checks ink pixels within the native interior (56,160)–(304,208), allowing the last glyph when its texture contains transparent margin. The HD drawing is clipped to the same projected interior. Original text and HD remain independent options.

Verification: fixture tests/test_text_layout.cpp covers edges, invalid sizes, narrow letters, height and baseline, and whole viewports at several resolutions. Real local capture: local/work/text-layout-qa/natural/scene.png. Native build correct; frontend/matching set: 24 tests passed. This is not a review of all dialogue.
