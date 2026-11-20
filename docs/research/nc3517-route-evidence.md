# Chapter 9 Iris route evidence

The Iris hallway event in `0904.BIN` requires heroine value 5 and an unset visit flag. The English disc 2 replay sets value 5 in Chapter 8 by ordinary input, carries it through both chapters' battles, and reaches the live Chapter 9 NC3517 draw.

## Read the active heroine selector

The reader in the English disc 2 `/SAKURA` at guest addresses `060198E4` through `06019924` separates each token into its high-byte bank and low-byte index. Bank `20` uses the BE32 pointer at `0607CC5C`, then reads a BE16 value at twice the index. The observed story states use base `00200300`, so token `2053` reads `002003A6`.

The [state vector parser](../../tools/audit_native_characters.py) returns High WRAM first and Low WRAM second. The story code and its table pointers can be unloaded on tactical maps. Read the registered bank from a story checkpoint before or after a battle, or check the corresponding in-game battery save after the game reports a successful write.

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path("tools").resolve()))
from audit_native_characters import state_vectors

high, low, *_ = state_vectors(Path("local/path/to/story.state").read_bytes())
base = int.from_bytes(high[0x7CC5C:0x7CC60], "big")
offset = base - 0x00200000 + 2 * 0x53
if 0x00200000 <= base < 0x00300000 and 0 <= offset <= len(low) - 2:
    print(int.from_bytes(low[offset:offset + 2], "big"))
