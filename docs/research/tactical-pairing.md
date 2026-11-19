# Tactical mode pairing (TS11): maps, units, items

Offline work, no runtime build. The 542 PC SPR candidates of tactical mode are 177 `SAKURA2/MAP`, 291 `SAKURA2/UNIT`, 57 `SAKURA1/ITEM` and 17 `SAKURA1/MAP` (strategy-map screens). This note records the evidence per block; the data is names, sizes and hashes only (no pixels). Regenerate with `tools/tactical_pairing.py`; tests are `tests/test_tactical_pairing.py` (synthetic, no game data).

Status words: `paired` (firm evidence), `ambiguous` (several candidates), `no counterpart` (nothing established or nothing decodable on the Saturn side). A paired map is `paired-not-wired` in the register until the runtime has a fingerprint and a sampler for it.

## Maps (block 1)

Data: `config/hd-tactical-map-pairs.json`. Command:

```powershell
python tools/tactical_pairing.py maps --pc <folder with the extracted PC SAKURA1/SAKURA2> --iso1 "local/prepared/disc1/Track 01.iso" --iso2 "local/prepared/disc2/Track 01.iso" --out config/hd-tactical-map-pairs.json
```

Method: every Saturn `/SAKURA2/MAPnn.BIN` (13 files on disc 1, 14 on disc 2, 27 in total) is compared by SHA-256 with `SAKURA2/MAP/MAPnn/MAPnn.BIN` of the PC edition. The two editions ship the same terrain file, so this is stronger than a luminance signature: all 27 are byte-identical. The PC `MAPnn.TAB` (a text file) then names the ground SPR. It is `Ground:` for 11 maps and `UnderGround:` for 16 (MAP02, MAP06 and MAP21 among them); the existing verified grounds (MAP01, 02, 04, 06, 21) were identified the same way. The luminance route of `match_hd_all.py` is not used here: it needs the Saturn ground rendered from the VDP2 page, which is what the runtime already does for the verified maps.

Result: 27 of 27 Saturn maps are `paired` to a PC ground SPR. Five are already `hd` in the runtime (MAP01 patch 0102, MAP02, MAP04, MAP06, MAP21; the disc 2 copy of MAP01 is the same file). The other 22 move from `unknown` to `paired-not-wired` in `config/hd-chapter-coverage.json` (generator change in `tools/hd_chapter_coverage.py`). Not paired: PC `MAP27` has a BIN and a TAB (it reuses the MAP06 files) but no Saturn file.

Two ground layouts matter for the runtime:

- single image (2048x2048, 2048x1280, 1392x960 ...): the Stage01/Stage02 sampler design applies;
- mosaic of equal tiles (MAP03 626 tiles of 64x64, MAP04 629 tiles, MAP05 46 tiles of 256x256, MAP20 96 tiles of 128x128; MAP23 holds four 1392x1232 images): an assembler is needed first. MAP04 is already `hd`; its assembler is in the patch that draws it.

What was not verified: no map beyond the five was drawn or compared in game; the pattern-name fingerprint of each unwired map is not recorded (it needs the disc and a run to the map); the ground cell alignment of the unwired maps is not checked. Wiring one map at a time is the open row TW6b.
