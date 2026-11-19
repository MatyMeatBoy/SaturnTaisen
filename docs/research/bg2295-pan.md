# BG2295 vertical panorama

The variant-B BG2295 picture on Saturn is 288×208. Both prepared disc files are byte-identical. The corresponding PC BG2295.SPR subimage 0 is 576×416. All sampled 288×144 windows matched their 2:1 PC crops with a minimum grey signature correlation of 0.99955.

A native crop starting at y uses the PC rectangle (0, 2y, 576, 288). The runtime uses the existing vertical-pan path with BG2295-specific pins for the Saturn file, NBG2 palette and cell identity, and PC file. For substitution, every visible pixel must have native NBG2 ownership and match one unique crop of the original. Hardware blends and other owners keep the native composition.

The cell key comes from the first uniquely named cell in the stored native pattern names with zero-filled unused names. This derivation also reproduces the separately observed BG2248 cell key. Direct C++ tests using BG2295's native file found all 65 possible offsets and rejected a modified byte. The synthetic guard test covers both BG2295 and BG2248 heights, another owner, a changed viewport pixel, and an ambiguous uniform viewport.

## Game evidence and limits

The prepared scripts request BG2295 at 0803.BIN offset 0xbee in Chapter 8. The two CD extents start at FAD 152081 and 128912. The bounded disc-2 cold route stayed in early Chapter 8 dialogue and made no reads for BG2295. The runtime path is implemented, with in-game appearance and package inclusion open.

A strict-native comparison to the previous build matched 1,500 opening guest hashes. Separate fixtures matched all 205 guest hashes and six 2560×1440 samples of BG2248 and all 60 guest hashes and three samples of BG2251, which shares BG2248's palette.

Private receipts and reconstruction scripts are in local/work/codex-tp2a. The files vertical-candidates.json and ab2295/negative-audit.json record the offline pair and previous-build controls respectively.
