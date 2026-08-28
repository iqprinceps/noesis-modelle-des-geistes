# EP02_EN Generation and Promotion Ledger

All listed exports use `series_usage=EP02_ONLY`. Native ImageGen exposed no
model identifier or seed; those fields are recorded as `not_exposed`, not
invented. The exact Vertex prompts, model identifiers, operation IDs, preview
paths and failures remain in `../GENERATED/VERTEX_GENERATION_LOG.jsonl` and the
per-asset JSON sidecars. The final Vertex call failed once with
`HTTP 429 RESOURCE_EXHAUSTED`; no retry was made.

## Native ImageGen — accepted

Common constraints: cinematic 16:9 raster, no text, logos, watermarks, visible
production labels, occult-stock iconography, malformed anatomy or asserted
supernatural proof.

| Export | Normalized prompt intent | Provider | Seed | Status |
|---|---|---|---|---|
| `../GENERATED/INNER/GW_EN_INNER01_MONROE_EXIT_NATIVE.png` | subjective separation above a restrained 1970s listening lab | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png` | analogue acoustics transforming into coherent spacetime geometry | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png` | anonymous observer at a mechanical temporal hub | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER04_NONPHYSICAL_PRESENCE_NATIVE.png` | empty perimeter reacting to ambiguous unseen pressure | Native ImageGen | not_exposed | accepted/source for motion |
| `../GENERATED/INNER/GW_EN_INNER05_BODY_RESONANCE_NATIVE.png` | body-bound vibration rendered as physical resonance, not aura | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER06_COHERENT_FIELD_NATIVE.png` | restrained synchronized wave field around an anonymous listener | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER07_FOCUS12_EXPANSION_NATIVE.png` | awareness expanding beyond a room while the body remains anchored | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER08_FOCUS21_THRESHOLD_NATIVE.png` | future threshold as spatial uncertainty, no portal cliché | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER09_RISE_UPWARD_NATIVE.png` | first-person attempt to rise from a physical body | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER10_DISTORTION_BLEND_NATIVE.png` | three perceptual inputs blending without clear provenance | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER11_DEFENSIVE_PERIMETER_NATIVE.png` | defensive spatial boundary implied through material response | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER12_STATE_NOT_INFORMATION_NATIVE.png` | altered subjective state contrasted with inaccessible target data | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER13_UNANSWERED_ANOMALY_NATIVE.png` | quiet anomaly in an otherwise credible experiment room | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER14_RECOMMENDATION_H_TRIAL_NATIVE.png` | three observers in isolated rooms, one later comparison | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER15_NONPHYSICAL_PRESENCE_NATIVE.png` | felt counterpart implied by light and negative space, never embodied | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER16_BODY_TURN_DIFFICULTY_NATIVE.png` | difficult bodily roll-out maneuver in a sparse test room | Native ImageGen | not_exposed | accepted |
| `../GENERATED/INNER/GW_EN_INNER17_INFORMATION_FIELD_NATIVE.png` | information-field hypothesis as spatial interference | Native ImageGen | not_exposed | accepted |
| `../GENERATED/STILLS/GW_EN_FILMIC19_PARTIAL_DIGIT_NOTES_NATIVE.png` | incomplete digit impressions as physical notes, no fabricated record | Native ImageGen | not_exposed | accepted |
| `../GENERATED/STILLS/GW_EN_FILMIC20_AUTHORIZATION_HAND_NATIVE.png` | anonymous decision-maker’s hand above blank authorization paper | Native ImageGen | not_exposed | accepted |
| `../GENERATED/STILLS/GW_EN_FILMIC22_MODERN_EEG_LAB_NATIVE.png` | modern EEG test context, commercially neutral | Native ImageGen | not_exposed | accepted |
| `../GENERATED/STILLS/GW_EN_FILMIC23_NO_DATASET_EMPTY_LAB_NATIVE.png` | empty controlled lab showing the absent evidentiary bridge | Native ImageGen | not_exposed | accepted |
| `../GENERATED/STILLS/GW_EN_FILMIC24_THREE_INPUTS_NATIVE.png` | three isolated input stations feeding one later comparison | Native ImageGen | not_exposed | accepted/source for motion |
| `../GENERATED/STILLS/GW_EN_FILMIC25_COLD_WAR_DESPERATION_NATIVE.png` | anonymous Cold War analysis room under pressure | Native ImageGen | not_exposed | accepted |
| `../GENERATED/STILLS/GW_EN_FILMIC27_ANONYMOUS_OPERATOR_NATIVE.png` | anonymous experimental operator at analogue equipment | Native ImageGen | not_exposed | accepted |
| `../../07_THUMBNAIL/GW_EN_THUMBNAIL_SOURCE_NATIVE.png` | one observer facing three temporal exposures of the same chamber | Native ImageGen | not_exposed | accepted; typography added locally |

One Native generation that produced a fake readable historical document was
rejected and isolated under `../REJECTED/`; it is not selected.

## Vertex preview promotion — no regeneration

Six already accepted 1K previews were promoted byte-for-byte to stable final
filenames: `GW_EN_FILMIC06_MONROE_RADIO_STUDIO_FINAL.png`,
`GW_EN_FILMIC07_MONROE_LAB_BUILDER_FINAL.png`,
`GW_EN_FILMIC08_GATEWAY_TRAINING_SESSION_FINAL.png`,
`GW_EN_FILMIC09_BENTOV_CATHETER_BENCH_FINAL.png`,
`GW_EN_FILMIC10_BODY_OSCILLATION_TEST_FINAL.png`, and
`GW_EN_FILMIC12_RIGHT_EAR_HEADPHONE_MACRO_FINAL.png`. Promotion avoided cost,
latency and visual drift; source operation metadata remains cached in the Vertex
log.

## Motion

- Three accepted Veo clips were reused from cache; none was regenerated.
- The literal smoky-figure Veo clip failed ambiguity QA and remains rejected.
- `GW_EN_CLIP09_NONPHYSICAL_PRESENCE_SAFE.mp4` and
  `GW_EN_CLIP12_THREE_INPUTS_PROGRESS.mp4` are deterministic local
  controlled-motion builds with SHA metadata and restartable scripts.
