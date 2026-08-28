# EP02_EN Gateway Process — Final Production QA

QA date: 2026-08-26  
Editorial status: **PASS**  
Picture-lock status: **PASS**  
Audio status: **PASS**  
Publication status: **READY**

## Final deliverable

- Master: `../06_RENDER/EP02_GATEWAY_EN_FINAL_MASTER_1080P.mp4`
- Content duration: 481.037 s; container duration: 481.132 s (AAC encoder padding)
- Video: H.264, 1920×1080, 30 fps
- Audio: AAC, 48 kHz, stereo; final mix −15.97 LUFS, −1.19 dBTP
- Subtitles: embedded English soft subtitle stream plus external SRT/VTT
- Full video and audio streams decoded without error.

## Voice and intelligibility

- Canonical script changes are recorded in `../01_SCRIPT/SCRIPT_CHANGELOG.md`.
- Two identical-excerpt auditions were compared; Candidate A (George,
  `eleven_multilingual_v2`, stability 0.58, similarity 0.80, style 0.08,
  speed 1.06) was selected. Only one full master was generated.
- Voice master: 481.037 s, 48 kHz mono PCM24, −18.02 LUFS, −2.00 dBTP.
- Full voice Scribe similarity: 0.992298; all locked names and terms detected.
  No pickup was necessary.
- The earlier `voice_to_residual_mid_snr_db=-11.241` result is invalid and
  superseded. It regressed an unfiltered mono source against a filtered,
  limited and loudness-normalized stereo sum and was not a voice/bed ratio.
- Correct stem measurement: processed voice −15.50 LUFS; ducked bed −34.53
  LUFS; integrated voice-over-bed margin +19.03 LU. Across fully active
  one-second voice blocks, P05 is +7.43 dB and median +17.65 dB.
- Critical-window minimum margins: hook +3.54 dB; dense music/SFX passage
  +6.68 dB; closing +5.27 dB.
- Scribe v2 transcription of the actual stereo mix: hook 0.976190, dense
  music/SFX passage 0.985714, closing 1.000000. All pass.

## Linear picture-lock metrics

| Test | Result |
|---|---:|
| Actual edit shots / contiguous asset runs | 122 |
| Distinct semantic motifs / selected exports | 122 |
| Asset return after interruption | 0 — PASS |
| Exact SHA-256 repeats | 0 — PASS |
| Near repeats, 64-bit DCT pHash distance ≤2 | 0 — PASS |
| Cross-episode exact collisions | 0 — PASS |
| Cross-episode near collisions | 0 — PASS |
| Visible production-category badges | 0 — PASS |
| Longest static hold | 7.625 s — PASS |
| Longest overall hold | 10.735 s |
| Unjustified holds over 10 s | 0 — PASS |

Top repetitions: none. Repeat Count: **0**. Every selected item is marked
`series_usage=EP02_ONLY`.

EP01 final EDL exports were not found in the three accessible project roots.
The series collision test therefore compared the stricter available EP01
release-oriented pool (ten files) and found zero exact or near collisions. The
searched roots are recorded verbatim in `../03_VISUALS/QA/GW_EN_PICTURE_LOCK_QA.json`.

## Long-hold review

1. `GW-SHOT-001`, 10.735 s: six visibly advancing protocol stages in one
   continuous hook clip; no restart or recycled frames.
2. `GW-SHOT-078`, 8.860 s: the ten-digit procedure advances from placement to
   blinding, partial retrieval, and incomplete result.
3. `GW-SHOT-114`, 8.070 s: continuous three-input motion visibly advances from
   three observations to delayed comparison.

No static hold reaches eight seconds.

## Full-render visual review

- All 14,434 master frames decoded; zero black frames by the defined luma test.
- Five paginated 4-second contact sheets contain 121 samples and cover
  00:00.000–07:59.999. Exact sample times, frame numbers, page and cell are in
  `../03_VISUALS/QA/GW_EN_FULL_RENDER_4S_COVERAGE.csv`.
- Page 4 covers 299.999–395.999 s and page 5 covers 399.999–479.999 s, fully
  exposing the previously problematic 303.94–467.355 s interval.
- Every one of the 121 shot boundaries was sampled before and after the cut,
  logged in `../03_VISUALS/QA/GW_EN_RENDER_TRANSITION_QA.csv`, and reviewed on
  five transition sheets. Identical before/after failures: 0.
- Every page was checked at beginning, middle and end. No visual loop, black
  interval, hidden tail, permanent mode label, malformed identity, unreadable
  generated historical text, or severe style break was found.
- The three older single-sheet files are retained only under
  `../03_VISUALS/QA/OBSOLETE_PARTIAL/` with `.INVALID_PARTIAL` names and are not
  valid QA evidence.

## Editorial balance and factual fit

- Documents 37.19%; maps 0.80%; cards 20.86%; filmic stills 25.30%; moving clips
  15.86%. Documents/maps/cards total 58.84%, down from the earlier document-led
  cut. The 303.94–467.355 s document/card chain has been broken by semantically
  aligned test-room, perception, presence, EEG and three-input imagery.
- McDonnell is established with his authentic signature block. Monroe and
  Bentov are established by authentic patent records; identity-neutral adjacent
  reconstructions do not claim their likenesses.
- Flight 191 uses the NTSB report, route context and a government crash-site
  image. Fort Meade uses geographic context and a separately caveated modern
  photograph.
- Army authorship and CIA archival provenance remain distinct in voice and
  picture. Recommendation H, binaural beats, acoustics-to-cosmology, Focus
  levels, ten-digit test, nonphysical presence and PEAR handoff are aligned to
  dedicated non-returning sequences.
- Monroe Institute CC BY-NC-ND photographs and the Bentov fair-use portrait are
  not selected in the release EDL. Their earlier rights risk no longer blocks
  publication.

## Clip review

All ten selected motion assets were fully decoded and reviewed at five points.
The rejected Veo nonphysical-presence clip remains isolated under
`../03_VISUALS/REJECTED/VEO/`; it is not selected. The replacement presence clip
shows measurable environmental progression without forming a literal entity.

Machine-readable evidence: `GW_EN_PICTURE_LOCK_HASH_REGISTRY.csv`,
`../03_VISUALS/QA/GW_EN_PICTURE_LOCK_QA.json`,
`../03_VISUALS/QA/GW_EN_FULL_RENDER_AV_QA.json`, and
`../03_VISUALS/QA/GW_EN_MIXED_SPEECH_QA.json`.

Final master SHA-256:
`b4514b0bfe2b2ccb72f8d36018089fe16b1fd5488653b84f837f40ad6e3cfef8`.
