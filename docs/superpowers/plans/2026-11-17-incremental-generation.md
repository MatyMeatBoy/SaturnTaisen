# Incremental generation during discovery

The Continue path added entries with addresses earlier than already-generated blocks. The current global order then changes hundreds of C++ files, even though only a few variants are being added. Keeping their positions fixed lets us extend the recompilation without repeating those builds.

- Add to the pinned generator a private order-manifest option: the first generation is identical to the previous order; later generations keep the entries and append the new ones at the end.
- Identify each variant by address and SHA-256 of its bytes. Reject duplicate manifests, file-size changes, and entry removal; regenerate in another folder if a different base is required.
- Test with synthetic SH-2 programs that adding a lower address, and another variant at the same address, keeps the previous files exactly unchanged, and that an invalid manifest does not modify the output.
- Enable the manifest in the local tool; keep runtime byte control, strict AOT, and grouped functions disabled.
- Initialize it with the 253,163 already-compiled blocks, incorporate the Continue menu, and check the real load before claiming it works.

This is an adaptation of the approved build flow, with no changes to guest instructions or game behavior. The manifest and derived C++ files stay under `local/`.
