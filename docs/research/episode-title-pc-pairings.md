# PC counterparts for the first nine episode title cards

The PC files contain the same episode artwork as the prepared Saturn English cards. Each PC SPR has one 640×480 image at index 0 with Japanese lettering baked into its pixels. The Saturn English cards contain their lettering in their 320×224 image. The catalog marks the PC donors `excluded` under the existing [TCODEX episode card decision](saturn-bg-format.md#approved-episode-cards-only-tcodex).

The approved English or Spanish center and the generated surrounds supply the Enhanced title presentation. Original mode uses the Saturn title card. That runtime behavior and its prior replay evidence carry forward.

## Pair metadata

Both prepared English discs contain identical copies of each Saturn BIN below. The palette fingerprints match the existing episode-card keys. The Saturn cell digest covers the decoded layout's cell bytes and the PC digest covers the SPR file. The paths are under `/SAKURA1` on Saturn and `SAKURA1/TITLE` on PC.

| Episode | Saturn BIN / PC SPR | Saturn palette FNV-1a | Saturn cells SHA-256 | PC SPR SHA-256 |
| --- | --- | --- | --- | --- |
| 1 | `TITLE1.BIN` / `TITLE1.SPR` | `F84F4FA528984E99` | `5fe79824d9a335ad844d4c683e8d3264265f73b6f41cd95e193cf218e1f9967d` | `255a26d64b909c32bff268f2f95bc172241214a6311bc52e505c445c80c5c66e` |
| 2 | `TITLE2.BIN` / `TITLE2.SPR` | `FA7EA6C32652FF94` | `196081401175e8c5413f45b18b8ef9fd341eb6f8a5be67dcab90ceb6b9869001` | `8ed5058710b7c6bbfe52a865a065cbcb0da64ca6d0e9c0e916162787e98afaf9` |
| 3 | `TITLE3.BIN` / `TITLE3.SPR` | `B17571E06A3D73A2` | `78ae6a0234f7e8a3ffa516b9b8d0b0f12be61cfa7856a042fb1da61ada3c566e` | `eb82c449a53b31fdf711d5fbb2f455fc39603035844a85172039c213253a71a2` |
| 4 | `TITLE4.BIN` / `TITLE4.SPR` | `9C6046FA0FD22004` | `c9fe59e8d95d34bfc2482febd6df6eebf603aa214b44d054ad89e1118d6d9dda` | `bf38f6aea911aede259384a14e1a5300448a286620aef5e60dce0214d448cfe5` |
| 5 | `TITLE5.BIN` / `TITLE5.SPR` | `584308F5B85AE012` | `fd55f80e67c907b339f940339df72aeaef06b1bff93f2174db95063bf114b14c` | `863e65285cabcdf5e01f3c9ac9ec2373c59e04c480b3359726ba369108f10341` |
| 6 | `TITLE6.BIN` / `TITLE6.SPR` | `F530E4A419F666C8` | `c758a0b2298bd555c1e7bb52d2291153d61053ca499076c3d65e68100c635e8c` | `ecd09196e1ccb5dcbd4c8cfd1444b53bab8a0e95e5a8a166d74e67b3dbf61182` |
| 7 | `TITLE7.BIN` / `TITLE7.SPR` | `FDCEEE68F831DE9F` | `bc8d47159384fc3aa87f9cf906a497addaf684bd32154303c3fe82574eb3b64e` | `5f387b4708dd6049d104ed7eaadd4d62dacade1d50cc98cc9278e85b6245d8b2` |
| 8 | `TITLE8.BIN` / `TITLE8.SPR` | `ECA61ED3EEA4FABB` | `97a59df1aeb21ab59d05e61c27d095b22eecc47a85091e9ee113003ee244017a` | `0fbcad3303278bb073111dd4bf3472ab39645d6564a76b08049118d2fa6a0110` |
| 9 | `TITLE9.BIN` / `TITLE9.SPR` | `E8DCC5B80A127438` | `2990d2ebba1324af802a4a36054042edc91a68c296c679f7f3fdf0118a0b6fb0` | `4881d950d6361bfeb86107328ce30296743e8726efa6985001c175bb0db81b75` |

The offline audit read each Saturn file at its inventory LBA, checked the full file against the inventory SHA, and decoded it with `tools/decode_saturn_bg.py`. It decoded the PC files with `tools/decode_spred.py` and compared the cards side by side. The contact sheet and metadata receipt stay in `local/work/codex-th1/tp3a-title-ledger`.

This resolves the catalog choice for TITLE1–TITLE9. The regenerated progress totals retain the existing integrated count.
