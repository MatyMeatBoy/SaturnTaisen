# THD11: Chapter 1 large bodies (19 observed NC)

This is the review table for the 19 NC bodies named in [Chapter 1 HD coverage](hd-chapter-1.md). It was compiled from the tracked evidence (coverage register, face reports, body-format report). The first-frame brackets are from the full cold route (`hd-chapter-1.md`). Follow-up replay evidence for NC95 and NC3004 appears below.

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
| NC95 | Upstairs (103,080) | 9 parts | **episodes 1 and 6 verified** | ep 1: one eye and mouth pair verified; ep 6: two faces verified | not witnessed | not witnessed |
| NC96 | Late chapter (105,600) | 272x320 body 0 | verified | all 9 registered (patch 0179) | native blend retained | not witnessed |
| NC55 | Iris room (189,240) | 368x320 body 5 | verified | 5 textures registered (patch 0168), 3 E + closed Ms; others fallback | none seen | not witnessed |
| NC81 | Theater sortie (245,940) | 208x144 | **episode 1 occurrence NOT verified** (verified in chapter 9: neck underlay patch 0149, E 15-17 patch 0241, M native) | ep 9 only | n/a | n/a |
| NC12 | Sortie, Sakura (248,400) | 346x320 body 2 | verified | 4 E + 6 M (patch 0184) | earlier blend identical | native blend |
| NC51 | Sortie, Iris (248,700) | 336x320 body 1 | verified | 3 E + 6 M (patch 0177) | earlier blend native | native blend |
| NC21 | Sortie, Sumire (249,000) | 320x320 body 1 | verified | 3 E + 6 M (patch 0180) | blend identical | native blend |
| NC32 | Sortie, Maria (249,240) | 304x320 body 2 | verified | 3 E + 6 M (patch 0182) | blend identical | native blend |
| NC3004 | Hanami ending (255,900) | 9 parts, 2 runs | **Episode 1 draw verified** | two eye phases and closed mouth verified | native transition and fallback verified | not witnessed |

## Findings

- 18 of 19 are `verified_in_game`. **NC81** (theater sortie) still needs chapter 1 verification.
- Bodies with an extra pose without a control: NC3250 (mouths other than ordinal 4), NC11 (LIPS layouts other than the hallway), NC20 and NC30 (runs beyond the verified groups), NC25 (poses other than the closed-eye smile), NC55 (poses beyond the five observed textures), NC82 and NC97 (fallback frames).
- Fade-in/out has a witness only for NC3250 and NC82; the other 17 need a fade control (dissolve plus donor-absent control) before the column can be "verified".
- Neck/blend controls: only NC81 (chapter 9) and NC11 (LIPS) have neck or panel blend controls; the sortie bodies rely on "earlier blend identical".

## Proposed batches

1. NC81 (ch 1): natural-route checkpoints, 2560x1440 Enhanced vs Original, donor present vs absent, identical guest hashes with 0 interpreted.
2. NC3250, NC82, NC97 fade controls and extra poses.
3. NC20, NC30, NC25, NC55 extra expression groups.

Reported deltas for this PR: attributed 0, integrated new 0, verified new 0.

## NC95 on the Episode 1 upstairs route

A retained checkpoint from the English disc 1 Chapter 1 cold route shows the 144 × 144 NC95 body sprite at (96, 8), texture FNV-1a `8CB41598D7FE8FC0`. The checkpoint is field 28146 of the [NC96 continuation](nc96-registered-faces.md#replay-results). The test resumes with the archived input suffix. It matches the next 180 hashes (recorded fields 28147–28326), with identical final SRAM across five profiles and zero interpreted blocks. The existing 0243 runtime has SHA-256 `129E505D229EB3520A9AD4E52F6873C2BC87F609DF15F3A520ABFCB086EA5C19`.

At 2560 × 1440 on Direct3D11, supplying only NC95.SPR changes 673,463 pixels in each of 12 paired captures. All changes are within (853, 29)–(1840, 1037), right and bottom exclusive. Independent projection matches the 4,093 sampled flat eye pixels of ordinal 1 at body-relative (32, 73) and 1,408 mouth pixels of ordinal 4 at (96, 121) in each capture. Missing and truncated donor controls match in Enhanced. The Original profiles with and without the donor also match.

The window verifies the observed Episode 1 body and face. The [Episode 6 occurrence](hd-chapter-6.md#verified-nc95-upstairs-body) remains independently verified. Other expressions and blends are outside the sampled window. There is no new integrated asset or runtime change.

## NC3004 at the Episode 1 hanami

Two retained checkpoints from the English disc 1 continuous route capture the appearance of NC3004. The relay begins at global field 239,080. The saved fields 16,820 and 17,150 correspond to approximately 255,900 and 256,230 on that route. The test replays the archived controller suffix and matches the corresponding 180 archived guest hashes from each checkpoint. Backup RAM matches every arm from the same checkpoint. Every strict run reports zero interpreted blocks.

The native body is the 288 × 144 VDP1 sprite at (16, 8), texture FNV-1a `657B89AB9FA498BB`. The sole donor is NC3004.SPR, with a 576 × 320 PC body. At 2560 × 1440 on Direct3D11, the opaque checkpoint changes 1,043,890–1,043,984 pixels per capture, all within (272, 29)–(2288, 1037). Original with and without the donor and Enhanced with a truncated donor match their controls in all 12 samples.

The transition checkpoint logs a blend over NC3004. Nine samples through offset 110 match the donor-absent control across the whole frame. The three later samples at 128, 145 and 172 show the expected donor area.

The sampled eye phases correspond to PC ordinals 1 and 2. Projection at the authored (217, 63) matches 2,007/2,023 and 2,044/2,059 flat opaque samples. The current refine pass places these phases at (218, 63), one donor pixel to the right, with no visible seam in crops of either phase. The closed mouth matches all 862 projected pixels for ordinal 4 at the authored (251, 118). The unsampled closed-eye phase reports a different heuristic offset and was not visually certified. No runtime patch is required for the witnessed draw.

Existing 0243 runtime SHA-256 `129E505D229EB3520A9AD4E52F6873C2BC87F609DF15F3A520ABFCB086EA5C19`. This evidence verifies the Episode 1 occurrence and the observed blend fallback. Other expressions and package inclusion remain open.
