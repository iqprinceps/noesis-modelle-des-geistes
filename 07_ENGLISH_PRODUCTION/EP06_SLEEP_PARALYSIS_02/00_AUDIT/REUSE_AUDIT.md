# EP06 English Part 2 — Reuse Audit

Status: asset selection lock before voice generation. All listed candidates were opened in the EP06–EP08 and English Part-1 reviews; EP07 candidates were additionally reviewed at full-frame contact-sheet scale in `REVIEW_SHEETS/`. Timecodes are the editorial target windows and will be replaced by forced-alignment times after the voice master.

## Decision rules

- `USE`: source is semantically exact, visually strong, rights-cleared for the project, and contains no misleading identity claim.
- `ADAPT`: source is sound, but needs an English rebuild, contextual crop, mobile highlight, regrade, or cadence conversion.
- `REJECT`: source drift, embedded German, poor mobile legibility, invented readable content, misleading named-person portrayal, repeat-state conflict, or old-render contamination.
- No old German final, `picture.mp4`, rendered segment, or English Part-1 render is a clip source.
- Every `REJECTED_SOURCE_DRIFT` file is hard-blocked regardless of apparent quality.
- A document may move through full-context and highlighted crops only as one uninterrupted progressive sequence. It may not return later.

## Locked selections

| Decision | Target | English voice beat / target TC | Provenance and rights | Embedded text / technical review | Required treatment |
|---|---|---|---|---|---|
| USE | `IMG001_SALEM_BEDROOM_COMAN_RECON.png` | Locked room; 00:00–00:07 | Internal NanoBanana generation for German EP07; fictional scene, no claimed portrait | No readable text; clean 16:9, good face/room separation | Cool moonlit grade; smooth eased motion |
| USE | `IMG002_COMAN_TRIES_TO_WAKE_WIFE.png` | Cannot wake wife; 00:07–00:14 | Internal generation; Coman reconstruction, not a portrait claim | No text; strong hand/face action | Slight warm-lamp lift; eased lateral move |
| USE | `SRC_EP07_Richard_Coman...p1_full.png` | Statement under oath; 00:14–00:19 | Public-domain Salem primary document; high-res derivative from project PDF | Original English handwriting; full context legible as object | Static contain; source/date footer in English |
| USE | `...p1_pressure_passage.png` | “lay upon my breast”; 00:19–00:25 | Same PD document, continuous progressive view | Exact source passage, no German | Static semantic crop + precise highlight; no pan |
| USE | `...p1_cannot_speak_nor_stir.png` | “could not speak nor stir”; 00:25–00:31 | Same PD document, continuous progressive view | Exact source passage, mobile-readable crop | Progressive highlight; remain in same document sequence |
| USE | `IMG003_PRIVATE_NIGHT_TO_COURT.png` | Private night crosses into court; 00:31–00:40 | Internal generation; composite transition, no named portrait | No text; strong spatial transformation | Mild amber-to-cold regrade; eased push |
| USE | `SRC_EP07_Bridget_Bishop_execution...full_scan.png` | Bishop hanged eight days later; 00:40–00:47 | PD archival scan | Original document context; low native resolution but sufficient contained | Static contain, restrained source/date footer |
| USE | `IMG004_BRIDGET_BISHOP_COURT_CONTEXT_RECON.png` | Larger prosecution; 00:47–00:55 | Internal historical reconstruction; no authentic-portrait claim | No text; faces/action visible | Neutral court grade, no name label on any invented face |
| USE | `SRC_EP07_Salem_Village_1692_map...full_map.png` | Salem as operating system; 00:55–01:02 | PD Upham 1866 map | Original English cartography, no production UI | Static viewer framing; one use only |
| USE | `IMG050_PRIVATE_TO_PUBLIC_NETWORK.png` | What Salem did with the night; 01:02–01:10 | Internal conceptual generation | No text; good scale change | Subtle eased parallax-style crop without layer invention |
| USE | `SRC_EP07_Fuseli_The_Nightmare_1781_full_painting.png` | Fuseli and date; 01:42–01:49 | PD artwork; Detroit Institute of Arts record checked | No embedded production text; 3013×2442 | Full contain with title/date footer |
| USE | `...woman_detail.png` | Body on bed; 01:49–01:54 | Same PD painting, continuous progressive view | Exact artwork crop | Static crop, continuous with full view |
| USE | `...incubus_detail.png` | Figure on chest; 01:54–01:59 | Same PD painting, continuous progressive view | Effective upscale acceptable at 1080p | Static crop, fine-grain added only if needed |
| USE | `...horse_detail.png` | Impossible eyes; 01:59–02:04 | Same PD painting, continuous progressive view | Effective upscale acceptable | Static crop, final state of continuous artwork sequence |
| USE | `IMG024_NIGHTMARE_PRINT_WORKSHOP.png` | Image spreads because it gives night a body; 02:04–02:11 | Internal generation | No readable text; bright historical interior | Warm print-shop grade; eased horizontal motion |
| USE | `SRC_EP07_Abildgaard_Nightmare_1800_full_painting.png` | European nightmare motif; 02:11–02:17 | PD artwork derivative | No production text; high native quality | Full context; static/eased micro-drift |
| USE | `CLIP002_NIGHTMARE_PRESSURE.mp4` | Mare/mara presses sleeper; 02:17–02:23 | Internal generated clip | 1920×1080, 24 fps, silent, no text | Motion-interpolate to 30 fps; inspect cadence and hands |
| USE | `IMG025_MANY_ORIGINS_ARCHIVE_TABLE.png` | Many names, no clean genealogy; 02:23–02:30 | Internal generation | No readable text; changes scale and brightness | Warm archival grade; eased overhead move |
| USE | `SRC_EP07_Jinn_from_Ali_manuscript_full_manuscript.png` | Other traditions name agents; 02:30–02:36 | PD manuscript image | Very wide/low native resolution; acceptable contained | Static contain with dark matte; no crop return |
| USE | `SRC_EP07_Kunisada_The_Ghost_full_print.png` | Japanese spectral tradition; 02:36–02:42 | PD print | Portrait format, low-to-moderate native resolution | Contain in textured neutral field; no artificial zoom |
| USE | `IMG027_KANASHIBARI_THRESHOLD.png` | Kanashibari / bound as metal; 02:42–02:49 | Internal generation | No text; strong human threshold scene | Cooler grade; eased forward motion |
| USE | `IMG028_NEWFOUNDLAND_ORAL_HISTORY.png` | Newfoundland / Old Hag oral memory; 02:49–02:56 | Internal generation; generic community, no named identity | No text; faces and daylight diversify bed imagery | Natural daylight grade; restrained eased motion |
| USE | `IMG026_SHARED_MECHANIC_RELIEF.png` | Known room, trapped body, approaching pressure; 02:56–03:04 | Internal conceptual generation | No text; relief-like body metaphor | High-contrast neutral grade |
| USE | `IMG029_HOUSEHOLD_EXPLANATION_CHOICES.png` | A culture supplies a cause; 03:04–03:12 | Internal generation | No text; household choices readable visually | Warm mids; eased overhead motion |
| USE | `IMG030_RITUAL_AS_PRACTICAL_RESPONSE.png` | Prayer/cross/iron/water as action; 03:12–03:20 | Internal generation | No occult symbols or readable text | Warm practical grade; avoid fetishizing objects |
| USE | `SRC_EP07_Malleus_1494...full_page.png` | Early-modern explanatory world; 03:20–03:26 | PD Wellcome historical page | Latin source page, full context | Static contain with source/date footer |
| USE | `SRC_EP07_Examination_of_a_Witch...later_depiction.png` | Household story becomes accusation; 03:26–03:33 | PD 1853 artwork; explicitly a later depiction | No production text | Footer “later depiction, 1853”; no portrait implication |
| USE | `SRC_EP07_Trial_George_Jacobs...full_later_depiction.png` | Enters machinery of court; 03:33–03:40 | PD later depiction | Strong court composition | Footer “later depiction”; static contain |
| USE | `CLIP003_SALEM_PUBLIC_TRANSFORMATION.mp4` | Bedroom opens outward; 03:40–03:46 | Internal generated transformation clip | Approved main clip; 1920×1080, 24 fps, silent | Motion-interpolate to 30 fps; visually verify transformed faces/textures |
| USE | `IMG031_HUFFORD_FIELD_INTERVIEW.png` | David Hufford fieldwork; 03:50–03:58 | Internal reconstruction; generic interviewer/participant, no claimed Hufford portrait | No text; faces/field setting | Do not label a face as Hufford; natural grade |
| USE | `IMG011_HUFFORD_FIELD_NOTES_RECON.png` | Studied Old Hag tradition; 03:58–04:06 | Internal reconstruction | No readable text; notebook/tape context | Warm fieldwork grade; eased macro move |
| USE | `IMG032_UNNAMED_FIRST_EPISODE.png` | People described pattern before local story; 04:06–04:14 | Internal generation | No text; strong human face | Cool-neutral grade; eased slow push |
| USE | `IMG043_FIRST_EPISODE_BODY_TRACE.png` | Paralysis, pressure, presence first; 04:14–04:22 | Internal conceptual generation | No text; anatomical counterimage | Clinical-neutral grade; preserve skin tones |
| USE | `CLIP001_CULTURAL_MASKS.mp4` | Story arrives later; 04:22–04:28 | Internal generated clip, approved main version | 1920×1080, 24 fps, silent; no baked labels | Motion-interpolate to 30 fps; inspect transitions |
| USE | `IMG044_SAME_BODY_TWO_INTERPRETATIONS.png` | Shared structure, different explanation; 04:28–04:36 | Internal conceptual generation | No text; material duality | Balanced warm/cool split |
| USE | `IMG034_TWO_EXPECTATIONS_THRESHOLD.png` | Two people enter same paralysis; 05:02–05:10 | Internal conceptual generation | No text; clear paired composition | Eased move toward center, no repeat later |
| USE | `IMG035_EGYPT_INTERVIEW_CONTEXT.png` | Egyptian sample; 05:10–05:18 | Internal contextual reconstruction, generic participant | No text; respectful human setting | Warm daylight grade; no country-as-person shorthand |
| USE | `ORIG_ORIG_EGYPT_MAP_PD_full_map.png` | Locate Egypt; 05:18–05:23 | PD map rebuild from acquisition replacements | No German/UI; 2560×1440 | Static viewer map; highlight only study location context |
| USE | `IMG036_DENMARK_INTERVIEW_CONTEXT.png` | Danish sample; 05:23–05:31 | Internal contextual reconstruction, generic participant | No text; distinct cold daylight | Cool daylight grade |
| USE | `ORIG_ORIG_DENMARK_MAP_PD_full_map.png` | Locate Denmark; 05:31–05:36 | PD map rebuild | No German/UI; 2560×1440 | Static viewer map, one use only |
| ADAPT | new English evidence card from Jalal/Hinton abstract | Specific samples and reported outcomes; 05:36–05:52 | Recreate from PubMed 23884906/24084761 facts; citation-only use | Existing German cards rejected; new English mobile card required | Two concise progressive panels, exact n and measures, no abstract wall |
| USE | `IMG045_EXPECTATION_ENTERS_BODY.png` | Meaning does not arrive the same way; 05:52–06:00 | Internal conceptual generation | No text; clear threshold metaphor | Cool-to-warm regrade |
| USE | `SRC_EP07_REM_Polysomnography_30sec_full_trace.png` | Physiological counterpoint; 05:16–05:19 | PD shared science asset | Low native resolution, but trace remains readable contained | Static full trace; English source footer |
| USE | `SRC_EP07_Sleep_Studies_NHLBI_Polysomnography_full_photo.png` | Body measured during sleep; 05:19–05:23 | NHLBI public-domain asset | Portrait photo, modest native res | Contain with clean neutral matte; no heavy zoom |
| USE | `IMG046_RAW_MATERIAL_TO_FORM.png` | Association, not one-way manufacture; 05:27–05:31 | Internal conceptual generation | No text | Neutral analytic grade |
| USE | `CLIP004_FEEDBACK_ENTITY.mp4` | Interpretation and distress entangle; 05:31–05:35 | Internal generated clip | 1920×1080, 24 fps, silent | Motion-interpolate to 30 fps; inspect cadence |
| USE | `IMG047_CULTURE_FEEDBACK_BRAID.png` | Fear fractures sleep; 05:38–05:42 | Internal conceptual generation | No text | Eased diagonal motion |
| USE | `IMG048_STORY_BODY_RETURN.png` | Another episode feels like confirmation; 05:46–05:50 | Internal conceptual generation | No text | Slight contrast lift; no later return |
| USE | `IMG052_QUESTION_BETWEEN_MODELS.png` | Story enters loop; 05:50–05:53 | Internal conceptual generation | No text | Controlled shadow detail |
| USE | `IMG053_PRESSURE_PRESENCE_RELIEF.png` | Return to Coman; 05:53–06:00 | Internal conceptual generation | No text; relief changes visual mode | Neutral stone grade |
| USE | `IMG055_CULTURAL_FORM_SETTLES.png` | Body and culture braid; 06:05–06:10 | Internal conceptual generation | No text | Warm-to-cool transition |
| USE | `IMG056_PRESSURE_AS_MEMORY_RELIEF.png` | Experience enters memory; 06:10–06:16 | Internal conceptual generation | No text | Fine texture; eased pullback |
| USE | `IMG057_PUBLIC_MEMORY_SHADOWS.png` | Testimony returns as public truth; 06:28–06:34 | Internal generation | No text; crowd scale, no named portraits | Public/court amber grade |
| USE | `IMG061_ONE_BODY_THREE_STORIES.png` | Body, memory, room of people; 06:34–06:39 | Internal conceptual generation | No text; strong closing synthesis | Eased move only |
| ADAPT | English `EXPERIENCE / STORY` interaction card | Viewer question; 06:39–06:47 | New in-house graphic | German CTA card rejected | 2–3 words only; mobile contrast QA |
| USE | `IMG060_WORD_LAYERS_CTA_BG.png` | “body may open the door”; 06:47–06:50 | Internal text-free background generation | No baked text | Add English kinetic words only in edit |
| USE | `SHOT04_FUSELI_TO_SCREEN_TRANSITION.png` | “face can travel”; 06:50–06:53 | Internal conceptual end image | No readable text; clear old-to-new visual bridge | End-state hold under final line; no old render sourcing |

