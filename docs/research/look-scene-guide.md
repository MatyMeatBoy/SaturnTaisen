# Look-at scene guide (THD15): steering the chapter-jump gaze scenes

Status: PARTIAL. Only bank-5 was probed; no `MAPnn` was reached and nothing was promoted to `hd`. This is the method and what the first page taught.

## Method (reproducible without screenshots)

- Exe: a private copy of `local/build/sakura-full2/sakura-full2.exe` (PR #691, AOT, `art/` beside it), run with `SATRECOMP_NO_CALLS=1 SATRECOMP_NO_FUNCTIONS=1 SATRECOMP_STRICT_NATIVE=1 SATRECOMP_CD_TRACE=1 --headless --unthrottled --mute --frames N --backup local/work/sweep/run2-CASE/backup.bin --settings .../settings.ini --state-load 0:D:/.../state-39999.bin --movie M --state-save N-1:end.bin --shot-every K:prefix`. Paths given to the exe must be `D:/...` form (an MSYS `/d/...` path silently loads no state).
- A segment of 300-1000 frames takes 1-3 s. The next segment loads the previous `end.bin`; movie frames count from the loaded state.
- Movie lines are `frame bits 0`, a press ends with a line of `0`. Bits: A 0400, LEFT 4000, RIGHT 8000, UP 1000, DOWN 2000. Direction presses must be HELD (about 40-100 frames); a 4-frame tap barely moves the cursor, which explains why 3 short taps looked like a no-op.
- A "Play Disc" load shows as a `cd cmd` Play line in `cd.log`; `tools/chapter_loads.py` maps it to the ISO file. No segment below produced a MAP/BBG/EVT load.

## bank-5 (state 39999 of the sweep), page 1: Sumire and Kanna, eyes cursor

What is shown: two characters (Sumire left, Kanna right) with an eyes icon near the centre. The cursor moves about 2 px per frame while a direction is held.

| Entry (frames after the state) | Result |
| --- | --- |
| RIGHT held ~40, then A | Cursor over Kanna: Ogami thought about the fight and Kanna's clothes; A to type out, A to close |
| LEFT held ~55 (from Kanna) or ~70 (from the start), then A | Cursor over Sumire: lines cycle ("shiner", then "I can't believe Sumire survived a fight against Kanna") |
| LEFT, RIGHT, UP or DOWN held past the edge (>= ~90), then A | Icon turns into a hand at the screen edge: Sakura says "Ogami, where are you going!?" then "You've got to stop those two!"; Ogami answers "You make it sound so easy..."; returns to the cursor. This is the loop of PR #687 |
| A pressed twice on the same hotspot (5 times each) | Lines repeat; no page change after 5 looks at Kanna |

Not yet found: the entry that leaves the page. Hypotheses to test: look at Sumire the full number of times (the line cycles), or look at both with a specific order, or the hand at the edge needs B/Start. The second phase of the 5x5 test moved the cursor too short a distance (stayed on Kanna), so Sumire was not looked at five times; redo with LEFT ~55 after the Kanna dialog is closed.

## Not done

bank-6, bank-7, public-7, the ground probe (`tools/tactical_ground_probe.py`) and the `hd` promotion were not attempted. No input script is committed because no state advanced past page 1.
