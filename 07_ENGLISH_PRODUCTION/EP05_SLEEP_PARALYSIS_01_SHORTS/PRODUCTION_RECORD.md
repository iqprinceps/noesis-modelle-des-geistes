# EP05 EN Shorts — Production record

## Source lock

The completed EP05 English package was treated as canonical, including the selected voice script, claim/tone/sync matrices, fine edit plan, source and rights registers, final QA, upload metadata and the decoded longform master. Current project-wide retention, viewer-card, visual-retention, documentary-evidence, smooth-motion, caption-safe and card-lock standards were applied before scripting the Shorts.

Longform anchor: `Sleep Paralysis: Why You Feel Someone in the Room`, video ID `dXwqAWc74Ts`.

## Editorial construction

- S01 is a standalone encounter-before-name story: immediate body/room events → Hufford identity → Newfoundland/Old Hag reveal → positive REM explanation → unresolved folklore/encounter fork.
- S02 is a standalone human-experiment story: interrupted sleep and 16 people → exactly six episodes → protocol progression and boundary → measured awareness/atonia contradiction → occupied-room question.
- Neither Short is a lifted timeline excerpt or shortened copy of the longform.
- Named-person identity appears only through authentic source anchors. Generated people are anonymous editorial reconstructions.

## Voice

| Short | Voice | Model | Speed | Seed | Selected duration |
|---|---|---|---:|---:|---:|
| S01 | George (`JBFqnCBsd6RMkjVDRZzb`) | ElevenLabs `eleven_multilingual_v2` | 1.08 | 260905 | 43.793 s |
| S02 | George (`JBFqnCBsd6RMkjVDRZzb`) | ElevenLabs `eleven_multilingual_v2` | 1.10 | 260906 | 48.623 s |

Both use stability 0.59, similarity boost 0.82, style 0.08 and speaker boost. Request IDs, source-text hashes and selected-audio hashes are retained in each `02_VOICE/raw/manifest.json`. Forced alignment drives shot boundaries, burned captions, SRT cues and SFX timing.

## Image generation

Eleven independent portrait hero assets were generated only after script, selected voice and exact cue timings were locked. They were created with the built-in OpenAI ImageGen tool in native portrait composition; no horizontal longform image was blindly centered. Prompts and outputs are recorded in `IMAGEGEN_PROMPT_LOCK.md`.

All additional historical, scientific and source anchors were newly recomposed for 9:16. S01 and S02 share no timeline asset file.

## Motion and edit

- Final delivery: 1080×1920, 30 fps, BT.709 TV range, H.264 High, yuv420p.
- Moving stills use the project `smooth_still_motion.py` eased pipeline with 4320×7680 supersampling and four temporal subframes.
- Evidence, count and viewer-choice cards are intentionally static for reading stability.
- S02's six-event clip is a deterministic 30 fps animation: six empty states are filled one at a time at the aligned starts of “one” through “six”; six matching SFX pings use the same timestamps.

## Audio

Each Short has its own newly synthesized procedural music bed and SFX stem. Voice, bed and SFX are mixed through voice-led sidechain ducking, dynamics control and final EBU loudness normalization. The upload master uses AAC 48 kHz stereo; the retained final mix is 24-bit PCM 48 kHz stereo.

## Captions

Dynamic captions contain at most four words per cue, use word-aligned timing, stay in the central mobile-safe region and are burned into the master. Matching English SRT and ASS files are retained beside each master.

## Render and QA tooling

- `tools/produce_ep05_en_shorts.py`: assets, motion segments, stems, captions, masters and covers.
- `tools/qa_ep05_en_shorts.py`: full decode, CFR/frame-count, stream, loudness/true-peak, black-frame, caption, duplicate/no-return, mobile, cover, metadata, smooth-motion, six-event and final editorial gates.
- `tools/smooth_still_motion.py`: shared eased still-motion implementation with portrait supersampling support.

## Publication state

`READY_NOT_UPLOADED`. No YouTube upload, schedule creation or remote metadata mutation was performed.
