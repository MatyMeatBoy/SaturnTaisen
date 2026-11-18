# PC characters for the Saturn HD mod

The user confirmed that girl sprites, other characters, portraits, and expressions should also be adapted. Saturn priority continues; this does not integrate PC-platform execution or translation. Text enhancement remains a separate option.

## Verified inventory

`tools/audit_hd_characters.py` compares the proprietary extracted resources against both prepared Saturn ISOs. It found 147 PC NC character files, with 3,596 non-empty images. All 147 names have native candidates. The inventory records file hashes, dimensions, formats, and per-disc locations; it does not include pixels or original data. Name matching does not demonstrate matching indices, expressions, or geometry.

Native inspection via `tests/inspect_pc_sprites.cpp` uses the runtime's own DecodePcSprites: all 147 files and 3,596 images decoded without errors, totaling 42,423,793 pixels. All observed NC image records use 0x15 (compressed RGB555). KAO.SPR (394 images) and KAO_P.SPR (25) were also inventoried; their decoding also passed with the runtime's native decoder. That is 4,015 verified images in total; their narrative correspondence is still pending.

There are 11,158,719 pure-green pixels in the NC output, and the current decoder does not assign transparency to these direct images. This exposes pending mask/compositing work: simply drawing them on top is not enough. Not all green is declared transparent, because a blanket rule could remove valid colors.

## Next integration

1. Identify the native images and compositing tables for a reproducible scene. Do not infer the native NC format from a header that merely resembles a size. An exploratory attempt applying LZSS SPRED directly to Saturn NC does not consume the full resource and is not considered a valid decoder.
2. Verify bodies, poses, eyes, mouths, and portraits with their anchors, masks, flips, and priorities. Preserve the expressions and animation timing chosen by the game.
3. Associate each substitution with a resource/image identity, not just a reusable VRAM address. Reject unknown sources and keep the original if a full, usable substitution is not obtained.
4. Reuse the enhanced compositor's integer transform so HD sprites, video, and the text box remain aligned; do not introduce fractional scaling or changes to collision or logic.
5. Prepare and load only the necessary characters, with a bounded cache and texture upload on the window thread. Invalidate/recreate resources on save-state load or device change.
6. Extend to the rest of the compatible characters and elements, checking both disc paths and without replacing English text with Japanese PC labels. Original mode must continue to offer its original sprites.

Status: HD backgrounds integrated experimentally; launcher selector/preparation implemented; character inventory and decoding verified. HD character sprites are not yet being drawn during gameplay.

## Correspondence-hypothesis check

An exploratory numeric field from PC table 12 was compared against byte 0x10 of the Saturn NCs. It only matches in 59 of 147 pairs and differs in 88 (for example NC14:52 versus 54; NC15:51 versus 52). Its full meaning is not yet validated. This rules out using that resemblance as a universal mapping of entries or animations: the mapping will need to be verified resource by resource and against real scenes.


## Verified native link and proportions

`tools/audit_native_characters.py` records all 147 NCs from both discs: common header 00020000, 9-byte entry table with signed coordinates (including negative values and horizontal flip), 512-byte palette at 0x410, and pixels from 0x610. Reserved bytes are not interpreted as an additional entry, nor are the sizes of all sheets inferred.

The Iris scene loads the 192×144 texture from the VDP1 0x80 command from NC55.BIN offset 0x610: the full 27,648 bytes match, and its 512-byte palette matches CRAM bank 0. Both ISOs reproduce the identity. This corrects the hypothesis of compression applied to the native NC; it does not yet prove its full animation.

Confirmed visual direction: the PC replacement keeps its proportion with a single height-determined scale, and aligns on the head/spine/torso central axis. PC width is not forced onto the Saturn texture box. Eye and mouth parts are composed via their metadata; the observed PC base body has a face without those layers, so it is not valid to display it alone as a complete replacement.
