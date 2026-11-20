# Bounded PC video on the Saturn film timeline

The six alternate PC cinema edits have matching footage at measured points
and cuts that differ from the Saturn sequence. Enhanced uses the matching
PC picture while the ordinary FILM stream continues to run in the guest.
Saturn supplies the audio for the entire alternate film. The presentation
keeps Saturn picture during its fades, during gaps in the PC correspondence,
after the last matching cut and when a state is loaded partway into a film.
Original displays the Saturn film.

The runtime keys each entry by Saturn disc and CD Play range. The first
complete native film plate supplies the guest-field origin. The PC decoder
is prepared before the next span while Saturn remains visible. The code
requires an unmodified native film plate before presenting the PC frame.
For the NBG3 fade, that includes the captured full film-weight case in which
the top floral layer contributes zero. The existing 44 full PC clip entries
retain their picture and audio path.

## Registered spans

Intervals use inclusive starts and exclusive ends. Guest fields are
relative to the first complete film plate. PC positions are decoder
milliseconds. The FAD in the table is the native FILM header.

| Disc | Movie | FAD | Guest fields | PC milliseconds | Saturn footage |
| --- | --- | --- | --- | --- | --- |
| 1 | MOVIE004 | 0x736D | [0, 3413) | 0–57155 | Opening fade and last tunnel shot |
| 1 | MOVIE009 | 0xC0AD | [0, 1226), [1524, 2621) | 0–20520, 24530–42875 | Internal edit and final shot |
| 1 | MOVIE011 | 0xE8A1 | [0, 649), [1107, 2202) | 0–10777, 17400–35735 | Opening fade, internal edit and final shot |
| 1 | MOVIE020 | 0x1556A | [0, 1185) | 0–19800 | Opening fade and Saturn radar continuation |
| 2 | MOVIE102 | 0x34BB | [0, 1185) | 0–19865 | Opening fade and final robot shot |
| 1 | MOVIE105 | 0x17081 | [778, 1396) | 12020–22355 | Opening and final shot |
| 2 | MOVIE105 | 0x6DE7 | [777, 1396) | 12020–22355 | Opening and final shot |

The map is [film-video-spans.json](../../config/film-video-spans.json).
[The table generator](../../tools/gen_film_clip_table.py) checks that the
edits refer to unique alternate cuts in the film catalog and that the
time ranges are ordered and within both source durations. The runtime
checks the donor's file size against the measured PC edition. Setup
copies the player's PC assets to the private HD pack.

## MOVIE004

The natural English disc 1 Chapter 1 run reaches CD Play 0x736E.
The first complete plate is field 38 in the relay. The first native
frame of the last tunnel shot is field 3451, identified against the
native Cinepak decode. The A/B matches 3,750 guest hashes and has
zero interpreted blocks. The opening fade and all sampled frames
beginning at 3451 are RGB-exact. During the replacement, the only
changed area is the film plate at (64,112)–(640,400) in the 704 × 512
window.

Local fixtures are in local/work/codex-th1/movie004-live. The replay
uses route/137970.state, its backup.bin and the suffix of the archived
Chapter 1 earned-route/input.movie at field 257750.

## MOVIE011

The natural English disc 1 Chapter 3 route resumes immediately after
Kanna and advances to battle entry. The guest opens the source at 0xE8A2,
and the first complete plate is field 2057. Independent source-frame
matches put the cut points at fields 2706, 3164 and 4259. The 5,150-field
route A/B preserves all guest hashes. The native bridge and tail match
RGB exactly. Replacement changes stay in (96,108)–(1824,972) at
1920 × 1080. Original, absent-donor and mid-film resume runs match
their native controls. Original and absent-donor runs each preserve
2,440 fields and 13 RGB samples. Mid-film resume preserves 500 fields
and three RGB samples. The existing full-replacement MOVIE001 path
opens its donor and preserves 1,800 guest fields and six RGB samples
against the prior runtime.

At normal speed a 2,440-field replay before the same Play preserves
1,800,457 stereo Saturn PCM sample frames. The guest dump on this
route has SHA-256
c88aa608714d40003e53956f9655d24d2ef238c40e5deb8a3a1f604793bf3ea6.
The host trace shows the Saturn stream throughout. Nine 2,048-sample
windows from 2 to 37 seconds also match the guest samples in each
SDL disk-device capture. Device captures have independent queue
timing.

Local inputs are the archived local/work/codex-th1/bg2290-live/chapter3-resume-after-kanna
state and backup, and chapter3-battle-entry/input.movie. The replay
can also resume immediately before Play from field 2040 and shift the
same input movie by 2040 fields.

## Controlled playback

The other four movies were played through the native game decoder
by redirecting two big-endian archive offsets in private save copies.
The disc and film content stay intact. The ordinary film Play
command opens the exact target FAD and the baseline and candidate
follow the same guest route after the redirect. The Chapter 3 pre-Play
state supplies the disc 1 fixture, and the disc 2 theatre boot before
MOVIE100 supplies the disc 2 fixture.

| Movie | Disc | Strict guest fields | Measured handoff fields in the fixture |
| --- | ---: | ---: | --- |
| MOVIE009 | 1 | 3040 | 1244, 1542, 2639 |
| MOVIE020 | 1 | 2150 | 1201 |
| MOVIE102 | 2 | 1540 | 1219 |
| MOVIE105 | 1 | 1760 | 794, 1412 |
| MOVIE105 | 2 | 1800 | 812, 1431 |

All five fixture comparisons have identical guest hashes and
zero interpreted blocks. Sampled replacement windows change only the
film plate. Native gaps and immediate shot boundaries are checked in RGB.
Near the MOVIE020 seam, adjacent native plates at fields 1200 and
1201 are identical. The PC plate aligns to the same stationary map,
with mean RGB (47.14, 92.80, 45.64) versus Saturn's (44.85, 99.17,
43.53). The native radar continuation retains the original positions,
duration and sequence.

Natural story encounters for the four controlled movies and package
inclusion remain separate verification work.
