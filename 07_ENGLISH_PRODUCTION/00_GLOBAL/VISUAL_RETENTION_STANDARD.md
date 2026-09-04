# Visual Retention Standard — English Editions

The English editions are new picture edits. They are not dubbed copies of the
German masters.

## Retention targets

These are diagnostic targets, not automatic failure conditions. A deliberate
exception is allowed when the finished viewer experience is stronger.

- The opening image changes as soon as the hook benefits from a new state; 2.5
  seconds is a useful diagnostic reference, not a timer to obey.
- First verifiable reality anchor normally by 15 seconds; exact source timing is
  defined per episode.
- Usually 16–22 meaningful visual changes in the first 60 seconds; no quota cuts.
- Static or nearly static shots normally live around 3–6 seconds. At roughly 8
  seconds, review whether new information, genuine movement, or rising tension is
  still arriving. Around 10 seconds is a rare upper edge, not an automatic cutoff.
  A longer hold needs visible internal development and a specific viewer reason;
  a slow zoom, crop, pan, or grade change alone is insufficient.
- No quantity quota, but every later visual is new: once an asset leaves the
  timeline, it does not return.
- No motion quota. Plan the smallest set that makes the episode materially better;
  the aligned story decides both clip count and moving-image coverage.
- Avoid every non-contiguous return of the same image or clip state.
- Reopen attention before a section feels settled. A mode change around 20–30
  seconds can help, but a strong unresolved image may hold longer and a dense
  passage may change faster.

## New-material rule

Each English episode receives only the new hero images, localized cards, document
crops, and motion moments its aligned cue sheet actually needs. German assets may
be reused when they are:

1. authentic archive material or an original document;
2. already language-neutral;
3. among the strongest images in the German master; and
4. not being reused to compensate for missing coverage.

A visual callback uses a genuinely new asset or a visibly advanced state. It never
replays the earlier export.

## No-return picture rule

The same still, document render, card export, or clip state may occupy several
adjacent voice cues as one continuous timeline block. After the edit leaves that
asset, it may not return later. A new crop, zoom, pan, grade, overlay, or filename
does not turn the same underlying image into a new motif.

A callback must use a genuinely new source, viewpoint, action, composition, or
visibly advanced state. Recurring people, machines, and locations keep continuity
through new images rather than repeated frames. A motion clip may be divided into
consecutive progressive states, but it may not restart later in the episode.

The audit also checks perceived repetition inside one continuous sequence. New
filenames or slightly different poses do not create visual variety when person,
room, framing, lighting, and screen balance remain substantially unchanged. A
matched comparison may briefly preserve those variables to make the comparison
legible; once that point is clear, the edit changes coverage through meaningful
macro detail, action, source evidence, anatomy, environment, laboratory context,
or another clause-aligned viewpoint before the sequence feels like variants of
the same card.

The rule also applies across the English series. A final still, card, or clip
export used in one episode cannot appear in another. Recurring people and subjects
receive a different authentic image, document detail, viewpoint, or scene. A
series-wide content-hash registry records the single episode that owns each asset.

## Internal visual modes

- `ARCHIVE`: identity, place, date, and historical reality.
- `ORIGINAL DOCUMENT`: the actual line that creates the story.
- `RECONSTRUCTION`: human action unavailable in archive material.
- `EXPLANATORY MODEL`: a mechanism, test, comparison, or statistical result.
- `INNER / HYPOTHESIS`: abstract, mystical imagery that makes a reported
  experience or unconfirmed theory emotionally visible.

These names live in manifests and cue sheets, not as permanent on-screen labels.
`INNER / HYPOTHESIS` is never burned into the film. At most, use one brief subtle
disclosure when a continuous reconstruction block first begins.

## Motion policy

Motion clips exist to explain, transform, or emotionally embody an idea. Pure
atmosphere may support a transition, but does not count as a core motion moment.
Each core clip needs a beginning, a change, and a resolved state that matches a
spoken beat.

One well-designed clip may supply several timeline shots or progressive states.
Generate an additional clip only when the aligned cue sheet exposes a real coverage
gap that cannot be solved by archive, a strong still, crop movement, or an existing
clip state. Cost and visual coherence outrank an arbitrary quantity.

Preferred forms:

- cinematic raster composites or generated explanatory imagery with a small,
  controlled overlay layer for tests, mechanisms and comparisons;
- controlled document reveals and line highlights;
- restrained historical reconstructions with one clear action;
- transformative clips where an idea changes state;
- surreal visual metaphors for altered time, disembodiment, intention, and
  autonomous inner imagery;
- one deliberate near-silent visual hold before the largest payoff.

Viewer-facing procedural SVG geometry is not the default explanatory layer.
Boxes, arrows, circles and charts may be added as restrained editorial overlays
to a strong image, authentic source or carefully built raster scene. A full-screen
shape card is allowed only when its visual quality and explanatory speed are
clearly stronger than an image-based solution. Generated scans, charts, documents,
microscopy, molecule structures and embedded labels are never evidence.

## Mixed-media picture grammar

The strongest prior episodes use a changing combination of visual worlds rather
than one repeated mode. Each episode therefore builds its own rhythm from:

- human faces, bodies and concrete action;
- authentic archive, portraits, objects and original documents;
- scientific anatomy, laboratory context and measured evidence;
- episode-specific mystical, symbolic or subjective imagery;
- genuine motion clips for actions, transformations and perceptual changes;
- brief cards or overlays only when words, one number or one distinction are the event.

