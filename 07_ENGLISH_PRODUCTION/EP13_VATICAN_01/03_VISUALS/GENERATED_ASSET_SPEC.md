# EP13_EN — Generated Asset Specification

Generated 2026-09-03 with Vertex AI on the secondary profile.
Image model `gemini-3-pro-image` (Nano Banana Pro), 2K, 16:9.
Video model `veo-3.1-generate-001`, 1080p, 24 fps, 6 s, no audio.
Generators: `tools/generate_ep13_vertex.py`, `tools/generate_ep13_veo.py`.

## The two registers

EP13 turns on a distinction the pictures have to carry on their own: what is
documented, and what somebody reported seeing. If the vision looks like footage,
the episode has lied. So the reconstruction runs in two registers that cannot be
mistaken for each other, and no shot ever blends them.

**Register A, HISTORICAL.** Naturalistic colour, plausible practical light,
readable shadow detail, tactile material, grounded static camera, normal lens.
Looks photographed.

**Register B, VISION.** Near-monochrome bone-white and pale grey, exactly one
warm ember accent per frame, highlights blooming past detail, no horizon line and
no ground anchor, figures small and faceless, true architectural scale. Looks
remembered. Never grainy, never sepia, never period-photographic, never like a
painting.

The ember is the connective tissue: one warm point in every vision frame, and it
is the only colour the register allows. It is also what visually rhymes with the
bullet at the end of the episode.

## Shot budget

The episode runs 9:04, which is 544 seconds. The visual standard puts normal
static holds at 3 to 6 seconds and reviews anything past 8, and the timeline may
not return to a state it has already used. So the episode needs roughly ninety
distinct visual states, not a dozen.

Current stock: 48 acquired originals, 24 generated stills, 7 clips, 9 cards.
That is 88 states, about 6.2 seconds each, which lands inside the band.

## Approved stills

| ID | File | Register | Script beat |
|---|---|---|---|
| V01 | `EP13_V01_ANGEL_SWORD.png` | B | angel with the flaming sword |
| V02 | `EP13_V02_FIGURE_IN_WHITE.png` | B | a bishop dressed in white |
| V03 | `EP13_V03_RUINED_CITY.png` | B | a large city, half of it in ruins |
| V04 | `EP13_V04_THE_WAY.png` | B | he passes bodies on the way |
| V05 | `EP13_V05_MOUNTAIN_CROSS.png` | B | steep mountain, large rough-hewn cross |
| V06 | `EP13_V06_THE_FALL.png` | B | soldiers fire, he falls |
| H01 | `EP13_H01_ENVELOPE_SEALED.png` | A | a reported vision becomes an object |
| H02 | `EP13_H02_SHEET_TWENTYFIVE_LINES.png` | A | the sheet, roughly twenty-five lines |
| H03 | `EP13_H03_HOSPITAL_ROOM_1981.png` | A | the request, 18 July 1981 |
| H04 | `EP13_H04_ARCHIVE_STORE.png` | A | 1957, the archive of the Holy Office |
| H05 | `EP13_H05_WRITING_HAND_1944.png` | A | a girl and a pencil, 3 January 1944 |
| H06 | `EP13_H06_FOLDING_SHEET.png` | A | the sheet becomes an object |
| H07 | `EP13_H07_SEALING_WAX.png` | A | sealed |
| H08 | `EP13_H08_ENVELOPE_CARRIED.png` | A | carried across a continent, 1957 |
| H09 | `EP13_H09_READING_ALONE.png` | A | John XXIII reads it |
| H10 | `EP13_H10_BOX_RETURNED.png` | A | he did not publish it |
| H11 | `EP13_H11_DESK_AFTER_READING.png` | A | the silence becomes a decision |
| H12 | `EP13_H12_SQUARE_CROWD_1981.png` | A | the square is crowded |
| H13 | `EP13_H13_CORRIDOR_1981.png` | A | taken into surgery |
| H14 | `EP13_H14_TWO_ENVELOPES.png` | A | the Portuguese original and an Italian translation |
| H15 | `EP13_H15_SETTING_THE_METAL.png` | A | set into the crown, 1989 |
| V07 | `EP13_V07_EMBER_ALONE.png` | B | connective tissue, in and out of the vision |
| V08 | `EP13_V08_EMPTY_SUMMIT.png` | B | the others are killed with him |
| V09 | `EP13_V09_THE_CLIMB.png` | B | he climbs with bishops, priests and lay people |

## Approved clips

Five, each 6 s, 1080p, no audio. Motion is only spent where the beat is temporal
in the source text and a still cannot carry it.

| Clip | From | What moves | Camera drift |
|---|---|---|---:|
| `EP13_CLIP01_FLAMES_FAIL.mp4` | V01 | flames spread as filaments, then cool to an ember | 7.2 |
| `EP13_CLIP03_WRITING.mp4` | H05 | the pencil advances, illegible marks grow behind it | 11.4 |
| `EP13_CLIP04_SEALING.mp4` | H07 | the seal presses, holds, lifts away, leaving blank wax | 12.6 |
| `EP13_CLIP06_THE_CLIMB.mp4` | V09 | the line of figures climbs; the rock stays fixed | 6.8 |
| `EP13_CLIP08_SETTING_THE_METAL.mp4` | H15 | tweezers seat the grey metal in the gold and withdraw | 23.7 |
| `EP13_CLIP09_PUTTING_IT_AWAY.mp4` | H10 | the envelope goes into the box, the lid closes over it | 7.4 |
| `EP13_CLIP10_THE_WAY.mp4` | V04 | a gust travels down the road, lifting the cloths | 5.6 |

