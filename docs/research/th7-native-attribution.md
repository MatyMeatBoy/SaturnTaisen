# Chapter 7 native picture and tactical residency evidence

The prepared English Saturn disc 1 bank 7 replay enters the 0700 family. The archived strict native relays below start from, or descend from, the preserved frame 11999 save and matching backup. The Chapter 7 catalog records three pictures by display and two tactical files by byte-exact residence.

| Disc 1 file | FAD | Replay witness |
| --- | --- | --- |
| `/SAKURA1/BG1267.BIN` | 144131 | `episode7-relay` frame 5850 |
| `/SAKURA1/BG1268.BIN` | 144154 | `episode7-fast` frames 6000, 7000 and 8000 |
| `/SAKURA1/BG2080.BIN` | 147854 | `medical-dialogue` frames 900, 1800, 2700 and 3600 |

Each source image is the unique disc 1 fingerprint for all 41,472 pixels in the native viewport at x16, y8, width 288, height 144. Comparison uses the original Saturn 5-bit channel values. The fast and relay logs record reads at 144131 and 144154. The preceding `episode7-continue` log records 147854; the medical relay inherits the loaded picture. The 8,500-, 6,200- and 3,600-frame relays each report zero interpreted blocks. The catalog retains their existing PC donor entries. This test measures the original picture only.

## Opening film

The cold, muted strict-native replay selects the visible Episode 7 File 1 and reads `0700.BIN` at FAD 131293. It then reads the `/SAKURA4` stream header at FAD 80874 and its payload at FAD 80875. Native frames 7000, 8000 and 9000 display the sequence. The existing film map identifies the stream at byte offset 164800512 as the `MOVIE019` counterpart. The replay completes 12,000 frames, reports zero interpreted blocks and ends at guest hash `bcc8f66ccbc73aee`, matching the archived cold route.

The same replay reads `TITLE7.BIN`, `BG1266.BIN`, `BG2014.BIN`, `BG2019.BIN` and `NC3014.BIN`. The sampled frames do not isolate those resources, so this pass records their reads without a display claim. The earlier `0700FCE.BIN` atlas entry retains its existing residency classification.

## First tactical overlay boundary

Selecting File 1 from the original `save7.bkr` labels the save Episode 7 at frame 3000. The strict replay reads the tactical resources below and stops after 6,668 frames on the missing master SH-2 entry at `00204000`. Its saved frame 6667 contains the following complete byte-for-byte file copies.

| Disc 1 file in `/SAKURA2` | FAD | Bytes | Native address |
| --- | --- | --- | --- |
| `EVT10.BIN` | 222101 | 75,508 | Low WRAM `00204000` |
| `WKL10.BIN` | 255134 | 529,264 | Low WRAM `0021f800` |
| `UNIT10.BIN` | 252473 | 81,420 | High WRAM `060c0000` |
| `FACE10.BIN` | 222685 | 92,740 | Low WRAM `002b3800` |
| `M10MES.BIN` | 231556 | 10,490 | Low WRAM `002dd800` |

`WKL10.BIN` and `UNIT10.BIN` enter the catalog as resident. The trace also reads `MAP10.BIN` at FAD 233232. No full copy was found in either WRAM bank and the strict replay has no map activity evidence. `FACE10.BIN` residence establishes a loaded bank with no individual portrait attribution in this test.

The strict chapter exit, displayed tactical map and units, and the proposed later EVT22/EVE207 route remain open. The archived relay, cold save, screenshots and memory state are local under `local/work/codex-eve207/`; the disc comparison receipt is under `local/work/codex-th7-attribution/`.
