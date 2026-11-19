# T100/S3 clip hook: design and what exists

Status: design, lookup reference and synthetic tests only. The runtime hook is **not** implemented: this machine has no C++ compiler, and `tools/build_runtime.py` was not run (the SDK is not touched, no patch added).

## What exists (tested)
- `tools/film_clip_hook.py`: `parse_play` (CD play command words to start FAD), `load_table`, `lookup_play_command` over `config/film-fad-map.json`. The key is `(disc, start FAD)`: the same FAD exists on both discs for different films (52 mapped start FADs, 50 distinct clips, 6 alternate cuts).
- `docs/research/film-clip-table.txt`: the table sorted by FAD, regenerable with `--emit-table`.
- `tests/test_film_clip_hook.py`: synthetic tests (the opening-film command from the T53 trace gives MOVIE001; non-play, non-FAD and mid-stream starts give no match).

Limit of `parse_play`: its layout (word0 = 0x10 plus bit 7 = FAD start, FAD = (word0 & 0x7F) << 16 | word1) is inferred from two commands in the T53 trace (`1080 2EC7`, `1082 7465`) and is not confirmed against the CD block firmware or the SDK source.

## Design of the runtime hook (to do)
1. In the CD model, when a `10xx` play command with an FAD start is accepted, call `lookup_play_command(disc, words)`. A miss, or a play outside a film, does nothing (guest and presentation unchanged).
2. On a hit, open `MOVIEnnn.MPG` from the owner's PC resources with `port::MovieDecoder` (T99) and keep the Saturn clip as the clock: ask `FrameAt(t)` with t = time since the play command, as the guest's FILM time.
3. Draw the RGBA frame in the 16:9 presentation in place of the Saturn picture only while a clip is active; stop and fall back to the Saturn picture at the end of the stream, on a new play, on a stop or when the decoder fails. Alternate cuts (6 clips) keep the Saturn picture until a review decides otherwise.
4. The guest keeps streaming sector data untouched, so guest hashes must stay equal with the hook on and off (check with the existing strict-native replays).

## Split rows
- T108: CD-model hook point in `local/deps/satrecomp` (patch after 0072) that exposes the accepted play command words and the active disc; needs a runtime build.
- T109: presentation draw of the decoded frame in 16:9 plus the on/off guest-hash check with a saved state of the opening film; needs a runtime build and PC resources.
- T110: confirm `parse_play` against the SDK CD block code and a second clip in another saved state, including skip and resume behaviour.
