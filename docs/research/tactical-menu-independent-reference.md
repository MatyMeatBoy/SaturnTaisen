# Independent reference for the tactical menu

Beetle Saturn v1.32.1 booted the English disc 1, loaded the chapter 1 file from internal RAM, and displayed the Move, Atk, and Def menus during the first battle's tutorial. In all three captures, the pop-up submenu covers part of the horizontal bar. The overlap appears on the translated disc under independent emulation.

## Verified captures

The table paths are relative to the private directory `local/work/worker-menu-oracle/cold-action-sequence`.

| Action | Frame | 330 × 224 PNG | Beetle Saturn state | PNG SHA-256 |
| --- | ---: | --- | --- | --- |
| Move | 14638 | `shot-014638.png` | `state-014638.bin` | `1f5df46eea67792a3d41d0353b44ef89bc01520f86e0464c0b88acb0c02835cc` |
| Atk, Special, and Normal | 15238 | `shot-015238.png` | `state-015238.bin` | `91f1ca0f1e294ca5cb805738cf11b886bb109f8fe8324a7a66725f0e295fa561` |
| Def, Heal, Defend, and Boost | 15388 | `shot-015388.png` | `end.state` | `ecf20d4b923f9b8c9ae28ef0d35e427ac23b42ae4743487d4308bb5977ae4ec7` |

All three cold-boot captures match byte-for-byte those from the trials with intermediate states.

## Local reproduction

```powershell
pwsh -File local/work/worker-menu-oracle/replay-menu.ps1
```

The private script invokes `local/work/mednafen-menu-oracle.py` with the prepared resources and saves the result to a new directory. Use `-Output` to change the destination. The evidence's `run.json` keeps the 284 events, 15,388 frames, and 30,776 controller-poll cycles. `loaded_state_sha256` is null on cold boot. Events start at zero and the captures count `retro_run` calls starting from one.

| Input | SHA-256 |
| --- | --- |
| Beetle Saturn v1.32.1 DLL | `8e62cd7a513c0c0f95c8a18856a68cd37d09a43df3a68b898325ed8e79e1aaa0` |
| English disc 1 data track | `5b19031460c87b4773ef2cbd70ef2170bef41c1117ec8cefe27b2af1309205ec` |
| Local internal-RAM seed, 32,768 bytes | `4aa58364c1eaa4d0cee384894861caa4cde1e426aa2e43da7aa6b4e94379bc5b` |

Control from the same title state for 160 frames remained on the title with no input. A Start press at index 20 for six frames opened Program. The core polled button 3 of port 0's controller twice per frame and received twelve active Start reads. The walkthrough waits for the title and uses Down for Continue and A to confirm Continue, File 1, and Yes.

The samples document the overlap at those three moments of the translated tutorial. Menu positions vary with the camera, the unit, and the action phase. This verification is limited to the observed layout of the submenu and its horizontal bar.

## Presentation fix in development

The Enhanced view recognizes the full set of the bar, five tabs, pop-up frame, options, and marker by hashes and geometry. The pop-up frame contains a 24-pixel ornamental extension that invades the bar. That extension is cropped and the remaining frame, options, and their highlight are shifted eight pixels upward. The native tab label and selection behavior are preserved.

The renderer rebuilds an auxiliary host framebuffer after completing the VDP1 list. It rejects the substitution if there are ambiguous commands, VRAM changes during drawing, content retained on the board, or differences outside the authorized zone. The region is only accepted if the finished native framebuffer first matches the uncorrected auxiliary raster. It does not write to the guest framebuffer; Original mode keeps its previous presentation.

In the local build, Move, Atk, Def, Info, and End were visually reviewed, Sumire with movement disabled and a position next to the map's edge. The playbacks compared 2,965 per-frame hashes between Original and Enhanced, with zero interpreted blocks. The `test_chapter1_widescreen_runtime.py` regression also checks that the center only changes within the submenu's rectangle and that the attack/camera path keeps its hashes. These results do not vouch for all menus in later chapters. The fix remains in development and is not in the previous ZIPs.
