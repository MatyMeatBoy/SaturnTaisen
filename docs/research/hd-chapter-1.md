# HD chapter 1 coverage report (TH1)

## Observations from the full cold route

The 511,978-frame Enhanced run for T03 reached Save Complete and the hanami epilogue on English disc 1. Its guest hashes and SRAM match the native replay. The local trace is `local/work/codex-th1/earned-route/hd/run.log` with SHA-256 `9b6907c1e2ac7331c90e8af3e2a6c0bb445bba9b8ef831ecae32aeda9e09e02a`. The executable SHA-256 starts with `d7db2813`. These observations cover the played route. The current catalog summary follows below.

### Scene pictures

The frontend logged 26 usable PC scene textures from active scene recognition. The table lists the first log callback between adjacent guest-frame markers. The callback proves the texture was selected and uploaded. The final rendered pixels need a separate witness.

For 25 donors, the catalog maps the PC filename and image index to one Saturn path. The native cell SHA and PC SHA agree between the archived map at `ca7df461` and the current catalog. The older runtime evidence for `BG2248/BG2251`, `BG1011/BG1012` and `BG1016/BG1017` also supports the scene identities in their shared-palette groups. The `BG2004.SPR` donor shares both palette and cells across the `BG2004–BG2010` family. Its row records the donor without attributing an individual BIN.

| Saturn disc 1 scene | PC donor in `SAKURA1/BG`, image 0 | Guest-frame bracket | Trace line |
| --- | --- | --- | --- |
| `/SAKURA1/BG1209.BIN` | `BG1209.SPR` | 8,760–8,820 | 174 |
| `/SAKURA1/BG2250.BIN` | `BG2250.SPR` | 10,440–10,500 | 243 |
| `/SAKURA1/BG2251.BIN` | `BG2251.SPR` | 12,180–12,240 | 450 |
| `/SAKURA1/BG2159.BIN` | `BG2159.SPR` | 20,100–20,160 | 1,199 |
| `/SAKURA1/BG1001.BIN` | `BG1001.SPR` | 21,840–21,900 | 1,299 |
| `/SAKURA1/BG1006.BIN` | `BG1006.SPR` | 29,280–29,340 | 2,175 |
| `/SAKURA1/BG1045.BIN` | `BG1045.SPR` | 30,180–30,240 | 2,229 |
| `/SAKURA1/BG1011.BIN` | `BG1011.SPR` | 37,200–37,260 | 2,954 |
| `/SAKURA1/BG1012.BIN` | `BG1012.SPR` | 37,560–37,620 | 3,703 |
| `/SAKURA1/BG1017.BIN` | `BG1017.SPR` | 50,160–50,220 | 31,508 |
| `/SAKURA1/BG1116.BIN` | `BG1116.SPR` | 57,000–57,060 | 32,112 |
| `/SAKURA1/BG1021.BIN` | `BG1021.SPR` | 59,760–59,820 | 32,985 |
| `/SAKURA1/BG2034.BIN` | `BG2034.SPR` | 61,020–61,080 | 33,474 |
| `/SAKURA1/BG1002.BIN` | `BG1002.SPR` | 74,340–74,400 | 34,400 |
| `/SAKURA1/BG1007.BIN` | `BG1007.SPR` | 77,400–77,460 | 34,744 |
| `/SAKURA1/BG1046.BIN` | `BG1046.SPR` | 94,560–94,620 | 36,237 |
| `/SAKURA1/BG1058.BIN` | `BG1058.SPR` | 105,360–105,420 | 39,942 |
| `/SAKURA1/BG1119.BIN` | `BG1119.SPR` | 118,260–118,320 | 40,441 |
| `/SAKURA1/BG1070.BIN` | `BG1070.SPR` | 142,860–142,920 | 52,924 |
| `/SAKURA1/BG2039.BIN` | `BG2039.SPR` | 143,040–143,100 | 52,945 |
| `/SAKURA1/BG1030.BIN` | `BG1030.SPR` | 228,540–228,600 | 92,090 |
| `/SAKURA1/BG2535.BIN` | `BG2535.SPR` | 232,920–232,980 | 92,341 |
| `/SAKURA1/BG2173.BIN` | `BG2173.SPR` | 239,220–239,280 | 93,118 |
| `/SAKURA1/BG1193.BIN` | `BG1193.SPR` | 253,260–253,320 | 94,364 |
| Shared native group | `BG2004.SPR` | 256,020–256,080 | 94,635 |
| `/SAKURA1/BG1216.BIN` | `BG1216.SPR` | 511,560–511,620 | 99,098 |


