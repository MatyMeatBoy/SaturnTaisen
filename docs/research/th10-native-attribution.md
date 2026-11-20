# Chapter 10 native opening evidence

The muted strict-native cold replay selects Finale File 1 on prepared English Saturn disc 2 and reads `1001.BIN` at FAD 109871. It completes 12,000 guest frames with zero interpreted blocks and matches the archived cold route's terminal hash `81abc300bd25a789`.

| Disc 2 file in `/SAKURA1` | FAD | Native evidence |
| --- | --- | --- |
| `BG1213.BIN` | 120007 | The cold trace reads the file. All 41,472 viewport pixels match the native source at frame 7000. |
| `BG1160.BIN` | 119024 | Exact scene plate in the Chapter 10 relay at frame 5000, with 35,579 pixels attributable only to this source. |
| `BG4055.BIN` | 131357 | Exact foreground plate in the same frame, with 5,815 pixels attributable only to this source. |
| `1001FCE.BIN` | 109878 | All 147,360 source bytes are present at Low WRAM `00251000` in cold frame 7800. |

The retained muted relay starts from the chapter sweep's frame 9000 state and reports zero interpreted blocks across 5,000 guest frames. Its frame 4999 state holds BG1160 cells at VRAM `0x34840` and palette at CRAM `0x200`, and BG4055 cells at `0x4a040` and palette at `0xe00`. The next capture accounts for all 41,472 viewport pixels using those two plates, with 78 shared source positions. The chapter register marks the three displayed images observed and the exact atlas resident. Individual portrait display is outside this witness.

The [existing BG1285 witness](bg1285-pan.md) remains the separately verified HD draw. The opening boot's `SAKURA4` bank and `OPSAKURA.CPK` reads precede Finale selection. A separate public save route for the final battle reaches EVT19 (FAD 203643), MAP19 (220633), UNIT19 (244259), and WKL19 (246866), then reaches the untranslated master SH-2 block at `00204000`. Its trace establishes load order. A separate [live ground review](tactical-pairing.md#live-map10-and-map19-ground-review) shows MAP19 with units and records why it retains the native ground. The complete HD exit test remains open.

Local evidence is under `local/work/codex-th10-attribution/`, `local/work/codex-tp2a/bank10-1001/`, and `local/work/codex-tw2-fullscreen-bbg/final-battle-relay/`.

## BG1160 HD draw

The 0188 runtime replays the final 2,000 fields of the same English disc 2
Chapter 10 relay at 2560×1440. The starting checkpoint is the retained
field-3000 state. The runtime reads BG1160 at FAD 119024 and the foreground
BG4055 at FAD 131357. Installing only the PC `BG1160.SPR` changes the
background inside the existing Zoom rectangle (272,29)–(2288,1037).
Both runs match all 2,000
archived guest hashes and final SRAM, with zero interpreted blocks.

In each of the two stable samples at replay fields 1,900 and 1,994, all
1,743,327 changed pixels agree within two RGB levels with the independently
decoded PC background. All 284,935 uniquely identified Saturn BG4055
foreground pixels remain pixel-exact. The seven preceding sampled
captures match in full. This verifies BG1160 on disc 2 for this occurrence.
The private repro is under `local/work/codex-th1/bg1160-live/`.

## Verified scene draws on the archived ending route

The English disc-2 ending route starts with the public Mednafen
`GameCompleted.bkr` seed and the archived `ending-cold-native/input.movie`.
A fresh strict-native replay matched all 20,164 archived guest hashes.
The checkpoints used below come from the same route.

| Disc 2 Saturn scene | FAD | Checkpoint field | PC donor | A/B capture offsets | RGB changes per capture |
| --- | ---: | ---: | --- | --- | --- |
| `/SAKURA1/BG2287.BIN` | 128721 | 10799 | `SAKURA1/BG/BG2287.SPR` | 520, 535, 548, 575 | 2,031,091 each |
| `/SAKURA1/BG2288.BIN` | 128744 | 11399 | `SAKURA1/BG/BG2288.SPR` | 8, 16, 30, 50 | 0 / 0 / 2,028,748 / 2,028,748 |
| `/SAKURA1/BG2162.BIN` | 126314 | 18599 | `SAKURA1/BG/BG2162.SPR` | 8, 16, 30, 50 | 1,958,477 each |

