# MAC.L: 48-bit saturated accumulation

Research from the cheviman thread flagged an SH-2 arithmetic case that was cross-checked against the [official Renesas SH-1/SH-2/SH-DSP manual, section 6.1.31](https://www.renesas.com/en/document/mas/sh-1sh-2sh-dsp-software-manual). With S enabled, the 48 low bits of the accumulator participate. Reading the third-party code was used as a lead; the test and the fix are our own and do not incorporate htmlsaturn code.

## Reproduction

With accumulator 0xFFFF000000000000 and both operands zero, the active bits represent zero. Before the change, the native generator returned the saturation maximum and our own interpreter the minimum. Both included inactive bits, and the generator additionally chose the saturation direction by the sign of the product. This is not proof that this case occurred during an observed Sakura scene.

The full logs are kept locally in v02-macl-red.log. The test failed on both paths before they were fixed. Both the interpreter and the generator are reviewed: fixing only one path could leave an incorrect reference or stale generated C++.

## Fix

The accumulator is masked and interpreted as signed 48-bit; the product and the sum are computed without signed overflow and are clamped by comparing the result against the allowed extremes. With S disabled, the 64-bit modular sum is kept. Read order, pointer increment, flags, and nominal cycles are preserved.

The synthetic test compiles the instructions emitted by production's sh2emit.py, without writing a hand-made substitute. It covers extreme operands and sign crossings, carry between halves, inactive high bits, matching and differing address registers, S enabled/disabled, and both SH-2s. There are 11,616 cases per path (native and interpreter), including addresses and flag preservation. MACH's inactive high bits are not treated as a defined 48-bit result. The expected model uses 128-bit arithmetic, independently of the production formula.

All 580,328 AOT blocks were regenerated: the generator rewrote 708 affected files and kept the rest. No coverage was removed to reduce recompilation. Files derived from the game remain local.

## Limits

This is a semantic fix, not a measured FPS improvement. The full synthetic check does not prove the entire campaign, all SH-2 instructions, or the GPU backend. The reference and the native code may share defects: comparison against documentation and independent expectations is maintained.

Final validation: full native build passed, and 68 tests in 103.707s. Includes real checks of a 600-frame boot and an initial 4,200-frame run with zero guest instructions interpreted. The published v0.1.5 is not modified.
