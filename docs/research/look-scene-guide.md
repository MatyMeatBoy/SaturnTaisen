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

## Attempts log, bank-5 page 1 (frames count from state 39999; none left the page)

Each segment started from the state; "hold" = direction held N frames. Presses: A 0400, B 0200, C 0100, Start 0800.

| # | Entry | Result |
| --- | --- | --- |
| 1 | LEFT hold 70 (on Sumire), then 8 looks (A, A+90, A+170 every 250 frames) | Cursor drifts to the edge after the first dialogs; only the "where are you going / stop those two / You make it sound so easy" loop (2100 frames) |
| 2 | RIGHT 40, 3 looks at Kanna (250 frames each); LEFT 55; 3 looks at Sumire | Kanna and Sumire lines appear in order (no new page) after 1800 frames |
| 3 | LEFT hold 120 (edge hand), then B x2, Start x2, C x2, B | B has no effect (loop line). Start opens a command menu (see below); C closes it |
| 4 | Start at frame 20, A at 80..300 | Menu with Item, Option, Return; A on empty space does nothing |
| 5 | Start 20, UP hold 10 (cursor lands on card 3), A | Item cards: 1 Sakura, 2 Kanna, 3 Maria, 4 Iris (RIGHT/LEFT hold 10 moves one card). A opens a two-choice box: first = look (description line: "It's a photo of ..."), second (RIGHT then A) = hold the card over the scene as a cursor |
| 6 | Held card, move LEFT 40 / RIGHT 25, A at 230 and 330 | Card stays held over the scene or returns to the menu; no reaction recorded; the cursor target while holding a card was not verified |

| 7 | Start 20, UP 80 (card 3), A 110, A 170 (second A), then LEFT 40 / RIGHT 20 / LEFT 15 from 230, A | The first A opens a two-choice box and the look view; the second A shrinks the photo to a small held card for about 30 frames and then returns to the item menu by itself. The "use the card on the scene" mode was not observed; cards are look-only on this page. Cards 1, 2, 4 behave the same (descriptions only) |
| 8 | Start, DOWN 20, A (Return) | The hand reaches Return (a pink block is drawn behind the hand, rendering artefact worth checking) but A does not close the menu; C closes it |
| 9 | Start, DOWN 20, LEFT 45, A (Option) | The hand overshoots left of the box (the cursor is free, about 2 px per frame); Option was not hit |

Result of the round: the "use a photo on Kanna or Sumire" hypothesis was not confirmed (no held-card cursor over the scene). Still untested: Option with a shorter hold (LEFT 30), Return with a different hold, B and Start inside the item menu, the Start menu opened after looking at both characters, and giving the photo of Sakura, then closing with C.

Findings: the page has a Start command menu (Item cards with a "use on the scene" mode, Option, Return) besides the gaze cursor. Using a card on a character is the most likely way to leave the page ("You've got to stop those two!" asks for an action). Untested: each card (1-4) held over Kanna and over Sumire with A pressed while the card is shown (pass the hold with short taps of 5-10 frames), Option/Return effect, and Item use after the edge-hand line.

## Not done

bank-6, bank-7, public-7, the ground probe (`tools/tactical_ground_probe.py`) and the `hd` promotion were not attempted. No input script is committed because no state advanced past page 1.