At the scheduled corridor capture, the 864×432 region at `(208,50)` in `earned-route/hd/corridor.png` reproduces the decoded PC `BG1119.SPR` image 0, resized bilinearly. The per-channel mean absolute RGB error is 0.102, 0.098 and 0.106. The nearest-neighbor Saturn decode comparison gives 25.255, 25.240 and 25.464. The PNG SHA-256 begins `256ed3cc`. The Saturn input was read from the disc inventory's LBA and checked against the inventory's full-file SHA before decoding. The hanami capture at the end of the replay shows the same result for `BG1216.SPR` image 0. The upper 864×24 strip at `(208,50)` lies above the character sprites. Its PC and native comparisons give 0.142, 0.127 and 0.132 versus 33.332, 32.233 and 33.295 respectively. The hanami PNG SHA-256 begins `b53c1e94`.

### Bodies and portraits

The VDP1 body bitmap recognizer resolved 19 NC package names. Each callback was reached after a matching presented body sprite and logged the available PC body texture. Face selection, occlusion and blend handling can keep some or all sprites native. This observation adds chapter attribution and leaves the body draw flags tied to their independent render evidence in [the body-format report](saturn-bg-format.md).

| Saturn disc 1 body in `/SAKURA1` | Guest-frame bracket | Trace line | PC parts / dimension runs |
| --- | --- | --- | --- |
| `NC3250.BIN` | 10,380–10,440 | 239 | 9 / 2 |
| `NC10.BIN` | 14,400–14,460 | 560 | 93 / 2 |
| `NC50.BIN` | 23,100–23,160 | 1,492 | 97 / 11 |
| `NC11.BIN` | 27,480–27,540 | 2,044 | 93 / 2 |
| `NC20.BIN` | 30,120–30,180 | 2,225 | 63 / 5 |
| `NC25.BIN` | 34,860–34,920 | 2,700 | 6 / 1 |
| `NC30.BIN` | 37,620–37,680 | 3,718 | 54 / 2 |
| `NC82.BIN` | 50,580–50,640 | 31,591 | 9 / 2 |
| `NC56.BIN` | 58,320–58,380 | 32,623 | 9 / 2 |
| `NC97.BIN` | 74,760–74,820 | 34,461 | 9 / 2 |
| `NC95.BIN` | 103,080–103,140 | 37,773 | 9 / 2 |
| `NC96.BIN` | 105,600–105,660 | 39,965 | 9 / 2 |
| `NC55.BIN` | 189,240–189,300 | 57,962 | 97 / 11 |
| `NC81.BIN` | 245,940–246,000 | 93,634 | 36 / 2 |
| `NC12.BIN` | 248,400–248,460 | 93,854 | 93 / 2 |
| `NC51.BIN` | 248,700–248,760 | 93,907 | 97 / 11 |
| `NC21.BIN` | 249,000–249,060 | 93,940 | 63 / 5 |
| `NC32.BIN` | 249,240–249,300 | 93,979 | 54 / 2 |
| `NC3004.BIN` | 255,900–255,960 | 94,622 | 9 / 2 |

