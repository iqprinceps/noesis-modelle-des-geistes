# EP06 V4 — NanoBanana Production Guide

**Status:** READY-FOR-GENERATION  
**Kanonische Ablage:** dieser Episodenordner  
**Coverage:** 32 MAIN + 8 RESERVE als flexibler Pool, ergänzt durch echte Wissenschafts-/Ortsassets und Motion Graphics.

## Format

Wie EP05 Jung–Pauli gilt pro Bild ausschließlich:

```text
EP06_IMG001_1963_BEDROOM_DOOR.png
Referenz: STYLE_CINEMATIC_EP06.png
Prompt:
<vollständiger eigenständiger Prompt> Keep the image visually readable on ordinary laptop and phone screens: use lifted but natural midtones, visible shadow detail, clear subject-background separation, and at least one warm or neutral visual anchor. Reserve true black for small accents only; do not crush large regions into featureless darkness or apply a uniformly bleak or depressive grade.
```

Es gibt keinen versteckten Global-Prompt.

## Batches

- `NANOBANANA_PROMPTS_V4_S1_S2.md` — 8 MAIN + 2 RESERVE
- `NANOBANANA_PROMPTS_V4_S3_S4.md` — 8 MAIN + 2 RESERVE
- `NANOBANANA_PROMPTS_V4_S5_S6.md` — 8 MAIN + 2 RESERVE
- `NANOBANANA_PROMPTS_V4_S7_S8.md` — 8 MAIN + 2 RESERVE

## Style-Master zuerst erzeugen

### STYLE_CINEMATIC_EP06.png
Referenz: Keine
Prompt:
Create a premium cinematic investigative-documentary style master in 16:9 for a film about sleep paralysis. Ordinary believable bedrooms, university rooms and sleep-lab interiors, practical lamps and window light, deep neutral shadows, realistic skin and optics, tactile fabric and wood, restrained blue-black night tones, subtle film grain, sober mystery without horror-movie exaggeration. Human fear should feel intimate and plausible, never theatrical. No monsters, glowing eyes, occult symbols, neon, cyberpunk, gore, text or watermark. Keep the image visually readable on ordinary laptop and phone screens: use lifted but natural midtones, visible shadow detail, clear subject-background separation, and at least one warm or neutral visual anchor. Reserve true black for small accents only; do not crush large regions into featureless darkness or apply a uniformly bleak or depressive grade.

### STYLE_CONCEPTUAL_EP06.png
Referenz: Keine
Prompt:
Create a premium conceptual documentary style master in 16:9 for visualizing the boundary between REM sleep, waking awareness, bodily immobility and sensed presence. Use physically plausible darkness, layered room geometry, subtle double-state visual logic, restrained graphite and muted cool tones, small warm practical-light accents, realistic depth and grain. The imagery may be uncanny but must never prove a supernatural entity. No aura, energy beams, ghost clichés, demons, medical misinformation, readable text or watermark. Keep the image visually readable on ordinary laptop and phone screens: use lifted but natural midtones, visible shadow detail, clear subject-background separation, and at least one warm or neutral visual anchor. Reserve true black for small accents only; do not crush large regions into featureless darkness or apply a uniformly bleak or depressive grade.

### STYLE_SCIENCE_EP06.png
Referenz: EP06_Sleep_Studies_NHLBI_Polysomnography.jpg; EP06_REM_Polysomnography_30sec.png
Prompt:
Create a clean premium 16:9 scientific-documentary style master inspired only by the uploaded real sleep-study and REM-record references. Clinical but cinematic, precise cables, sensors, monitor light and dark neutral laboratory space, high legibility for later editor-added graphics, realistic materials and no futuristic technology. Never fabricate readable EEG values or pretend a generated frame is an original study photograph. No sci-fi glow, no medical claims embedded as text, no watermark. Keep the image visually readable on ordinary laptop and phone screens: use lifted but natural midtones, visible shadow detail, clear subject-background separation, and at least one warm or neutral visual anchor. Reserve true black for small accents only; do not crush large regions into featureless darkness or apply a uniformly bleak or depressive grade.

## Factual reference files

Use only when named in an individual prompt:
- `EP06_Fogo_Island_Newfoundland_fishing_village_2002.jpg`
- `EP06_Fogo_Island_to_Cape_Bonavista_Admiralty_Chart_1873.jpg`
- `EP06_Sleep_Studies_NHLBI_Polysomnography.jpg`
- `EP06_REM_Polysomnography_30sec.png`
- `EP06_Slow_Wave_Sleep_PSG.jpg`
- `EP06_SAK_Wilson_portrait_pre1937.jpg`

YELLOW assets such as identifiable sleep-lab models are excluded from default generation references unless their production review is explicitly cleared.

## Hard visual locks

- David Hufford and J. Allan Cheyne: no photorealistic identity imitation without reusable portrait rights. Reconstruct anonymously or from behind.
- Takeuchi 1992: generic laboratory reconstruction only; never claim generated subjects are the real participants.
- No external entity is visually established as objective reality.
- Intruder/Incubus imagery stays ambiguous, human-scale and room-bound; no monster design.
- REM-Atonie is shown as a timing/state problem, not paralysis from an external force.
- Original scientific images remain original edit layers; generated science frames are clearly explanatory/reconstructive.
- German labels, CTA typography and study numbers are added in edit, not generated into images.
- 16:9, no watermark.

## Ausgabeordner

`05_GENERATED/EP06_SCHLAFPARALYSE_V4/`

The image count is a coverage pool, not a quota. The final edit follows the finished voice and the strongest available archive/reconstruction mix.
