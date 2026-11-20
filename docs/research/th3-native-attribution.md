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

The 0301 cold run also reads BG4114.BIN at 155055. Its complete cells at VDP2 address 0x4A040 and palette at CRAM 0xE00 were resident alongside BG1198 in the archived frame-9000 state. The archived frame-9200 witness now verifies its PC cut-out with the foreground sprite preserved in [patch 0219](chapter-one-cutout-followup.md).

## Tactical resources

The Chapter 3 second-battle save loads EVT04 at 221874. The same trace reads MAP04 at 232311 and UNIT04 at 252233. FACE04 (222410), WKL04 (253487), and FIX04 (223008) were also read. The continued mission shows the tactical map and unit activity. At continuation frame 3850, Kanna is selected, with her unit HUD and movement grid visible. MAP04 and UNIT04 are the only map and unit resources read in that route.

The third-battle save reads EVT05 at 221912, MAP05 at 232479 and UNIT05 at 252273. Frame 6677 contains all 76,672 bytes of EVT05 at Low WRAM offset 0x4000 and all 81,420 bytes of UNIT05 at High WRAM offset 0xC0000. The tested 674,182-block local AOT binary stops after frame 6679 at untranslated master SH-2 entry 00204000, before a tactical frame. MAP05 has a separate [interpreter ground witness](map05-pc-ground.md). UNIT05 has a residency witness. This result is specific to the tested local AOT binary and does not alter the earlier rebuilt sweep result in the [overlay registry](evt-overlay-registry.md).

## Body, portrait and film reads

The 0301 trace loads 0301FCE at 128883 and NC99 at 165862. The extended archived route also reads NC30 at 162269, NC31 at 163522 and NC95 at 165781. These reads establish resource use. NC30 and NC95 retain their existing Chapter 1 rows. The four exact portrait base draws are documented below.

The two recognized cold film starts, FAD 405 and 166362, occur before the 0301 load. Their use as Chapter 3 story clips remains unobserved.

The native and tactical observations support a bounded attribution update. The complete chapter replay, per-frame HD exit test and package inclusion remain open. Private CD, state and pixel receipts are in local/work/codex-th3-attribution.


## Witnessed 0301FCE portrait bases

Two original checkpoints in the strict 15,000-frame cold Continue replay
have exact active 40×48 VDP1 bases from the Chapter 3 narrative atlas.
In both states the full English `0301FCE.BIN` is resident at `0x00251000`
in low WRAM, with SHA-256
`543d7e3dbd7f83dfc1921ede23ba277d75fec70f2af0544b57487a8bdce41ca1`.
The `0301TBL` table is resident at `0x00224000`. The script cursor at
`0x0606851C` identifies record 10413 in the first state and 10430 in
the second.

| Cold snapshot | 0301TBL cursor | FCE identity | Active base FNV-1a | PC KAO.SPR index |
|---|---|---|---|---|
| `f9200.state` | `0x0022C728` | `0116` | `66FD59ED72423AA3` | 277 |
| `f14999.state` | `0x0022CA2E` | `0068` | `8C50320163B0ADBA` | 103 |

The two unmodified states were replayed for 12 guest frames in the
patch 0141 executable, muted and strict-native. Enhanced and Original
each ran with the exact single-portrait pack present and absent.
The shared bundled `KABE21` and `KABE20` backdrops respectively selected
the usual narrative layout. At pass 2 the Enhanced renderer selected
the corresponding prepared base (patch 0, density 2, white mix 0).
Every one of the 69,120 RGB pixels inside (404,1090) to (644,1378)
matches the prepared pixels in both 2560×1440 captures. All pixels
outside the rectangles match. Original screenshots match in full,
all four guest logs per state match, and all runs report zero
interpreted blocks.

| Identity | Snapshot SHA-256 | Matching 12-frame guest log SHA-256 | Prepared 2× PNG SHA-256 |
|---|---|---|---|
| `0116` | `7c4f183bb7c2f179b23c29370c33baada1af15b585da41e7571928ba491db879` | `917f94a58d14293831f2a2cf36271f0c9557cc7930cf9f5f86950d513e42ad9f` | `525dfeb8365f46537ec64b30c9460a09cd1d3d2af38705935a440f65a68b98b7` |
| `0068` | `90fe5f103fc03d71a6dc33b45be7ecfd554c3cf665c34140507e42279714a897` | `ed03037d52359e8938e4eed19da06b2a54626e2a5ac257e6c398f24de4c23d93` | `889f1b17c7b0b135a735a180d1ce77592a14799ae4edd609dd8afd503b2e804b` |

The registry marks these Chapter 3 occurrences as observed and
verified. The existing Chapter 1 association for `0068` remains inferred.
Animation strips and full chapter parity remain outside this sample.
The source snapshots are in `local/work/codex-th3-attribution/strict-0301`.
Test inputs, images and logs are in `local/work/codex-tp3c/th3-portraits`.

At block close the project measured 63,994,634,805 logical bytes, above
the 20 GB cap. The delivered development ZIP remains 6,315,009,692 bytes.


### Archived 0301 continuations

Two unmodified narrative continuations preserve the same complete
English `0301FCE.BIN` and `0301TBL` at the addresses above. The labels
identify the archived investigations. No battle inputs were replayed.
Each active VDP1 command uses an exact atlas base with no separate strip.

| Archived checkpoint | 0301TBL record and cursor | FCE identity | Active base FNV-1a | PC KAO.SPR index |
|---|---|---|---|---|
| `chapter3-bbg004-relay/latest.state` | 10412, `0x0022C6C4` | `00fe` | `C6ED133A60FCCD06` | 253 |
| `chapter3-bbg004-continued/latest.state` | 10459, `0x0022CF62` | `013d` | `7B92D69329B35A44` | 316 |

The same muted patch 0141 procedure replayed 12 input-free strict
frames in each of the four modes above. With the bundled KABE21
and KABE20 backgrounds respectively, pass 2 shows both exact PC bases.
Each 2560×1440 Enhanced sample matches all 69,120 expected prepared
pixels at (404,1090)–(644,1378), with zero changes outside.
Each set of four guest logs matches, all Original pixels match and
no blocks were interpreted.

| FCE identity | Unmodified snapshot SHA-256 | Matching guest log SHA-256 | Prepared 2× PNG SHA-256 |
|---|---|---|---|
| `00fe` | `cb14b9c4f3a7c05fa75bcd1c24521226bee2d52fee8691a0c77cc91b0ef6f103` | `3f9728473e60c0e1f1b95a3fc23362d09b7bc5c8af4dcfe13c574255fbd0e967` | `b03d958d5948ba8c94365ffe82d86cab96c852f855d355ae71b202c4a2814b14` |
| `013d` | `dde0f980cdba8ea9f8eca37fb284462f354e114f17d916c2a2500524247689b9` | `4c96a3614768d57fc77a2ba46739d0009dd05a4deb05c1658ed29573b676d2ce` | `b4d60a48443cee782e2ab9231ba97a5ea743593722f9ad5eafd68ed17df94dfa` |

The alternate `chapter3-bbg004-extended/latest.state` contains base
`0001` at record 10661. It has the renderer's exact full-white weight 32
and both paths show the same plate. The 96-frame input-free follow-up
moved to the backdrop layout without a witnessed exposed PC portrait.
This occurrence stays outside the verified rows. Private receipts and
the 1440p pairs are under `local/work/codex-tp3c/th3-portraits-extra`.

After this follow-up and cache cleanup, the project measured
64,945,697,743 logical bytes. The delivered development ZIP remains
6,315,009,692 bytes.