Two follow-up 240-field Enhanced runs at 1440p separated body availability from expression coverage. In the `iris-correct-room-3000` replay, NC55 loaded the 97-part PC atlas. The matcher accepted PC eye parts 19 and 21, while a 24×24 mouth and a 56×32 eye retained the native pixels. In `prebattle-3000`, NC11 loaded its atlas, then rejected an intersecting sprite outside the recognized face strips. Subsequent full-size shots drew the PC body and selected the logged eye and mouth parts. The two replays completed with zero interpreted blocks. Trace and capture evidence is under `local/work/codex-ch1-body-triage/`.

Patch 0168 [registers five NC55 face textures](nc55-registered-faces.md) from the Iris-room replay to the authored PC eye and mouth positions. The 600-field A/B verified both observed closed mouths and three eye textures. Other expressions retain the existing fallback.

Patch 0171 [registers eleven NC50 face textures](nc50-registered-faces.md) from the lobby staircase replay, including three blink frames and the full six-part mouth cycle of the second expression. The native overlap remains visible in both builds.

Patch 0173 [preserves the eyes drawn on the NC25 PC body](nc25-baked-eyes.md) and places three witnessed mouths at the authored coordinates. The Chapter 1 replay retains the native NC25 blend.

Patch 0176 [registers the NC56 expression bank](nc56-registered-faces.md). Its first paired 1440p draw proof verifies the wink and both visible mouth poses at their authored coordinates. The earlier blink during the blend retains the native image.

Patch 0179 [registers the NC96 face bank](nc96-registered-faces.md) and removes the displaced hair and cheek rectangles seen with the previous placement. The late Chapter 1 replay selects all nine parts and retains the native blend.

Patch 0177 [registers the NC51 theater sortie expression](nc51-registered-faces.md). The 900-field English replay verifies all three eyes and six mouths at their authored coordinates. The earlier blend retains the native image.

Patch 0180 [registers the NC21 theater sortie expression](nc21-registered-faces.md). The 900-field English replay verifies all three eyes and six mouths at the authored positions. The earlier blend remains pixel-identical.

Patch 0182 [registers the NC32 theater sortie expression](nc32-registered-faces.md). The 1,000-field English replay verifies all three eyes and six mouths at the authored positions. The earlier blend remains pixel-identical.

Patch 0184 [registers the NC12 theater sortie expression](nc12-registered-faces.md). The 900-field English replay verifies all four eyes and six mouths at the authored positions. The earlier blend remains pixel-identical.

Patch 0169 [registers Sakura’s ten NC10 park face textures](nc10-park-faces.md) at their authored PC positions. The English Yoneda replay exercised the full four-eye and six-mouth set. The Spanish park replay verified the same four eyes and three of those mouths.

The NC11 overlap is the timed LIPS choice display over Sakura, rather than a missing face part. The first rejected command is at nominal (160,76), size 272×120, mode `00A0`, color `C500`, and texture fingerprint `4ADC5FF69258EF85`. It appears after the body in VDP1 draw order. The 1440p capture shows the translucent panel, timer, and ink over her face and shoulders. Any replacement must preserve the native overlay and its ordering, including the visible body through the panel. Simply accepting the intersecting sprite would erase or cover part of that display.

A strict replay of the frame-20 checkpoint captured the sprite plane and the separate VDP2 panel. In native rectangle (40,48)–(280,121), 6,316 of 7,811 distinct-color pixels with both planes present match `(panel × 21 + sprite × 11) / 32` with per-channel truncation. Another 168 match a sprite weight of 31, and 1,327 match no single ratio in that pair of source planes. The sprite plane already contains text, timer and chrome as well as the character, so a uniform overlay cannot recover their individual ownership. The local layer captures are under `local/work/codex-ch1-body-triage/save-prebattle-3000/`.

