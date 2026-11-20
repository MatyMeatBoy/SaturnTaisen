# NC36 and NC72 face registration

The live NC36 eye and mouth layers can drift from their authored locations when Enhanced estimates their placement. The largest observed NC36 eye displacement was 24 donor pixels vertically for ordinal 80. NC72 uses a different head placement from the other faces in its PC bank. Its prior mouth position was three donor pixels right and two down.

Patch 0235 registers the observed Saturn textures against the exact disc and PC files. The donor body origins and face offsets come from the PC SPRED tables. Other textures retain the existing fallback.

| Natural English disc 2 witness | Body ordinal | Authored eye position and ordinals | Authored mouth position and ordinal |
| --- | --- | --- | --- |
| Chapter 8, module 0805, bank 8 relay field 9000 | 78 | (104, 73), 79–81 | (152, 97), 82 |
| Chapter 9, module 0902, item-return checkpoint | 2 | (112, 54), 25 | (136, 102), 65 |

At 2560×1440 on Direct3D11, the changes from the prior runtime stay inside the face. Each of the four sampled opaque fields matches the authored PC projection for every sampled flat eye and mouth pixel. Live trace additionally confirms NC36 ordinal 81. Missing and truncated donors and Original mode match their controls exactly. All seven arms per checkpoint ran 55 fields with identical guest hashes and backup RAM and zero interpreted blocks.

NC36 and NC72 add two verified disc-file rows. Package inclusion is pending.
