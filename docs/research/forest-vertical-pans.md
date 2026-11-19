# Chapter 10 forest vertical panoramas

The Saturn 288×296 BG2207 and BG2265–BG2269 files use the same forest setting with six Koubu color variants. Their separately matched PC subimage-zero files are 576×592. Each Saturn BIN has identical bytes on both prepared discs. The Chapter 10 scenario 1003.BIN references the backgrounds at offsets 0x13f4, 0x1420, 0x144c, 0x1478, 0x14a4, and 0x14d0 in that order.

The shared backdrop makes grayscale comparisons ambiguous. The right-hand Koubu at (113,193)–(173,258) distinguishes the pairs. After subtracting each platform's six-variant mean RGB in that rectangle, the strongest Saturn-to-PC match is the same named variant in all six cases. Similarity ranges from 0.813 to 0.859 with a minimum 0.100 margin over the next candidate.

The same vertical viewport matcher uses (0, 2y, 576, 288) in each PC picture. The six asset rows have distinct Saturn file, palette, cell, and PC file fingerprints. A full 288×144 Saturn match and unique vertical origin are required. Runtime activation is scoped to the same NBG2 ownership rules as BG2248 and BG2295.

## Evidence

- All 918 possible vertical origins passed the direct C++ viewport probe using the actual Saturn files. A one-byte change in each file failed the corresponding native pin.
- Both builds matched the opening for 1,500 strict-native frames. The BG2248 vertical panorama and same-palette BG2251 fixtures matched all 205 and 60 guest hashes and nine 2560×1440 screenshots in total.
- The six replacements are connected. Their actual Chapter 10 appearance and package inclusion remain open.

The coefficient matrix and native-offset receipts are in local/work/codex-tp2a/forest-variant-matrix.json and local/work/codex-tp2a/forest-native-offsets.json.