A priority trace on the same checkpoint recorded 6,341 pixels with the panel above the sprite and the exact 11/32 sprite weight. The other 1,495 pixels with both planes present had the sprite above the panel without color calculation. The diagnostic capture matches the uninstrumented RGB exactly. This separates actual panel blends from coincidental matches to the weight of 31. The remaining requirement is VDP1 command ownership within the sprite plane, so the remaster can replace body and expression samples while retaining the glyph, timer and frame writes.

An isolated VDP1 write-owner probe then distinguished the NC11 body, eye, and mouth commands from the later UI. On both newly drawn frames after restore, those three commands own exactly 6,341 samples in the panel rectangle. The other 1,495 samples belong to UI commands. Reconstructing the owned body pixels with the 11/32 sprite weight and preserving the UI pixels verbatim reproduces all 7,836 samples. The restored framebuffer initially has no owner history, so a replacement must wait for new draws or preserve the native first frame. All three diagnostic frames matched the uninstrumented RGB exactly. The probe and raw owner maps are private at `local/work/codex-ch1-body-triage/layer-priority-probe/`.

An offline substitution at 7× used the PC NC11 body wherever the native body command owned the pixel and the donor was fully opaque. It reapplied the witnessed panel color ratio independently for every subpixel. The proof changed 207,766 body subpixels and preserved all 1,495 UI-owned tiles exactly. Eyes, mouth, silhouette edges, and the normal runtime path remain separate validation work. The private output is `nc11-panel-body-ownership-proof.png` in the same probe folder.

A private SDL runtime trial enabled the replacement only on the witnessed NC11 body, palette, and 11/32 transfer. In the timed-choice replay at 1440p it changed 202,645 subpixels in each of frames 20 and 35, all inside native body-owned tiles. The post-choice frame 120 was RGB-identical, and all 240 guest hashes matched with zero interpreted blocks. The trial still uses diagnostic capture and requires a renderer-owned lifetime, bounded capture and additional route controls before it can ship. Logs and paired PNGs are private under `local/work/codex-ch1-body-triage/lips-runtime-*`.

Patch 0172 replaces the captured NC11 body in the confirmed timed choice, including both uncovered body pixels and the 11/32 panel transfer. Its per-buffer VDP1 ownership is confined to the native 168×144 body rectangle and discarded on a state restore or invalidated framebuffer. A prepared texture is cached by blend data and integer viewport scale. Native face parts, UI writes, and any unwitnessed blend modes stay in their normal composition. The draw requires the confirmed Saturn body hash and PC donor fingerprint.

At 1440p, frames 20 and 35 changed 417,252 subpixels each, all traced to the native body writer. The 1080p pair also changed only the body area. Frame 120 after the choice matched at both sizes. All 240 guest hashes matched within each pair, including Original, missing, and altered donor controls. The three controls also matched their nine complete sampled RGB frames. This verifies the English Chapter 1 hallway choice. Other LIPS layouts and eye and mouth replacement during the overlay remain open. The build and controls are private under `local/work/codex-ch1-body-triage/lips-owned/`.


The trace also named 62 portrait IDs after successful replacement texture upload. Each row preserves its first appearance bracket and the trace line. The separately observed viewport and blend traces can be used for renderer review.

