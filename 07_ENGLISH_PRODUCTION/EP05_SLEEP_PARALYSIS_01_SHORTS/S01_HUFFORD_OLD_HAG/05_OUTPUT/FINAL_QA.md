# S01_HUFFORD_OLD_HAG — Final QA

**Status: PASS**

- Master: `07_ENGLISH_PRODUCTION/EP05_SLEEP_PARALYSIS_01_SHORTS/S01_HUFFORD_OLD_HAG/05_OUTPUT/EP05_EN_SHORT_S01_MASTER_1080x1920_30.mp4`
- SHA-256: `30fa3584cda689303956cdb9000f87663d67b9a530f7332e60028b197c1f4757`
- Duration: 43.800 s; 1314 decoded frames
- Video: h264, 1080x1920, 30/1 fps, yuv420p
- Audio: aac, 48 kHz stereo; -14.4 LUFS; -1.0 dBTP
- Captions: 34 cues; max 4 words; no overlaps
- Timeline visuals: 18 distinct; no exact reuse
- Moving-still cadence: 9 segments checked

## Visual and editorial review

Hook, information changes, science/history contrast, mobile caption safety, identity framing, claim limits, longform bridge, interaction close and cover frame were reviewed from the final encoded master.

## Machine checks

- [x] decode_complete
- [x] resolution_1080x1920
- [x] constant_30_fps
- [x] frame_count_matches_duration
- [x] yuv420p
- [x] audio_48k_stereo
- [x] retained_stems_48k_stereo
- [x] loudness_target
- [x] true_peak_ceiling
- [x] no_black_events
- [x] captions_valid
- [x] sidecar_srt_present
- [x] cover_1080x1920
- [x] metadata_within_platform_limits
- [x] unique_timeline_assets
- [x] native_vertical_assets
- [x] smooth_motion_cadence
- [x] six_events_exact
- [x] burned_captions_visual_review
- [x] mobile_safe_visual_review
- [x] hook_retention_end_visual_review
- [x] identity_claim_tone_editorial_review
