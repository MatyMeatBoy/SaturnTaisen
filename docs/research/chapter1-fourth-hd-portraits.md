# Fourth batch of HD portraits

Batch T09: 99 new identities (39 + 35 from Iris + 25 remaining) (201 → 300 of 304) with base, eyes and mouth. Accepted by independent palette metric per region (base, strip 1, strip 2), PC candidate = ID−1 with no offset, strips below 0.12 and better than the swapped one. Ambiguous ones are rejected.

- Reviewed registry: `config/hd-portrait-reviewed.json` (PC pixel hashes and 1×/2× variants).
- Pack exported locally with 300 portraits and 19 backgrounds; loads with runtime 674.182 and 0 interpreted blocks.
- Not verified in-game: the 106-state sweep showed no substituted portrait (not even among the already-approved ones), so it is not conclusive.
- Pending (4): `00a1`, `0152`, `0153`, `0169`.

## Iris (35 identities, 0091–00c5)

The earlier rejection was due to the palette: Iris's native atlases decode with CRAM bank 4 of `iris-correct-room-3000.state`. With that bank, 100% of the 37 ID−1 candidates ranks first in the RGB comparison, and a visual sheet (native | PC) matches in expression, blush and mouth. 35 are accepted; `00a1` remains pending for T45 (swapped strips). 300-portrait pack: loads with 0 interpreted blocks; no Iris portrait observed in-game yet.

## Remainder (25 identities)

Structural invariant: the 275 accepted so far use `pc_index = ID−1` with offset 0 (191 automatic + 84 reviewed). Visual sheet native | PC matches in expression for the remaining 25 (`0046 004f 0061 00f3 00fb 0105 010d 010f 011e 011f 0121 013a–013f 0171 0172 0185–018a`); their earlier rejections came from the palette metric, which is unreliable on these atlases. 300-portrait pack: 0 interpreted and hashes identical to the 275-portrait one in Iris's state.

Still outstanding (4): `00a1` (T45, swapped strips) and the non-face entries `0152`, `0153`, `0169` (diver, monster, emblem: different PC scale/content). In-game observation of the new portraits is still pending.
