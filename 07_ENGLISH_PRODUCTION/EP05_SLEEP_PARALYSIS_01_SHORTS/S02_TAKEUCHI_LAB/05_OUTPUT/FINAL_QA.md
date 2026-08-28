# S02_TAKEUCHI_LAB — Final QA

**Status: PASS**

- Master: `07_ENGLISH_PRODUCTION/EP05_SLEEP_PARALYSIS_01_SHORTS/S02_TAKEUCHI_LAB/05_OUTPUT/EP05_EN_SHORT_S02_MASTER_1080x1920_30.mp4`
- SHA-256: `18ba0dbc0e83bf4910b5bdd6e582ccd466e4a4a9d035336b5bb1e2471986e35a`
- Duration: 48.633 s; 1459 decoded frames
- Video: h264, 1080x1920, 30/1 fps, yuv420p
- Audio: aac, 48 kHz stereo; -14.0 LUFS; -1.0 dBTP
- Captions: 34 cues; max 4 words; no overlaps
- Timeline visuals: 14 distinct; no exact reuse
- Moving-still cadence: 6 segments checked
- Six-event sync: exactly six visible/sonic signals at 7.039s, 7.419s, 7.940s, 8.500s, 9.000s, 9.579s

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
