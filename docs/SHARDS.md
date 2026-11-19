# Shards: what is left for the HD mod, split so other bots can send PRs

Each shard is independent, has its own files and its own "done" test. Rules for every shard: author MatyMeatBoy, PRs only (the coordinator reviews and merges), never commit discs, BIOS, saves, game pixels, `local/` or original PC assets (names, hashes, scores and code are fine), do not move the approved Zoom framing, guest hashes must stay identical (`interpreted 0`, same per-frame hashes as `main`), update `docs/PENDIENTES.md` with what is implemented, tested and packaged. Read `docs/HANDOFF.md` and `docs/research/hd-completion-handoff.md` first. Runtime code lives in the satrecomp dependency as a numbered patch in `patches/` (see `tools/build_runtime.py`); do not run it while someone else has unrecorded dependency changes.

"Needs assets" means the shard cannot be finished without the owner's own Saturn discs and PC edition; a bot without them can still do the **code and tests** half (use the synthetic tests) and leave the data half to the owner.

## Priority: finish HD mode first (owner, 2026-11-19)

Bots take shards in this order; anything that does not move HD mode toward done waits. Conflicts in shared files (`docs/PENDIENTES.md`, `docs/research/bg-matching-progress.md`, `config/hd-scene-bg-review.json`): rebase on `origin/main` and keep both sides (lists and keys are unions); the coordinator does the same when integrating.

1. **Runtime, visible in game:** S3 clip hook (T100), S4 clip audio (T101), S5 HUD and menus (T102), S8 scrolling/battle backgrounds (T105), S9 faces and body fade-in (T106).
2. **Data that feeds the runtime:** the background review shards (T76-T711), item and body maps.
3. **Performance:** S6 VDP (T103), S7 SH-2 (T104), only after a visible item is blocked on someone else.
4. **Owner-only:** painted art (T87).

| Shard | Queue | Needs assets | Files it owns | Done when |
|---|---|---|---|---|
| S1 clip map | T98 | no | `tools/gen_film_fad_map.py`, `config/film-fad-map.json`, a test | For every `/SAKURA4` stream of both discs, `FAD = 150 + 255 + offset/2048` (disc 2 has its own archive LBA) is paired with its `MOVIEnnn` using the 44+6 pairing in `docs/research/video-equivalence.md`; unit test checks the formula against the verified start FAD `0x2EC7` = disc 1 stream 1 |
| S2 MPEG decode | T99 | no (use any MPEG-1 file) | `port/movie_decoder.h` in a new patch | A class wrapping `pl_mpeg` (header at `local/deps/pl_mpeg`, MIT; add it with its licence to `THIRD_PARTY_NOTICES.md`) decodes video on a worker thread into a double-buffered RGBA frame and exposes MP2 audio; test decodes a generated clip. Measured: `pl_mpeg` decodes the PC clips (576x288, 24 or 30 fps, MP2 44.1 kHz) correctly |
| S3 clip hook | T100 | yes | patch in `port/frontend_sdl.cpp` | The CD model reports the start FAD of a `10xx` play command; in HD mode the PC clip replaces the Saturn picture in the 16:9 presentation, the Saturn clip clock drives the PC frame, skip and end follow the guest; guest hashes identical |
| S4 clip audio | T101 | yes | audio mixing in the runtime | PC audio replaces the Saturn audio only for the 44 pairs whose duration matches (±0.5 s); the six alternate cuts keep the Saturn audio; mute and volume respected |
| S5 HUD/menus | T102 | yes | `tools/match_hd_items.py`, `config/hd-item-map.json`, a recogniser | The menus and HUD that have a PC equivalent (T23/T54 inventory) are recognised by hash and drawn from the PC art without distorting proportions; unknown menus fall back to native |
| S6 VDP speed | T103 | no | `video/*` of the dependency, a patch, an equivalence test | VDP software drawing (about 7 ms per frame) is faster with **pixel-identical** output (test compares frames before and after over the saved scenes); report the new ms per frame with `SATRECOMP_FRAME_PROFILE_SLOW` |
| S7 SH-2 speed | T104 | no | block dispatch in the dependency | SH-2 time (about 6.5 ms per frame) lower with identical guest state hashes |
| S8 scroll and battle backgrounds | T105 | yes | `tools/decode_saturn_bg.py`, `gen_scene_bg_table.py`, recognisers | The BBG/EVE and scrolling pictures are decoded, paired with the PC pictures and recognised at runtime like the 459 scene pictures; variant-B wide pictures handled |
| S9 faces | T106 | yes | body/face tables | `NC30` and `NC20` get native-face patches (mouth/eye frames the matcher leaves native) and the fade-in of a body is checked |

