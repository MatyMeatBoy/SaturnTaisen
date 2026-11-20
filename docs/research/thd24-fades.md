# THD24: fades, pointer and dialogue box, chapter 1 witness

Same build, route and 2560x1440 Enhanced Zoom captures as [THD23](thd23-episode-cards.md) (`title-final.state` + `tests/chapter1-title-new-game.movie`, 6,701 frames, Original vs Enhanced guest hashes identical, `interpreted 0`).

Seen in the captures (every 40 frames, 5940 to 6700):
- Entry: floral background, card fades in over it (6140), card steady, card fades out (6620 to 6660).
- Letter to Sakura: after the card, floral background with the empty dialogue box (6660 to 6700), then the letter fades in under the box with its badge (6700). No black frame in the sampled shots.
- Empty box position stable in the sampled captures; earlier work: patch 0163 (held empty box), 0167 (cursor at the four edges, verified 940-frame replay), floral continuity patch 0040.

Not verified here: pixel check of the four box borders, pointer at all four edges, blink black on the real route, Spanish, 1080p, per-frame (every frame) captures. Existing evidence is in `chapter1-wide-transitions.md`.

## Spanish Episode 1 card to letter, v0.2.16.1-alpha

The installed Spanish disc 1 completed 8,751 strict fields from cold boot using `tests/opening.movie`. At 2560 x 1440, 35 captures every five fields from 8,580 to 8,750 show the card dissolving over the widescreen flowers, then the empty dialogue box, then the letter. None of the captures is black and all four corner samples remain nonblack. This covers the card-to-letter transition. Letter-to-Sakura, pointer motion and fields between samples remain open. Private evidence: `local/work/codex-th1/thd41-combined/card-es-fade/enhanced-1440`.

A second cold run captured every field from 8,580 through 8,630 at 2560 x 1440. All 51 frames and all four corner samples per frame remained nonblack while the card dissolved into the floral screen. Frames after 8,630 retain the five-field sampling above. See also the separate [letter-to-park and Spanish Sakura-entrance replays](chapter1-wide-transitions.md#held-empty-dialogue-position). Private evidence: `local/work/codex-th1/thd41-combined/card-es-fade-dense/enhanced-1440`.

## Inspection cursor edges with the published executable

A 940-field strict English disc 1 replay from the Maria inspection checkpoint reproduced all 940 guest hashes and 11 exact RGB captures from the [four-edge reference](chapter1-wide-transitions.md#inspection-hand-at-the-viewport-edges). The window measures 2560 x 1440. The v0.2.16.1-alpha executable was run outside the release marker directory so it could load the archived checkpoint. Its SHA-256 matches the packaged executable. Private results: `local/work/codex-th1/thd41-combined/pointer-regression-load/edges-final-1`.

## Spanish letter to Sakura at 1440p

The published v0.2.16.1-alpha executable and installer-produced Spanish disc completed a 6,361-field strict checkpoint replay from the letter through Sakura's park dialogue. The isolated runtime allowed checkpoint load. At 2560 x 1440 the 61 samples every five fields from 1,930 through 2,230 held the upper gold dialogue edge at y=1048 through the empty floral screen. Four corner pixels remained nonblack in each sample. The later sampled route reached Sakura at 4,560 and her Yoneda line at 5,280. Private evidence: `local/work/codex-th1/thd41-combined/letter-to-sakura-final/enhanced-1440`.

## First letter dialogue panel in Zoom

A Spanish disc 1 replay from cold-opening field 8650 showed the emblem
for 27 fields before the picture appeared. The default whole-frame
viewport drew the early panel at 4× at 1080p. The narrative viewport
then moved the panel to its final 5× layout.

Patch 0270 uses the same Zoom geometry for the witnessed standalone
floral dialogue panel before the first picture. In the 220-field A/B,
the emblem stays at (230,788), size 200 × 240, at 1080p and at
(404,1090), size 240 × 288, at 1440p throughout the sampled fade and
settled dialogue. Field 70 changes within the panel area, while the
six captures after the picture appears match exactly at each resolution.
All eight 1080p Original control captures match, as do guest hashes and
save memory in each pair. Release packaging is pending.
