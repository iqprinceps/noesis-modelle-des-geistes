# EP01_EN Recovery Audit — 2026-08-26

## Scope and preservation

Only `07_ENGLISH_PRODUCTION/EP01_KOZYREV` was changed. The interrupted production was resumed from the last clean cached state. Verified sources, the two short auditions, the single full voice master, alignment, subtitles, accepted chamber candidates and accepted generated images were preserved. Rejected previews remain rejected. No German master and no other episode was modified.

Malformed provider text or token-like output is not a production asset and was not copied into viewer-facing material.

## Recovery corrections

- Rebuilt the picture plan from the 7:14.632 forced alignment.
- Replaced the former `KZ_EN_HERO01` overuse with a linear 129-cue journey.
- Locked 122 distinct visual states in 34 contiguous editorial families; these counts describe the resulting cut and are not quotas.
- Removed every fallback that could silently return to an earlier image.
- Added exact SHA-256, perceptual hashes and `series_usage=EP01_ONLY` for all selected exports.
- Registered all 122 selected exports in the shared English-series asset register.
- Replaced three overly similar patent-detail states with distinct viewer functions: a line-level polished-surface quote, a new focus-geometry model and a later 50-cm line detail.
- Kept all production categories internal. No permanent ARCHIVE, ORIGINAL DOCUMENT, RECONSTRUCTION, MODEL or INNER/HYPOTHESIS badge is selected.
- Preserved the EP01-only Novosibirsk-to-Fort-Meade transition without borrowing a Gateway/EP02 export.

## Recovered and completed package

- Source manifest: 14 original-source/provenance records.
- Voice: 2 short identical-text auditions, 1 selected full master, 0 pickups.
- Timeline: 129 cues with selected file paths and stable asset IDs.
- Selected viewer assets: 103 local deterministic source/card/map/model states, 3 accepted Nano Banana Pro stills, 11 Native ImageGen stills and 5 local progressive clips.
- Visual QA: contact sheets, mobile 246 px proof, clip start/middle/end proof, no-return QA and hash-bound near-duplicate review.

## Final recovery status

- Script, voice, alignment and subtitles: **READY**.
- Cue sheet, required set, asset manifest and series register: **READY**.
- Picture and local motion package: **READY** for timeline assembly.
- Public-release rights: **PARTIAL** pending legal/editorial sign-off for five retained/unclear archival portrait or clipping sources.
- Veo: **BLOCKED** by `fetch failed`; three scene-analysis calls failed, no paid generation job started and no blocker retry was attempted. Selected local progressive clips cover the required motion slots.

The authoritative readiness decision is in `05_QA/FINAL_READINESS_MATRIX.md`.
