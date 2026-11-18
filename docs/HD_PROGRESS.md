# HD progress

**Global goal: 100% verified. Status: Indeterminate.**

The percentages correspond to the defined inventory for each row. A "No data" cell indicates a pending measurement, and a zero indicates a confirmed absence. Candidate counts are detailed separately.

| Area | Unit | Inventoried | Matched | Prepared | Integrated | Verified in game |
| --- | --- | --- | --- | --- | --- | --- |
| Portraits and animation | Saturn identities | 304/304 (100%) | 300/304 (98.6%) | 300/304 (98.6%) | 300/304 (98.6%) | No data |
| Videos | unique clips | 50/50 (100%) | 44/50 (88%) | 0/50 (0%) | 0/50 (0%) | 0/50 (0%) |
| PC/Saturn HUD and menus | shared screens and pieces | No data | No data | No data | No data | No data |
| KABE decorative backgrounds | KABE inventory themes | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) | No data |
| Large NC characters | native poses and compositions | No data | No data | No data | No data | No data |
| Scenes and transitions | distinct scenes in execution | No data | No data | No data | No data | No data |

## What counts at each stage

- **Inventoried**. Native elements identified within the declared scope.
- **Matched**. Approved correspondence of the asset and its required variants.
- **Prepared**. Substitution packaged and validated against the runtime format.
- **Integrated**. Substitution connected to the corresponding execution path.
- **Verified in game**. Distinct elements validated in traceable captures or playbacks.

The global goal is reached when each category has a confirmed total and all its stages cover that total. Units are evaluated per category, without averaging them.

## Scope and pending items

### Portraits and animation

Identities from the Saturn atlases audited on both discs. Eye and mouth strips are counted once per identity.

- Reproducible checkpoint. 201 identities with base, eyes, and mouth available. 402 PNGs were checked at two densities. The delivered v0.1.2 package keeps 191 portraits.
- Chapter 1. 91/123 identities with all three regions prepared and 32 pending. The six scope FCEs appear in the audit.
- Verified in game: Sakura 0013 and 0014, Sumire 0045 and María 0064 bases. In Sumire 0040 and 0041 the first strip was observed at Y=16. In the third batch, in-game strips and verification of the other four bases remain pending.
- 394 PC candidates. The availability of the strips in the package leaves pending the accumulated coverage per identity during gameplay.
- **Next step**. Review the pending identities and validate blinking, mouth, both strips simultaneously, effects, and in-game fallback.

Pending Saturn ID ranges in hexadecimal

`00a1` `0152-0153` `0169`

- [portrait-animation-coverage.md](research/portrait-animation-coverage.md). SHA-256 of the local receipt `f76f05657f88e9d37af6517e878ccdfd81abc9a8a0db38c899fa1e62bce13aac`.
- [first-sakura-hd-portraits.md](research/first-sakura-hd-portraits.md). SHA-256 of the local receipt `8aef026bb744db43f813f3435455fec694a432bc6dbe87ad09a88619c6d9a3b1`.
- [chapter1-sumire-hd-portraits.md](research/chapter1-sumire-hd-portraits.md). SHA-256 of the local receipt `3ff2e8dfe039d3c64489ebb784a0c3f7f5b56572148197025ff53840fc857f48`.
- [chapter1-third-hd-portraits.md](research/chapter1-third-hd-portraits.md). SHA-256 of the local receipt `182ad5f38ab46b744e8a5ef2682f2e3477792f80c47ef13d7e17b74802ac035e`.
- [v0.1.2.md](releases/v0.1.2.md). SHA-256 of the local receipt `e1653a18a41ae3f68acce1fde82c4fba82f6a00228353d160a402d1e5a940b5f`.

### Videos

Full correspondences between Saturn and PC clips, with their editing variants, subtitles, audio, and skip behavior.

- 50 unique Saturn clips (FILM streams deduplicated across both discs; the 0.15 s logo short is excluded) versus 52 PC MPEGs (51 MOVIE + REDLOGO).
- 44 pairs with duration within 0.5 s and identical consecutive order (stream k of /SAKURA4 ↔ MOVIE00k). Six pairs require editing review due to a duration difference: 743bce↔009, d33904↔105, b39c1e↔004, ab833c↔011, 7b1472↔102, and def7a6↔020 (3.7 s).
- No integrated substitution: MPEG-1/MP2 decoding in the runtime, audio sync, subtitles, and skip are still missing.
- **Next step**. Review the editing of the six pairs with a duration difference, check audio/subtitles/skip, and design PC playback within the runtime.

- [scene-tagging.md](research/scene-tagging.md).
- [intro-petals-transition.md](research/intro-petals-transition.md).

### PC/Saturn HUD and menus

Joint inventory per screen or equivalent piece, including map, battle, status, and save elements.

- Tactical menus were observed on Saturn and their presentation was adjusted. Still need to link the shared HD pieces and count the covered screens.
- **Next step**. Inventory the screens and shared pieces per edition. Separate HD substitution from Saturn layout adjustments.

- [tactical-menu-independent-reference.md](research/tactical-menu-independent-reference.md).
- [v0.2.0-test.1.md](releases/v0.2.0-test.1.md).

### KABE decorative backgrounds

The 19 unique decorative themes from the KABE catalog with HD alternatives, including the cataloged day/night pairs.

- 19 background variants ready for the runtime. Preload and loader parity measure the prepared assets. Scene coverage is tracked separately.
- **Next step**. Gather validations per theme and scene, including lighting variants, fades, dialogue, and transitions.

- [provenance.json](../assets/generated/pc-backgrounds/provenance.json).
- [saturn-background-workers.md](research/saturn-background-workers.md).
- [v0.1.2.md](releases/v0.1.2.md). SHA-256 of the local receipt `e1653a18a41ae3f68acce1fde82c4fba82f6a00228353d160a402d1e5a940b5f`.

### Large NC characters

Bodies and poses outside the dialogue portrait. The total of native poses and compositions remains open.

- 147 PC packages and 3,596 decoded images. There are 147 candidate name pairs. Per-pose equivalences are still missing.
- **Next step**. Link indexes per pose and validate anchor, proportion, and animation in Saturn captures for each substitution.

- [saturn-hd-characters.md](research/saturn-hd-characters.md).
- [pc-character-inventory.json](research/pc-character-inventory.json).

### Scenes and transitions

Visits, choices, maps, battles, menus, films, and transitions navigated on both discs.

- The initial index lists 166 asset candidates and nine execution observations. A dialogue table or a video stream can appear in more than one path.
- Priority pending items: other map-to-room paths, dialogue continuity and animation in later scenes, complete battles, disc change, and clips with subtitles.
- **Next step**. Link each occurrence to a stable scene or transition, record the native mode, and verify HD, Zoom, and fallback where applicable.

- [scene-tagging.md](research/scene-tagging.md).
- [wide-map-crossfades.md](research/wide-map-crossfades.md).
- [chapter-sweep.md](research/chapter-sweep.md).

## Updating the record

Add the reviewed result to `config/hd-progress.json`. Record the unit and scope of the total, the checked stage, and the corresponding public evidence. Use `null` if the inventory or count is missing, and count each identity once even if it appears on several discs or scenes. A name match, extraction, and decoding alone count as candidates. When approving a portrait, update the number of matches and its pending ranges. Keep images, videos, saves, scripts, and owner-local paths out of the record.

```powershell
python tools/build_hd_progress.py
python tools/build_hd_progress.py --check
python -m unittest discover -s tests -p test_hd_progress.py
```