Order for the fastest visible gain: S1, S2 (independent, small), then S3 and S4, then S5 and S8. S6 and S7 are performance and can run in parallel with anything else.

Each PR should say which shard it closes, the commands run and their results, and what is still not verified.

## HD by chapter (added 2026-11-19)

The remaining HD work is split by chapter so several bots can work at once without touching the same files. Every chapter shard has the same scope and the same exit test; take one, say so in the queue row, and keep PRs small.

**H0 (TH0), do first, anyone:** `tools/hd_chapter_coverage.py` + `config/hd-chapter-coverage.json`: for each of the 10 chapters list the resources the chapter shows (scene pictures BG/EVE/CG, NC bodies, portraits, FILM clips, tactical maps and units, menus/HUD) from the scene index and the existing `config/hd-*-map.json`, marking each as `hd`, `paired-not-wired`, `unpaired` or `unknown`. Also refresh `docs/HD_PROGRESS.md` and `config/hd-progress.json`, whose counts are stale (it still reports 0 integrated scene pictures; 459 are wired and the bodies and clips are in).

**H1-H10 (TH1-TH10), one per chapter** (chapters 1-5 on disc 1, 6-10 on disc 2; take the numbering from the scene index). Scope of each: (a) every scene picture the chapter shows has an HD pair or a recorded reason it has none; (b) every NC body and portrait the chapter uses is matched and, where the matcher leaves a face native, listed with its frame layout (follow T106a-d); (c) the chapter's FILM clips are mapped (`config/film-fad-map.json`) and each alternate cut has a decision; (d) the tactical maps/units of the chapter are listed for S11. Exit test: a continuous strict-native replay of the chapter's path with the HD runtime shows per-frame guest hashes identical to the build without HD and a short report (`docs/research/hd-chapter-N.md`) with the screenshots the owner can open, what is HD, what stays native and why. Do not claim a chapter complete from a saved state alone.

**S11 tactical mode (TS11):** the 542 PC SPR candidates (UNIT, MAP, ITEM): pair, wire a recogniser, wide extension of the maps (generated art welcome; keep generated files separate from game pixels).

**S12 packaging (TS12):** the release package gate for everything generated or paired (cards sides, clips, art folders) and a clean-machine run of `preparar-juego.exe` with a PC edition that has MOVIE.

Rows TH0-TH10, TS11 and TS12 in `docs/PENDIENTES.md` mirror this list; update the row of the shard you take.

## Rules for many workers at once (read before opening a PR)

1. **Take one row**, write your name and branch in its `Status` cell in a first small PR, then work. Do not take a row another worker already marked.
2. **Branch from the latest `origin/main`**, one shard per branch, `pendientes/<row>-<topic>`. Rebase on `origin/main` again right before the PR.
3. **Shared files conflict**: `docs/PENDIENTES.md`, `docs/research/bg-matching-progress.md`, `config/hd-scene-bg-review.json`, `config/dependencies.json`. For the docs and the JSON, keep both sides (lists and keys are unions); never delete another worker's row or entry. Keep your own text in rows you own only.
4. **SDK patches**: take the next free number after the highest in `config/dependencies.json` at the moment of the PR, list it last, and run `python tools/check_patch_stack.py` (numbers unique and increasing, every file listed, the whole stack applies). If it reports a duplicate number, `git mv` your patch to the next free one and fix the list. Never edit an earlier patch: add a new one.
5. **Row IDs**: a new row takes the next free `T` number only after you grep `docs/PENDIENTES.md` for it; sub-rows use a letter suffix of your parent row (`T105a`).
6. **Never commit** discs, BIOS, saves, original PC assets, game pixels, `local/`, or untranslated Japanese script text. Generated art goes under `assets/generated/` with `provenance.json`.
7. **A PR says**: which row it closes or advances, the commands run with their output, and what is still not verified. Mark "implemented", "tested" and "in a package" separately. A saved state or a screenshot does not complete a chapter.
8. **Runtime changes** must keep the guest per-frame hashes identical to the previous build (strict native replay, `interpreted 0`); say which replay.
9. **Run from your own copy of the executable.** Several workers share this machine and a running `sakura.exe` locks the file, so the linker fails with `Permission denied` for everybody (seen 2026-11-19). Copy the build to `local/build/sakura-<your-name>/sakura.exe` and run your replays from there; never kill another worker's process; build when no process holds the shared path. **One dev runtime at a time** builds in `local/build/sakura`: workers without a compiler or the discs do the code, tests and data halves and say so; do not run `build_runtime.py` while another worker has unrecorded dependency edits.

