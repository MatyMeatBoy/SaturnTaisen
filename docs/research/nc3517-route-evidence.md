# Chapter 9 Iris route evidence

The Iris hallway event in `0904.BIN` requires heroine value 5 and an unset visit flag. The native Chapter 8 route below sets value 5 through ordinary input and reaches the Chapter 8 tactical rematch. The Chapter 9 hallway event and the live NC3517 draw remain open.

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

The chapter dispatch identifies Ogami's room as `D4` and Iris's room as `D9`. The route table gives `D4` a single exit through `CF`, so a natural route from Ogami's room toward Iris's room crosses the target waypoint. From other starting rooms, the forced Sakura or Sumire scenes can interrupt the route. Check current location again after those scenes before selecting Iris's room.

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

The states, battery images, inputs, screenshots and logs stay in the private archive at `local/work/codex-th1/nc3517-live/`. The two story-route journals record the exact sequence, inputs and state hashes through MAP12 turn 2. This evidence establishes a natural Iris-selected start for further replay. NC3517 rendering, the natural Chapter 9 draw, and package coverage remain open.

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
from the authored frame tables. Natural command positions, rendered
face pairing and coverage during dialogue are pending the live 0904
witness. Capture the frame before the FAD read and settled frames
covering both characters' expressions. The fit scripts and private
image evidence are under `local/work/codex-th1/nc3517-registration`.
