# EP13_EN — Delivery Note

Rendered 2026-09-03 with `tools/render_ep13_en.py`, re-rendered 2026-09-04 after
the pre-publication rights audit replaced eight stills.

## What this file is

`EP13_EN_FINAL.mp4` is the full cut: picture, narration, score and SFX, mixed to
the channel's delivery loudness.

| | |
|---|---|
| Duration | 8:08.4 (488.37 s) |
| Video | H.264, 1920x1080, 30 fps, 5.0 Mbps |
| Audio | AAC 192 kbps, 48 kHz mono |
| Size | 301 MiB |
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
rather than on a grid: 25 events, among them the pencil, the wax press, the box
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

## Eight stills replaced after the rights audit

The pre-publication licence pass found eight CC BY-SA photographs in the finished
cut. Every still is cropped and moved by the Ken Burns pass, which makes the film
Adapted Material rather than a collection of unmodified works, and ShareAlike
would then oblige the whole film to carry a licence YouTube cannot express.

Two of the eight also carried a photographer's watermark burned into the frame,
and one was a broadly smiling cardinal portrait sitting under the line "Which
brings your answer back", which was wrong for the beat on its own merits.

| Beat | Was | Now |
|---|---|---|
| moving slowly through the crowd in an open car | museum photograph of the jeep | reconstruction, the vehicle in a 1981 crowd |
| which brings your answer back | smiling cardinal portrait | a lit crucifix in a dark chapel |
| how does a bullet get into a crown | colonnade to the tower | the basilica tower |
| set into the precious crown | watermarked mosaic | the crowned statue, cropped to the crown |
| it is still there | chapel under canopy | the same chapel, CC0, already acquired |
| absorbed into an object made for devotion | watermarked relief | the apparition relief |
| here, the form was an envelope | statue in a niche | the handwritten sheet |
| the next form is much larger | flat plaza | the sanctuary esplanade |

Five replacements are new acquisitions recorded in
`02_SOURCES/COMMONS_SHAREALIKE_REPLACEMENT_MANIFEST.csv`, one is a reconstruction
from round 7, one is a CC0 file already in the acquired pool, and one is a
generated sheet that was acquired but unused.

The crowned statue was cropped to the crown and head. The line names the crown,
and the uncropped frame sat pillarboxed with the object small.

After the swap the cut contains no ShareAlike material, no unlisted material and
no non-contiguous repeats. Licences now: 22 public domain, 8 CC BY 2.0, 6 CC0,
1 CC BY 3.0.

While remixing, one dead SFX cue was found and fixed. Four keys in the effects
map still pointed at states the people pass had replaced. Three of those had a
working duplicate on the new state; the clinical corridor did not, so that sound
had been silent. The corridor tone is restored and the new crowd shot was given
the crowd bed, which is why the count is now 25 rather than 23.

## The vision act was rebuilt

Seventeen states carry the reported vision, about sixty-three seconds. Seven of
them were a pale field with a small ember on it and nothing else: V02, V07, V11,
V15, V18, V19, V20. That is thirteen percent of the film spent on frames with no
subject in them.

The cause was the same one that emptied the rooms earlier. `REGISTER_B` says
near-monochrome bone-white, one ember accent, figures small and distant with no
readable face, no horizon and no ground plane. Those are instructions for how to
render substance. Read as a description of the content itself they produce an
empty frame, and that is how they were read. The vision text is not abstract: an
angel with a burning sword, a city half in ruins, bodies on the road, a steep
mountain, a great cross, soldiers who fire, a man in white who falls and does not
get up. It is a sequence of scenes.

`REGISTER_B2` replaces it. It keeps the register otherworldly and cool, and adds
what was missing: full tonal range instead of blown-out white, real texture and
atmosphere, bodies with weight, and faces on the unnamed people around the man in
white. It states the failure test directly, that a frame which could be described
as a pale background with a small mark on it is wrong.

All seventeen were rebuilt rather than only the seven, because a register that
changes halfway through is worse than a weak one applied consistently.

Three of them changed more than their tone.

**V03** was an aerial ruined city, and the new V15 is one too. Its own line is
"He walks through a large city, half of it in ruins. He passes bodies on the
way", which is a street at his shoulder, so it became that. **V05, V06 and V08**
are the mountain sequence and had nobody climbing it, although the text says he
climbs with other bishops, priests and lay people and that they are killed with
him. Those people are in the frames now.

Nine states were renamed, because the old names described content that no longer
exists: `V18_EMBER_GOING_OUT` is now `V18_THE_MAN_DOES_NOT_RISE`,
`V19_OPEN_FIELD_WAITING` is `V19_LOOKING_FOR_YOURSELF`, and so on.

**One generation had to be rejected and redone twice.** V06 came back as a man
with long dark hair and a beard, kneeling in a white robe at a wooden cross,
which reads unmistakably as a depiction of Christ. The source says a bishop
dressed in white whom the children thought was the Holy Father, and the reveal of
this episode turns on that. The identity constraint now names the failure
explicitly: short grey cropped hair, no beard, no long hair, no halo, no bare
feet, no outstretched arms, and if the frame could be mistaken for a devotional
image of Christ it is wrong. V18 was regenerated for the same reason.

Faces of the man in white were checked at full resolution in V02, V06 and V18
after the rebuild. None is readable.

## The camera moves were juddering

They juddered because this renderer carried its own zoompan implementation. The
visual standard forbids that in as many words, and requires the shared engine in
`tools/smooth_still_motion.py`, which is what EP07 uses and what the channel owner
named as the reference for motion that does not judder. Writing a private motion
path was the original mistake, and every repair before this one was applied to a
construction that should not have existed.

