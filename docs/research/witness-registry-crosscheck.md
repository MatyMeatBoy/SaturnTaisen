# Witness routes against the coverage register (TW7-confirm-bg)

Cross-check of the scenes loaded in the witness sweeps (PR #441, `docs/research/witness-routes.md`, `tools/witness_sweep.py`; states in `local/work/witness/`, never committed) against `config/hd-chapter-coverage.json` at `origin/main` 153b0c9.

## Result: no row can move to `hd` from these sweeps

Rows `wired-unverified` or `paired-not-wired` in the `scene-pictures` group: none inside chapters 1-10 (chapter scene-pictures are only `hd` 71, `excluded` 17, `unpaired` 4, `unsupported-size` 2). The `unassigned` group holds 19 `wired-unverified` and 23 `paired-not-wired`:

- `IC02..IC1006` (disc 1 wired by patch 0185, disc 2 paired-not-wired), `AI/GE/KA/KO/MA/SA/SU_CG`, `EVE105`: **no IC, ENDING, CG or EVE file was loaded in any sweep** (witness-routes.md, point 4). No coincidence.
- `BG2290` (`wired-unverified`): listed as a target in witness-routes.md and **not reached** in any sweep. No coincidence.

Every BG/BBG/MAP name the sweeps did reach is already `hd`, `excluded`, `unsupported-size` or `unpaired` in the register (for example BBG204 and MAP06 `hd`, BG2093 `unsupported-size` with its own dream witness [bg2093-dream-transition](bg2093-dream-transition.md), BG4055 `unpaired`, BG3132/3133/4059/4187 `excluded`). They are not rows in the requested states, so nothing was promoted and no captures were taken (the A/B hash check and 1440p captures apply only to a promotion candidate).

## Not verified / what is missing

- IC, CG, EVE105 and BG2290 need a scripted route (finish a battle or reach an intermission); the random `--auto` sweep does not. Owner of that route: the TW7 IC-route work (branches `pendientes/TW7-ic-route`, `pendientes/TW7-ch2-victory`).
- No emulator run was made in this PR; the register is unchanged.
