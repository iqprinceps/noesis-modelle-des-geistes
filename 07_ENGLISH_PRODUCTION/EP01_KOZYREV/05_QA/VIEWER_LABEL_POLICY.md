# EP01 Viewer Label Policy

Status: binding production override, 2026-08-26

## Viewer-facing rule

No permanent mode badges are allowed. The words `ARCHIVE`, `ORIGINAL DOCUMENT`,
`RECONSTRUCTION`, `MODEL`, and `INNER / HYPOTHESIS` are never burned into the
viewer image as continuing labels.

Allowed exceptions are limited to:

1. one optional, subtle 1.5–2.0 second contextual line at the first entrance to
   a continuous reconstruction block;
2. one concise source/date line or a targeted original-line highlight when a
   primary document first becomes relevant.

Portrait source and license information belongs in the manifest and credits.
Abstract/mystical imagery has no visible production-category label.

## QA tests

- Scan OCR results for all five forbidden mode terms.
- Inspect every core clip at first, middle, and final frame.
- Confirm any allowed contextual line ends within 2.0 seconds.
- Confirm document source/date lines occur only on the first relevant reveal.
- Keep `visual_mode_internal` populated in manifest and cue-sheet rows.
