# THD11: Chapter 1 large bodies (19 observed NC)

This is the review table for the 19 NC bodies named in [Chapter 1 HD coverage](hd-chapter-1.md). It was compiled from the tracked evidence (coverage register, face reports, body-format report). **No new runtime capture was made for this table.** The first-frame brackets are from the full cold route (`hd-chapter-1.md`). The local checkpoints for the three unverified bodies (fields near 103,080, 245,940 and 255,900) were not available in this workspace, so they remain open.

State columns follow `config/hd-chapter-coverage.json`: *attributed* = observed in the route with a PC donor named; *connected* = runtime draws the PC body; *verified* = `verified_in_game` with a paired capture. Expression = how eyes (E) and mouth (M) are chosen. Fade and occlusion are only listed where a report witnesses them; "not witnessed" is not a negative result.

| Body | Route / scene (first field) | Pose / PC body | State | Expression (E / M) | Occlusion | Fade in/out |
| --- | --- | --- | --- | --- | --- | --- |
| NC3250 | Opening orders, Ogami salute (10,380) | 446x320 body 0 | verified | E authored; M ordinal 4 registered (patch 0234), other mouths fallback | none seen | alpha fade and BG2250 underlay witnessed (T106e) |
| NC10 | Park, Sakura (14,400) | 176x144, group 0 | verified | 4 E + 6 M registered (patch 0169) | LIPS panel over body in choices: native kept | not witnessed |
| NC50 | Lobby staircase, Iris (23,100) | 288x320 | verified | 11 parts registered (patch 0171), 2 expressions | native overlap kept in both builds | not witnessed |
| NC11 | Hallway, Sakura, timed LIPS choice (27,480) | 93-part atlas | verified (hallway) | E 20-23, M 65-70 registered (patch 0227); other LIPS layouts open | LIPS 11/32 panel: body replaced, UI preserved (patch 0172, ownership proof) | frame 120 after choice identical |
| NC20 | Post-3000, white-hairband girl (30,120) | 5 runs | verified (one group) | E 11-13, M 45 via verified table (TW4); other groups fallback | other sprites crossing: native fallback | not witnessed |
| NC25 | Sumire (34,860) | 440x320 body 6 | verified | eyes baked in PC body (closed smile), 3 M registered (patch 0173); other poses fallback | native blend retained | blend native |
| NC30 | Blond woman, dark kimono (37,620) | 54 parts, 6 runs | verified | E 12-14, M 42 via verified table (TW4); others fallback | native fallback where crossed | not witnessed |
| NC82 | Man with glasses (50,580) | exact layout | verified | exact-layout match, fallback for the rest | none seen | fade-in witnessed (T106c) |
| NC56 | Iris (58,320) | 288x320 body 6 | verified | 3 E + 6 M registered (patch 0176); blink during blend native | native blend retained | not witnessed |
| NC97 | Short-hair girl (74,760) | 272x320 | verified | exact layout 3 E + 6 M | none seen | not witnessed |
| NC95 | Upstairs (103,080) | 9 parts | **episode 6 occurrence verified; episode 1 occurrence NOT verified** | ep 6: two faces verified (hd-chapter-6) | not witnessed | not witnessed |
| NC96 | Late chapter (105,600) | 272x320 body 0 | verified | all 9 registered (patch 0179) | native blend retained | not witnessed |
| NC55 | Iris room (189,240) | 368x320 body 5 | verified | 5 textures registered (patch 0168), 3 E + closed Ms; others fallback | none seen | not witnessed |
| NC81 | Theater sortie (245,940) | 208x144 | **episode 1 occurrence NOT verified** (verified in chapter 9: neck underlay patch 0149, E 15-17 patch 0241, M native) | ep 9 only | n/a | n/a |
| NC12 | Sortie, Sakura (248,400) | 346x320 body 2 | verified | 4 E + 6 M (patch 0184) | earlier blend identical | native blend |
| NC51 | Sortie, Iris (248,700) | 336x320 body 1 | verified | 3 E + 6 M (patch 0177) | earlier blend native | native blend |
| NC21 | Sortie, Sumire (249,000) | 320x320 body 1 | verified | 3 E + 6 M (patch 0180) | blend identical | native blend |
| NC32 | Sortie, Maria (249,240) | 304x320 body 2 | verified | 3 E + 6 M (patch 0182) | blend identical | native blend |
| NC3004 | Hanami ending (255,900) | 9 parts, 2 runs | attributed + connected, **not verified, no face registration** | native fallback assumed, not observed | not witnessed | not witnessed |

## Findings

- 16 of 19 are `verified_in_game`. The three not verified in chapter 1 are **NC3004** (hanami), **NC81** (theater sortie; only the chapter 9 occurrence is proven) and **NC95** (only the episode 6 occurrence is proven).
- Bodies with an extra pose without a control: NC3250 (mouths other than ordinal 4), NC11 (LIPS layouts other than the hallway), NC20 and NC30 (runs beyond the verified groups), NC25 (poses other than the closed-eye smile), NC55 (poses beyond the five observed textures), NC82 and NC97 (fallback frames).
- Fade-in/out has a witness only for NC3250 and NC82; the other 17 need a fade control (dissolve plus donor-absent control) before the column can be "verified".
- Neck/blend controls: only NC81 (chapter 9) and NC11 (LIPS) have neck or panel blend controls; the sortie bodies rely on "earlier blend identical".

## Proposed batches

1. NC3004, NC81 (ch 1), NC95 (ch 1): natural-route checkpoints, 2560x1440 Enhanced vs Original, donor present vs absent, identical guest hashes with 0 interpreted.
2. NC3250, NC82, NC97 fade controls and extra poses.
3. NC20, NC30, NC25, NC55 extra expression groups.

Reported deltas for this PR: attributed 0, integrated new 0, verified new 0.
