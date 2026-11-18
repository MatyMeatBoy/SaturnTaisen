# References from the cheviman thread

Review requested by the user on November 17, 2026. [Original thread](https://www.reddit.com/r/decomps/comments/1xyt6gy/everything_im_building_arcade_decompilation_lan/). The public repositories, their selected sources, and licenses were read; result announcements are not treated as tests run on Sakura. No code from these projects was incorporated.

|Project|Reviewed revision|Concrete use in SaturnTaisenFirst|
|---|---|---|
|[htmlsaturn](https://github.com/cheviman/htmlsaturn/tree/d7e4798da9ea49f2604d0cb7acdad146aeec4287)|`d7e4798da9ea49f2604d0cb7acdad146aeec4287`|SH-2, stall diagnostics, and render separation by snapshots/rows.|
|[arcade-decomp](https://github.com/cheviman/arcade-decomp/tree/ec413d6eb04bc419f1677ee132358dc65efe0785)|`ec413d6eb04bc419f1677ee132358dc65efe0785`|Reproducible scenarios, state/image/sound comparison, and regression selection.|
|[console-decomp](https://github.com/cheviman/console-decomp/tree/b9380842a84f0a09438add3083c808a662b054b7)|`b9380842a84f0a09438add3083c808a662b054b7`|Console-modeling reference; its public backend is Mega Drive.|
|[arcade-lan](https://github.com/cheviman/arcade-lan/tree/ad5dfe746c13a1dc18ce3b89d9ed6803e4db0b52)|`ad5dfe746c13a1dc18ce3b89d9ed6803e4db0b52`|Not needed for the single-player campaign; no network dependency is added.|

## Immediate application

htmlsaturn splits VDP1 and VDP2 into workers. In `vdp2-worker.js`, each worker owns its own chip instance, reads a stable snapshot, and writes interleaved, non-overlapping lines. The interlace field is passed from the owner to prevent an out-of-phase worker from drawing the opposite field. Its diagnostics compare pixels and measure the cost of an empty round. It's a guide for research, not an improvement that carries over directly: our `RenderLine` is invoked during the frame and observes that moment's state. Before parallelizing, per-line writes, priorities, shadows, and the planes used by the enhanced compositor must be preserved.

Patch21's CPU background preparation already separates independent jobs without touching guest state. Final compositing uses Direct3D11. This new finding does not prove our rasterizer is GPU-bound or that more threads always speed up a scene.

`diag/sh2-oracle.mjs` points to a concrete MAC.L accumulation case with saturation: interpreting the accumulator's active bits. Our own native generator and interpreter will be checked against the [official Renesas manual, section 6.1.31](https://www.renesas.com/en/document/mas/sh-1sh-2sh-dsp-software-manual). This does not imply it explains a fault observed in Sakura without reproducing it.

`cd.js`'s load comment illustrates how a read still in progress can look like a stall. Its commented rate will be checked against Saturn documentation; it is not adopted as a hardware value. For our optimizations, host read, sector delivery, CPU position, and DMA/CD completion will be measured separately. Speeding up the SSD does not authorize removing the game's sync waits.

`arcade-decomp` contributes a scenario-and-hash comparison methodology and change analysis. Its reviewed public frontends are V60/V70, Z80, and 68000; it is not an SH-2 substitute ready for this game. `console-decomp` documents open items in the independence of its graphics reference: reusing its methodology requires watching that reference and change don't share the same bug.

## Availability and licenses

The announcement presents saturn-fullset, an open SGL built on libyaul, and Saturn recompilation to native executables. The author himself states that repository was not public at the time of the announcement; there is no publicly reviewed implementation in this investigation. It is kept as a future reference, without changing the current SDK or relying on promises.

The reviewed arcade/console/lan repositories declare BSD3-Clause. htmlsaturn declares GPLv2-or-later with components from several origins; any future incorporation must preserve attributions and review the specific file. For now, only ideas and cases to check against are taken. cranker-llm is a reading tool for agents, not an acceleration of Sakura's executable, and is not installed as part of the game.

## Concrete result of this review

The MAC.L lead made it possible to reproduce a defect in our own two paths. The interpreter and generator were fixed, the AOT was regenerated, and 68 tests passed. [Reproduction, case matrix, and limits](macl-48bit-regression.md). No external code was incorporated, and the SDK was not changed because of saturn-fullset.