This is not a percentage quota. The retention review asks whether one visual world
has dominated long enough for the episode to feel monotone. Documents establish
proof and context, then the edit returns to people, action, place or a meaningful
visual transformation. Cards clarify; they do not substitute for missing pictures.

## Anatomy and scientific-image gate

Every medical or anatomical image is reviewed for orientation, scale, number of
structures and the exact spoken claim before it enters a proxy. For the pineal
series specifically, the gland must appear as one small midline structure near the
roof of the third ventricle. Bilateral-looking highlights, multiple ambiguous
markers, oversized glowing regions or labels pointing to different structures fail.

Use verified anatomical references for location claims. Generated anatomy may
support a clearly illustrative transition only after comparison with the reference;
it may never become the sole evidence for the location, structure or mechanism.

Mystical imagery should be specific to the episode. It may be bold, beautiful,
and temporarily overwhelming. It must not resemble generic meditation stock,
fantasy game art, or a literal reenactment presented as proof. The transition
into and out of `INNER / HYPOTHESIS` must be visually legible.

## Technical smooth-motion gate

Creative motion remains episode-specific. Camera judder is a delivery defect,
not a creative choice. Every still-image push, zoom, pan, or compound move must
use the shared supersampled/subpixel motion path in `tools/smooth_still_motion.py`
or an independently demonstrated equivalent. A render script may not introduce
its own delivery-resolution `zoompan` implementation merely for convenience.

Before a picture master can pass:

- moving-still segments are rendered at the delivery frame rate from a
  supersampled or true subpixel path;
- **the ramp does not reach zero velocity.** Measured on EP13 on 2026-09-04: a
  smoothstep ramp froze 26 of 179 frames on a six second shot, because a ramp
  that eases to a stop must hold the picture still while it does. A linear ramp
  on the same shot froze none. "Continuous easing" is not the requirement and
  never was; constant velocity is. Ease the cut, not the move;
- **the move is fast enough to clear the pixel grid.** zoompan lands its crop on
  whole pixels of the working image, so on a 3840 px working width one step is
  half an output pixel. A 3 percent zoom over six seconds advances about 0.3
  output pixels per frame, which is below that step: the picture sits still, then
  hops. Scale the amplitude to the shot length so apparent speed is constant
  rather than fixing one amplitude for every duration. EP13 uses 0.0083 zoom per
  second, clamped to 1.5 and 9 percent, and holds zero frozen frames from 1.0 s
  to 9.1 s;
- **temporal supersampling is a quality dial, not a fix.** It cannot smooth a
  move that never crosses a pixel boundary, because every sub-position rounds to
  the same pixel. Fix the ramp and the amplitude first, then raise it if the
  cadence gate is still marginal. EP13 needed 8 sub-samples to clear the last ten
  of 108 shots;
- every still in a JSON visual EDL explicitly declares `motion`, `motion_mode`,
  or `motion_amplitude`, so QA can distinguish deliberate locked frames from
  moving frames instead of guessing from compressed pixels;
- documents, diagrams, cards, eye instructions, and other registration-sensitive
  frames remain locked unless motion itself communicates new information;
- the rendered segments are checked with `tools/qa_smooth_still_motion.py` and
  any cadence failure is inspected at full speed, not waived from a contact sheet;
- the final concatenated master is constant-frame-rate and contains no accidental
  duplicate/drop cadence at segment boundaries;
- a new episode may reuse the shared engine, but it may not assume that an older
  episode's successful QA automatically covers a new renderer or new segments.

Judder is measurable and must be measured, not eyeballed. The number that matters
is how many frames do not change at all, taken from raw frames rather than from an
encoded file, and how much the frame-to-frame change varies. Phase correlation is
the wrong instrument for a centred zoom: it measures translation, a centred zoom
has none, and it will report noise.

This gate is intentionally technical. It does not prescribe how many shots move
or impose a visual style; it prevents the recurring pixel-rounding judder that is
visible during otherwise slow camera motion.

## Render-economy preflight gate

Do not discover ordinary layout, crop, text-safe-area, face/hand, or document
problems after an expensive full-length master render. Before the delivery encode:

- render every unique procedural state and a representative frame from every
  still/video state as a cheap proxy or source-resolution frame;
- inspect a full contact sheet plus denser sheets for the hook, documents, cards,
  generated faces/hands, and previously weak retention windows;
- check viewer-facing text at mobile size and verify that highlights preserve the
  complete relevant sentence or paragraph;
- run smooth-motion QA on the final moving-still derivatives before they enter the
  master;
- prefer cached, segment-based assembly so an isolated correction invalidates only
  the affected segment and downstream concat, not every frame in the episode.
- review a real-time audiovisual proxy of every rewritten retention window; a
  contact sheet cannot verify whether the picture arrives on the correct word.

A monolithic full-frame renderer remains allowed when it is genuinely the best
implementation, but its complete proxy/contact-sheet preflight must pass first.
Successful encoding alone never justifies a second avoidable full render.

## Episode-selected QA

- hook contact sheet when it materially helps judge the opening;
- representative full-episode contact sheet or timeline review;
- mobile-text check at 246 px width;
- repetition report by source asset and semantic motif;
- zero non-contiguous asset returns, verified by asset ID, content hash, and a
  perceptual near-duplicate review;
- zero reuse of final content assets across episode manifests;
- longest static hold plus a reasoned review of every hold at or above 8 seconds;
- reconstruction/source distinction check without persistent badges;
- source-to-spoken-claim check;
- motion review using the frames needed to verify its actual transformation.

The episode owner selects the lightest QA package that can reveal real viewer,
rights, continuity, or comprehension problems. QA artifacts are not deliverable
quotas.
