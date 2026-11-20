# IC witness route (TW7, partial: Chapter 2 battle not finished)

Goal: a scripted input route (entries only, no state transplants) that finishes the Chapter 2 battle and reaches the Chapter 2 intermission (IC), as a witness for the IC pictures. **Not reached in this PR.** This note records what was built, what was measured and where the route stops, so the next worker does not repeat it. States, movies and pictures stay in `local/work/route` (never committed); only names, frames and SHA-256 are here.

## Tool

`tools/route_segment.py` runs one segment: load a state with its SRAM copy, replay typed inputs, save a state at `FRAMES-1` and print the disc files the CD block asked for (every `Play Disc` mapped to its ISO file, FAD = LBA + 150), the last frame hash and whether `interpreted 0` held. `--dump` writes work RAM at exit. Inputs are `FRAME BUTTONS`, each press held 8 frames (`--hold`). A run of 900 frames takes about 5 s unthrottled, so search by trial is practical.

Pad bits verified in game (movie `FRAME HEX HEX`): RIGHT `8000`, LEFT `4000`, DOWN `2000`, UP `1000`, A `0400`; B `0100` as used by the T30 movies. Keep presses 30 frames apart, as the T30 segments do.

## Start point and executable

- Start state: `local/work/t30-chapter2-followup/maria-elimination/finish.state`, SHA-256 `f1084a893b337712195d700b110855138e6f20b00104bd108742c7100302ca01`; SRAM from the same folder, SHA-256 `4c22bf1edd1437b082ccd05e12df5bbf46bdcc5c9058fa3cc869db281f043908`; English disc 1 (`local/prepared/disc1/game.cue`).
- Executable `local/build/sakura-route/sakura-route.exe` (copy of `sakura-witness.exe`, the 2026-11-19 `sakura-ic-base` build, SHA-256 `f2fcb44a037b1427cf9fc18f927747f826809461312b2a16e276d4cce93684a4`) and `sakura-674182.exe` (the build that made the state) both load this state and, replaying 300 empty frames, end on the same frame hash `300 2d2272f09f31ac0d` with `interpreted 0 (0.00%)`. States saved by the two builds differ in bytes, so keep one build per chain.
- Reproduce the facts below: `python tools/route_segment.py --exe E --disc 1 --root D:/01Claude/TaisenFirst/workspace --state S --backup B --inputs "8 A,40 RIGHT,70 RIGHT,100 UP,130 UP,160 UP,190 UP,230 A" --frames 900 --out OUT --dump` (movie SHA-256 `01111ca1d7b3d781d20e92ab4ae59db4aeeb331279d5a36a1495be14ebf8af7d` for the 600-frame variant).

## What the state is (measured)

The state is the start of allied round 3: Maria's order menu (Move, Def, Info, End; no Atk because nothing is in range). Info -> Map (`8 RIGHT, 38 RIGHT, 68 DOWN, 98 A`) shows the whole field: our five units in the south-east, a tower in the north-west and about a dozen enemy markers on the terraces between.

Work RAM at `06057410`, stride `0x60`, 16-bit big-endian `hp` at `+0x08` and `max` at `+0x0A`:

| index | what | HP at the start state |
|---|---|---|
| 0-4 | allies | 96, 120, 120, 71 (Maria), 120 / 120 each |
| 5-8, 10-13 | eight cannons (green) | 80 each |
| 9 | Musket #7, already destroyed | 0 |
| 14-17 | four units with 150 HP (orange markers on the map) | 150 each |

So the battle has **12 live enemies**; no end condition was found yet (kill-all or boss). After the eight cannons and the four 150-HP units, a victory scene would follow, as in Chapter 1. Enemy HP is the objective measure of progress: after each trial read `hp[5:18]` from `--dump` (`ram-high.bin`, offset `0x57410 + 0x60*i + 8`).

## Controls learned

- The map cursor is a screen **pointer**, not a cell cursor: one press moves it 40 px horizontally (LEFT/RIGHT) or 20 px vertically (UP/DOWN) and the camera follows it. A on a blue move tile moves the unit; A elsewhere does nothing. The pointer is therefore not blocked by the move range and can leave it.
- `8 A` (Move), then `RIGHT x2, UP x4, A` walks Maria to the north-east edge of her range (animation about 400 frames); afterwards the field is free and A on another unit selects it (Sakura said "Here" and her menu `Move Atk Def Info End` opened). Maria's turn ended with the move; no Atk menu was seen after the move (the menu was not captured open; the cannon may be out of range or the menu was skipped), so this is unresolved.
- A brute-force search of every 0 to 3 press direction sequence for Maria (85 trials of about 1,500 frames, then `RIGHT, A, A, A` for Atk) changed no HP in any trial: three pointer steps from her own tile are not enough to bring a cannon into range. A bigger search needs pointer targets chosen from the blue tiles, not blind presses.
- The nearest cannon is on the terrace about four to five tiles north of Maria's start (seen in screenshots; not measured).

## Not done and why

- No IC: the battle is not finished (12 enemies, each cannon needs two Maria or Kohran hits and the enemy phase fires back), and no `IC####` file was requested in any run (`disc_files` shows only `/SAKURA2/SLG1ADP.DAT`, the battle audio).
- Because there is no IC witness, **no palette fingerprint of layer 4 and no RGB hash were measured**, and the comparison with the ICLOGO derivation of PR #431 (`config/hd-ic-table.json`, `logo_palette_fnv E9107F892185CCC8`) is **not made**. No row was changed to `hd`.
- Not verified: the pad bit for B in the new build, the effect of the Restart/Options menu (START opens it; do not press A there), and whether the other builds in `local/build` replay this state.

## Next steps

1. Drive each allied unit with a pointer-based move (choose the blue tile from a screenshot, then `RIGHT/LEFT/UP/DOWN` counts of 40/20 px), then `RIGHT, A, A, A` for Atk when the menu shows it; finish the unit with the `End` item (`Move Atk Def Info End`: End is four RIGHT presses with Atk, three without).
2. Evaluate every segment by `hp[5:18]` and chain `finish.state` into the next segment (`--state`), keeping the movies so the whole route composes with `tools/stitch_battle_replay.py`.
3. On the first `IC####` in `disc_files`, save the state and movie, check with `python tools/coverage_campaign.py --exe E --state STATE --seeds 1 --frames 600 --out OUT` that the plate is drawn on screen (not preloaded), then measure the layer-4 palette fingerprint and the RGB hash against `config/hd-ic-table.json`.
