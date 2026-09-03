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

## Approved clip

`CLIPS/EP13_CLIP01_FLAMES_FAIL.mp4`, from V01, 6 s, locked camera.

Motion is used here because the beat is temporal in the source text: the flames
appear as though they will set the world on fire, and they go out. A still cannot
say that. The flame spreads as thin filaments across the pale field, reaches far,
then cools and retracts to a single ember. The figure never moves and the face
never appears.

## Rejected, and why

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

## What still needs building

These are cards and object states, not generated imagery:

1. the evidence card family for the dates and locators;
2. the subtraction card for `what the page never says`;
3. the `WORLD or MYSELF` decision card and its end-card repeat;
4. the attribution card for the crown photograph, CC BY 3.0.
