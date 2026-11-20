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
