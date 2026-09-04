# EP13_EN — Production Completion Report

*The Third Secret of Fatima: Why a Bullet Sits in Her Crown* — Vatican Files 1 of 5.
Completed 2026-09-04.

## State

The master is finished and the upload package is written. One item is open, and
it is a judgement rather than a task: nobody has listened to the narration end to
end. Everything that can be checked mechanically has been.

## What was built

| Stage | Result |
|---|---|
| Script | 1,342 words, 8:08 at delivery pace |
| Sources | 15 claims live-checked; 14 locked, 1 secondary only |
| Originals acquired | 253 candidates, 37 in the cut |
| Reconstructions | 9 generation rounds, 71 stills and 7 clips in the cut |
| Cards | 10, composited on generated material substrates |
| Voice | ElevenLabs, blind-transcribed back with Scribe for content QA |
| Timing | forced alignment; every state bound to a word range |
| Picture | 125 segments, sub-pixel Ken Burns |
| Audio | 11 sectional score passages over 5 textures, 25 placed effects |
| Master | −14.3 LUFS, −1.1 dBTP, 301 MiB |

## Checks that passed

| Check | Result |
|---|---|
| Non-contiguous repeat of any state | none |
| Beats without an assigned state | none |
| Holds at or beyond 8 s | one, reviewed and justified |
| Picture against voice duration | 488.37 s against 488.37 s |
| Unresolved states at render | none |
| ShareAlike or unlisted material in the cut | none |
| Attribution present for every CC BY file | yes, in the description |
| Named figures synthesised | none |
| Thumbnail legibility at 25 and 18.75 percent | pass |
| Shared cadence gate, 102 moving stills | pass |
| Frozen frames in the delivered master | 3 of 1301 sampled |
| Repeated or near-duplicate images | none; highest pair similarity 0.52 |
| Title length against mobile truncation | 58 characters |

## Things that were wrong and were fixed

Recorded because the pattern is more useful than the individual fixes.

**The episode had almost no people in it.** Three real constraints — no likeness
of a named figure, the bishop in white must stay unidentifiable, no imitation of
Lucia's hand — were generalised into a blanket ban written as "no face" eighteen
times across 54 prompts. The result was a film of empty rooms. Fourteen states
were rebuilt with visible faces once the rule was narrowed to what it actually
says.

**Eight stills in the finished cut were CC BY-SA.** Found in the pre-publication
audit, after the master had already been rendered and mixed. Ken Burns makes the
film Adapted Material, so ShareAlike would have applied to the whole film. All
eight were replaced and the film was re-rendered. Two of them also carried a
photographer's watermark, which had been sitting in the master unnoticed.

**The vision act was seven empty frames.** Thirteen percent of the film was a
pale field with an ember dot on it, because the vision register's rendering
instructions were read as a description of the content. All seventeen vision
states were rebuilt with depth, texture and human bodies. Two of them had to be
generated three times: the model kept returning the man in white as a
long-haired, bearded figure kneeling at a cross, which reads as Christ and
destroys the reveal.

**The camera moves juddered.** Two arithmetic causes. A smoothstep ramp reaches
zero velocity at both ends, so it has to hold the picture still while it eases,
and a fixed 3 percent zoom advances 0.29 output pixels per frame, which is below
the pixel grid zoompan lands on. Measured: 26 of 179 frames on a six second shot
did not change at all. A linear ramp with the amplitude scaled to the shot length
brings that to zero, and the delivered master now measures 3 frozen frames in
1301. The shared cadence gate, which the standard requires and which had never
been run on this episode, now passes.

**A sound effect had been silent since the people pass.** Four cues pointed at
states that no longer existed. Three had working duplicates; the clinical
corridor did not.

**The voice read "John XXIII" as "John the Thirteenth".** Caught by diffing the
blind transcription against the script. Ordinals are now spelled out, and the
same sweep was applied to EP14 through EP17.

**The state count was inflated.** An earlier report claimed 88 images. Clips
replace the stills they were generated from, and roughly eighteen acquired
originals do not serve the script. The honest figure at that point was 58.

## The one claim that is not locked

`C15`: that the projectile was set into the crown in 1989.

The Shrine confirms the projectile is in the crown. It gives no date, no donor
and no account of how it arrived, and the Holy See has published nothing on it.
Secondary reporting is consistent on 1989 and inconsistent on the handover, which
some accounts place at Fatima on 13 May 1982 and others in 1984. Two searches
found no primary source.

The script is already written around this: it names no donor, no recovery
location and no handover date. The published description says plainly that the
year rests on secondary reporting. Changing the line costs one narration take,
one segment and a remix, and that option stays open.

One detail was verified independently rather than taken on trust. The secondary
accounts place the projectile at the junction of the eight arches beneath the
sky-blue orb, and that is exactly where the dull grey cone sits in the licensed
photograph. It is the reason the thumbnail rings that spot.

## Handoff

EP14 picks up the 1530 letter: eighty-three signatures, eighty-one seals, a pope
who refused, and an archive partly carried over the Alps and sold by weight.
