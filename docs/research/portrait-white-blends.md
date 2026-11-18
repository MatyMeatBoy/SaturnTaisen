# HD portraits during white blends

Patch 0037. The previous guard compares the native portrait without effects against the framebuffer already blended by VDP2. A valid difference caused by white blending triggers a fallback. Simply allowing an approximate color would be incorrect: it would draw the HD version without the fade and could accept an occluded sprite.

The compositor tracks per pixel whether the sprite actually participates in a white blend and at what weight. Shadows, non-zero offsets, additive blends, or untested effects invalidate that data. The substitution requires the same accepted weight and an exact RGB match of **every** opaque pixel of the presented portrait. The observed weights 5, 15, and 25 over 32 are accepted, plus the no-effect case. The HD texture receives the full matching transform, keeps its alpha, and its cache key includes the weight. No white inference is ever made solely from color similarity.

## Validation

- `test_portrait_match.cpp`: exact blend, accepted weights, alpha, incomplete metadata, occluded/differing pixels, and the no-effect case.
- `test_vdp2_color.cpp`: the real compositor blends a synthetic sprite over white with weights 5/15/25, emits the correct weight, and produces exactly the RGB of the HD transform; additive blending is rejected. The formula is not duplicated as an independent oracle.
- Isolated renderer/frontend build approved; the shared executable was not replaced.
- Two Yoneda save points (`office-return-3000` and `6000`) each ran 132 frames with zero interpreted instructions and kept the substitution with no effect. The additional 1,800-frame replay observed no white blend; it is not used as positive proof of the fade.
- `morning-9000.state`, SHA-256 `81de5f7ba12e092b174ee98a64e386c979460cc17d8c0b13b9407850668ca2b8`, did confirm portrait `0009` with a **25/32** blend and HD2 density at 2560×1440. The 132 per-frame hashes match test.1. In this particular sample, the presented RGB matches the native one exactly, so no visual difference is attributed where none exists. The record demonstrates that the HD version is accepted and transformed during blending.
- `test_portrait_white_runtime.py` compares HD on/off at that save point, requires the trace `density=2 white_mix=25`, zero interpreted instructions, and guest/RGB parity. Weights 5/15 are covered by the synthetic compositor, not by a real path claimed as tested.

States, packs, images, and logs stay private under `local/work/portrait-white-*`. The improvement is prepared for future builds; the published ZIPs are not replaced. Other animations, identities without a match, different effects, and physical interaction tests remain pending.
