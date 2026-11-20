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

## Published runtime cross-check

On v0.2.20-alpha, a retained disc 2 MAP14 turn-nine save reached 90 strict
fields with matching donor and control guest hashes and final SRAM, and zero
interpreted blocks. At 2560x1440 the two samples changed 1,854,972 and
1,854,792 centre pixels respectively, with zero changes outside the centre.
The probe creates a separate trial directory for each invocation so earlier
captures and shared assets are preserved.
