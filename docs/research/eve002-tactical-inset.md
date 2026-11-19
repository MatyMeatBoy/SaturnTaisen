# EVE002 airship tactical inset

The Episode 2 intro replay from the EVE202 checkpoint reads all 22 sectors
of EVE002 at FAD 221023. The airship is visible in native captures 904–1032
sampled every eight frames. The restorable checkpoint at replay frame 960
contains the entire picture's tiles at VDP2 VRAM 0x6A000 and its palette
at CRAM 0x600.

The 2560×1440 stock-runtime capture confirms opaque layer 5 at
native (16,8,288,144), zero scroll and unit step. The captured layer
palette is `5D66F0207B8DD266` and the visible inset RGB fingerprint is
`CE6250F015B307ED`. The shared inset loader and the existing tactical
guard use the frame's captured palette, exact top-source footprint and RGB.
Patch0110 adds the BBG002.SPR subimage 0 crop (0,24,576,288), using the
same integer fit. The asset is pinned by length and FNV-1a. The guard
retains native presentation when the frame or asset differs.

## Verification

- At 2560×1440, asset-present, disabled, missing-asset and both Original
  runs match all 60 guest hashes. In Enhanced, the only RGB differences
  occupy (416,96)–(2144,960), right and bottom exclusive. At frame 36
  every inset pixel matches the nearest-scaled PC crop. Missing assets
  match disabled, and both Original output pairs are pixel-identical.
- Replaying 130 frames from the checkpoint with the archived intro inputs
  rebased to 960 matches all guest hashes. Enhanced changes only the same
  rectangle through sampled frame 75. Captures at 80, 95 and 120 match
  the disabled native output.
- The EVE202 regression pair still draws in the same rectangle and
  matches all 60 guest hashes. All runs reported zero interpreted blocks.
  Runtime SHA-256 is
  `449177c51ae00816bb971d068e3ff0ad34ad198439d12652c6e3d36183a563c6`.

EVE102 appears in the Episode 2 EVT file and pairs with BBG102 offline.
The intro and 13 later tactical segments did not read its start FAD
221105. The later segments total 10,500 frames and 47 CD play commands.
The EVE102 presented frame and placement remain open. The covered EVE002
route is on prepared English disc 1. No release package was built.

The main workspace measured 49,318,453,652 logical bytes, with hard links counted
once and reparse points excluded, above the 20 GB cap. The existing development ZIP remains
6,315,009,692 bytes. The private proof executable is recoverable from an
archive whose executable SHA-256 and CRC were verified.
