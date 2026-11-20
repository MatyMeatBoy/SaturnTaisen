# Iris NC51 face registration in Chapter 1

Patch 0177 registers the three eye poses and six mouth poses used by Iris in her Chapter 1 theater sortie. Enhanced places these PC face parts at their authored coordinates. Other NC51 expressions retain the existing matching and native fallback.

## Asset and placement evidence

The full cold Chapter 1 trace first recognizes NC51 between fields 248,700 and 248,760. The compact replay starts from the earlier Yoneda introduction checkpoint in the Chapter 1 Iris portrait trial and holds on Iris's spoken introduction. All nine native eye and mouth strips are used in the 900-field trial.

The native 168 × 144 body starts at offset 1,552 in /SAKURA1/NC51.BIN and has FNV-1a 533E47EEF956F35F. The full Saturn resource has FNV-1a BD48D984612C5BB2 in the prepared English and Spanish editions of both discs. The PC donor SAKURA1/NC/NC51.SPR has FNV-1a 6DF3B8AE5CA82D57 and a 336 × 320 body at ordinal 1. The registration requires those two full-file identities.

The three consecutive native eyes begin at offset 71,120 and map to group 5 in PC SPRED table 6. Its corresponding six-mouth sequence begins at 76,496. The matching open eyes and closed mouth also have identical native texture fingerprints in the registered NC55 group 5. Table 7 puts the NC51 body at (−40, 0). Tables 8 and 9 place donor eyes at (88, 81) and donor mouths at (120, 121), yielding positions (128, 81) and (160, 121) relative to the body.

| Native offset | FNV-1a | Dimensions | PC ordinal |
| --- | --- | --- | --- |
| 71,120 | 24EF353C40FD9286 | 56 × 32 | 20 |
| 72,912 | FE3C25AD5CF1028C | 56 × 32 | 21 |
| 74,704 | 412A893FE556BAA8 | 56 × 32 | 22 |
| 76,496 | 83B38D30B6C5BB4E | 24 × 24 | 71 |
| 77,072 | DBF39177420BE488 | 24 × 24 | 72 |
| 77,648 | 9CA380300233B275 | 24 × 24 | 73 |
| 78,224 | 7F74F79F7C038936 | 24 × 24 | 74 |
| 78,800 | 0F14ADD1DCE919C2 | 24 × 24 | 75 |
| 79,376 | 66540C4C0E410BF4 | 24 × 24 | 76 |

## Replay results

The exact 0176 and 0177 builds match all 900 guest hashes, decoded PCM and final backup RAM in each of the Enhanced, Original, missing-donor and altered-donor pairs. All runs report zero interpreted blocks. The altered donor has one byte changed in SPRED table 12, outside the image decoder. All 15 sampled frames across Original and the donor controls are RGB-identical.

The enhanced 2560 × 1440 comparison changes 15 samples only within the face bounds (1112, 309) to (1504, 645). Three earlier samples, including the fade, remain RGB-identical. Comparisons against the independently decoded donor cover all three eye poses and six mouth poses. The eye sample RGB mean absolute error is 2.09–2.75, compared with 50.45–65.52 in the matching baseline shots. The mouth error is 0.60–1.53, compared with 21.46–44.89. The private crops show the new face pixels meeting the existing body without the displaced low-resolution overlays.

Live certification covers this dialogue on English disc 1. Spanish and disc 2 live playback, other NC51 expressions, and package inclusion remain open. Private evidence and build response files are in local/work/codex-nc51-expression. Cleanup removed 215,060,536 bytes of regenerable checkpoint and image probes. The workspace measured 108,592,257,209 logical bytes with private assets and existing packages. The immutable development ZIP measured 6,315,009,692 bytes.