Each A/B replay used D3D11 at 2560×1440 and the original route input suffix
for its checkpoint. Only the named PC donor differed between arms. A/B
and the archive match across all 694 guest fields, terminal SRAM matches
within each pair, and all runs report zero interpreted blocks. Runtime
SHA-256 was
`02AC1AAAB7D0CBDFEA8A3E1950D1583B7FEBF765AC5D0B67319678BC93C0E89C`
(cumulative 0213).

All changed pixels fell within the existing Zoom rectangle at (272, 29) to
(2288, 1037). Each changed control pixel matched the independently decoded
Saturn plate after RGB555 quantization and nearest scaling. Each corresponding
donor pixel matched the independently decoded bilinear PC plate within two
levels per channel. The first two BG2288 captures were pixel-identical to the
control. The BG2287 proof uses stable samples before the dissolve. A separate
test during the dissolve failed the source pixel comparison and is excluded
from the verification.

Late route captures from fields 19,920 through 20,160 had matches for the
closely related BG2257 and BG2258 plates in portions of the native image.
Independent A/B runs beginning at field 20,039 and supplying only one donor
at a time yielded no changed pixels at fields 8, 16, 30 or 50. These
two entries remain unverified. Local receipts and exact restart state hashes
are under `local/work/codex-witness-441-review/hud/chapter10-plates/`.
The verification covers the three named scene draws. The chapter exit and
release package gates remain open.

## Verified 1001 monitor draws

The English disc-2 Finale File 1 route loads the 1001 narrative.
The archived `strict-1001/f11999.state` checkpoint and its SRAM
supply the starting state. A strict continuation with ordinary confirm
inputs reaches the briefing monitor and the meeting that follows.
A short replay matches the first 2,420 guest fields of the 15,000-field
continuation and preserves field 1459 for the paired runs below.

| Physical PC donor | Saturn FAD | Replay fields | Positive capture offsets | Changed RGB pixels per positive capture |
| --- | ---: | ---: | --- | ---: |
| `BG2244.SPR` | 127668 | 56 | 8, 16, 30 | 1,911,152 |
| `BG2245.SPR` | 127691 | 230 | 74, 92, 116, 148, 184 | 1,959,065 |
| `BG2246.SPR` | 127714 | 390 | 240, 260, 280, 300, 320, 350, 375 | 2,006,665 |

The paired tests replay the original inputs after field 1459 at 2560×1440
with D3D11. Each pair differs only by the listed PC donor. The cumulative
0213 executable SHA-256 is
`02AC1AAAB7D0CBDFEA8A3E1950D1583B7FEBF765AC5D0B67319678BC93C0E89C`.
All 676 strict guest fields match both arms and the continuous reference.
Each terminal SRAM pair matches. No interpreted blocks run.

All 15 stable positive samples change only pixels inside the existing
Zoom rectangle (272, 29)–(2288, 1037). The control at each changed pixel
matches the independent Saturn decode after RGB555 quantization and
nearest scaling. The PC replacement matches the independently decoded
bilinear sample within two RGB levels per channel. Five samples outside
the selected donor phases match the native control in full. BG2245
offsets 52 and 60 include the mixed native image while the display
transitions from BG2244. The PC donor changes those samples, and the
mixed controls fail the single-source Saturn oracle. Those two samples
remain outside the verified stable windows.

The runtime identifies the three distinct cell keys under their shared
palette. Private receipts and captures are under
`local/work/codex-witness-441-review/hud/finale-monitor-plates/`,
`finale-monitor-trim/` and `finale-monitor-late/`. These witnesses
cover the stable monitor draws. The mixed transition, chapter exit
and package gates remain open.
