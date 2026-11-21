# Identification of the first film transition

Playback starts from `title-final.state` with `tests/chapter1-title-new-game.movie`, English disc 1, and `sakura-test1.exe` at 614,024 blocks. The continuous replay under strict AOT produced the same 6,201 frame hashes as the windowed path, with zero interpreted blocks. The probes, states and logs stay under `local/work/intro-petals-audit/t33-analysis`. The candidate's log of every cursor change is at `local/work/first-film-phase-boundary/enhanced/run.log`.

## Script identity and observed phases

| File | Low WRAM address | Size | SHA-256 |
| --- | --- | ---: | --- |
| `0100.BIN` | `00204000` | 15,404 bytes | `fd6e18df40fe670341c178588c2f27e10e3599827d31622d66ec8625d952d1e3` |
| `0100TBL.BIN` | `00224000` | 54,018 bytes | `1924569ae54147c461a2bef077ff2ef7bf9c8e668a649e49b609b7421538c7c4` |

The loaded regions matched byte for byte with the disc files in the samples. `0100.BIN` contains bytecode and its cursors are addresses within the region. Its 64-bit FNV-1a is `5DA24532C9356735`. The cursor is the BE32 word in High WRAM `060685B4`. The adjacent BE32 word `060685B8` was 0 in samples 804 and 5992, and 1 in 812, 820 and 5956. The meaning of the second word remains unattributed.

| First frame cursor appears in the continuous trace | Cursor | Evidence |
| ---: | --- | --- |
| 705 | `00204006` | Entry to the transition. The previous cursor `00204000` was observed at 650, 703 and 704. |
| 806 | `00204462` | Cursor during a single consecutive callback between `4006` and `4ED8`. |
| 807 | `00204ED8` | Probe 807 shows ornamentation with no image. States 812 and 820 corroborate this cursor and the badge during the fade. |
| 824 | `00204EDE` | Appears in the intervals before the image, during the video and during the exit. Still present at state 5956. |
| 5968 | `00204EE4` | Word immediately preceding `00204EE6`. |
| 5987 | `00204EE6` | Persists after the footer disappears and during the later episode title. |

The trace establishes the order of states visible to the host. It remains to identify the SH-2 instruction that writes the cursor and the semantics of each opcode. The sampled PC alternates between wait routines and decoder routines. The FILM header is still resident at `06080000` when the floral background returns, and it alone does not delimit playback either.

## Limits of footer suppression

The observed footer is a normal VDP1 sprite with no rotation or flip, mode `00A0`, color `C500`, origin (8, 152), size 304 × 64 and texture fingerprint `924C9C726F152DB2`. The badge uses mode `00A0`, origin (16, 160), size 40 × 48 and fingerprint `7CA30C1792ED4682`. Its color changes from `C400` to `4400` during the fade. The samples from the segment before and after lack dialogue glyphs. There are also samples after the video with the residual VDP2 shadow and zero drawable sprites.

The intersection of exact module match, known cursor, absence of image layers and a closed sprite list delimits the suppression. In sample 807, layer 0 occupies 1,214 pixels, layer 3 occupies 16,922 and layer 5 occupies 53,544. During the video, layer 1 occupies the 288 × 144 region. On reaching the episode title, `00204EE6` is still present and layer 4 occupies the full 71,680 native pixels. These cases require the image-layer veto even with an accepted cursor.

Of 160 archived states, 29 matched the full module. A single state was found outside the intro sampling with one of the verified initial cursors. `cold-load-discovery.state` shows this same film, with 41,472 layer-1 pixels. The theater, later dialogue and conversation-with-Maria checks use `0020582C`, `00205990` and `00205FA8`, respectively. The sampling covers this English path and its local checks. On the host, the script identity and cursor must be captured with the same presented frame to preserve this relationship with run-ahead.

## Current wide background in the first story film

The 1440p replay from the title exposed the native floral pattern
inside the movie rectangle during the entry and exit fades. The
renderer had captured Saturn's blend recipe but bypassed composition
for movie-only scenes. Patch 0281 uses that recipe over the selected
wide floral background during the verified first-film phase. The
shadow opacity follows the film. A registered PC clip follows uniform
fade weights with texture alpha. Native colour mixing covers the
nonuniform case.

Packaged background lookups use the shipped asset roots for screen,
floral and PC backgrounds. A stale profile image can no longer
override these in a packaged run. A development profile can supply a
fixture when the executable has no bundled image.

The 1440p replay retained all 6,072 strict guest hashes and SRAM
in the native and PC donor paths. Before/after RGB differences
were confined to the film rectangle and its shadow. Captures of
the fully opaque film and the floral scene after the film matched
within their respective playback paths. The PC trace opened
MOVIE001 and its image was retained during the measured fade.
