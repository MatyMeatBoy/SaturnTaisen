# Chapter 10 native opening evidence

The muted strict-native cold replay selects Finale File 1 on prepared English Saturn disc 2 and reads `1001.BIN` at FAD 109871. It completes 12,000 guest frames with zero interpreted blocks and matches the archived cold route's terminal hash `81abc300bd25a789`.

| Disc 2 file in `/SAKURA1` | FAD | Native evidence |
| --- | --- | --- |
| `BG1213.BIN` | 120007 | The cold trace reads the file. All 41,472 viewport pixels match the native source at frame 7000. |
| `BG1160.BIN` | 119024 | Exact scene plate in the Chapter 10 relay at frame 5000, with 35,579 pixels attributable only to this source. |
| `BG4055.BIN` | 131357 | Exact foreground plate in the same frame, with 5,815 pixels attributable only to this source. |
| `1001FCE.BIN` | 109878 | All 147,360 source bytes are present at Low WRAM `00251000` in cold frame 7800. |

The retained muted relay starts from the chapter sweep's frame 9000 state and reports zero interpreted blocks across 5,000 guest frames. Its frame 4999 state holds BG1160 cells at VRAM `0x34840` and palette at CRAM `0x200`, and BG4055 cells at `0x4a040` and palette at `0xe00`. The next capture accounts for all 41,472 viewport pixels using those two plates, with 78 shared source positions. The chapter register marks the three displayed images observed and the exact atlas resident. Individual portrait display is outside this witness.

The [existing BG1285 witness](bg1285-pan.md) remains the separately verified HD draw. The opening boot's `SAKURA4` bank and `OPSAKURA.CPK` reads precede Finale selection. A separate public save route for the final battle reaches EVT19 (FAD 203643), MAP19 (220633), UNIT19 (244259), and WKL19 (246866), then reaches the untranslated master SH-2 block at `00204000`. Its trace establishes load order. The chapter's later display, tactical activity and complete HD exit test remain open.

Local evidence is under `local/work/codex-th10-attribution/`, `local/work/codex-tp2a/bank10-1001/`, and `local/work/codex-tw2-fullscreen-bbg/final-battle-relay/`.