| Portrait | Guest-frame bracket | Trace line | Portrait | Guest-frame bracket | Trace line |
| --- | --- | --- | --- | --- | --- |
| `0001` | 58,500–58,560 | 32,721 | `0092` | 25,440–25,500 | 1,758 |
| `0002` | 57,420–57,480 | 32,342 | `0093` | 58,320–58,380 | 32,644 |
| `0003` | 61,860–61,920 | 33,822 | `0094` | 57,720–57,780 | 32,453 |
| `0004` | 57,600–57,660 | 32,380 | `0095` | 26,520–26,580 | 1,926 |
| `0005` | 121,500–121,560 | 40,664 | `0096` | 57,120–57,180 | 32,162 |
| `0006` | 57,180–57,240 | 32,198 | `009b` | 255,420–255,480 | 94,574 |
| `0007` | 58,260–58,320 | 32,603 | `009c` | 251,580–251,640 | 94,183 |
| `0009` | 234,840–234,900 | 92,574 | `00e2` | 54,900–54,960 | 31,934 |
| `000a` | 247,440–247,500 | 93,786 | `00e3` | 126,300–126,360 | 41,856 |
| `000b` | 249,840–249,900 | 94,050 | `00e4` | 50,580–50,640 | 31,614 |
| `000f` | 245,640–245,700 | 93,610 | `00e5` | 52,680–52,740 | 31,791 |
| `0013` | 16,260–16,320 | 749 | `00e9` | 245,520–245,580 | 93,574 |
| `0014` | 14,400–14,460 | 564 | `0134` | 74,580–74,640 | 34,438 |
| `0015` | 15,180–15,240 | 652 | `0136` | 74,940–75,000 | 34,520 |
| `0016` | 243,120–243,180 | 93,393 | `013a` | 103,380–103,440 | 38,141 |
| `0017` | 57,660–57,720 | 32,415 | `013c` | 104,700–104,760 | 39,592 |
| `0018` | 57,000–57,060 | 32,113 | `0142` | 105,660–105,720 | 39,987 |
| `001a` | 138,420–138,480 | 52,419 | `0148` | 10,620–10,680 | 289 |
| `001c` | 248,400–248,460 | 93,876 | `0149` | 10,140–10,200 | 199 |
| `001d` | 256,260–256,320 | 94,673 | `015e` | 61,020–61,080 | 33,475 |
| `0023` | 251,880–251,940 | 94,230 | `015f` | 61,620–61,680 | 33,718 |
| `0040` | 30,480–30,540 | 2,273 | `0161` | 61,140–61,200 | 33,544 |
| `0041` | 30,840–30,900 | 2,352 | `0163` | 60,540–60,600 | 33,298 |
| `0043` | 32,700–32,760 | 2,569 | `0166` | 60,600–60,660 | 33,333 |
| `0045` | 32,340–32,400 | 2,525 | `0168` | 72,120–72,180 | 34,163 |
| `0047` | 34,920–34,980 | 2,722 | `0176` | 12,540–12,600 | 458 |
| `004a` | 249,000–249,060 | 93,949 | `0177` | 10,440–10,500 | 246 |
| `0064` | 38,280–38,340 | 5,192 | `0179` | 31,980–32,040 | 2,481 |
| `0065` | 37,800–37,860 | 4,114 | `017a` | 15,720–15,780 | 703 |
| `006e` | 245,280–245,340 | 93,536 | `017b` | 16,800–16,860 | 803 |
| `0091` | 23,100–23,160 | 1,496 | `017c` | 39,300–39,360 | 7,260 |


### FILM and tactical witnesses

The CD trace names each start and the successful PC open. The exact guest frame below is the audio-source switch. The start FAD is one or two sectors after the catalog FAD. The archive offset is verified against the disc 1 inventory. The matched cuts have no alternate-cut flag.

| PC clip | `/SAKURA4` byte offset | Archive FAD | Played FAD | Audio guest frame | Attribution |
| --- | --- | --- | --- | --- | --- |
| `MOVIE000` | 0 | 405 | 407 | 591 | Shared boot sequence |
| `MOVIE001` | 23,695,360 | 11,975 | 11,977 | 2,962 | Chapter 1 |
| `MOVIE002` | 45,410,304 | 22,578 | 22,579 | 230,371 | Chapter 1 |
| `MOVIE003` | 56,039,424 | 27,768 | 27,769 | 244,189 | Chapter 1 |


The full replay shows the first tactical battle and postbattle SRAM menu. The scene trace does not enumerate individual tactical sprites or HUD assets. Exact stage ground replacement retains [its separate visual evidence](stage01-pc-ground.md). The [Satan inset](eve0116-tactical-inset.md) and [victory pose](eve0118-tactical-inset.md) have their own targeted checkpoints and comparisons.

