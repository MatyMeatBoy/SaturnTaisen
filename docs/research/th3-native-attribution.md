# Chapter 3 native attribution

These observations use the prepared English Saturn disc 1. The routes start through Continue with the preserved Chapter 3 saves and recorded controller input. CD play commands identify files by matching each starting frame address to its named ISO extent. The native picture checks compare captures to the decoded disc pixels in Saturn RGB555 precision.

## Displayed pictures

The current 0301 cold replay completed 15,000 strict-native guest frames with zero interpreted blocks. It repeated the named scene reads below.

| File | CD start FAD | Frame evidence |
| --- | ---: | --- |
| BG1198.BIN | 142883 | All 41,472 pixels of the native picture window matched the continued 0301 replay at its frame 1050. |
| TITLE3.BIN | 172232 | All 71,680 pixels of the captured native frame matched at continuation frame 1400. |
| BG1022.BIN | 139525 | The entire picture matched at continuation frames 2450, 2800, 3150, and 3500. |
| BG1008.BIN | 139203 | The entire picture matched at continuation frame 7000 and again in the separate extended replay. |

The 0301 cold run also reads BG4114.BIN at 155055. Its complete cells at VDP2 address 0x4A040 and palette at CRAM 0xE00 were resident alongside BG1198 in the archived frame-9000 state. Its displayed composition is open.

## Tactical resources

The Chapter 3 second-battle save loads EVT04 at 221874. The same trace reads MAP04 at 232311 and UNIT04 at 252233. FACE04 (222410), WKL04 (253487), and FIX04 (223008) were also read. The continued mission shows the tactical map and unit activity. At continuation frame 3850, Kanna is selected, with her unit HUD and movement grid visible. MAP04 and UNIT04 are the only map and unit resources read in that route.

The third-battle save reads EVT05 at 221912, MAP05 at 232479 and UNIT05 at 252273. Frame 6677 contains all 76,672 bytes of EVT05 at Low WRAM offset 0x4000 and all 81,420 bytes of UNIT05 at High WRAM offset 0xC0000. The tested 674,182-block local AOT binary stops after frame 6679 at untranslated master SH-2 entry 00204000, before a tactical frame. MAP05 has a read witness and UNIT05 has a residency witness. Both remain outside the observed tactical catalog rows. This result is specific to the tested local AOT binary and does not alter the earlier rebuilt sweep result in the [overlay registry](evt-overlay-registry.md).

## Body, portrait and film reads

The 0301 trace loads 0301FCE at 128883 and NC99 at 165862. The extended archived route also reads NC30 at 162269, NC31 at 163522 and NC95 at 165781. These reads establish resource use. Body frame ownership, portrait identities, and new HD draws remain open. NC30 and NC95 retain their existing Chapter 1 rows.

The two recognized cold film starts, FAD 405 and 166362, occur before the 0301 load. Their use as Chapter 3 story clips remains unobserved.

The native and tactical observations support a bounded attribution update. The complete chapter replay, per-frame HD exit test and package inclusion remain open. Private CD, state and pixel receipts are in local/work/codex-th3-attribution.