`render_ep13_en.py` now imports `eased_zoompan_filter` and does no camera
arithmetic of its own. The engine supersamples to 7680x4320 rather than
3840x2160, so its position quantum is a quarter of an output pixel instead of a
half.

**A measurement mistake made this take three passes.** The first metric counted
frames that did not change at all, which said the fix had worked while the moves
still visibly stuttered. It was the wrong question. A one pixel hop every second
frame passes that test. The right measurement tracks an off-centre patch of the
picture and reports how evenly it advances, and by that measure the private path
was moving 0.31 px per frame with a standard deviation of 0.34, swinging between
0.05 and 1.21 px. The variation was larger than the motion.

| | private path | shared engine |
|---|---|---|
| supersample | 3840x2160 | 7680x4320 |
| position quantum | half an output pixel | a quarter |
| step irregularity, sd over mean | 1.10 | 0.63 |
| step range | 0.05 to 1.21 px | 0.011 to 0.288 px |

**Amplitude, and why the middle is the worst place to be.** With the engine, the
per-frame step becomes more even as the amplitude grows: sd over mean is 1.16 at
zoom 0.017, 0.94 at 0.023, 0.71 at 0.043 and 0.58 at 0.070. EP07 uses 0.017 and
reads as clean anyway, because at 0.087 px per frame the move is too small for
its unevenness to be visible at all.

So there are two safe places and a bad one between them: subliminal, or fast
enough that the steps are as even as this pipeline gets. EP13 sat in the middle
at 0.043, visible enough to notice and uneven enough to stutter. It now uses
EP07's range, 0.010 to 0.023 scaled by shot length, median 0.014.

**Sources that are not 16:9** are composited to a 16:9 plate first, with the
blurred darkened background this channel uses, and the engine then sees an
ordinary 16:9 image. The engine letterboxes to black on its own, so this keeps
the look without modifying shared code.

**Five stills are locked** and hold still: the Duerer engraving, the 1917
photograph of the three children, the newspaper stack, the calendar pages and the
archival photograph of the first sculpture. Fine line work and old photographic
grain shimmer when moved a fraction of a pixel per frame, no encoder setting
touches that, and the standard already asks registration-sensitive frames to hold
still. Shots under 0.35 s hold still as a rule: nobody sees a camera move in seven
frames.

That leaves 102 moving stills, 10 cards, 5 locked stills, 1 short lock and 7
native clips. `tools/qa_smooth_still_motion.py`, which the standard requires and
which had never been run on this episode, passes with no failures. Its report is
kept at `08_QA/EP13_EN_SMOOTH_MOTION_QA.json`.

## Render progress is visible

`python tools/render_ep13_en.py status` reports finished and outstanding
segments, throughput and an estimate, and is safe to run while a render is in
progress: the cache is written after every segment rather than at the end.

## Picture runs 0.07 s short of the voice

Frame counts are exact integers, so the picture lands at 488.30 s against a
488.37 s voice master. The last audible syllable is at 488.07 s, which leaves
0.23 s of tail. Nothing is clipped.

## Four faults found on viewing, and fixed

**A clip was looping.** `CLIP09_PUTTING_IT_AWAY` is a 6 s clip on a 7.2 s shot,
and the renderer filled the gap with `-stream_loop -1`, so the action restarted
and the first 1.2 s played a second time. That is now impossible: a clip shorter
than its shot is slowed to fit, up to 1.35x, and beyond that holds its last
frame. A clip is a performance and never begins again inside one shot.

**The box in that clip opened from both sides**, which no box does. Regenerated
with one lid hinged along its far edge: the sheet goes in, the lid swings down,
the hands settle on it.

**The seal was pressed on its edge** like a coin being stood up. A seal matrix is
pressed face down, flat and parallel to the paper. Third attempt at this shot, so
the geometry is now stated before anything about mood, and it is correct.

**Eight document states were blank.** Three empty white sheets on a table,
envelopes with no writing on them, a page and an envelope with nothing on either.
Blank paper does not read as a document, it reads as a placeholder, and this
episode is about a document. The cause was an over-correction: an earlier pass
was rejected for parchment carrying readable pseudo-names, so the prompts started
asking for no text at all. The actual requirement is narrower, that nothing
resolves into readable words.

All eight were rebuilt with ink on them. Two had to be done twice: the first
attempt put a large, sharp, level address across the envelope, which always
resolves into pseudo-words, and one of them wrote out the English label from the
prompt. They were redone with the writing small, steeply foreshortened and
falling out of focus, with the wax seal as the sharp element.

## An end screen hold was missing

The film ended 1.3 s after the closing line, which left YouTube nowhere to put
its subscribe badge and next-video thumbnail. There is now a 20 s held card after
the narration: `CARD11_END_SCREEN`, dark wood with everything written in the left
third and the right half deliberately bare for those elements. The score returns
to the texture of the cold open and fades out over the last seven seconds. No
narration runs under it.

Runtime is 8:28.3, from 8:08.4.


## Repeated images

None. 125 segments resolve to 125 distinct state ids and 125 distinct files, so no
asset appears twice. Checked further for images that merely look alike, comparing
a frequency signature and a coarse colour layout for all 7,750 pairs: the highest
similarity in the film is 0.52, between two cards that share the same typographic
design by intent. Nothing approaches a perceptual duplicate.

## Still open before publication

1. an aloud review of the narration, which is a judgement only the channel owner
   can make;
2. `C15` in the source lock: the 1989 setting of the projectile into the crown is
   corroborated only by secondary sources, and a second search on 2026-09-04
   found the sources also disagree about when the projectile was handed over. It
   is disclosed in the published description.
