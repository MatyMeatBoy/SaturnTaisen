# THD24: fades, pointer and dialogue box, chapter 1 witness

Same build, route and 2560x1440 Enhanced Zoom captures as [THD23](thd23-episode-cards.md) (`title-final.state` + `tests/chapter1-title-new-game.movie`, 6,701 frames, Original vs Enhanced guest hashes identical, `interpreted 0`).

Seen in the captures (every 40 frames, 5940 to 6700):
- Entry: floral background, card fades in over it (6140), card steady, card fades out (6620 to 6660).
- Letter to Sakura: after the card, floral background with the empty dialogue box (6660 to 6700), then the letter fades in under the box with its badge (6700). No black frame in the sampled shots.
- Empty box position stable in the sampled captures; earlier work: patch 0163 (held empty box), 0167 (cursor at the four edges, verified 940-frame replay), floral continuity patch 0040.

Not verified here: pixel check of the four box borders, pointer at all four edges, blink black on the real route, Spanish, 1080p, per-frame (every frame) captures. Existing evidence is in `chapter1-wide-transitions.md`.

## Spanish Episode 1 card to letter, v0.2.16.1-alpha

The installed Spanish disc 1 completed 8,751 strict fields from cold boot using `tests/opening.movie`. At 2560 x 1440, 35 captures every five fields from 8,580 to 8,750 show the card dissolving over the widescreen flowers, then the empty dialogue box, then the letter. None of the captures is black and all four corner samples remain nonblack. This covers the card-to-letter transition. Letter-to-Sakura, pointer motion and fields between samples remain open. Private evidence: `local/work/codex-th1/thd41-combined/card-es-fade/enhanced-1440`.
