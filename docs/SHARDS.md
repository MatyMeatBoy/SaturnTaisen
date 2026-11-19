# Shards: what is left for the HD mod, split so other bots can send PRs

Each shard is independent, has its own files and its own "done" test. Rules for every shard: author MatyMeatBoy, PRs only (the coordinator reviews and merges), never commit discs, BIOS, saves, game pixels, `local/` or original PC assets (names, hashes, scores and code are fine), do not move the approved Zoom framing, guest hashes must stay identical (`interpreted 0`, same per-frame hashes as `main`), update `docs/PENDIENTES.md` with what is implemented, tested and packaged. Read `docs/HANDOFF.md` and `docs/research/hd-completion-handoff.md` first. Runtime code lives in the satrecomp dependency as a numbered patch in `patches/` (see `tools/build_runtime.py`); do not run it while someone else has unrecorded dependency changes.

"Needs assets" means the shard cannot be finished without the owner's own Saturn discs and PC edition; a bot without them can still do the **code and tests** half (use the synthetic tests) and leave the data half to the owner.

## Priority: finish HD mode first (owner, 2026-11-19)

Bots take shards in this order; anything that does not move HD mode toward done waits. Conflicts in shared files (`docs/PENDIENTES.md`, `docs/research/bg-matching-progress.md`, `config/hd-scene-bg-review.json`): rebase on `origin/main` and keep both sides (lists and keys are unions); the coordinator does the same when integrating.

1. **Runtime, visible in game:** S3 clip hook (T100), S4 clip audio (T101), S5 HUD and menus (T102), S8 scrolling/battle backgrounds (T105), S9 faces and body fade-in (T106), S10 Spanish cards (T107).
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
| S10 Spanish cards | T107 | yes | `tools/es/portadas_es.py`, the Spanish layer | The 16:9 widening recognises the Spanish cards (their palette fingerprints) and painted art replaces the program drafts (the owner reviews T87) |

Order for the fastest visible gain: S1, S2 (independent, small), then S3 and S4, then S5 and S8. S6 and S7 are performance and can run in parallel with anything else.

Each PR should say which shard it closes, the commands run and their results, and what is still not verified.
