# NC24 and NC3250 mouth placement

In Enhanced Zoom, the heuristic placed these mouth pieces slightly below and to the left of the positions in the PC expression tables. For NC24 the observed displacement was two donor pixels on both axes. For NC3250 it was three. Patch 0234 registers the three observed mouth textures against the exact disc-file and PC-file signatures. Both eyes already resolve to their authored positions. Unregistered textures continue to use the existing lookup.

| Field witness | Saturn and PC assets | Observed PC mouth ordinals | Body-relative PC position |
| --- | --- | --- | --- |
| Chapter 9 English disc 2, natural 0904 route, checkpoint f1980 | NC24.BIN and NC24.SPR, body ordinal 7 | 99, 102 | (200, 101) |
| Chapter 1 English disc 1, campaign relay checkpoint f01350 | NC3250.BIN and NC3250.SPR, body ordinal 0 | 4 | (250, 210) |

The hidden Direct3D11 comparison rendered at 2560×1440. At the opaque samples, the pixel delta is confined to the shifted mouth area. Donor projection checks matched all sampled opaque interiors. The native blended fields, Original mode with and without the donor, and Enhanced with missing or truncated donors matched their controls. Each arm ran 55 fields with identical guest hashes and backup RAM and zero interpreted blocks.

NC24 adds one verified disc-file row to Chapter 9. NC3250 already has a Chapter 1 verification; see [the NC3250 native underlay witness](saturn-bg-format.md#nc3250-alpha-fade-and-native-underlay-witness-t106e). These results apply to the observed mouth textures. Package inclusion is pending.

A separate NC3250 comparison with BG2250.SPR usable in both builds confined the changes to the same mouth bounds. The scene plate, blended fields, guest hashes and backup RAM matched.
