# BG scene-image matching: running log

Goal: pair the 766 PC BG images (`SAKURA1/BG`, `SAKURA2/BG`) with the Saturn scenes, by comparing game screenshots against decoded PC images (`tools/decode_spred.py`, `tools/match_bg_screenshots.py`). Counts only; images stay under `local/`.

Signature: 32x20 luminance of the scene area (x 5-95 %, y 4-66 % of the frame), z-scored correlation against all 766 decoded BG images (`tobytes` grayscale). Candidates need a visual confirmation; a margin under 0.05 is ambiguous.

## Confirmed pairs (visually checked)

| PC image | Scene | Notes |
| --- | --- | --- |
| `SAKURA1/BG1119` | Chapter 1 corridor, day | `BG1120` is the night variant (lights lit) |
| `SAKURA1/BG1209` | Letter with seals | Saturn frame mid-fade; PC image is the full-brightness version |
| `SAKURA1/BG2251` | Cherry-blossom avenue | |
| `SAKURA1/BG1001` | Theatre lobby, front doors | |
| `SAKURA1/BG1002` | Theatre lobby with visitors (variant) | Actors in the PC image |
| `SAKURA1/BG1006` | Lobby, staircase and desk | |
| `SAKURA1/BG1007` | Theatre lobby with crowd (variant) | |
| `SAKURA1/BG1021` | Lobby staircase, green carpet | |
| `SAKURA1/BG1116` | Corridor with windows and door | |
| `SAKURA1/BG2039` | Group photo (academy cadets) | |
| `SAKURA1/BG1075` | Library, green curtains | |
| `SAKURA1/BG1120` | Corridor at night (lamps lit, dark window) | Night variant of `BG1119` |

Rejected: `SAKURA1/BG2173` for the episode title card (false positive, no matching structure).

## Pass 1: cold New Game, continuous run

- Source: the 297,107-frame cold run (inputs of `local/work/rb-full/input.movie`), one screenshot every 250 frames (about 1,190 frames), strict native mode.
- Status when written: running; 875 screenshots ranked (93 strong, 13 distinct candidates, 12 confirmed). After it ends: rank all screenshots, confirm candidates visually, and update this table and the scene-images counter in `config/hd-progress.json`.
- Count so far: 12 of 1,267 scene images matched, 0 integrated.

## T711: shard F, number-tier eye review

Method: `config/hd-scene-bg-map.json` (T67) pairs by file number; contact sheets of Saturn picture next to PC picture, reviewed by eye. Reviewed 5 tier-number pairs of shard F (BBG218, BBG238-BBG240, BBG242): all 5 confirmed (ring emblem and four character portraits). BBG pairs of tier content were already covered by T74. SAKURA1 BG0xxx: BG0000 was already rejected (blank). No Saturn counterpart found in the map for the `SAKURA2_GO_` PC images. Results are in `config/hd-scene-bg-review.json`; no screenshots needed. Not verified in the runtime.

## T710: shard E, number-tier eye review

Method: `config/hd-scene-bg-map.json` (T67) pairs by file number; contact sheets of Saturn picture next to PC picture, reviewed by eye. Reviewed 25 tier-number pairs of shard E (BG40xx-BG43xx): 14 confirmed (cut-outs), 11 rejected: BG4053-BG4058 different figure grouping than the PC picture of that number (frames look swapped between numbers, to re-pair by content later); BG4067, BG4071, BG4162 PC picture has the background baked in; BG4204 partial Saturn decode; BG4302 garbage decode. The 41 content-tier pairs were already covered by the T74 review. Results are in `config/hd-scene-bg-review.json`; no screenshots needed. Not verified in the runtime.

## T79: shard D, number-tier eye review

Method: `config/hd-scene-bg-map.json` (T67) pairs by file number; contact sheets of Saturn picture next to PC picture, reviewed by eye. Reviewed 25 tier-number pairs of shard D (BG2515, BG30xx-BG35xx): 17 confirmed (same art; BG3xxx are cut-outs on a key colour, the runtime generator never draws them as full pictures), 8 rejected: BG2515 garbage decode; BG3044, BG3054, BG3060, BG3069, BG3097, BG3119, BG3165 PC picture has the background baked in. The 65 content-tier pairs of the shard were already covered by the T74 review. Results are in `config/hd-scene-bg-review.json`; no screenshots needed. Not verified in the runtime.

## Shard C review (T78, 2026-11-19)

Shard C = `SAKURA1/BG20xx`..`BG23xx`: 254 decoded pictures (171 `content`, 83 `number`). 67 `number` pairs were already reviewed; the remaining 16 were compared by eye on contact sheets (Saturn left, PC right) and all confirmed as the same scene: BG2077, BG2093, BG2130, BG2172, BG2176, BG2207, BG2238, BG2247, BG2248, BG2252, BG2265-BG2269, BG2295. BG2207 and BG2265-BG2269 are one misty-forest background with different small objects (colour/lighting variants) and each Saturn variant matches its PC variant. Many Saturn decodes show strip artefacts (decoder layout), so these matches rest on composition and the visible variant details, not pixel correlation. Added to `eye_confirmed_number_tier`. `config/hd-scene-bg-pairs.json` is unchanged (it needs screenshot evidence frames).

## Shard B review (T77, 2026-11-19)

