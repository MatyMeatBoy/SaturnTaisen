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

## Attempt 2 (TW7 ch2-victory): playing the battle in a screenshot loop

Result: **2 of 12 enemies destroyed, no victory, no IC####**. The run ended in a Game Over (Sakura died in the enemy phase). All chains used the same build (`sakura-route.exe`), `--hold 8`, unthrottled, `interpreted 0` held in every segment. About 95 segments of 60-3000 frames were run; states, shots and movies stay in `local/work/route2` (not committed).

### Turn model (new, measured)

- Allied phase is **sequential by unit**: the active unit's order menu opens by itself; units go Kohran, Maria, Sakura, Ogami, Sumire in the order the menu appears (not chosen by the pointer). Pressing A on an inactive unit only shows its range (blue), A on a blue tile then ends in a yellow attack-range view without moving: do not use it.
- Active unit menu: `Move Atk Def Info End [Spcl]`. From the cursor at `Move`: End = 4 RIGHT, then A. After a move the cursor starts on `Atk` and End = 3 RIGHT. After an attack the menu is `Move Def Info End` and End = 3 RIGHT. After End the camera pans to the next unit and its menu appears about 250-400 frames later; pressing too early selects the wrong item.
- Move: menu `Move` (A), blue range, pointer to a blue tile (verify in a picture that the diamond is on a blue tile: A on a non-blue tile silently enters the yellow view), A, animation about 500-650 frames, then A opens the menu again.
- Atk: `RIGHT, A` (opens Special/Normal, Normal preselected), `A` (yellow range, pointer jumps to the first enemy in range, portrait of the enemy shown), `A` (pink target area), `A` (confirm). If nothing is in range the pointer does not jump and A does nothing. About 500-800 frames of animation. Damage seen: Kohran 74, Ogami 60 and 65, Sumire 20 on 80-HP cannons ("Foot Soldier" portrait).
- B in the menu after a move **undoes the move** (the unit returns to its start tile) and B again leaves the menu with the pointer free; the unit then shows only range on A. Use B only to cancel, never to leave a menu you want to keep.
- The enemies walk to the allies in their phase (the four 150-HP orange units reached the group in about 2,500 frames, a Musket and cannons fire at range) and the allies counter. The enemy phase takes about 2,000-3,000 frames.
- **Losing Sakura (unit 0) ends the game** (Return to Title / Restart screen). She entered round 5 with 26 of 120 HP and died in the enemy phase. Any next attempt must keep her out of reach (or use `Def > Heal`) first.

### RAM facts (06057410 table, big endian 16-bit)

- Unit record stride 0x60: HP at +0x08, max +0x0A, screen pixel x at +0x4c and y at +0x50, flag byte +0x39 (0x08 = already moved/acted). The table is **compacted** when a unit dies (after the first two kills the live enemies are indices 5-14, not 5-8 and 10-17).
- Map pointer (work RAM high offset 0x1f84): tile x (+1 per RIGHT), tile y at 0x1f86 (steps of 2 per DOWN/UP), pixel x at 0x1f88 (step 0x30) and pixel y at 0x1f8a (step 0x18, terrace dependent). A unit is under the pointer when the pixel pair equals the unit's (+0x4c,+0x50). Used to aim the pointer instead of guessing.

### Progress log

| segment | inputs (frame action) | frames | result |
|---|---|---|---|
| r4 | `8 A,40 RIGHT,70 RIGHT,100 UP,130 UP,160 UP,190 UP,230 A,700 A` from `finish.state` | 900 | Maria moved NE, Sakura menu opens at 700 |
| r6 | Sakura: `8 A,40 UP x5 (30 apart),200 A` | 800 | Sakura moved 2 tiles north |
| r33, r36, r41 | End Sakura (`50..110 RIGHT x3,140 A`), Ogami move `LEFT x3,UP x3,A`, Sumire move + End | about 2,000 | allied round 3 finished, no attack possible |
| r43-r46 | empty, enemy phase | 2,700 | Sakura 96 to 46, Maria 71 to 71, enemies close in; round 4 starts at Kohran |
| r51-r55 | Kohran move + Atk | 1,500 | cannon index 7: 80 to 6 (first hit) |
| r64 | Sakura Atk on adjacent cannon | 800 | cannon index 7 destroyed (HP 0) |
| r68, r71 | Ogami Atk then Sumire move+Atk | 1,600 | cannon index 6 destroyed |
| r72 | End Sumire, enemy phase | 1,800 | round 5 starts at Kohran; HP 26, 99, 120, 71, 120; 10 enemies alive; **state to resume** |
| r82 | Ogami Atk on cannon (HP 80 to 15), Sumire moved but could not reach | 1,500 | one cannon at 15 HP |
| r92, r93 | End Sumire, enemy phase | 3,000 | **Game Over**: Sakura dead |

States (SHA-256, local only): round 5 start `d45ce69122628ec786db71b55cd5b6ade505d477ef04e9742643ab9c1e1fa4cd` (`local/work/route2/r72/finish.state`); end of round 5, just before the enemy phase that killed Sakura `f16791b6148e8eef434910726ef521b1502b4289f6d9b670c23c44293e8e3879` (`r92`). Resume from r72 with Sakura protected; the pad inputs of every segment are in `local/work/route2/rNN/input.movie`.

### Not done / next steps

1. Same as before: no IC####, so the coverage check, the layer-4 palette fingerprint and the RGB hash against PR #431 (`config/hd-ic-table.json`) remain unmeasured; no row changed to `hd`.
2. Resume from the round-5 state. Keep Sakura (26 HP) out of range (move her east toward Maria and `Def > Heal`), use the pointer RAM above to aim, and attack with Kohran, Ogami and Sumire every round (about 70 HP per hit, 8 cannons need 2 hits each, the four 150-HP units 2 to 3). Expect about 6 more allied rounds, each about 6,000 frames and 15-20 segments by hand; a scripted driver that reads the unit table and the pointer and writes the next movie would remove the picture reading.
3. Pad inputs shorter than 8 frames drop pointer moves; keep presses 30 or more frames apart.
