# Iris and Ogami's MAP13 combo

The English disc 2 battle can naturally trigger the Iris and Ogami combo. The 1,800-field replay from the preserved aiming state matches the archived guest and SRAM. It reads GATTAI.BIN, GK004.BIN and G0004.ADP for its code, effects and audio.

At fields 600 and 650, NBG3 carries the pair's first pose with VDP2 color calculation. Fields 700, 720, 750 and 800 show the second pose with NBG3's vertical scroll at 256 and color calculation disabled. VDP1 draws the intro portraits, rotating ring, particles, and bows. The map remains behind the pair. The 64 × 144 ring command at field 720 matches the original GK004.BIN payload at offset 0x11F18.

The PC GTB_IRS.SPR holds two 640 × 480 counterparts. An independent decode of the two Saturn pattern-map regions and their palette reproduced the complete isolated NBG3 plane at the sampled poses. The 68,096-byte tile range beginning at VDP2 VRAM 0x68000 matches GK004.BIN from file offset 0x14778. The state census found only the GK004 combo across 1,868 archived states, so other heroine combo poses remain unverified.

Patch 0199 uses GTB_IRS index 1 for the opaque second pose in Enhanced. It pins the PC archive, the exact native pattern name and cell ranges, the palette and the scroll. The replacement only touches the interior of the native silhouette when both captured source IDs are NBG3 and the final native RGB agrees with the decoded pose. The PC cyan key keeps the native pixel. Patch 0199 keeps the blended first pose native. All VDP1 effects retain their original rendering.

Five strict 1,800-field Direct3D 11 replay variants (donor, missing, one-byte corrupt, Original donor, Original missing) and the prior runtime matched the archived guest hashes and final SRAM. All completed with zero interpreted blocks. The candidate reference hash log is 88fa335905b12b899ac4ca3a877e2e943805aedcd3ddca0d85bb790bd0a45c81. The valid donor drew 124 times. Enhanced missing and corrupt, and Original with or without the donor, matched their respective controls at all 12 samples. The three intro samples and four samples after the second pose were unchanged.

At 2560 × 1440, the five sampled second-pose frames changed 495,027 to 872,622 output pixels. Every changed pixel matched the independent PC projection and lay within the verified native NBG3 silhouette. Map, native sprite effects, and framing were preserved. Other heroine combos and public package inclusion remain open. Private fixtures and commands are retained under local/work/codex-th1/map13-combo-hd.


## First pose blend

Patch 0201 registers GTB_IRS index 0 for the first pose. It identifies the first NBG3 pattern-name range and uses the same pinned GK004 tiles and palette. For a visible NBG3 pixel over native source 2 or 4, it checks the captured color-calculation recipe against the final Saturn RGB. On a match it uses the registered donor color in the same recipe, retaining the backing color, weight, and post-mix offset. The cyan key, silhouette edge, VDP1 pixels, and unsupported mixtures keep their native RGB.

The six 1,800-field strict Direct3D 11 variants reproduced the same archived guest hashes and SRAM with zero interpreted blocks. The valid donor drew 119 blended first-pose and 124 opaque second-pose fields. Missing and one-byte-corrupt donor controls agreed at all 14 samples, as did Original with or without the donor. At nine shared captures the missing-donor output also matched patch0199. The pre-combo, opaque-pose and later valid-donor samples matched the baseline.

At replay fields 601 and 651, the prior 2560 × 1440 render reduced to the exact first frame after the respective archived field 600 and 650 checkpoints. Independent decoding verified 4,952 native blend positions in each frame, with lower-plane weights of 22/32 and 10/32 respectively. The runtime changed 81,063 and 137,493 output pixels. Every changed pixel matched the independent 2× projection and all independently predicted differences were present. Three additional intro samples also changed only inside the registered viewport. The runtime uses the same PC archive as patch0199.
