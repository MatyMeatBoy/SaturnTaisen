# BG1331 bounded HD hatch room

The PC plate depicts the same room under darker lighting and loses
part of the right and lower edges once aligned. The bounded Enhanced
composition keeps the native perimeter and all foreground sprites.
It registers the in-bounds PC overlap at 2x, corrects the low-frequency
tone to the native room, and returns gradually to the native floor
between rows 103 and 115.

The archived disc 1 MAP07 hatch checkpoint identifies the layer and
proves ownership of the pointer-composited frame. Source 2 uses page
0x40000, palette C9D2219DDED2655D, cell key 306786D0EE296458 and
a native RGB offset of -16. The offline render
changed 119,424 eligible 2x pixels and preserved all foreground,
matte and out-of-range donor pixels. Mean seam gradient deviation
fell from 7.27 levels with a hard cut to 2.95 at the lower transition.

Registration shares the asynchronous preparation and the draw-time
ownership check of [BG1338](bg1338-bounded-hd.md). A linked HD comparison,
disc 2 and packaging remain pending.