## How to read the coverage numbers (read before picking work from them)

`config/hd-chapter-coverage.json` and `docs/HD_PROGRESS.md` count catalog entries, not pictures a player sees, and the two discs share many files, so a count is up to twice the real number. Statuses (regenerated 2026-11-19 after a miscount: the first version called every accepted pair that is not a documented draw "paired-not-wired", which made 246 bodies and 474 pictures look like unfinished wiring when 129 bodies and 459 pictures were already in the runtime tables):

- `hd`: the runtime draws it (a documented draw for a body, a table entry for a picture or clip).
- `wired-unverified`: in the runtime table and tried whenever it appears, but nobody has recorded seeing it in game. The work is **verification**, not wiring.
- `excluded`: paired but never replaced by design (character cut-outs on a key colour, the blank picture). Do not wire it.
- `unsupported-size`: accepted pair whose size the runtime cannot draw yet (not 288x144). The work is runtime scroll/size support (T105c), not pairing.
- `paired-not-wired`: genuinely missing from the runtime. Read its `reason` first. Today: 128 BG entries (64 per disc) share a palette with a picture that maps to another PC file, so the palette fingerprint cannot identify them (they need a second key, for example a hash of the layer's tile data); 32 IC and 12 EVE pictures wait for their recogniser (T96); alternate film cuts stay native on purpose.
- `unpaired`: rejected or without a counterpart. `unknown`: not established.

Rules for a worker: never turn a `paired-not-wired` count into a to-do list without reading the `reason`; do not re-review pictures or bodies the review files already decide (`config/hd-scene-bg-review.json`, `config/hd-body-review.json`: 15 NC bodies and 45 pictures are rejected, 118 are cut-outs); a number that disagrees with the runtime tables is a bug in the generator (`tools/hd_chapter_coverage.py`), fix it there and regenerate with the command in `docs/research/hd-chapter-coverage.md`.

## A shard PR must arrive connected (owner rule, 2026-11-19)

A pairing, a review or a report is not a finished shard. The PR that closes a shard row contains the whole chain, so the coordinator only has to review it:

1. **The data** (map/review JSON, generated table input, names and hashes only).
2. **The connection**: the generated table or header regenerated by the tool, the SDK patch (next free number, `tools/check_patch_stack.py` passes) and the recogniser change that makes the runtime use it. If the runtime cannot be built where you work, say so in the PR and deliver the code, the regenerated tables and the tests; the coordinator builds and checks it.
3. **The proof**: the unit tests, and for runtime changes the per-frame guest hash comparison with the previous build (`interpreted 0`), plus a screenshot or a trace line showing the item drawn in game (a saved state is enough for `wired-unverified`, never for "chapter done").
4. **The bookkeeping**: the queue row and `docs/HD_PROGRESS.md`/`config/hd-chapter-coverage.json` regenerated with the documented command, so the status moves from `paired-not-wired` or `wired-unverified` to `hd` only with evidence.
5. **If something blocks the connection**, the PR says what (a missing runtime feature, the owner's discs, an ambiguous key) and opens or links the row that unblocks it; it does not close the shard.

Reviews and pairings that are still waiting on a human eye are the only exception: they may ship as data-only PRs, marked as such in the title.

## How a pairing becomes a drawn picture (follow the chain, send it whole)

| Class | Data (names, hashes) | Generator | Runtime table in the SDK | Runtime code (`port/frontend_sdl.cpp`) | Proof |
| --- | --- | --- | --- | --- | --- |
| Scene pictures 288x144 | `config/hd-scene-bg-map.json` + `hd-scene-bg-review.json` | `tools/gen_scene_bg_table.py` | `port/scene_bg_table.h`, key = palette fingerprint of the picture layer | T74 draw: PC picture under the native overlays | `tests/test_saturn_bg_decode.py`, replay hashes, screenshot |
| Large bodies NC | `hd-body-map.json` + `hd-body-review.json`, `hd-nc30/nc20-face-map.json` | `tools/gen_body_table.py` (needs the disc image) | `port/body_table.h`, key = hash of the VDP1 texture | body + face draw (matcher by layout, shape, lip colour) | `SATRECOMP_BODY_TRACE`, HD/native pairs |
| FILM clips | `film-fad-map.json`, `clip-audio-map.json` | `tools/gen_film_clip_table.py` | `port/film_clip_table.h`, key = (disc, start FAD range) | `UpdateClip` + `port::MovieDecoder` | `SATRECOMP_CLIP_TRACE`, opening-film replay |
| Items / menus / HUD | `hd-item-map.json`, `hd-item-review.json`, `hd-system-hud-review.json` | `tools/gen_item_table.py` | `port/item_card_table.h` | not connected yet (T109): VDP1 sprite + CRAM bank to PC picture | ITEM07 witness in `docs/research/pc-menu-hud.md` |

A table is regenerated by its generator and added to an SDK patch (`port/*.h` in `patches/00NN-*.patch`, listed last in `config/dependencies.json`); `python tools/check_patch_stack.py` must pass. The runtime change that reads it goes in the same patch.

## Where the shards stand (2026-11-19) and the open connected shards

Done and in `main`: S1 film map (T98), S2 decoder (T99), S3 video in the runtime (T100/T116, patches 0073/0078/0080), S4 clip audio (T101/T111, patches 0074/0080/0083, listening open), S6 VDP speed (T103), S7 SH-2 dispatch (T104), TH0 coverage register, the card work moved to Codex (TCODEX).

Open, each one a PR that arrives connected (see the rule above):

- **W1 ambiguous-palette pictures**: 128 BG entries (64 per disc) share a palette with a picture that maps to another PC file. Add a second key (for example a hash of the layer's tile data or of its VDP2 cell table) to `gen_scene_bg_table.py`, extend the runtime match, regenerate. Closes up to 64 pictures.
- **W2 IC and EVE recognisers (T96/T105b)**: 32 IC and 12 EVE pictures, decoders and pairs exist; write the runtime recogniser for the palette-first full-screen pictures.
- **W3 wide and tall pictures (T105c/T105d)**: 73 entries of another size; the variant-B decoder and the native scroll witness (BG2252) exist; add per-frame scroll offset to the T74 draw.
- **W4 NC30 and NC20 native faces (T106a/b)**: the face maps are verified offline; the runtime consumer is missing.
- **W5 HUD and menus (T102/T109/T110)**: the table generator and the ITEM07 witness exist; connect the item pictures (VDP1 sprite + CRAM bank to the PC picture) and the SYSTEM menus.
- **W6 tactical mode (TS11)**: 542 UNIT/MAP/ITEM files, nothing paired yet; pair, table, recogniser, wide maps.
- **W7 verification replays (TH1-TH10)**: 246 body entries are `wired-unverified` and most chapters have no replay; each replay needs the owner's discs and records which items drew, with hash parity. Attribute resources to chapters through `CHAPTER_WITNESSES` in `tools/hd_chapter_coverage.py`.
- **W8 video leftovers**: the six alternate cuts (decided: they keep the Saturn film, 0.4-3.7 s edit difference against the guest's clock), disc 2 clips, resume after a skip, listening to the audio (T112: MOVIE005/018/030/119 need special review), the release package.
- **WRA RetroAchievements (TRA)**: the whole feature, see its row: rcheevos client, badge popups, sync and offline queue, launcher login and log; save states are never available to players.
- **W9 packaging (TS12)**: gate and clean-machine run for everything generated or paired.

Rows W1-W9 are in `docs/PENDIENTES.md`; take one, write your name in its status, and send the PR whole.

## Claims and the 30-minute rule (owner, 2026-11-19)

Take a shard by claiming its row in a first small PR: `python tools/shard_claims.py --claim TW1 --who <name> --branch pendientes/<branch>` (it writes `CLAIM[name|branch|UTC time]` at the start of the row's status cell). A claim stays valid while its branch gets commits; **a shard nobody has worked on for 30 minutes goes back to the pool**: any worker or the coordinator runs `python tools/shard_claims.py --release-stale` (add `--dry-run` to look first) and every claim older than 30 minutes with no newer commit on its branch becomes `open · released (stale claim of <name>, <time>)`. `--list` shows the claims and their idle time. Push a commit (even a draft) to keep a claim alive; if you stop, release it yourself. A released shard may be taken by anyone, and the previous worker's branch is fair material for the next one.

## Save states are for testing only (owner rule, 2026-11-19)

The game is played naturally: save states, load states, quick states (F5/F9), the reset point (F2/F3), the slot keys (F6/F7) and their menu rows never reach players. The runtime (patch 0097, `port/dev_states.h`) switches them off whenever a `release.marker` file sits beside `sakura.exe`; `tools/package_release.py` writes that file into every package, so a package is always natural play, and development builds (no marker) keep `--state-load/--state-save` for replays. Never copy `release.marker` next to a development executable, and never ship a package without it (`tests/test_release_marker.py`). A future in-game save-anywhere feature (owner idea: like a modern visual novel) is a separate design and not these tools.

## Speed against completeness (owner, 2026-11-19)

Send PRs as early as you have a verified slice, then keep sending: the coordinator integrates everything that arrives, and a fast, small, honest PR is worth more than a late perfect one. The balance:

- **Always in the PR (never skip):** the data or code of the slice, the tests you can run, the evidence you have (hashes, a screenshot, a trace) and an explicit list of what is not verified. A runtime patch must at least apply to the current stack (`python tools/check_patch_stack.py`) and compile in your build, or say plainly that it was not compiled.
- **May come later (the coordinator completes it):** the full-chapter replay, other resolutions, packaging, a second asset, listening or eye checks that need the owner. Say which of these are pending; do not hold the PR for them.
- **Draft or ready?** Ready if the slice is verified as far as you can; a draft only for an unfinished experiment. The coordinator marks a draft ready after verifying it, so a draft is never wasted.
- **Split instead of waiting:** if a shard has an offline half (data, generator, tests) and a runtime half, send the offline half now and the runtime half as its own PR.
- **Rebase before sending** (`git merge origin/main`, then `python tools/check_patch_stack.py`; `python tools/rebase_patch.py <patch> --author-ref=origin/<branch>` re-anchors a patch whose context moved, but it can misplace a block: always compile after).


## Priority order (owner, 2026-11-19)

Scene pictures first (TP1 ambiguous, TP2a/b scroll, TP3a/b/c unknown pairings, TP4a/b/c unpaired), then large bodies (TP5), portraits (TP6), videos (TP7); verification and cleanup last (TP8). Each shard is sized for one PR; send it as soon as the picture is connected and its A/B hash check is done.

## Lessons for shard workers (from the integration desk)

- **Scene pictures (TP1-TP4):** the table has two keys. First key = palette; second key = palette + hash of the cell data. A group of Saturn pictures sharing a palette is resolved by comparing the PC candidates: identical PC images (pixel-identical although the SPR bytes differ) -> keep the lowest name; tint variants -> choose by mean absolute difference at 288x144 against the Saturn picture (see `shared_cell_choice` in `config/hd-scene-bg-review.json`, patch0118). Do not trust the 48x24 coarse signature alone.
- **IC pictures (IC02-IC1006):** they belong to the intermission between episodes. Battle saves and chapter jumps land inside a dialogue and never reach them. Needs a backup RAM saved at each chapter's intermission (or a full play to the end of an episode). Without that, do not wire blind (patch0107 depends on a witnessed frame).
- **Counting:** the register counts a picture once per disc and chapter; the single HD total (docs/HD_PROGRESS.md) counts connected items over candidates. Do not compare them.
- **Before sending a runtime patch:** `tools/check_patch_stack.py`, compile, link your own exe (the shared `sakura.exe` is locked), replay the opening film and compare `frames.hash` with the previous release. A table-only patch still needs the compile and the replay. The integration desk repeats the build, but a PR that already says what was drawn arrives faster.
- **Chapter jump:** `tools/chapter_jump.py` states at frame 11,999 are inside dialogue; pressing Start there does not open any menu. For a menu or an intermission you need a save made there.
- **Do not re-anchor patches by script without compiling:** a re-anchored hunk can land outside its scope (it broke main once).
- **When you finish:** update the row in docs/PENDIENTES.md in the same PR and say what you drew, what you compared and what you did not run.

## Speed rule: no scene-by-scene verification (owner, 2026-11-19)

Shard workers do **not** verify every picture one by one in game. For a scene picture, body, portrait or clip it is enough to: match it to its PC counterpart with the method already used and proven on the pictures that were tried in game, connect it, make sure it compiles (`tools/check_patch_stack.py`, build) and that the opening-film replay hashes are unchanged. Assume the matching is right unless a witnessed case says otherwise. Do not spend time on per-picture screenshots, 1440p A/B captures or campaign runs; the integration desk and the later cleanup phase (TP8) look at what is visible. If you do see something wrong, say so in the PR. Send the PR as soon as it is connected.

## Fast path for a picture shard

1. Take the row, claim the shard (`tools/shard_claims.py`).
2. Find the pair: palette fingerprint and cell hash from the Saturn picture against the PC set (see the lessons above); a group sharing a palette is resolved by comparing candidates.
3. Add it to `config/hd-scene-bg-map.json` / the review file, regenerate `port/scene_bg_table.h` with `tools/gen_scene_bg_table.py`, record the patch.
4. `tools/check_patch_stack.py`, compile, replay the opening film, hashes unchanged.
5. Update the register (`tools/hd_chapter_coverage.py`) and the row in the same PR; send. Do not verify in game: one picture in ten is spot-checked later (TP9).

## Working in parallel without stepping on each other

- Several agents must never share one checkout: each does its git work in its own `git worktree` or clone (an agent once committed onto another's branch in the shared tree). Respect the limit of two worktrees in AGENTS.md; reuse the auxiliary one.
- Build from a clean copy of the stack, not from the shared SDK tree (it may lag behind main). Link your own exe; never overwrite shared build outputs.
- Take the next patch number only after `git fetch` and a look at the open PRs; if another PR lands first, renumber at rebase time. Two patches that touch the same function (for example the scroll pictures) are one shard: say so in the claim.
- `tools/integrate_prs.py` with no arguments integrates every open PR in order and skips those that conflict; the PR author rebases the skipped ones.

## Chapter order (owner, 2026-11-19: finish chapter 1, then 2, and so on)

State of the register by chapter (resources with a witnessed chapter, not yet `hd`/`excluded` / attributed): chapter 1 is nearly closed (bodies 0/19, clips 0/3, scene pictures 1/32, portrait rows 8/129); chapters 2-10 have only a handful of attributed resources each (scene pictures 0 of 1-3 pending, portrait rows 3-7 pending). The rest of the material, about 1,500 scene pictures, 275 bodies and 195 menu/HUD images, is **not attributed to a chapter yet** (`unassigned`), so the shards cannot be sliced by chapter until it is.

Therefore:
1. **Attribution comes first, in chapter order.** TH2 ... TH10 (attribute the resources each chapter draws, by a traced replay from that chapter's save/jump, see `tools/chapter_jump.py` and `docs/research/hd-chapter-N.md`) are P0 and are taken in order 2, 3, 4 ... 10. Their output is rows moving from `unassigned` to the chapter in `config/hd-chapter-coverage.json` (the `CHAPTER_WITNESSES` table in `tools/hd_chapter_coverage.py`).
2. **Completion follows the chapter.** Once a chapter has attributed resources, a worker finishing the type shards (TP1-TP7) takes the items of the lowest chapter first, then the next. Chapter 1 is done when its register shows no `unknown`/`paired-not-wired` row except the documented blocked ones (`00a1`, `0169`, the IC pictures).
3. Until a chapter is attributed, the type shards (TP1-TP7) stay the way to make progress: they are chapter-independent (palette/cell matching).