Camera drift is the mean edge-pixel deviation between the first and last frame.
Under about 6 is a locked camera, over 15 is a camera move. All five hold.

`CLIP09_PUTTING_IT_AWAY` is the strongest of the set. It performs the line the
script only asserts: he did not publish it. Hands lower the envelope, press it
flat, and the lid comes over and closes.

`CLIP08` exceeds the drift threshold at 23.7 and is kept as a documented
exception. At macro scale on a jeweller's bench the movement reads as the
operator's own hand rather than as a camera move, and it does not destroy the
frame the way the rejected street dolly did.

### What went wrong in the middle round, and the rule it produced

Two clips were scrapped after the first attempt at motion. `CLIP05_EMBER` measured
0.6 to 1.2 frame-to-frame: a brightness change on a static image, not a clip.
`CLIP04_SEALING` jiggled for four seconds and then jump-cut, with the envelope
teleporting to a new position.

The cause was in the prompt. Long camera-lock sentences and inline prohibition
lists suppressed the action along with the camera. Prohibitions belong in
`negativePrompt`. The prompt gets one short camera sentence and then a three-beat
physical action written with verbs, so something visibly starts, happens and
finishes. Every clip in the table above was rebuilt or built that way.

## Rejected, and why

**CLIP07, the fall completing.** Veo lost the white figure entirely: muzzle-flash
flares appeared at the head of the clip, the falling shape deformed, and by the
sixth second the figure had vanished into a smoke plume. V06 stays a still.

**CLIP02, the figure walking away down the ruined street.** Two attempts. Veo
adds a forward dolly that the prompt explicitly forbids: measured edge deviation
between first and last frame was 42.3, where a locked camera sits under 5. The
architecture stayed coherent, so the failure is camera discipline rather than
morphing. Fighting the model further is poor render economy when the still plus a
controllable editor push delivers the same beat. V03 stays a still.

**First pass on V01 and V03.** Heavy vignette, and V03 read as a tilt-shift scale
model. Both are now explicit prohibitions in the global lock.

**First pass on V02.** The figure was too close and too specific: visible hair, a
modern robe cut, a recognisable individual. The register forbids exactly that.
Regenerated at under one tenth of frame height, dissolving into the light.

**First pass on V06.** Letterbox bars and an unreadable composition. Regenerated
full frame.

**First pass on CLIP01.** Veo produced a row of dark orange explosion clouds at
the two-second mark. Fireballs, blasts, plumes and sparks are now in the negative
prompt, and the spread is described as filaments rather than volume.

## Hard constraints these assets satisfy

- No imitation of Sister Lucia's hand. H02 carries the rhythm and grey texture of
  handwriting with no formed letter in any language, verified at full resolution.
- H01 shows no address, no stamp and a wax seal with no device.
- The bishop in white is never identifiable and is never John Paul II: no mitre,
  no crozier, no pectoral cross, no insignia, no face, no period marker.
- V04 shows covered forms only. No body, no limb, no skin, no blood, no wound.
- V06 is distant silhouette. No impact, no blood, no violence detail.
- No vignette, no letterboxing, no tilt-shift, no legible generated text anywhere.

## Cards

Nine, built by `tools/build_ep13_cards.py`. None of them is a drawn primitive.
Each begins as a photographed material surface generated for this episode in
Register A, blank and with deliberate empty space, and the typography is
composited onto it at full resolution. That keeps the cards inside the episode's
own material world rather than importing a template, and it satisfies the card
lock's rule against cheap full-screen SVG standing in for imagery.

Type is Georgia, which the channel already uses for card titles. Ink never sits
at pure black. The ember is the only colour allowed, and on dark wood it is
lifted to a brighter amber because the deep ember is unreadable there.

| Card | Substrate | Says |
|---|---|---|
| `CARD01_1944` | laid paper | 3 January 1944, she writes the third part out |
| `CARD02_1957` | blank envelope on wood | 1957, the envelope reaches Rome |
| `CARD03_TWO_POPES` | aged paper | 1959 and 1965, neither publishes it |
| `CARD04_1981` | dark wood | 18 July 1981, two envelopes are brought to him |
| `CARD05_2000` | warm ivory paper | 26 June 2000, the manuscript is published |
| `CARD06_CONTAINS` | pale field | what the page contains, four items |
| `CARD07_NEVER_SAYS` | pale field | what it never says, each struck through |
| `CARD08_DECISION` | dark wood, mirrored | `WORLD or MYSELF` |
| `CARD09_CREDIT` | dark wood, rotated | crown photograph, CC BY 3.0 |

`CARD06` and `CARD07` are a deliberate progressive pair on the same substrate,
which the standard permits for contiguous states. Everywhere else each card has
its own surface, because three cards on one sheet would be the near-identical
repeat the standard forbids. That is why seven substrates were generated for
nine cards rather than one.

Every card was checked at a 246 px viewport and four failed the first build: text
running off the paper onto the wood, an envelope covering its own headline, and
ember labels invisible against dark wood on two cards. All four were rebuilt.

## What still needs building

Voice, forced alignment, then the cue sheet that binds every state above to a
spoken beat. No further imagery.
