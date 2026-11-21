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
Linked HD playback and package inclusion are pending.
