# Manual advance of voiced dialogue

Sumire's first spoken line after entering the chapter 1 dining room was checked, using Saturn English disc 1 and the isolated executable at block 643,320. The voice is identified in the game's real activity. PLAY commands with FAD `02AA3B` and `02AA53` read LBA 174,501 and 174,525 inside `/SAKURA1/VCEADV`. The 44,100 Hz stereo PCM from the same run was captured.

## A, B and C test

From `local/work/sakura/theater.state`, an eight-frame A press at 100 enters the scene. The private state `first-sumire/f0899.state` preserves the previous line, already written. All comparisons start from that state with an SRAM copy and press A at relative frame 20 for eight frames to enter the spoken line. A, B or C is then tested separately, with four-frame presses at 120 and eight-frame presses at 155 and 300. The button is released between presses.

| Button tested | Incomplete text at 120 | Complete text at 155 | Late press at 300 |
| --- | --- | --- | --- |
| A | Completes the text, fully visible at 140. | Sumire's line remains. | Advances to the next speaker, visible at 360. |
| C | Same visual and PCM result as A. | Sumire's line remains. | Advances to the next speaker. |
| B | Completes the text and alters the voice flow. | Advances before A/C. The box changes between captures 160 and 180. | By then it's already on the next line. |

The control with no presses after the line starts still shows partial text at 180. B's PCM starts to differ from A's and C's around frame 123, right after the first B press. B's run skips the second PLAY of the `VCEADV` region. In A/C, the first segment still has eight sectors buffered at state 119 and four at 139. By 159 the drive is already paused, with zero sectors buffered, although the CPU keeps copying samples to sound RAM. CD-reader state alone does not indicate whether a voice is still sounding.

Each movie was repeated with strict AOT and the SH-2 interpreter on the same binary, with recompiled functions disabled in both modes for the comparison. The 460 hashes per movie match, as do all captures and all PCM. Under AOT there are zero interpreted blocks. This equivalence verifies the CPU mode for this case. It still needs comparison against physical Saturn or another independent implementation.

## Input received by the game

Save states taken before frame 159 contain the SMPC digital report for the active port 1, low, with `FBFF` for A, `FEFF` for B and `FDFF` for C. The values match between AOT and interpreter. The lack of early advance with A/C occurs even though the game receives the input.

In that sample, A/C have PC `0600AEEC`, PR `0600AE1C` and R7 `25A7D470`. The code writes sample words to the sound RAM mirror. In B, the CPU is at `060041BA` with PR `060041BE`. These samples demonstrate distinct execution paths. The instruction that decides whether to allow the advance has still not been isolated.

It was verified that the native menu allows switching `Voice` from On to Off, with captures of the selector in both states. From that other context, the later dialogue sample made no new reads of `VCEADV`, so it was not used to compare On/Off on Sumire's line.

The movies, states, PNGs, hashes, CD traces and PCM dumps stay under `local/work/dialogue-voice-advance`. The test documents manual advance on a spoken line. Its scope excludes the auto-skip feature and other scene types.