## Explicit rejects

| Decision | Candidate/group | Voice beat | Reason |
|---|---|---|---|
| REJECT | `RESERVE_CLIPS/CLIP001_CULTURAL_MASKS_REJECTED_SOURCE_DRIFT.mp4` | none | Hard-blocked `REJECTED_SOURCE_DRIFT`; never copy or render. |
| REJECT | `RESERVE_CLIPS/CLIP003_SALEM_PUBLIC_TRANSFORMATION_REJECTED_SOURCE_DRIFT.mp4` | none | Hard-blocked `REJECTED_SOURCE_DRIFT`; never copy or render. |
| REJECT | all German `CARDS/CARD*.png` | all | Embedded German and previous-episode pacing; rebuilding the two needed English cards. |
| REJECT | all `render/**`, `picture.mp4`, old final masters and old rendered segments | all | Old finals are not source media; prevents baked edits, duplicate states and generation loss. |
| REJECT | `SRC_EP07_Bridget_Bishop_lithograph_*` | Bishop | Later low-resolution portrayal could be mistaken for an authentic portrait of a named person. |
| REJECT | `ORIG_ORIG_HUFFORD_PORTRAIT_LICENSED_portrait.png` | Hufford | It is a German source-replacement card explicitly “without image,” not an authentic portrait. |
| REJECT | German Hufford book/source cards | Hufford | Embedded German; replacement card, not original book photography. |
| REJECT | German Jalal/Hinton paper/source cards | study | Embedded German and source-card design; build concise English evidence panels from primary abstract data. |
| REJECT | `IMG037_FEAR_SLEEP_DAY_NIGHT_LOOP.png` | feedback loop | Baked German labels. |
| REJECT | `IMG040_PRINT_TO_RADIO_NETWORK.png` | none | Generated readable-ish book content and unused Art Bell tangent. |
| REJECT | `IMG041`, `IMG042`, `IMG058` and Art Bell replacement frame | none | The English Part-2 viewer arc ends before broadcast history; would dilute the central question. |
| REJECT | `IMG051_NAME_WAITING_IN_SHADOW.png` | archive | Figure can be read as a real archive worker or named historical person; semantic ambiguity. |
| REJECT | `IMG054_BODY_RAW_MATERIAL.png` | science | Tiny museum-like label fails mobile confidence; stronger clean alternatives exist. |
| REJECT | reserve `CLIP001_SALEM_EMPTY_BED_DAWN.mp4` | hook | Too bed-heavy and less active than the selected hook sequence. |
| REJECT | reserve `CLIP002_RITUAL_TABLE_CANDLE.mp4` | ritual | Redundant with higher-resolution selected still and adds little action. |
| REJECT | reserve `CLIP003_HUFFORD_FIELDWORK_DOLLY.mp4` | Hufford | Invented figure movement risks implying authentic footage of Hufford. |
| REJECT | reserve `CLIP004_FUSELI_SCREEN_LIGHT_SHIFT.mp4` | end | Repeats the selected end concept without sufficient new action. |
| REJECT | EP06/EP08 bed, Hag, shadow-person and generated named-person candidates not listed above | all | Visually reviewed as continuity context; rejected for bed monotony, wrong Part-2 thesis, or repeat-state pressure. |
| REJECT | English Part-1 final render and its rendered segments | all | Continuity reference only; Part 2 must have an independent viewer arc and no final-render sourcing. |

