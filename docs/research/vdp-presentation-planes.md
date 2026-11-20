# T117: lazy presentation planes (measured, not shipped)

Tried on top of the T116 line reuse (patch 0144): `BeginFrame` cleared only the rows of the sparse planes (panelMix, underPanelMix,
floralCoverMix, glyphPlate, mapFadeEdges) that the previous frame wrote, instead of `assign` of about 6 MB, with a row-dirty flag set
in `ComposeLine`/replay. Switch `SATRECOMP_LAZY_PLANES=0` restored the old path in the same executable.

Proof of equality: per-frame guest hashes and a per-frame FNV hash of every presentation plane (a temporary `SATRECOMP_PLANE_HASH`
aid) identical with the switch on and off in office, night, resume, attack, intermission, chapter1-continuous and options
(1,200 frames each, 0 interpreted).

Timing, same executable, interleaved, median of 3, `video (vdp phases)` ms/frame (switch off -> on): office 3.814 -> 3.865, resume
4.524 -> 4.626, attack 8.023 -> 8.177, night 2.223 -> 2.011. Differences are inside run-to-run noise, so there is no verified gain
(the 6 MB clear is mostly cheap memset on already-cached rows). The patch was therefore dropped.

Not done: (b) struct-of-arrays pixel loop, (c) caching `SampleNormalPresentation` columns in tactical scenes (needs an exact
key: map signature, scroll, sprite layer and window state); both remain open for anyone with the tactical scenarios.
