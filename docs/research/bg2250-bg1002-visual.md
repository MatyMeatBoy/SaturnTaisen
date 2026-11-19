# BG2250 and BG1002 at 1440p

Both asset-controlled pairs ran for 60 frames without inputs in Enhanced
Zoom at 2560×1440. They used the v0.2.6 campaign executable with SHA-256
`6fcd9aba866a1f3c14c706b8c1a9edc4b40ad4f5a555daa2454c9a59a9269482`.
Each HD profile saw only its target SPR. The control used an empty PC
asset directory. Both runs in each pair reported zero interpreted
blocks. The only RGB differences in captures 20, 40 and 58 fit the
picture rectangle (272,29)–(2288,1037), right and bottom exclusive.

## BG2250 blue gradient

The Chapter 1 route on prepared Spanish disc 1 starts from the retained
`pruebas/largo/carta-9900.state` with its matching backup RAM and
`run.movie` rebased at 9900. The 7,360-frame relay saves the salute scene
at frame 7359. That state has BG2250 cell bytes at VDP2 VRAM 0x34840 and
its palette at CRAM 0x200. Its SHA-256 is
`ab5be516ee2ba429503b0cc824c364c5981c42a3ed0a22b9f280ebf6be721d9f`.
The English and Spanish disc 1 BG2250.BIN files are byte-identical.

The asset-present run drew the PC blue gradient behind the saluting
character. All 60 guest hashes match (log SHA-256
`84cea0a734ef5b35f3932cb77608dea97995db4aa1ffebab6fead01ab17932f0`).
Each native foreground comparison covers 1,030,372 inset pixels whose
maximum channel difference from the nearest-scaled decoded Saturn
gradient exceeds 18. All those pixels are identical between profiles.
The Spanish fixture's test dialogue also matches.

## BG1002 theatre lobby

The English disc 1 relay reuses `after-options-3000.state`, its matching
backup seed, and `after-options.movie` rebased at 3000. After 1,500
frames, the checkpoint has the exact BG1002 cells at VDP2 VRAM 0x4A040
and palette at CRAM 0xE00. Its SHA-256 is
`d8846f7bff0f3d2ecb1aa6af464cee14f3fc60e7126c3c77c2409bfb0b404e35`.
The native viewport matches the decoded BG1002 with luminance
correlation 0.99994. The similar BG1001 picture scored 0.86874 and
had neither its tile payload nor its palette in the checkpoint.

The PC artwork shows the same lobby, sunlight, arches and crowd. All 60
guest hashes match (log SHA-256
`ee69fe6ac28800f507a306f85cdb899e000ff681fc5443250e481acb8b15d981`).
The surrounding presentation and English dialogue are pixel-identical.

These witnesses cover two scenes on disc 1. No runtime or package was
built. The main workspace measured 50,856,551,978 logical bytes with hard links
counted once and reparse points excluded, above the 20 GB cap. The delivered development ZIP
remains 6,315,009,692 bytes.
