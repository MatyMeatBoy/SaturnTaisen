# Saturn ↔ PC video equivalence

T20 scope, inventory only: no playback is replaced. Measurements came from ffprobe on the FILM streams of both discs (extracted by LBA/offset from the scene inventory) and on the PC MPEGs extracted from the cabinet; no original file is version-controlled.

| Data | Value |
| --- | --- |
| Unique Saturn FILM streams | 51 (50 clips + 0.15 s logo stub) |
| PC MPEGs | 52 (standalone MOVIE000–MOVIE120 + REDLOGO) |
| Pairs with consecutive order and duration ≤ 0.5 s | 44 |
| Pairs with differing duration (review edit) | 6: 743bce↔009 (0.65 s), d33904↔105 (0.98), b39c1e↔004 (1.06), ab833c↔011 (1.08), 7b1472↔102 (1.51), def7a6↔020 (3.73) |
| PC with no assigned Saturn pair | MOVIE118 (9.43 s, similar to MOVIE015), REDLOGO (5.32 s) |

Method: relative duration, 24×12 grayscale thumbnails at five relative points, and stream order in `/SAKURA4` (stream k ↔ `MOVIE00k`). Thumbnails alone are weak (the Saturn palette differs), so the assignment is driven by duration and order; no equivalence is declared for edit, audio, or subtitles.

Content check of the six pairs (5-frame luminance signature, 24x12, against all 52 PC clips): each assigned PC clip is the unique best match with a margin of 1.5x-3.0x over the runner-up (distances 14.4-25.1 versus 27.3-44.9; the closest are MOVIE011 at 1.5x and MOVIE102 at 1.6x). They are accepted as matched, recorded as alternate cuts (PC runs 0.6-3.7 s different). The pairing is by content, not by audio or subtitles.

Pending: compare audio/subtitles/cuts of these six alternate cuts and design MPEG-1/MP2 decoding and runtime sync. Not integrated in test.4.

## T53 decoder authorised (2026-11-19)

The owner authorised adding **pl_mpeg** (MIT, single header, MPEG-1 video + MP2 audio + MPEG-PS demuxer, https://github.com/phoboslab/pl_mpeg). Downloaded to `local/deps/pl_mpeg/pl_mpeg.h` (141,424 bytes, SHA-256 `3a8cb30c83c2a1147719c30fe0c8b93da2987aa43140077c575b39aaa75fc2c9`), not committed yet; it will be added with its licence to `THIRD_PARTY_NOTICES.md` when the runtime uses it.

Design for the next block (nothing implemented yet):
1. Identify the FILM stream that the Saturn is streaming (the 51 streams of this document, by the stream start LBA or the hash of its first sector) and map it to its `MOVIEnnn` through the 44+6 pairing above.
2. Decode the PC MPEG with pl_mpeg on a worker thread, upload YUV→RGB frames to a texture and draw it in the 16:9 presentation in place of the Saturn picture, keeping the guest running untouched (guest hashes must stay identical).
3. Sync to the guest's FILM time (the Saturn clip is the clock), skip and end with the guest; the PC audio replaces the Saturn audio only if its duration matches (the six alternate cuts keep the Saturn video).
4. Verify with a clip in a saved state; unpaired MOVIE118 and REDLOGO stay unused.
