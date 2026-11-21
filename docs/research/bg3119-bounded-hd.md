# BG3119 garden figures

The controlled 0102 garden replay used for BG2119 also reads BG3119 on
disc 1. The field-179 state holds its exact cells at VDP2 address
`0x4A040` and palette at CRAM `0xE00`. The native art matches 13,589
visible cells in the field-180 capture, with the dialogue portrait
occluding part of the group.

The PC donor has the garden painted behind the figures. The registered
region uses the native silhouette and local color agreement to admit only
matching interior pixels. The offline compositor accepted 4,463 visible
cells with zero samples outside the native silhouette. Foreground
occlusion is preserved by the existing runtime layer and RGB checks.

## Linked 1440p comparison

The first linked build produced identical frames with and without BG3119.
The loop stopped after claiming the matching BG2119 floor layer even when
its PC donor was missing. Patch 0334 gives the floor and foreground their
own texture and upload state so either layer can draw independently.

The candidate `f72ac94a7fbc29a8dd6b927afb63c7e87eef4facd409e7fa34c0e906fc9d231a`
completed six 180-field strict replays with identical guest hashes. At
2560 × 1440, BG3119 alone changed 208,365 pixels and BG2119 alone changed
187,347. Their masks were disjoint and the combined capture matched the
exact union. Original mode matched pixel for pixel with both donors
present or absent. This verifies the controlled garden checkpoint.
Package inclusion remains pending.
