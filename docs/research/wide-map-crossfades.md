# Map-to-dining-hall crossfade

The `map-room.state` path and `tests/chapter1-map-dining-hall.movie` were played for 900 frames in Original and Enhanced with the same patch-44 executable. Enhanced used Zoom at 2560×1440, the delivery's local resources, and the prepared v0.1.2 HD pack. Both runs produced the same game hash log and the nine native RGB captures were identical. Both recorded zero interpreted blocks.

| Displayed-output check | Capture frames | Result |
| --- | --- | --- |
| Map's outer strip against the previous map and the later floral background | 403, 405, 410, 425, 450, 464 | 854 samples per capture exactly matched map weights of 32, 32, 29, 22, 9, and 2 out of 32. |
| Dining-hall image with the stable scene's Zoom framing | 490, 500, 520 | 5,184 samples per capture matched image weights of 5, 10, and 20 out of 32. 2016×1008 image, scale 7. |
| Dining-hall right-side shadow with native RGB `505050` | 490, 500, 520 | 890 samples per capture matched the same image weights. The offset was 28 pixels. |
| Cursor against the top-left edge | 175 in a separate playback | The gradient kept occupying the width. This playback stayed on the map after pressing A with the cursor outside a room. |

The map's exterior uses its native border pixels and the floral background sampled at the same final position as the center. The exterior comparison uses columns on both sides of the native view. In some rows, the inner border's RGB shifts a few levels relative to frame 400 even at full map weight. That frame serves as the reference for the exterior. The native RGB equality test uses both runs of the same frame.

On the Saturn compositor, native samples 410, 425, and 450 verified the NBG3-over-NBG0 blend across the 71,255 pixels outside the cursor per sample. The window capture and the saved state may correspond to adjacent fade steps. That's why the table uses the weights measured directly in each window capture.

Private evidence in `local/work/map-floral-fade-final/`. The manifests keep the commands, profiles, inputs, and hashes. The executable has SHA-256 `de45af3dcb7713921c88bda56e71f611b1de4c738f3472ae28e52385c38a9800` and the game hash log has SHA-256 `49e4093e867bd76fe1137f69da9a0a48b0fd8c50837d44254347d9a89173a593`. Validation covers this dining-hall entrance and the gradient's occlusion by the map cursor. A room entrance with the cursor next to the edge at the fade's first frame is still missing.