Shard B = `SAKURA1/BG11xx`, `BG12xx`, `BG13xx`: 200 decoded pictures (138 `content`, 60 `number`, 2 `missing`). 53 `number` pairs were already reviewed; the 7 remaining were compared by eye on a contact sheet (Saturn decode left, PC picture right) and all confirmed as the same scene: BG1207 (blossom picnic), BG1257 (ruined buildings), BG1280 (battle scroll), BG1282 (breaking wave), BG1283 (ruined street), BG1285 (burning street), BG1310 (large wave). Correlation is low (-0.27 to 0.47) because the Saturn decodes of BG1257, BG1283, BG1285 and BG1310 show band/strip artefacts (decoder layout, see `docs/research/saturn-bg-format.md`), so the match rests on composition, not pixels. Added to `eye_confirmed_number_tier`. `config/hd-scene-bg-pairs.json` is unchanged: it records screenshot-confirmed pairs with an evidence frame and none was taken.

## Shard A review (T76, 2026-11-19)

Shard A = `SAKURA1/BG10xx`: 99 decoded Saturn pictures, 65 tier `content` and 34 tier `number` in `config/hd-scene-bg-map.json`. All 34 `number` pairs were already confirmed by eye in `config/hd-scene-bg-review.json` (contact sheets, Saturn next to PC), so nothing is left to review at that tier and no new pair was added. Re-checked by a contact-sheet script that no `number` pair of the shard is missing from the confirmed or rejected lists. Not done: a side-by-side check of the 59 shard-A `content` pairs above correlation 0.905 (only the 96 lowest correlations of the whole set were reviewed side by side); the Saturn side was checked for baked-in English text.

## Content-tier side-by-side review, shards A-F (T76-T79, T710, T711, 2026-11-19)

Method: contact sheets (Saturn decode from `tools/decode_saturn_bg.py` left, PC picture from `tools/decode_spred.py` right, 16 pairs per sheet) of every `content`-tier pair not yet compared side by side: 300 pairs of shards A-D (the ones previously checked only on the Saturn side for baked-in text) plus 106 more of shards C-F that had no recorded review (BG2290, BG2515, BG2533, the BG3xxx/BG4xxx cut-outs and the BBG pictures), and the one number-tier pair BG2518. Per shard (content pairs confirmed this pass): A 56, B 96, C 132, D 60, E 40, F 18 (402 in all). Results: all confirmed as the same scene, recorded in `content_tier_side_by_side_2026_11_19` of `config/hd-scene-bg-review.json`, except four new rejects (BG3051 and BG3091: PC picture has a background baked in; BG4284: different frame, pedestal and prop only on Saturn; BG4375: PC picture has an extra teddy bear baked in). BG2518 added to `eye_confirmed_number_tier`.

Notes: the Saturn BG1081-BG1097 door pictures have a more saturated yellow-green wall gradient than the PC ones (same layout); BG1334 is bluer on Saturn, BG2275 darker on Saturn (lighting variants of the same scene). BG2515 and BG4302 are listed above as garbage decodes in the number-tier reviews; with the current decoder both match the PC picture (correlation 0.998 and 1.0), so those older notes are stale (neither is in `rejected`). Seven files of shard C (BG2002, BG2003, BG2014, BG2016, BG2023, BG2038, BG2337) were read from the disc image because they are missing from the local raw extraction.

Compiled table: `tools/gen_scene_bg_table.py` skips BG3xxx/BG4xxx by name, so the four new rejects do not change it; BG2518 would add one entry if the table is regenerated. The table tool has no tests and the generated header is not in the repository, so it was not regenerated here. `config/hd-scene-bg-pairs.json` is unchanged (screenshot evidence from the cold run only). Not verified in the runtime.

### BG2251 cherry-blossom avenue at 1440p

The Chapter 1 route on prepared Spanish disc 1 replays from
`pruebas/largo/carta-9900.state` with its matching backup seed and
`run.movie` rebased at frame 9900. After 8,560 strict-native frames, the
presented inset matches the decoded Saturn BG2251 picture with luminance
correlation 0.99996. The retained relay state at frame 8559 contains the
BG2251 tiles at VDP2 VRAM 0x34840 and its palette at CRAM 0x200.
Its SHA-256 is
`81464c7832d71365180485007548550537f16da85d7266fb1d2086eb02d6e9d7`.

From that exact state, two independent 60-frame Enhanced Zoom profiles
at 2560×1440 ran without inputs on the v0.2.6 campaign runtime.
Only one profile could see BG2251.SPR and reported a usable texture.
All 60 guest hashes matched (log SHA-256
`8ad542d2a569e885d0e170f02dc9c120de7e27f22266843376a0adb2d28dfcca`).
Both runs reported zero interpreted blocks. The runtime SHA-256 is
`6fcd9aba866a1f3c14c706b8c1a9edc4b40ad4f5a555daa2454c9a59a9269482`.

At frames 20, 40 and 58, every RGB difference stays inside
(272,29)–(2288,1037), right and bottom exclusive. The avenue, tree trunks
and lantern strings match the composition by eye. The surrounding
presentation and the archived fixture's test-only dialogue markers are
pixel-identical in the controls. The prepared English and Spanish disc 1
BG2251 picture files are byte-identical. Visual checks here cover the
BG2251 scene itself. No package was built.

The main workspace measured 51,405,524,876 logical bytes with hard links counted
once and reparse points excluded. The delivered development ZIP remains
6,315,009,692 bytes.
