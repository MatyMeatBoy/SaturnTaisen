# Jumping to a chapter or scene for testing

Test tool only. The game is played naturally: save states, load states and the reset point never reach players (`release.marker`, patch 0097; see `docs/SHARDS.md`). A future "save anywhere like a modern visual novel" feature is a separate design that may reuse the state machinery; none of this is it.

## What works today

1. **Continue from a copied backup RAM (chapters 3 to 10).** The game's own Continue loads a save file. A 32 KB backup RAM copy that holds a save of the chapter, the input movie `tests/cold-load.movie` (Continue, file 1, confirm Load) and, for file 2 or 3, one or two steps down, puts the game at the start of that chapter without playing: `python tools/chapter_jump.py <case> --exe <your runtime> --frames 12000 --state-at 9000 --state-at 11999`. The sweep of 2026-11-19 (`docs/research/chapter-sweep.md`) did this for 17 saves and every route ran 12,000 frames with zero interpreted blocks (episode 4 locks at frame 6,678 on `/SAKURA2/EVT06.BIN` under AOT, an open item there).
2. **A saved state at any frame** (`--state-save FRAME:path`) of that run, loaded later with `--state-load 0:path` by any windowed run, so the HD presentation can be looked at: `tools/coverage_campaign.py --state <state>`.
3. **Random exploration** from any state with `--auto SEED:FROM` (what the campaign tool runs, many seeds in parallel) to reach scenes nobody scripted.

## Seeds (local only, never committed)

`local/work/later-chapter-audit/chapter-sweep/seeds.json` lists the cases: `bank-3-battle-1` ... `bank-10-final-battle` (14 public "Battle Saves", one per battle of chapters 3 to 10, file 1, disc 1 for chapters 3-7 and disc 2 for 8-10) and `public-7`, `public-9`, `public-finale` (public ending saves, files 2 and 3). The `.bin` files are in `seeds/`, built by `run.py setup` from the public saves archive in `local/research/noahsteam-repo`. Chapters 1 and 2 have no battle-save seed: chapter 1 starts from `local/work/intro-enhanced/title-final.state` plus `tests/chapter1-title-new-game.movie`; chapter 2 from the `beetle-ep2*` runs in `local/work/later-chapter-audit`. A seed is a game save of the owner's collection: keep it local.

## Not done / ideas (each would be a shard row)

- **Script jump by writing the guest's event cursor** (the BE32 cursor in High WRAM `060685B4` that walks `0100.BIN`, see `first-film-script-phase.md`) or the episode and file variables to land in a chosen scene of any chapter, including chapters 1-2. Unverified: the script files are loaded per episode family (`0301`, `0501`, ... `1004`), so a jump needs the matching `BIN/TBL/FCE` family resident first.
- **A scene index to state table**: for each dialogue table record (`scene-index.json`) a saved state that shows it, built by `--advance` runs and `--state-at` captures, so a worker can open any scene directly.
- **Battles**: the battle-save seeds start at the tactical map, so battle scenes (the `BBG` backgrounds) are reachable by letting the battle play (`--auto`).

## Caveats

Run from your own copy of the executable (the shared `sakura.exe` is locked by long runs). The runtime used for a jump must be a development build; a package refuses `--state-save/--state-load`. Hashes of a jump are comparable between builds only with the same seed, movie and flags (`report.json` records them).
