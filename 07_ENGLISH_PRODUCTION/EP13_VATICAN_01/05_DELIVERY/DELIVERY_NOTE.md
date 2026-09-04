# EP13_EN — Delivery Note

Rendered 2026-09-03 with `tools/render_ep13_en.py`.

## What this file is

`EP13_EN_FINAL.mp4` is the full cut: picture, narration, score and SFX, mixed to
the channel's delivery loudness.

| | |
|---|---|
| Duration | 8:08.4 (488.37 s) |
| Video | H.264, 1920x1080, 30 fps, 5.0 Mbps |
| Audio | AAC 192 kbps, 48 kHz mono |
| Size | 307 MB |
| Loudness | −14.3 LUFS integrated, −1.1 dBTP, LRA 2.1 |

This matches the channel's existing masters, which sit at −14.0 LUFS and −1.0
dBTP. Do not normalise the file again.

## Score and SFX

Both are project-owned deterministic synthesis built by `tools/build_ep13_audio.py`,
following the channel's existing audio approach: no third-party recordings and no
library stingers.

The score is sectional rather than a single drone, which the standard requires.
Eleven sections follow the act turns and use five textures: `object` for the
crown and the cold open, `paper` where the episode handles documents, `held` for
the waiting passages, `pressure` for the attack and the handoff, and `vision`,
which is the only section that opens above the bass register.

SFX are placed from the cue sheet, so each one lands on the state it belongs to
rather than on a grid: 24 events, among them the pencil, the wax press, the box
lid closing, keys, the crowd turning, the clinical room tone, metal seals, the
scale weights and the cart. Both beds are sidechained under the narration, the
score at 62 percent depth and the effects at 45.

Gain is measured and corrected across up to four passes with the true peak
checked each time, because limiting costs loudness and a single loudnorm pass
lands about a decibel short.

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

## People in the reconstructions

An earlier version of this episode had almost no human beings in it. The
constraints that produced that are real but narrow: the bishop in white must stay
unidentifiable because the reveal depends on it, and no likeness of John Paul II,
Lucia, John XXIII, Paul VI, Sodano or Agca may be synthesised. Those were
generalised into a blanket ban, written as "no face" eighteen times and "no
person" twelve times across 54 prompts, and the result was an episode of empty
rooms.

The line that actually applies, and now does:

| | |
|---|---|
| named historical figure | their real photograph only, never generated |
| the bishop in white | stays unidentifiable |
| everyone else | ordinary people with visible faces |

Fourteen states were rebuilt with people: the nurse at the bedside, the archivist
lifting a box, two crowds with readable faces, a congregation waiting, two men
talking, pilgrims at the candles, shepherd children, a clerk in a corridor, the
1981 press with period-correct SLR bodies, the handover of the envelope, a woman
writing in 1944, doctors in a corridor and a man alone in a pew.

Reference images were supplied for period accuracy only, with the prompt stating
explicitly that no face from a reference may be reproduced.

## Still open before publication

1. thumbnail;
3. an aloud review of the narration, which is a judgement only the channel owner
   can make;
4. `C15` in the source lock: the 1989 setting of the projectile into the crown is
   corroborated only by secondary sources;
5. upload metadata, description and tags.
