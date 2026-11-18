# Scene display: optional Zoom

Keep the current joint composition as the Original option and add Zoom to Display settings. Narrative scenes only, recognized in Enhanced presentation. Image on top and dialogue below, both with independent integer scales. Reserve a four-native-pixel right/bottom shadow and a visible gap. HD text/portrait uses the dialogue projection. If it doesn't fit, or the scene has elements outside the known region, keep the joint composition.

First verify pure layout at 720p, 1080p, 1440p, 2160p and ultrawide; then a real 1440p capture of both modes and the absence of cropping/overlap. Record a reproducible patch and keep v0.1.5 intact.


## Implementation

Settings > Display > Scene display: Original / Zoom. Original is the default and keeps the joint group. Zoom uses a 288×144 image on top, a four-native-pixel shadow, and a dialogue with a scale independent from the window's background. At 2560×1440: image ×7 (2016×1008), shadow 28, gap 2, and dialogue ×6 (1836×402, y1038). The shadow is drawn before the dialogue, which keeps visual priority. Only the native image-shadow remainder identified in layer 3, x20–307, y153–155, is removed; the box's own frame and shadow are kept.

Requires a recognized scene, with no upper art outside the safe rectangle; other scenes keep the joint composition. Geometry tested at 720p, 1080p, 1440p, 2160p and ultrawide. Real 1440p capture compares the exact native image between ×6/×7 and identical text mask to ×6. The shadow fix changes only (482,1038)–(2156,1056) versus the previous capture.


## Margin adjustment approved by visual direction

Zoom now compacts the two visible blocks and centers the set vertically. The gap is one unit of the dialogue scale (minimum 2 pixels); the image shadow can go behind the box. When computing the scale, outer margin is reserved, keeping integer scales and no cropping. At 2560×1440 it keeps image ×7 and dialogue ×6: top margin 12, image y12–1020, gap 6, dialogue y1026–1428, bottom margin 12. Original is unchanged. Geometry verified at 720p/1080p/1440p/2160p/ultrawide and width 2044; real capture and image/text-ink pixel-equality test correct.


## Downward shift

The Zoom set moves down by up to three dialogue-scale units, limited by the bottom edge. At 1440p it moves down 18 pixels: top margin 30, image y30–1038, gap 6, and dialogue y1044–1446. Hiding a bottom native row is only allowed when the framebuffer source confirms it contains shadow/background; if there is content or a frame, the downward shift is limited to the screen edge. Scales ×7/×6 and Original are preserved. Geometry and real image/text comparison verified; local capture lowered.png.


## Final dialogue gap

Only the dialogue is lowered by half a scale unit (3 pixels at 1440p), with no image movement. The gap goes from 6 to 9; the box starts at y1047. The runtime identifies up to two final rows that are exclusively shadow/background and limits the shift to protect the frame and content. Image y30, scales ×7/×6, and Original mode preserved. Geometric fixture and real image/ink comparison correct; capture dialogue-lowered.png.


Final Zoom composition confirmed: image and shadow move up 1 output pixel; dialogue and shadow move down 1, within the croppable shadow limit. At 1440p: image y29, dialogue 1048, gap 11; scales ×7/×6. Geometry and real image/text capture approved.


Later confirmed limit: 16:9 maximum. FitInteger and Zoom compute over a bounded width; the renderer centers a 16:9 area with side bars on wider surfaces. Backgrounds use that same area. Real test verifies black bars and a center equivalent to 2560×1440 (tolerance 2 HD-font coverage levels). Ultrawide is not offered as a play mode.
