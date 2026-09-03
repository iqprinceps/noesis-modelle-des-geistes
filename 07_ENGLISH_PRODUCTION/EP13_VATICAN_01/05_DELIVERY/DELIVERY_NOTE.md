# EP13_EN — Delivery Note

Rendered 2026-09-03 with `tools/render_ep13_en.py`.

## What this file is

`EP13_EN_FINAL.mp4` is a **picture master with narration**. It is not the final
audio mix: there is no music bed and no SFX. Per the render orchestrator, score
and effects belong to the episode audio workflow, which has not run yet.

| | |
|---|---|
| Duration | 8:08.4 (488.37 s) |
| Video | H.264, 1920x1080, 30 fps, 5.0 Mbps |
| Audio | AAC 192 kbps, 48 kHz mono |
| Size | 307 MB |
| Loudness | −18.3 LUFS integrated, −2.0 dBTP, LRA 2.2 |

Loudness matches the pipeline that produced the published EP05 master. It sits
below YouTube's −14 LUFS target on purpose; the music mix is where that is
closed. Do not normalise this file on its own.

## How it was built

The cue sheet binds every visual state to a word range from the forced
alignment, so no timing is estimated. 134 states across 115 spoken beats, 125
rendered segments after contiguous holds are merged.

Camera technique is taken from `tools/noesis_render.py`: the source is scaled to
3840x2160 before zoompan outputs 1920x1080, so one integer position step is half
an output pixel, and four temporal sub-positions per frame are averaged with
tmix. That keeps the sub-pixel move smooth and avoids pixel-rounding judder.

The episode profile is deliberately calm: zoom amplitude 3 percent, 1.2 percent
on short holds. This episode is carried by objects that should be looked at
rather than swept. Cards do not move at all. Clips run natively with no camera
added on top.

## Checks

| Check | Result |
|---|---|
| Non-contiguous repeat of any state | none |
| Beats without an assigned state | none |
| Holds at or beyond 8 s | one, reviewed, see below |
| Picture against voice duration | 488.37 s against 488.37 s |
| Black frames or gaps | none detected |
| Unresolved states at render | none |

**The reviewed hold.** `CARD03_TWO_POPES` runs 9.1 s at beat 30. The card carries
three lines the viewer has to read: 1959 John the Twenty-Third reads it, 1965
Paul the Sixth reads it, neither publishes it. The standard asks for a review
past 8 s rather than forbidding it, and the reading time justifies the hold.

## Two failures found during the render, both fixed

**Missing pause coverage.** The first pass produced 476.6 s of picture against
488.4 s of voice, and `-shortest` would have cut the last twelve seconds of
narration. The segments covered only the spoken beats, not the 67 pauses between
them. A picture now holds through the pause that follows its beat, and the last
shot runs to the end of the voice master.

**An SVG in the asset chain.** The Portugal locator map is a vector file and
ffprobe reports its dimensions as zero, which crashed the renderer at segment 91.
It was replaced with the calendar-pages state, which serves that beat better than
a map: the question there is when a prophecy counts as fulfilled, which is about
time rather than geography.

## Still open before publication

1. music and SFX pass, then a final mix at the channel's delivery loudness;
2. thumbnail;
3. an aloud review of the narration, which is a judgement only the channel owner
   can make;
4. `C15` in the source lock: the 1989 setting of the projectile into the crown is
   corroborated only by secondary sources;
5. upload metadata, description and tags.
