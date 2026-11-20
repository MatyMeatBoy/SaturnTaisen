# THD23: episode cards and initial scroll, witness table

Runtime: development build of main at 0684db8 (patch stack through 0245), strict native, hidden window, own copy `local/build/sakura-thd23/sakura.exe`. Enhanced and Original at 2560x1440 (integer scale 6, center box 320,48 to 2240,1392), Enhanced Zoom, profile with `art/screen-backgrounds` from `assets/generated`. English prepared disc 1 only. Evidence is private under `local/work/thd23`.

| Ep | Surround in package | Drawn in Enhanced | 1440p witness (EN) | 1440p witness (ES) |
| --- | --- | --- | --- | --- |
| 1 | yes (`EPISODE01-surround-v2`, `-es-lettering-v1`) | yes | **yes** (`title-final.state` + `tests/chapter1-title-new-game.movie`) | yes (v0.2.16.1-alpha cold replay below) |
| 2 | yes | not seen | falta (no run reaches TITLE2) | falta |
| 3 | yes | not seen | falta: Continue run of 12,000 frames ends in dialogue, no TITLE3 | falta |
| 4 | yes | not seen | falta (run stops at EVT06 without the overlay build) | falta |
| 5, 6 | yes | not seen | falta | falta |
| 7 | yes | not seen | falta: the black "Episode 7" text at frame 10,500 is a FILM title, not TITLE7 | falta |
| 8, 9, 10 | yes | not seen | falta | falta |

All ten surrounds and Spanish lettering layers are in `assets/generated/screen-backgrounds` and the package gate. PC TITLE donors stay excluded (TP3a).

## Episode 1, English, 6,701 frames

- Guest hashes Original vs Enhanced: all 6,701 identical, `interpreted 0` in both.
- Card fades in about frame 6140, steady 6180 to 6580, fades out 6620 to 6700 into the floral background and the letter.
- Steady frame 6300: center box pixel-identical to Original; only a 3 px host outline around the card differs. Original shows the host frame on a flat pink field; Enhanced shows the generated surround to the screen edges.
- Fade frames 6140, 6620 and 6660: center differs from Original, as expected (Enhanced blends the card over the floral plane).
- Not verified: Spanish, CARGANDO/LOADING scroll in both languages, 1080p, Original at 1080p.

## Not witnessed here (needs a worker with a route)

Episodes 2 to 10 need a state or movie that reaches TITLEn; Continue-from-save routes in `chapter-sweep` do not (they land in dialogue). A Spanish disc (`tools/es/construir_todo.py --disc 1`) is not prepared on this machine.

## Episode 1, Spanish, v0.2.16.1-alpha

The installed Spanish disc 1 and packaged runtime completed 10,500 cold strict fields using `tests/opening.movie`. Enhanced 2560 x 1440 and 1920 x 1080 have identical guest hashes. The Spanish card appears at 8,250 and 8,500, following the floral backdrop at 8,000 and before the letter transition at 8,750. The center-to-surround join is still visible, and the packaged lettering differs from the requested serif reference. These captures establish the current behavior. A per-frame fade comparison, Original and episodes 2-10 remain open. Private captures are under `local/work/codex-th1/thd41-combined/card-es-cold`.

## Spanish profiles prepared from either disc

The setup helper now prepares localized Enhanced centers from each
available English and Spanish disc pair. Their names use the Spanish
TITLE fingerprint, so a disc 2 installation can populate all ten
centers independently. A pair with English TITLE bytes in the Spanish
image reports a preparation error for that disc and does not stop the
other pair from being processed.

The corrected Spanish disc 2 media and the Spanish disc 1 media
independently generated the same ten keyed centers with the release
art. An older retained Spanish disc 2 image contains all ten English
TITLE files. It still needs its Spanish media layer refreshed.
The helper and the installed-media migration shipped in v0.2.25-alpha.
In v0.2.26-alpha the launcher also restores missing generated centers.

## Published Spanish Episode 1 at 1440p

An A/B of v0.2.26-alpha used the same Spanish opening with and without
the installed center. During sampled fade-in fields 8160, 8180 and 8200,
the center contribution increased. The corresponding fade-out fields
8580, 8600 and 8620 show it decreasing. In the sampled steady interval,
fields 8220–8560, all 2,580,480 center pixels matched the installed PNG
at integer 6× scaling. The center occupies (320,48)–(2240,1392).
All changes between these two profiles were confined to that rectangle.
The widescreen surround was unchanged by the presence of the center.
No black pixels appeared in the exterior strips in the sampled fade and
steady fields. In Original, 26 full-window captures matched exactly with
and without the installed center. All 8,810 guest hashes and the final
save memory matched across the four cold runs, with zero interpreted
blocks. The report lives in the private v0.2.26 card verification folder.
