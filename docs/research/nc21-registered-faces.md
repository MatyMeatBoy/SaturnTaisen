# Sumire NC21 face registration in Chapter 1

Patch 0180 registers the three eye poses and six mouth poses used in Sumire's Chapter 1 theater sortie introduction. Enhanced places these face parts at their authored PC positions. The existing matcher and native fallback continue to handle other expressions.

## Asset and placement evidence

The full cold Chapter 1 route first recognizes NC21 between fields 249,000 and 249,060. The short replay resumes after Iris's introduction, lets Sumire's dialogue play, and holds the pose. The previous matcher drew a different mouth on her neutral pose and fell back to a native patch for the closed eyes.

The native 152 × 144 body starts at offset 1,552 in /SAKURA1/NC21.BIN and has FNV-1a 1DCD784AFB2AE7CC. The full native file has FNV-1a 7421084549F2AD18 in the prepared English and Spanish editions of both discs. The PC donor SAKURA1/NC/NC21.SPR has FNV-1a 63308CEB4FBE148A and uses 320 × 320 body ordinal 1. The registration requires both full-file fingerprints.

The nine native part fingerprints match those already verified for NC20 group 1. The corresponding decoded PC image pixels are also identical at all nine ordinals. NC21's SPRED table 7 gives its own body origin (−32, 0). Tables 8 and 9 put these eyes at (120, 53) and mouths at (136, 101). The resulting body-relative positions are (152, 53) and (168, 101).

| Native offset | Texture FNV-1a | Dimensions | PC ordinal |
| --- | --- | --- | --- |
| 46,480 | 6DCC379CDC564E30 | 48 × 16 | 11 |
| 47,248 | 77223F8DD72DA99C | 48 × 16 | 12 |
| 48,016 | 68B1E2BD1B57FDAF | 48 × 16 | 13 |
| 48,784 | 04730AFBE17C2375 | 24 × 24 | 45 |
| 49,360 | DB6B782331D6CF10 | 24 × 24 | 46 |
| 49,936 | 42239773C0671A3E | 24 × 24 | 47 |
| 50,512 | BAEB1C0B96B2402E | 24 × 24 | 48 |
| 51,088 | 00C3995FAC06E28D | 24 × 24 | 49 |
| 51,664 | B39FF1B9201E7BF4 | 24 × 24 | 50 |

## Replay results

The exact 0179 and 0180 builds match all 900 guest hashes, decoded PCM, and final backup RAM in each of the Enhanced, Original, missing-donor and altered-donor pairs. All four pairs report zero interpreted blocks. The altered donor changes one byte in SPRED table 12 outside the image decoder. All 15 sampled Original and donor-control screenshots match at 2560 × 1440.

The Enhanced comparisons exercise all nine parts. Ten changed screenshots differ only within (1056, 204) to (1392, 533), the envelope of the eye and mouth artwork. The other three screenshots match, including the earlier fade. The independent PC decode reproduces the three eye poses and six mouths at their authored positions. Mean absolute RGB error on the eye samples falls to 2.28–2.56 from 3.00–30.70 and on the mouth samples to 0.62–1.01 from 5.52–17.34.

Live evidence covers this English disc 1 scene. Spanish and disc 2 live playback, the other NC21 poses, and package inclusion remain open. Private evidence and build files are under local/work/codex-nc21-expression. Cleanup removed 1,029,216,031 bytes of regenerable prototype executables, objects, and captures. The project measured 111,728,181,871 logical bytes with existing private assets and packages. The immutable development ZIP measured 6,315,009,692 bytes.