Alt routes, exact attribution of the shared `BG200x` family, and untraced tactical, menu and body rendering outcomes remain open. The paired stage and inset evidence covers its specified runtime. This evidence does not validate a release package.

Source: `config/hd-chapter-coverage.json` (chapter 1, disc 1), cross-checked with `config/hd-scene-bg-map.json`, `hd-scene-bg-review.json`, `hd-body-map.json`, `hd-item-map.json`, `film-fad-map.json`, `docs/PENDIENTES.md`. The stage ground has [its own replay evidence](stage01-pc-ground.md). The chapter-wide asset inventory remains open. The cold replay result and the actual route observations are recorded above.

## Status per class (refreshed to the `main` register)

| Class | Register | Notes |
|---|---|---|
| Scene pictures (34) | 33 `hd`, 1 `excluded` (`TITLE1`) | `IC01` (to ICATCH IC0100) and `EVE0101` (to BBG001) are `hd`: [IC01](ic01-hd-intermission.md), [EVE0101](eve0101-registered-inset.md) |
| NC bodies | 19 `hd` | |
| Portraits | 129 `hd` | `00a1` is `hd` (PC index 160, strips exchanged, patch 0141, [natural Command Room replay](portrait-animation-coverage.md#iris-00a1-command-room-portrait)). `0169` is `hd` with the PC emblem chosen by the owner ([Spanish letter scene](portrait-animation-coverage.md#pc-emblem-0169-in-the-letter-scene)). The 6 FCE atlas rows (`0100FCE`, `0101FCE`, `0102FCE`, `0103FCE`, `0108FCE`, `0109FCE`) are resolved |
| FILM | 3 `hd` + 1 `bounded` | MOVIE004 is an alternate cut that keeps Saturn audio by design ([bounded spans](bounded-film-video-spans.md#movie004)) |
| Tactical maps | 1 `hd` (`MAP01`) | |
| Tactical units, menus/HUD | no data | |

No chapter 1 row is `unknown` or `paired-not-wired`. The initial inventory
(2026-11-19) that listed `IC01`, `EVE0101`, `00a1`, `0169` and the atlas
files as open is superseded by the register above; the first-pass notes
about the unassigned pool no longer describe chapter 1.

## Still open for chapter 1

- Repeat the full Chapter 1 cold route on the current release candidate. The historical cold route above already reached the hanami epilogue.
- Inclusion in the release package (packaging gate, TS12).
- Other occurrences of the `0169` emblem: only the Spanish letter scene is witnessed.
- `00a1` evidence covers only the English disc 1 route; disc 2 and Chapter 7 are outside it.
- Tactical units and menus/HUD have no chapter 1 data in the register.

## Isolated donor witnesses for Iris's room and the Chapter 9 opening

The English disc 1 Iris room checkpoint and the English disc 2 Chapter 9 opening checkpoint were replayed through patch 0217. Each case ran two 56-field strict-native profiles differing only in the availability of one PC file. All paired guest hashes and final SRAM matched. The runtime reported zero interpreted blocks.

| PC file | Natural checkpoint | Changed pixels per 2560 × 1440 capture |
| --- | --- | ---: |
| BG1101.SPR | Iris room, disc 1 | 1,250,234 |
| BG2018.SPR | Chapter 9 opening, disc 2 | 803,557–803,773 |

All eight comparisons changed only pixels in the (272,29)–(2288,1037) scene viewport. Every changed pixel came from the independently decoded native background and matched the bilinearly scaled PC decode within two RGB levels. The donor for the Chapter 9 opening has the shared native BG2017/BG2018 identity. The retained draw proves the PC file and the shared art. File-specific attribution is being checked separately against the CD read trace.

Private replay and pixel receipts are under `local/work/codex-th1/two-room-witnesses`. This evidence uses the existing runtime.
