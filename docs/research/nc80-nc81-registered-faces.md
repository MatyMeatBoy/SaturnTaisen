# NC80 and NC81 face registration

Two archived English disc 2 scenes show Saturn facial strips over the PC body in Enhanced Zoom. Patch 0241 identifies the observed strips by texture signature and uses the positions authored in the PC SPRED tables. The registration requires the exact Saturn and PC files.

| Checkpoint | Body | PC eye ordinals and position | PC mouth ordinal and position |
| --- | --- | --- | --- |
| Chapter 8, module 0804, BG1019 terminal | NC80 | 9–11 at (132, 57) | 42 at (143, 119) |
| Chapter 9, module 0901, after storage | NC81 | 15–17 at (138, 74) | Native mouth |

NC81 keeps the native mouth and the [existing neck underlay](nc81-nc90-1440p.md). The sampled eye interiors agree with the authored donor projection. The controls use Direct3D11 at 2560×1440 and preserve guest hashes and backup RAM. Ordinary missing or truncated donor fallback and Original mode match their controls.

NC80 adds one verified disc-file row in Chapter 8. The Chapter 9 NC81 body already has a verification row. Package inclusion is pending.

The candidate included 161 additional local MAP14 AOT variants, pending separate integration. The two individual headless replays matched the 0240 guest hashes and SRAM for all 55 fields in every profile, with zero interpreted blocks. In five NC81 capture pairs, the mouth and neck crop matched the 0240 output pixel for pixel.
