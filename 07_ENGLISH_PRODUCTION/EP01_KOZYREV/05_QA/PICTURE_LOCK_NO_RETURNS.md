# EP01_EN Hard Picture Lock — No Returns

## Rule

Every viewer-facing still, document view, card, map or clip may appear in one contiguous timeline run only. Adjacent cues may share the same running asset. Once the edit switches away, that asset cannot return.

The following do **not** create a new asset:

- a new zoom, crop, pan, color treatment or overlay on the same export;
- restarting a clip or reusing a segment from it;
- re-exporting identical source framing under a new filename;
- presenting the same portrait or full document page as a callback.

A later callback must use a genuinely different authenticated image, source detail, perspective, action, composition or progressively new clip state. Chamber geometry may remain consistent.

## Cue-sheet enforcement

- `primary_asset_id` is the contiguous deliverable family.
- `visual_state_id` is the concrete picture/document/card/clip state.
- Both fields are validated as ordered runs. Any ID return after a different ID is a hard failure.
- `fallback_asset_id` is intentionally blank until a non-repeating semantic fallback exists.
- `visible_mode_badge` must equal `NO` for every cue.

## Final file QA

The selected-asset manifest must be checked before READY:

1. SHA-256 for byte-identical duplication.
2. Perceptual dHash/pHash comparison for visually near-identical stills and sampled video frames.
3. First/middle/last frame comparison for every clip, including restart detection.
4. Manual review of all near-match pairs to distinguish a legitimate continuous sequence from disguised reuse.
5. Any exact duplicate or unexplained near-duplicate in separate timeline blocks is a hard failure.

No status may be upgraded to picture READY while any required family is missing or any no-return check fails.

## Series-wide ownership

- Every final EP01 export must carry a stable SHA-256 content hash and `series_usage=EP01_ONLY` in the asset manifest.
- No EP01 export may later be reused in Gateway, PEAR, Jung or another English episode.
- The Fort Meade handoff is an EP01-owned transition. It must not use, preview or reserve an EP02 final image.
- Final selected hashes are copied to the shared English-series asset register. Later episodes must collision-check exact and perceptual hashes before selection.
