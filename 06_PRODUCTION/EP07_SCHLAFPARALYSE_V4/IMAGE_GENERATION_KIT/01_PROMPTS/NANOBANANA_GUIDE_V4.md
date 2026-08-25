# EP07 V4 — NanoBanana Production Guide

**Status:** READY-FOR-GENERATION  
**Kanonische Ablage:** dieser Episodenordner  
**Coverage:** 20 MAIN + 4 RESERVE AI-Frames. EP07 ist bewusst archive-first; Salem-Primärdokumente und historische Kunst sind die visuellen Hero-Belege.

## Format

Wie EP05 Jung–Pauli:

```text
IMG001_SALEM_BEDROOM_COMAN_RECON.png
Referenz: STYLE_ARCHIVE_EP07.png
Prompt:
<vollständiger eigenständiger Prompt> Keep the image visually readable on ordinary laptop and phone screens: use lifted but natural midtones, visible shadow detail, clear subject-background separation, and at least one warm or neutral visual anchor. Reserve true black for small accents only; do not crush large regions into featureless darkness or apply a uniformly bleak or depressive grade.
```

Kein Global-Prompt muss ergänzt werden.

## Batches

- `NANOBANANA_PROMPTS_V4_S1_S2.md` — 5 MAIN + 1 RESERVE
- `NANOBANANA_PROMPTS_V4_S3_S4.md` — 5 MAIN + 1 RESERVE
- `NANOBANANA_PROMPTS_V4_S5_S6.md` — 5 MAIN + 1 RESERVE
- `NANOBANANA_PROMPTS_V4_S7_S8.md` — 5 MAIN + 1 RESERVE

## Style-Master

### STYLE_CINEMATIC_EP07.png
Referenz: Keine
Prompt:
Create a premium cinematic historical-documentary style master in 16:9 for a film about sleep paralysis, Salem testimony and cultural interpretation. Plausible late-seventeenth-century New England interiors, restrained European historical rooms and modern research spaces, practical candle/window light, tactile wood, cloth and paper, realistic human behavior, deep neutral shadows and subtle film grain. Serious and investigative, never gothic entertainment. No fantasy witch costumes, green magic, glowing eyes, fog-machine horror, fake archive text or watermark. Keep the image visually readable on ordinary laptop and phone screens: use lifted but natural midtones, visible shadow detail, clear subject-background separation, and at least one warm or neutral visual anchor. Reserve true black for small accents only; do not crush large regions into featureless darkness or apply a uniformly bleak or depressive grade.

### STYLE_ARCHIVE_EP07.png
Referenz: EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692.pdf; EP07_Fuseli_The_Nightmare_1781.jpg
Prompt:
Create a premium 16:9 archival-documentary style master using the uploaded real Salem record and Fuseli artwork only as authentic source objects. Preserve original page/art content instead of regenerating it. Museum-like neutral lighting, restrained paper texture, precise crops, negative space for editor annotations and subtle depth. No fake handwriting, no invented seals, no aging filter that changes the source, no red-string conspiracy aesthetic, no generated text or watermark. Keep the image visually readable on ordinary laptop and phone screens: use lifted but natural midtones, visible shadow detail, clear subject-background separation, and at least one warm or neutral visual anchor. Reserve true black for small accents only; do not crush large regions into featureless darkness or apply a uniformly bleak or depressive grade.

### STYLE_CONCEPTUAL_EP07.png
Referenz: Keine
Prompt:
Create a restrained 16:9 conceptual documentary style master for showing how a recurring bodily experience acquires different cultural interpretations. Use the same simple bedroom/body geometry across translucent layers while surrounding symbols, clothing or room context change subtly. Human-scale, historically sober, graphite and muted paper palette, no supernatural proof. No linear genealogy arrows, glowing demons, sacred symbols as decoration, readable text or watermark. Keep the image visually readable on ordinary laptop and phone screens: use lifted but natural midtones, visible shadow detail, clear subject-background separation, and at least one warm or neutral visual anchor. Reserve true black for small accents only; do not crush large regions into featureless darkness or apply a uniformly bleak or depressive grade.

## Default factual references

Use only when named:
- `EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692.pdf`
- `EP07_Bridget_Bishop_Examination_1692.pdf`
- `EP07_Bridget_Bishop_lithograph.jpg`
- `EP07_Fuseli_The_Nightmare_1781.jpg`
- `EP07_Abildgaard_Nightmare_1800.jpg`
- `EP07_Queen_of_the_Night_Burney_Relief.jpg`
- `EP07_Malleus_1494_Bull_Innocent_VIII_Wellcome.jpg`

PDFs and RED/reference-only URLs are research inputs, not direct image-generation references.

## Hard visual locks

- Bridget Bishop is not portrayed as being convicted because of one sleep-paralysis-like account; Coman's testimony is one element in a larger proceeding.
- Salem reconstructions are labeled `REKONSTRUKTION` in edit and never look like discovered photographs.
- No direct historical lineage Lilu/Lilith/Incubus is visually asserted.
- Burney Relief is an ancient comparative/echo object, not proof of a continuous sleep-paralysis demon lineage.
- Hufford and modern researchers without reusable portraits are not photorealistically imitated.
- Real court pages/artworks are shown as real source layers; AI does not fabricate replacement facsimiles.
- CTA typography and country comparison graphics are built in edit.

## Ausgabeordner

`05_GENERATED/EP07_SCHLAFPARALYSE_V4/`

The smaller AI pool is intentional. A strong original document is better than an extra reconstruction.
