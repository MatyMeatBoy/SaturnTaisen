# Maria NC32 face registration in Chapter 1

Patch 0182 registers the three eye poses and six mouth poses used in Maria's Chapter 1 theater sortie introduction. Enhanced places the face parts at their authored PC positions. The existing matcher and native fallback handle other expressions.

## Asset and placement evidence

The full cold Chapter 1 route recognizes NC32 between fields 249,240 and 249,300. The compact disc 1 replay starts after Iris's introduction, advances through Sumire, then lets Maria's voiced line play. The baseline keeps the nine face poses as native overlays on the HD body.

The native 144 × 144 body starts at offset 1,552 in /SAKURA1/NC32.BIN and has FNV-1a 2E5433ACBE9D8FBE. The full native file has FNV-1a E9C38BD90B69ADD7 in the prepared English and Spanish editions of both discs. The PC donor SAKURA1/NC/NC32.SPR has FNV-1a D3972C2B4121E5FD and uses 304 × 320 body ordinal 2. The registration requires both full-file fingerprints.

The nine native fingerprints match NC30 group 1. The decoded PC source pixels also match the corresponding NC30 ordinals. NC32 table 7 places the body at (0, 0). Tables 8 and 9 place group 1 eyes at (112, 65) and mouths at (112, 105).

| Native offset | Texture FNV-1a | Dimensions | PC ordinal |
| --- | --- | --- | --- |
| 30,736 | E0F4C969ABFD88B0 | 32 × 16 | 9 |
| 31,248 | CB187D90C06DCE92 | 32 × 16 | 10 |
| 31,760 | CAA0D6E0E55A0EAA | 32 × 16 | 11 |
| 32,272 | 3C18961EC9A8F8EE | 24 × 16 | 36 |
| 32,656 | 2DBF4F875FFC6075 | 24 × 16 | 37 |
| 33,040 | E9302D1A1734BDBC | 24 × 16 | 38 |
| 33,424 | 79B03685BC82D8D2 | 24 × 16 | 39 |
| 33,808 | 0F39D30A1DFD13CF | 24 × 16 | 40 |
| 34,192 | 77DCA7E0D07E3F85 | 24 × 16 | 41 |

## Replay results

The exact 0181 and 0182 builds match all 1,000 guest hashes, decoded PCM, and final backup RAM in each of the Enhanced, Original, missing-donor and altered-donor pairs. All runs report zero interpreted blocks. The altered donor changes one byte in SPRED table 12 outside the image decoder. All 18 sampled Original and donor-control screenshots are RGB-identical at 2560 × 1440.

The Enhanced replay exercises all nine parts. Fifteen changed screenshots differ only within (1096, 234) to (1410, 533), the envelope of the authored face artwork. Four earlier samples, including the fade, match exactly. The independent PC decode confirms all three eye and six mouth poses at their authored positions. Mean absolute RGB error on the eye samples falls to 2.21–2.45 from 33.51–35.99 and on the mouth samples to 0.80–1.55 from 17.19–32.57.

Live evidence covers this English disc 1 scene. Spanish and disc 2 live playback, other NC32 expressions, and package inclusion remain open. Private evidence and build files are in local/work/codex-nc32-expression. Cleanup removed 458,755,329 bytes of regenerable checkpoints and captures. The project measured 113,711,804,509 logical bytes including existing private assets and packages. The immutable development ZIP measured 6,315,009,692 bytes.
