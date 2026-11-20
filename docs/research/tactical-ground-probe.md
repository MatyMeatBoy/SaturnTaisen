# Tactical ground probe (THD16)

`tools/tactical_ground_probe.py` decides whether the runtime draws the PC tactical ground. The ground is loaded with `tactical_ground::Load` from `SAKURA2/MAP/MAPnn/MAPnn_A.SPR` and prints no trace line, so `tools/scene_draw_probe.py` cannot see it. The probe runs the same state twice at 2560x1440 (donor root, and a control root made of hard links without that map's `_A.SPR`), strict native, and compares captures inside the integer-scaled 320x224 centre rectangle (320,48)-(2240,1392). It requires one guest hash per frame identical in both runs, equal final SRAM and `interpreted 0`. Verdict: drawn when at least 2% of the centre pixels differ; changes outside the centre are reported.

Executable: `local/build/sakura-tgprobe/sakura-full.exe`, private copy (with `art/`) of the PR #621 full-stack build, SHA-256 `96d48742606321825f94bf9a2b0c07ec915b091adb2c82cdf6bea0624df1b6ee`. Pass `--disc` for the disc of the state.

```powershell
python tools/tactical_ground_probe.py --exe local/build/sakura-tgprobe/sakura-full.exe `
  --state local/work/sweep/run2-bank-8-battle-2/state-6999.bin --backup local/work/sweep/run2-bank-8-battle-2/backup.bin `
  --disc local/prepared/disc2/game.cue --pc-assets local/work/pc-cab/out-tac --map MAP14 --frames 240
```

Add `--expect not-drawn` for MAP19. Tests: `python -m unittest tests.test_tactical_ground_probe`.

## Results (240 frames, 2 captures per run, all with identical guest hashes, same SRAM, interpreted 0)

| Map | State (T55 sweep) | Reached | Ground drawn |
| --- | --- | --- | --- |
| MAP14 | bank-8-battle-2 state-6999 | yes | yes, 1,859,328 of 2,580,480 centre pixels (72.1%), 0 outside |
| MAP14 | state-9999 | yes | yes, 1,785,852 (69.2%) |
| MAP14 | state-7999 | yes (partly covered) | yes, 405,108 (15.7%) |
| MAP19 | bank-10-battle-2 state-6999 | yes | no: 0 changed pixels (native by review, as expected) |
| other 15 of the 17 | no retained state loads them | not reached | n/a |

MAP14 captures were read by eye: PC ground drawn, units, centre sprites and the floral border unchanged. MAP14 was already `hd` in `main` (`tactical-pairing.md#live-map14-pc-ground`); this is a reproducible re-witness, not a promotion. The 17 `wired-unverified` rows of the generated table (PR #440, not in `main`) other than MAP14 still need a state that reaches them (MAP03, 07, 08, 09, 11, 17, 18, 20, 22, 24, 25, 26 and the rest). No register delta.

## Reach attempt (THD15): why the 12 pending maps are still not reached

No new map was reached and nothing was promoted. Facts measured (names, frames and hashes only; states and movies stay in `local/work/reach`):

1. **The probe executable cannot draw the 12 maps.** The PR #621 build (`sakura-full.exe`) contains the hand-written signatures (MAP01, 02, 04, 05, 06, 21) and MAP12 to 16, but not the generated rows of PR #440 (patch 0188 table) for MAP03, 07, 08, 09, 11, 17, 18, 20, 22, 24, 25, 26 (the 8-byte signatures of `config/hd-tactical-ground-table.json` are absent from the binary; present in `local/build/rebuild-maps/sakura.exe`, the #440 build on an older stack). Even with a saved state at one of these battles, the probe would report "not drawn" on `sakura-full.exe`. A witness needs a full stack build that includes the #440 table (rebuild after #440 merges), or the older `rebuild-maps` build if the state loads there (not tested).
2. **The chapter jumps do not stop at a battle but in interactive look-at scenes.** Continuing the 17 sweep states with a confirm every 120 frames (`tools/chapter_loads.py --state run2-CASE/state-39999.bin`, 40,000 more frames, about 5 min each, `interpreted 0`; bank-8-battle-1, 9-battle-1 and 10-battle-1 for 100,000 frames) produced no `MAP`, `BBG`, `IC` or `EVT` load. bank-5, bank-6 and bank-7 (and public-7) sit in a scene where Ogami's gaze cursor (eyes icon, or a hand icon in the bank-7 capsule scene) is shown and A on it repeats the same dialogue ("What's wrong, Ogami? You were staring at me a little...") forever. bank-3-battle-1 ends in a free-roam map of the theatre. These need real directed input, not a confirm press.
3. **The cursor is steerable.** In bank-5 (state 39999 of the sweep) moving the cursor LEFT or RIGHT with three presses 30 frames apart and then A leaves the loop (Sakura says "Ogami, where are you going!?"). A blind periodic pattern (A, A, LEFT x3, A, A, RIGHT x3, A every 480 frames) did not escape in 40,000 frames, because the cursor target changes per page. A route needs per-page decisions (read the pointer, as battle_driver does for the map pointer).
4. The T55 sweep note's lists (chapter 3 battles load MAP04/MAP05, chapter 4 MAP06/MAP21, chapter 8 battle 2 MAP14, chapter 10 battles 2/final MAP19) are unchanged; no state loads MAP03, 07, 08, 09, 11, 17, 18, 20, 22, 24, 25, 26. No battle was won; the IC after a battle is not reached (the #566 driver was not run: it needs the Chapter 2 state and loses Sakura before the victory).

Next: (a) steer the look-at scenes per page for bank-5, 6, 7 (they lead to the battle of their chapter); (b) rebuild with the #440 table before probing; (c) unchanged owner of IC route: desk.
