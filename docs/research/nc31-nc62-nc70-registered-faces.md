# NC31, NC62 and NC70 face registration

The natural Iris route on English disc 2 provides three checks for Enhanced Zoom. NC31 retained both Saturn face sprites over its PC body. NC70 retained the Saturn mouth. NC62 picked two donor layers from different expressions. Patch 0238 binds the live texture signatures to their matching PC expression groups and uses the body-relative locations from the PC tables.

| Checkpoint | Asset | Matched eye ordinal and position | Matched mouth ordinal and position |
| --- | --- | --- | --- |
| Chapter 9, 0900 theater field 5760 | NC31 | 21 at (96, 65) | 54 at (112, 105) |
| Chapter 9, 0901 briefing field 9450 | NC62 | 10 at (56, 65) | 46 at (72, 113) |
| Chapter 9, 0901 Ayame field 3600 | NC70 | Existing eye lookup | 41 at (112, 101) |

The registration requires the exact Saturn and PC files. Other textures continue through the existing lookup. At 2560×1440 on Direct3D11, the changed pixels are confined to the face. A projection of the sampled opaque donor pixels agrees with the candidate captures. Missing or truncated donors and Original match their controls. All seven arms per case ran 55 fields with identical guest hashes and SRAM and zero interpreted blocks.

The three observed disc-file rows are now verified in Chapter 9. Package inclusion is pending.
