# T105e runtime check, 2026-11-19 (patch 0090): FAILED to show the feature

Isolated build `local/build/rebuild-t105` (sources `local/deps/satrecomp-t105`). It was not finished: `port/frontend_sdl.cpp.obj`
(13:12) predated the patched source (13:16), so the first exe did not contain 0090. `ninja sakura.exe` rebuilt 13 objects
(vdp, state, vdp1, raster, cd, sh2, layers, hle_bios, machine, renderer, frontend and others) and relinked; the exe below is that one,
run from the private copy `local/build/sakura-t105run/t105.exe`.

Scenes: EVE0101 = `battle-entry-ref-3000.state` (the table's witness); EVE202 = `t30-chapter2-followup/cold-native/finish.state`
(the table's witness). Each run: strict native, hidden unthrottled window, `--pc-assets local/work/pc-cab/out-bg`,
presentation_mode=1, scene_view=1, pc_hd_backgrounds=0 (the T74 path only runs with that value), 1,200 frames, with and without
`SATRECOMP_NO_EVE_HD`, `SATRECOMP_BACKGROUND_STATS=1`.

| scene | frames | per-frame hashes with / without NO_EVE_HD | interpreted | `EVE picture:` lines | frame-1198 shot with / without |
| --- | --- | --- | --- | --- | --- |
| EVE0101 | 1200 / 1200 | identical | 0 / 0 | none | 6af81aac8606 / 6af81aac8606 |
| EVE202 | 1200 / 1200 | identical | 0 / 0 | none | 0dbb277cfb71 / 0dbb277cfb71 |

Result: guest parity holds (hashes identical, 0 interpreted), but the feature never fired: no `EVE picture:` line and no
difference in the window shot in either scene, so the PC picture was never drawn. Both scenes show the story inset with the
dialogue box. Not established which condition fails: the EVE code sits inside the branch that is entered only when
`uploadLayer` of the picture mix fails (the check listed as missing in the PR), the layer-5 palette fingerprint may differ from the
table's, or the layer is not static or has fewer than 12,000 visible pixels. Status stays "unverified in game"; the table rows
must not be treated as working. Local captures (not committed): `local/work/t105e-eve/*/shot.png`.
