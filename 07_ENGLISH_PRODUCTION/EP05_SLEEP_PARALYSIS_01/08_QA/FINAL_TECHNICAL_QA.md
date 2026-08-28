# EP05 EN — Final Technical and Viewer QA

Date: 2026-08-28  
Authority tested: `09_UPLOAD/EP05_SLEEP_PARALYSIS_PART1_EN_MASTER_1080P30.mp4`

## Final verdict

**PASS — upload-ready.** The actual delivery MP4 was fully decoded and checked
after the final two targeted embodiment corrections. No remaining technical,
semantic, rights, cadence, readability, or viewer-journey defect was found.

## Integrity and streams

- File size: 238,367,801 bytes
- SHA-256: `FEBB7F69C505A90BE7616E43E5777C828194223C337C54F0DB378F825357997A`
- Container duration: 493.266016 s
- Video: H.264, 1920×1080, yuv420p, TV range, Rec.709, 30/1 nominal and
  average frame rate, 14,798 frames, 493.266016 s
- Audio: AAC, English, 48,000 Hz, stereo, 493.250000 s
- Embedded subtitles: mov_text, English, final cue end 492.920000 s
- Complete video+audio decode: **PASS**, no decoder error or damaged segment
- A/V tail difference: 0.016016 s, below one 30 fps frame; no frozen or silent
  overhang

## Cadence, motion, cuts, black/freeze checks

- `vfrdet`: `VFR:0.000000 (0/14797)` — constant cadence **PASS**
- Blackdetect at 0.20 s / 0.02 threshold: no events — **PASS**
- All 57 moving states were scanned through their central 60%. Smooth/eased
  still motion passed. The only automated review flag is EP05_EDIT_079: 20
  near-identical frames (about 0.67 s) in the source-native blank-sketch setup,
  followed by a visible shadow transformation. Manual frame contact review:
  intentional anticipation, not duplicated-frame conversion — **PASS**.
- Freezedetect events at the strict -60 dB / 2 s threshold map to deliberate
  source pages, reading cards, and progressive highlight states. Their endpoints
  align with planned cuts. No action clip, pan/zoom state, transition, or final
  tail has an unexpected freeze.
- Two states reach the eight-second review threshold: the Fogo map (9.001 s) and
  PSG connections (8.970 s). Both are single-focus geography/mechanism reading
  beats with semantic visual development and were manually retained.

## Audio

- Integrated loudness: -14.1 LUFS — **PASS** (-14 ±0.5 target)
- Loudness range: 2.3 LU
- True peak: -1.0 dBTP — **PASS** (must not exceed -0.8 dBTP)
- Voice/SFX/score ducking: **PASS**. Named material events remain audible while
  narration stays forward; science clears spatially; presence-before-form uses
  controlled low density; Salem uses wood/ink/paper and distant room tone.
- No arbitrary horror hit or SFX assertion of an external entity was found.

## Captions

- 177 SRT cues and 177 WebVTT cues from one timing source
- 1,246 caption words match the 1,246-word canonical voice script in sequence
- No overlap; maximum two lines; maximum 42 characters per line
- First cue 00:00.100; last cue ends 00:08:12.920
- Sidecars and embedded English captions remain synchronized to the selected
  493.249875-second voice/mix authority — **PASS**

## Visual and semantic viewer QA

- 107 contiguous viewer states cover 0.000–493.250 s; no gap or overlap
- No missing timeline asset, exact asset reuse, `REJECTED_SOURCE_DRIFT`, or
  non-adjacent perceptual near-duplicate at dHash Hamming distance ≤7
- Contrast rhythm visibly travels through nocturnal human experience, bright
  Fogo reality, neutral science/anatomy, controlled experiential descent,
  bright Takeuchi measurement, subjective presence, paper/ink explanation,
  warm Salem consequence, and dawn aftermath
- Faces, bodies, and readable perceived entities land at emotional peaks; beds,
  empty rooms, and objects serve as setups or semantic transitions rather than
  the episode's dominant visual channel
- Hufford, Cheyne, Takeuchi, and Bridget Bishop are preceded or accompanied by
  authentic identity/publication/source anchors. Generated people remain
  non-identifying dramatizations
- Takeuchi sequence provides one reading task per state; `six episodes` lands as
  six visible events; laboratory awareness, body immobility, and the actual
  waking-awareness/muscular-atonia source context remain distinct and aligned
- Viewer-facing cards contain no retrieval dates, asset IDs, paths, QA labels,
  licensing notes, deployment/admin language, ticker text, or cropped critical
  context
- No English timeline state contains embedded German text. Reused German-series
  clips are source-native assets, never extracts from old final renders
- `just a hallucination`, `only a hallucination`, `nothing supernatural`, and
  repetitive `not proof` framing are absent. Cards never become more categorical
  or skeptical than the voice

## Beginning and ending

- Opening begins immediately on a human eye/face and proceeds through door,
  steps, failed hand, mattress, embodied pressure, and authentic Hufford anchor;
  no black or contextless-room lead-in
- Final sequence carries the Salem consequence into a human historical close,
  then releases into a bright dawn/aftermath image. There is no corrupted end,
  frozen tail, abrupt black frame, or separate credit roll requiring review

Supporting machine reports and viewer contacts:

- `08_QA/EP05_EN_FINAL_MASTER_VISUAL_QA.json`
- `08_QA/EP05_EN_MOTION_CADENCE_QA.json`
- `08_QA/EP05_EN_FINAL_MASTER_STATE_CONTACT_SHEET.jpg`
- `08_QA/EP05_EDIT_079_CADENCE_CONTACT.jpg`
- `08_QA/AUDIO_VIDEO_SYNC_QA.md`
- `08_QA/DOCUMENT_TIMING_PREVIEW_QA.md`
- `07_THUMBNAILS/EP05_EN_THUMBNAIL_MOBILE_QA.jpg`

No upload or YouTube change was performed.