## Additional USE states added after exact voice duration

Final George forced alignment fixed the narration at 06:52.990. To keep every
state below the eight-second review point without returning to an underlying
source, the following already-reviewed, text-free EP07 candidates are also
locked `USE`: `IMG005`, `IMG006`, `IMG007`, `IMG008`, `IMG009`, `IMG010`,
`IMG012`, `IMG013`, `IMG014`, `IMG015`, `IMG016`, `IMG017`, `IMG018`, `IMG033`,
`IMG038`, `IMG039`, `IMG049`, and `SHOT03`. They supply continuous intermediate
states for the REM counterpoint, cross-cultural sequence, ritual logic,
Hufford reversal, matched-sample comparison and feedback loop. All are internal
text-free generations; none is presented as an authentic portrait, document or
archive frame. Treatment is the same Rec.709 regrade and shared eased-motion
pipeline described below.

`SHOT02_MANY_NAMES_PAPER_LAYERS.png` was added after the first exact EDL pass
to split the only 8.8-second synthesis hold. It is a previously reviewed,
text-free internal generation and now carries the “new account changes the next
expectation” beat as a separate source/state.

Final semantic QA added two new in-house bibliographic identity cards at the
spoken name beats: David J. Hufford's documented 1982 book, and the exact
Jalal/Hinton 2013 paper citation. These replace generic imagery at the named
beats and do not imitate a portrait or book cover. `SHOT04_FUSELI_TO_SCREEN_TRANSITION.png`
replaces the weaker final room state because it supplies a materially later
media perspective for “that face can travel.”

## Regrade and cadence lock

- Stills: Rec.709, 1920×1080 delivery, moderate film grain only when it does not obscure evidence; all movement through shared supersampled eased-motion pipeline.
- Documents/maps: static full-context or semantic crop only; exact English source footer, mobile-safe highlight, no decorative camera motion.
- Generated 24 fps clips: convert once with motion-compensated interpolation to 30 fps; check frame strips, hands/faces, cadence, first/last frames, and no freeze.
- No selected underlying source returns after its sequence ends. The closing Salem recall uses later-stage public-memory images rather than the opening room/document states.