```

The ordinary Chapter 9 public-slot replay has value 1. The separate archive slot that opens `0904` after the defense has value 3. The latter reaches the ordinary Iris room visit with the nightmare flag clear.

## Trigger the Chapter 9 hallway route

At `0904.BIN` offset `0x17D2`, the waypoint handler checks `2053 == 5`. It then checks visit flag `102B == 0`. Bank `10` uses the BE32 pointer at `0607CC60` and the same word indexing. The story snapshots place `102B` at `00200156`.

The waypoint handler at `0x17CE` is entry `CF` of the table at `0x1572`. Opcode `0024` in the script calls the native resolver at `06022278`. The resolver uses current location and selected destination with its group table at `060594F8`. Its result is the next path node. The visible room label selects the destination and the path may visit several intermediate nodes.

The live second-floor dispatch identifies Ayame's Room as `D4`, Captain's Quarter as `D5`, and Iris's Room as `DA`. The route table gives `D4` a single exit through `CF`. After the Sakura balcony and Sumire salon scenes, enter Ayame's Room from the second-floor map. Move the door cursor down until it turns into a walking-person icon and confirm. This returns to the map with current node `D4`. Selecting Iris's Room then takes the hallway route through `CF`.

The handler calls the encounter at `0x3322`, where the script sets `102B`, shows BG1129 and NC55, then selects BG2517, BG2053 and NC3517. The first NC3517 operand is at `0x33CE`. There are 14 calls to this body in `0904.BIN`, and the other four-digit story BIN files across both prepared English discs contain no identical body opcode. These are script observations.

## Natural Chapter 8 checkpoint

Starting from the archived English disc 2 `0801` checkpoint, the ordinary inputs inspect Sumire's mouth, finish the New Year gathering, let the initial date offer expire, and visit Iris's room from the second-floor map. The selector changes from 0 to 5 when Iris accepts the shrine outing. The 16 archived slices through the first `0802` checkpoint total 33,500 strict-native fields. The game reads all 11 sectors of `0802.BIN` at FAD 108568.

The festival cursor moves to the far right edge and confirms to leave the stalls. A portable run through the optional cork-shooting game returned to `0802` with selector 5. The game then wrote an ordinary Chapter 8 File 1 save at the [IC08 intermission](ic-intermission-table.md#ic08-on-english-disc-2). The saved record has chapter/subepisode bytes `0802` and heroine value 5.

| Private checkpoint | SHA-256 | Observation |
| --- | --- | --- |
| `iris-0801-ask/f960.state` | `11d1d2213588d90e9353e82d1a82e36479e5c623ab0e617811050e21fd7e67eb` | Value 5 in the still-active `0801` module. |
| `iris-0802-ic08/terminal.state` | `531ffb4cc1b455e8507ccb2467c1d8dad1b54a6256865be8c4fc8d2416bb98a6` | Settled natural prebattle intermission. |
| `iris-0802-ic08/backup.bin` | `a9ea92da7634f0060b9d72a94671646eb0eaa7db64c8020acfa5f8d4190391b0` | The completed in-game save with selector 5. |
| `iris-map12-start/terminal.state` | `06711f6696c2bc4261315a7e3e2c2124ed12224ac58f604ce11e30cca1480754` | Iris's first tactical turn, MAP12 at FAD 219422 for 151 sectors. |
| `iris-map12-airship/terminal.state` | `3c54029e145e5e957f147091db8f22aa9c2a5f407f791cb2ea2b1b09ebf51ead` | The tactical rematch after the shrine-gate retreat, MAP13 at FAD 219573 for 178 sectors. |

The tactical route records Kohran's attack and subsequent enemy attack, then the allies' retreat through the shrine gate. Kanna retreats after taking damage before the remaining party clears the gate. The next tactical map opens and gives Iris the first move. The tactical receipts use the portable interpreter through this boundary. [Bounded EVT12 strict coverage](evt-overlay-registry.md) has its own witness scope.

The states, battery images, inputs, screenshots and logs stay in the private archive at `local/work/codex-th1/nc3517-live/`. The two story-route journals record the exact sequence, inputs and state hashes through MAP12 turn 2. This evidence establishes the natural Iris-selected start for the Chapter 9 replay below.

## Natural Chapter 9 witness

The English disc 2 replay won the MAP16 theater defense with all seven allies active. Maria's normal shot reduced Shika from 37 HP to 0. The in-game File 1 save after 0903 has battery image SHA-256 `b38873d51699152082efce9e9778f3e1b2b81a9feca6c0a5ac20480c4b5fb68b`. Resuming reads 12 sectors of `0904.BIN` at FAD 109650. The checkpoints before and after that read retain `2053=5` and `102B=0`.

Exiting Ayame's door returns to the map with `10F0=10F1=10F2=D4` and `102B=0`. Selecting Iris's Room starts the `CF` handler, which redirects the next location to `D0`. The visit flag changes from 0 at field 320 to 1 at field 480 of the click replay, and the game reads BG1129 at FAD 118748. This is the hallway encounter before the bedroom picture.

The next input slice reads BG2517 at FAD 129192, BG2053 at FAD 124053, and NC3517 at FAD 140992. Starting from its field-900 checkpoint, the rebased input reproduced all 240 archived frame hashes across those reads. At field 30 of the rebased replay, the BG2517 tiles are in VDP2 and the BG2053 tiles are in Low WRAM. By field 60 both plate textures are in VDP2 and the NC3517 texture is in VDP1.

| Private checkpoint | SHA-256 | Observation |
| --- | --- | --- |
| `iris-0904-earned-from-d4-hover/terminal.state` | `57b1f99e50a546de38a020edd494e78286d27dfb8a13e6d93bec74073f0d4a92` | Before the click into the hallway route from D4. |
| `iris-0904-earned-nightmare1/f900.state` | `c9e40ec05ecb2bb6d360617dedeeabaec2a3df5e3dbe85633e24007f0e998253` | Before the two plate reads and body read. |
| `iris-0904-earned-nightmare1/f1260.state` | `b1d855e8f057b586364c1e24c2b05acef49f6a4dcabd6e8d240cdb3bcbc2391b` | Both faces are visible. The left mouth selects authored index 4. |
| `iris-0904-earned-nightmare1/f1440.state` | `f7a35c629ce74e7489d2e92514f34145a71122c796a2166e0b3e61d939197b51` | The left mouth selects authored index 6. |

Nine sampled states draw the exact 200 × 80 NC3517 body at `(48,8)` with palette bank 0. Their native face sprites align at `(112,16)`, `(56,48)`, `(184,24)`, and `(192,56)` for left eyes, left mouth, right eyes, and right mouth, respectively. The journal `iris-natural-0904-nc3517-journal.json` records 35 clips and 62,820 fields from the 0903 continuation through the first bedroom draw. The states, inputs, screenshots and palette scan are retained privately under `local/work/codex-th1/nc3517-live/`.

## Offline body and face registration checkpoint

The two prepared Saturn discs contain the same 44,048-byte NC3517 file.
The disc 2 extent starts at FAD 140992. A 200 × 80 comparison strip at
offset 0x610 has 10,112 opaque native texels. PC subimage 0 is 473 × 184.
The shared axis fit uses scale (2088, 2254) and origin (−9775, −2197)
in thousandths. Its 23 landmark inliers have a median residual of
0.676 PC pixels and a maximum of 2.408.

The existing registered-body compositor and an independent integer
projection agreed on all 64,000 output RGBA samples. With the existing
12-sample edge taper, 37,521 of the 40,448 opaque 2× samples use the
donor and all 23,552 transparent body samples stay clear. The sampled
donor region contains opaque art and passes the chroma check.

| Candidate native part | Slots | Proposed native size | Authored PC origin |
| --- | ---: | ---: | ---: |
| Left eyes | 3 | 24 × 32 | (119, 17) |
| Left mouth | 6 | 72 × 32 | (6, 94) |
| Right eyes | 3 | 56 × 48 | (268, 17) |
| Right mouth | 6 | 16 × 24 | (288, 107) |

The four candidate groups consume the 26,496-byte native tail exactly.
Each slot has a distinct byte fingerprint. The PC face origins come
from the authored frame tables. The natural 0904 witness above identifies the four command positions and records distinct dialogue expressions. The fit scripts and private
image evidence are under `local/work/codex-th1/nc3517-registration`.

### Compositor fixture and retained-state search

The 200 x 80 body ran through the current Windows renderer in an
isolated synthetic fixture. Eight 12-field profiles matched guest
hashes and SRAM within their fixture, including Original and missing
donor controls. With a valid donor and a clear silhouette, all 784,000
samples in the 1440p draw rectangle matched the projected overlay or
the native coverage. At exact nearest-neighbor ties, either adjacent
projected texel is valid. The known overlapping sprite produced a
native RGB match because the visibility guard rejected the overlay.

The retained-state search read VDP1 VRAM from 2,252 Sakura version-9
states and found no resident match for the exact 16,000-byte texture.
The constructed fixture separately confirmed the scanner identifies the
active command and CRAM bank. The fixture and build receipts are private
under `local/work/codex-th1/nc3517-registration`. The later natural route provides separate live sprite and expression evidence.

## Natural 0904 body and faces

Patch 0247 registers the PC body and four expression groups against the native draw commands. It draws each expression only when the corresponding body overlay was drawn and the native command, geometry, palette and visible pixels match. Transparent texels and unsupported overlap retain the native draw.

At 2560 × 1440 the ordinary-input English disc 2 Iris route produced the body and both faces. The alternate-expression checkpoint comparison changed 650,429 pixels inside (535, 40)–(1896, 589). Original, the truncated PC donor, and the pre-body checkpoint each matched their control RGB exactly. Each donor/control pair matched all 48 guest hashes and final SRAM with zero interpreted blocks. The missing-donor control used the same checkpoint and settings. The earlier controlled fixture exercised native occlusion. Package inclusion is pending.


## BG2517 bedroom scene

Two 48-field donor/control comparisons at 2560 × 1440 from the natural `iris-0904-earned-nightmare1/f1260.state` checkpoint confirm the BG2517 PC draw. The released executable and the patch 0247 candidate each reported BG2517 usable, with 1,232,185 changed pixels inside the narrative scene bounds (272, 29)–(2288, 1037). The candidate comparison supplied NC3517 in both profiles. Both pairs matched guest hashes and ending SRAM with zero interpreted blocks. The dialogue frame and floral surround were outside the changed bounds.

At `iris-0904-earned-nightmare3/f720.state` the solo sleeping Iris shot selects BG2053 even with BG2517 available. The BG2517-only and empty-pack captures matched pixel for pixel, with 48 matching guest hashes and identical SRAM. Private receipts are under `local/work/codex-th1/thd01-probe/iris-bg2517-witness`.
