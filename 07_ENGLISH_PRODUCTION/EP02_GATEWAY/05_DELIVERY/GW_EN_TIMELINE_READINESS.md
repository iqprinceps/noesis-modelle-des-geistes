# EP02_EN Final Readiness

Status: **READY FOR UPLOAD**

The synchronized 481.037-second voice, 122-shot no-return EDL, picture lock,
original score/SFX mix, subtitles, thumbnail and upload copy are complete. The
final 1080p master has passed full-stream decode, paginated whole-episode visual
review, all-transition inspection, picture-lock hash/pHash collision QA and
mixed-signal speech-intelligibility QA.

## Canonical handoff files

- `../06_RENDER/EP02_GATEWAY_EN_FINAL_MASTER_1080P.mp4`
- `GW_EN_EDIT_SHOT_LIST.csv`
- `GW_EN_VOICE_ALIGNED_CUE_SHEET.csv`
- `GW_EN_ASSET_MANIFEST.csv`
- `GW_EN_PICTURE_LOCK_HASH_REGISTRY.csv`
- `GW_EN_PRODUCTION_QA_REPORT.md`
- `../04_VOICE/MASTER/GW_EN_VO_MASTER.wav`
- `../04_VOICE/ALIGNMENT/GW_EN_VO_ALIGNMENT.json`
- `../08_SUBTITLES/GW_EN_MASTER.srt`
- `../08_SUBTITLES/GW_EN_MASTER.vtt`
- `../07_THUMBNAIL/GW_EN_THUMBNAIL_FINAL_1280x720.jpg`
- `../09_UPLOAD/GW_EN_UPLOAD_METADATA.md`

Internal mode fields are metadata only and must never be rendered as permanent
viewer-facing labels. The EDL must remain linear: no selected asset may be
restarted or recalled after its assigned contiguous block.

## Regeneration boundary

Vertex/Veo generation is not required for this release. The last Vertex request
returned `HTTP 429 RESOURCE_EXHAUSTED`; accepted cached previews and the three
accepted Veo clips were reused, while remaining gaps were completed with Native
ImageGen or local controlled-motion builds. Do not retry external generation
unless a later editorial revision creates a real visual gap.
