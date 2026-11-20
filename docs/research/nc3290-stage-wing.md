# NC3290 stage-wing close-up

The natural English disc 1 Chapter 3 stage-wing route selects NC3290 at
offset `0x69C6` in `0301.BIN`. The CD trace reads FAD 164022 in ten sectors.
At the retained frame 4600 the active VDP1 command at byte `0x80` draws the
exact 80×96 texture at native (192,8) using the first CRAM bank. All 2,816
opaque texels match the native RGB under the 1440p presentation crop. The
separate eye and mouth commands retain their own textures.

Patch 0181 uses presentation's existing registered-body overlay with PC
`NC3290.SPR` subimage 0 (167×210). A fit against the interior of the naturally
composed face measured mean RGB correlation 0.9294. The baked thousandth-unit
scale is (2180,2257) with origin (−19522,−3028). The 12-sample donor edge
taper covers 8,412 of 11,264 opaque 2× samples, leaving the uncovered crop
and both face openings native. The existing full visibility check also
preserves the native composite during fades or overlays.

The strict replay starts from the unchanged frame-4550 state before the
close-up and follows normal input from the archived stage-wing replay.
Six 145-frame runs agree on every guest hash. The candidate draws at
(1504,29), size 560×672, on 118 frames and rejects native visibility on
15 early frames. Five positive 1440p samples each change 102,102 pixels,
all matching independent projection of the registered donor and confined
to the native body silhouette. An early frame and all six sampled frames
in Original and missing-donor replays match their reference images. The
native face holes also match through an observed 7,448-pixel change in
the eye and mouth region between samples 30 and 130.

Both discs carry byte-identical NC3290 resources. This route verifies the
disc 1 appearance. Disc 2 scene coverage and package inclusion remain
pending. Private replay data is under `local/work/codex-nc3517-route/`.
