# Final Master QA — PASS

Master under review: `EP06_SLEEP_PARALYSIS_02_EN_MASTER_1080P30.mp4`

- SHA-256: `839b43c54148849cfb23ce46b22d4772e2a40ff0f784dc0bedaffa977df36ae6`
- Duration: 07:34.000
- Publication status: **not published; explicit approval still required**

## Technical delivery

| Check | Result | Actual |
|---|---|---|
| Full decode | PASS | no video or audio decode errors |
| Picture | PASS | H.264 · 1920×1080 · progressive 30/1 fps · yuv420p |
| Picture cadence | PASS | 13,620 frames; VFR test clean; all 81 segment frame counts exact |
| Audio format | PASS | AAC · 48 kHz · stereo · 320 kb/s target |
| Integrated loudness | PASS | −13.98 LUFS |
| True peak | PASS | −0.79 dBTP |
| A/V duration delta | PASS | 0.006 s |
| Black events | PASS | none at ≥0.5 s threshold |
| Moving-still cadence | PASS | shared 8K supersampled/eased pipeline; no central cadence failures |
| 24→30 fps clips | PASS | four motion-compensated conversions; no pixel-identical repeats or freeze padding |
| Near duplicates | PASS | no non-adjacent perceptual-hash candidates among 81 midpoint states |
| Static holds | PASS | longest state 7.72 s; static documents/cards/maps intentional and excluded from freeze alarms |

Machine-readable evidence: `TECHNICAL_QA.json`, `SEGMENT_RENDER_MANIFEST.json`,
`CLIP_CONVERSION_QA.json`, `SUBTITLE_QA.json` and the master manifest.

## Voice, claims and synchronization

- Two auditions used the identical locked excerpt. Both returned perfect Scribe
  word order; the slower investigative Ryan style was selected.
- The final voice master is 454.008 s at 48 kHz. Scribe sequence similarity is
  0.998131. Its only token difference is that spoken `1781` is transcribed as
  `seventeen eighty one`; no omission, insertion, repeat or pickup is needed.
- Forced alignment drives the exact cue sheet and both caption files.
- Claims stay inside their locked boundaries: Coman is attributed and not
  diagnosed; his testimony is not made the sole cause of Bishop's death;
  cultural parallels are not a demon genealogy; Egypt/Denmark findings remain
  sample-specific associations.
- No `not proof`, `just a hallucination`, permanent reconstruction label or
  later self-debunking appears.

## Documents, named people, art and maps

- Coman's testimony progresses continuously from full manuscript context to
  two mobile-readable evidence views. It never returns later in the film.
- Bishop's execution document is shown at the hanging beat; no later portrayal
  is passed off as her authentic portrait.
- Fuseli's authentic 1781 artwork begins at the exact name/date beat, then moves
  continuously through woman, incubus and horse details.
- David J. Hufford is identified at his spoken name by a bibliographic card for
  his documented 1982 work, not by a generated portrait.
- Baland Jalal and Devon E. Hinton are identified at their spoken names by the
  exact 2013 paper citation, followed by concise sample/result cards.
- Egypt and Denmark appear as uncluttered viewer maps with no admin or source-
  management UI.
- Later Salem artworks are used as later depictions, never eyewitness archive.

## Viewer and semantic QA

- All five actual-master contact sheets were visually reviewed after the final
  semantic correction pass. The opening, ending and 11 boundary frames were
  also inspected directly from the final MP4 in `BEGIN_END_ACTUAL_MASTER.jpg`.
- Opening: human face and locked room within the first frame; sworn manuscript
  evidence arrives before 10 s; the private-to-public transformation is clear
  before the central question.
- Middle: lighting, temperature, scale and image type alternate among people,
  art, manuscript, relief, ritual interior, court, fieldwork, maps, source
  cards, sleep trace and abstract feedback states. The film is not a run of
  dark beds or empty rooms.
- Recalls use later states: the Salem return is public memory and testimony,
  not the opening bedroom/document/map; the final Fuseli callback is a new
  painting-to-screen media state.
- The interaction card contains only the actual choice, `EXPERIENCE / STORY`,
  and remains legible in the 246 px check.
- The final line lands on the painting-to-screen state with a clean visual tail;
  there is no black or unintended freeze at the end.

## Packaging and captions

- English SRT and VTT: 179 forced-aligned cues, maximum seven words, maximum
  36 characters per rendered line.
- Three materially different thumbnails passed 1280×720 and 246 px QA. Default
  is the human Salem/evidence direction; alternatives test iconic art and the
  culture/body question.
- Title, description, sources, tags, chapters and interaction prompt are locked
  in `09_UPLOAD/YOUTUBE_METADATA.md`.

## Release gate

The asset is upload-ready. No YouTube upload or publication action has been
performed. A new explicit approval is required before any upload.
