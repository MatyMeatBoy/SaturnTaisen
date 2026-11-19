# Disc 2 opening film in the native theatre

The English disc-2 cold boot issues Play at FAD 0x197, within the
MOVIE100 mapping. Its 288×144 video plate occupies (16,8)–(304,152)
in the 320×224 Saturn theatre. The initial runtime drew this plate
natively even when it had the owner-supplied PC file, because the
usual movie hook ran inside the recognized backdrop paths.

Enhanced can now draw the PC movie on the existing theatre plate.
The guard requires the exact top layer inside the rectangle, no
layer-1 pixels outside it, matching visible composition, and no
colour offset. Framing, ornaments and the stock fallback are retained.
The new path uses the synchronized Saturn soundtrack. In preliminary
tests of the old PC-audio feeding rule, the SDL disk driver showed
+293 ms and +3,660 ms audio lead after 20 seconds at different load.
The remaining audio-clock work is separate from the video change.

## Verification

On English disc 2, the final 1080p runtime opened MOVIE100 at the
expected Play event. Start at frame 900 exits the film. Six 1,800-frame
runs formed three PC/native A/B pairs (Enhanced with Start, Original
with Start, and normally paced Enhanced audio capture with Start).
Each pair preserved all guest hashes, with zero interpreted blocks.
In Enhanced the two active film captures differ only inside
(384,124)–(1536,700). Captures before the film and after the skip
are identical. All six Original screenshots are identical.

The final PCM captures have nonzero native audio during and after
the film, and the runtime never switched to the PC audio source.
The tested runtime SHA-256 is
`502cc417f7f36559e81505b9b8657718d0d0d3693926a0394377bb55cb96febe`.
The remaining disc 2 titles, audio clock work, and clean package
validation remain in TW8. No release package was replaced or built.
