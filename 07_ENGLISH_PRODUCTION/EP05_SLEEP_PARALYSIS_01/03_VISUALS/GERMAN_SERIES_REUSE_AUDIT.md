# EP05_EN German-Series Reuse Audit

Date: 2026-08-28  
Gate: **PASS — source-native German assets selected before any further generation**

Scope: EP06, EP07 and EP08 source/generation pools plus their Phase2 manifests.
The audit reads the large production masters from the canonical German project
checkout, but every selected file is copied into this EP05_EN folder before
timeline work. No frame is extracted from an old final render. Files containing
`REJECTED_SOURCE_DRIFT` are excluded without exception.

Rights basis:

- German generated stills/clips are channel-owned internal production assets;
  the channel owner explicitly authorized reuse in this new English viewer edit.
- Original/archive assets retain the Phase2/episode license and attribution.
- A generated or reconstructed German asset is never presented as original
  historical footage, a named-person portrait, or Takeuchi's actual 1992 lab.

## Still and source-image decisions

| Candidate | Origin / provenance | English voice beat | Quality finding | Decision |
|---|---|---|---|---|
| `IMG007_FOGO_PLACE_ANCHOR_RECON.png` | EP06 internal generated reconstruction, source-guided by public-domain Fogo fishing-village photograph; 2560×1440, German QA PASS | 79.46–84.50, inhabited Fogo context | bright real-world reset; boats, houses and people; no embedded text | **USE** |
| `SHOT02_FOGO_MAP_TABLE.png` | EP06 deterministic source-locked composite of public-domain 1873 Admiralty chart; 2560×1440 | 84.56–89.37, local place/pattern | high-luminance material surface; one clear reading object | **USE** |
| `IMG061_FOGO_FIELDWORK_INTERVIEW_RECON.png` | EP06 internal non-identifying fieldwork reconstruction, grounded in Fogo location material | 99.56–106.00, accounts collected from people | human faces/gesture and daylight coast; never identified as Hufford | **USE** |
| `IMG017_SLEEP_LAB_WIDE_RECON.png` | EP06 internal reconstruction, NHLBI sleep-study reference; German sync already notes “not Takeuchi original”; 2560×1440 | 217.16–224.32, sixteen participants / experiment question | inhabited lab, white bedding, clear observer; moderately bright | **USE** |
| `IMG018_SLEEP_INTERRUPTION_CLOCK.png` | EP06 internal protocol reconstruction; 2560×1440, German QA PASS | 225.06–230.08, awakened / one hour | visible clock and period lab surface; no fake data | **USE** |
| `IMG011_WAKE_BODY_LAG.png` | EP06 internal generated mechanism metaphor; 2560×1440, German QA PASS | 342.70–348.62, the brain continuously predicts the room | bright non-bedroom reset; doubled walking body makes an active internal model visible without a neon-brain cliché | **ADAPT / USE** |
| `SHOT05_LAB_SENSOR_MACRO.png` | EP06 internal sensor macro; 2560×1440, German QA PASS | 230.42–241.75, monitoring / conditions | clear hand, leads and electrodes; one visual task | **USE** |
| `ORIG017_BRAINSTEM_ANATOMY.png` | Blausen Medical brainstem anatomy, CC BY 3.0; EP06 original-derivative manifest | 126.22–143.26, dream runs / motor handover | bright, anatomically legible; must carry attribution in register | **USE** |
| `SHOT03_REM_VS_SLOW_WAVE_SOURCE_TABLE.png` | EP06 editorial comparison built from source PSG images | 121.08–131.94 | technically clean but small dual windows and dark empty field compete at mobile size | **REJECT**; use source-native REM PSG full-frame instead |
| `SHOT08_DAWN_AFTER_PARALYSIS.png` | EP06 internal generated aftermath still; 2560×1440, QA PASS | 486.84–492.92, “The body wakes. The story keeps moving.” | restrained daylight human silhouette; useful final release | **ADAPT** as fallback if the source clip fails cadence QA |
| EP07 Fuseli/Abildgaard derivatives | public-domain art, already acquired source-native in EP05_EN | 427.70–444.40, culture gives darkness a face | strong, but reusing the German derivative would duplicate the same underlying work | **REJECT duplicate**; use one EP05_EN source-native state per artwork |
| `IMG007_MARA_INCUBUS_KANASHIBARI_BASE.png` | EP07 internal cultural composite | none exact in Part 1 | attractive, but Mara/Kanashibari are not spoken here | **REJECT semantic expansion** |
| `IMG006_SAME_MECHANIC_DIFFERENT_ROOMS.png` | EP07 internal cultural composite | 432.60–444.40 possible | adds unspoken cultures and repeats the three-family idea | **REJECT** |
| EP07 Coman full page + semantic crops | Massachusetts archive source, GREEN in Phase2; full context and 2560×1440 guided derivatives | 449.44–466.48, night enters record / pressure / cannot speak or move | substantially stronger than the previously blocked web endpoint; full page preserved | **USE** |
| EP07 Salem/Bishop source derivatives | public-domain court art, lithograph and execution record | 459.12–480.90 | real context; each underlying work used once | **USE** selectively |
| `IMG006_SHADOW_DRAWINGS_SPREAD.png` | EP08 internal generated research-table spread; no Hat-Man label or web text | 171.73–176.53, reports repeatedly form broad families | human-made drawings make clustering tangible without adding a named entity | **USE** |
| `IMG024_NIGHTMARE_PRINT_WORKSHOP.png` | EP07 internal non-identifying print-workshop reconstruction; 2752×1536 | 427.70–432.60, folklore may preserve recurring forms | warm human/material reset; visible making and circulation of an image, never presented as an authentic historical workshop photograph | **ADAPT / USE** |
| Other EP08 Hat-Man/network assets | internal generated pool | no exact Part-1 Hat-Man or network beat | attractive but late-series specificity and dark-palette duplication | **REJECT** |

## Source-clip decisions after frame inspection

Every candidate was opened through five actual source frames. The proof sheet is
`QA/GERMAN_REUSE/EP05_EN_GERMAN_CLIP_CONTACT_SHEET.jpg`; technical probe data is
`QA/GERMAN_REUSE/EP05_EN_GERMAN_CLIP_TECHNICAL_INVENTORY.json`.

All candidates are 1920×1080 yuv420p H.264 at native 24 fps. Selected clips are
converted to 30 fps with motion-aware interpolation (`minterpolate`), never
frame duplication. “Subrange” is source time.

| Clip | Actual visual / embedded German text | English beat / timeline time | Subrange | QA / regrade-retime | Decision |
|---|---|---|---|---|---|
| EP06 `CLIP001_SOUL_BODY_OFFSET.mp4` | bright curtains and tiny figure in a surreal shore space; none | body without borders, 189.80–200.92 | — | stable and bright, but does not clearly show a body leaving or looking back | **REJECT semantic weakness** |
| EP06 `CLIP002_REM_SIGNAL_GATE.mp4` | human hand, orange signal ring halts at wrist; none | “mind reaches the room before movement reaches your muscles,” 137.34–143.26 | 0.20–5.80 | stable locked frame; short blue-dark insert inside brighter anatomy run; interpolate 24→30 | **USE** |
| EP06 `CLIP003_OLD_HAG_THRESHOLD.mp4` | daylight coastal/domestic room; restrained older figure forms from haze; none | `Old Hag` reveal, 20.14–26.76 | 0.25–5.95 | stable; no monster drift; mild neutral lift only | **USE** |
| EP06 `CLIP004_PRESENCE_GEOMETRY.mp4` | white sterile corridor and fabric form; none | possible presence-form beat | — | clean cadence but violates the no-sterile-corridor direction and lacks a human observer | **REJECT** |
| EP06 `CLIP005_MOTOR_FREEZE.mp4` | second near-identical glowing hand gate; none | REM motor failure | — | motion is acceptable, but duplicates `CLIP002` and the new human-pathway still | **REJECT duplicate** |
| EP06 `CLIP007_INTERRUPTION_CYCLE.mp4` | protocol objects on a warm desk change state; none | sleep → wake → hour → return, 225.06–235.60 | 0.20–5.80 | stable but meaning is not self-evident without voice; use only between explicit clock/lab states | **ADAPT / RESERVE** |
| EP06 `CLIP008_SIX_EPISODES_SIGNAL.mp4` | six physical measuring events land one after another on a lab table; none | exact `six episodes`, 242.06–247.62 | 0.15–5.75 | strong exact reveal, stable camera, no text; interpolate 24→30 | **USE** |
| EP06 reserve `CLIP002_SLEEP_LAB_SENSOR_MACRO.mp4` | hand and real-looking electrode/sensor leads on white surface; none | monitoring brain activity and muscle tone, 230.42–235.60 | 0.20–5.70 | clean, bright, tactile; slight neutral-green grade; interpolate | **USE** |
| EP06 reserve `CLIP004_DAWN_AFTER_PARALYSIS.mp4` | adult silhouette sits upright before a bright morning window; none | final `The body wakes`, 486.84–492.92 | 0.10–5.95 | stable, quiet, distinct from night imagery; no extra camera; interpolate | **USE** |
| EP07 `CLIP001_CULTURAL_MASKS.mp4` | eye/art/mask collage becomes a modern silhouette; none | no exact Part-1 wording | — | visually rich but introduces unspoken cultural examples | **REJECT semantic expansion** |
| EP07 `CLIP002_NIGHTMARE_PRESSURE.mp4` | relief-like eye, ribs and hand-pressure symbolism; none | Incubus, 183.50–188.88 | — | clean, but duplicates stronger embodied Incubus and reduces human intimacy | **REJECT duplicate** |
| EP07 `CLIP003_SALEM_PUBLIC_TRANSFORMATION.mp4` | full source page and later Salem court image remain stable while audience shadows enter; none | `private night entered the public record`, 449.44–455.44 | 0.15–5.95 | German EP07 QA confirms source lock; warm lift, interpolate; no source-drift variant | **USE** |
| EP07 `CLIP004_FEEDBACK_ENTITY.mp4` | cream drawing: eye, clock, seated witness and ink loop form then resolve; none | name → story → next expectation → feedback, 395.30–405.58 | 0.15–5.95 | high-luminance explanation reset, stable paper texture; interpolate | **USE** |
| EP07 reserve `CLIP003_HUFFORD_FIELDWORK_DOLLY.mp4` | warm research room, person seen from behind; none | possible Hufford fieldwork | — | technically stable but risks implied identity and duplicates the clearer Fogo interview reconstruction | **REJECT** |
| EP07 reserve `CLIP004_FUSELI_SCREEN_LIGHT_SHIFT.mp4` | Fuseli-like painting beside a modern monitor; none | culture/story callback | — | stable, but the screen adds an unspoken media claim and duplicates source-native art | **REJECT** |
| EP08 `CLIP002_SHADOW_DETACHES.mp4` | low-key door shadow separates into a figure; none | presence gains form | — | good motion, but repeats the new observer/form still and deepens the dark cluster | **REJECT duplicate** |
| EP08 `EDIT007_BLANK_SKETCH_TO_SHADOW.mp4` | cream sketch page develops a shadow figure; none | `ambiguity may acquire a body`, 348.62–355.40 | 0.05–3.45 | short, stable, brighter material change; interpolate | **USE** |
| EP08 `EDIT009_VESTIBULAR_LAYER_REVEAL.mp4` | blue bed/body layer reveal; none | body without borders | — | semantically close but darker and less embodied than the selected EN double-body still | **REJECT duplicate** |
| EP08 `EDIT019_BODY_STORY_THRESHOLD.mp4` | blue scanner/body threshold becomes desk/sketch context; none | theory/callback possible | — | mixed metaphor and digital-blue palette muddy the spoken mechanism | **REJECT** |
| EP08 reserve `CLIP003_CAUSE_SHADOW_ASSEMBLY.mp4` | warm lit doorframe, coat and object shadows assemble into a human-scale observer; none | `coat and doorway align into a shoulder`, 330.18–335.44 | 0.15–5.85 | exact semantic match, controlled warm contrast, stable camera; interpolate | **USE** |

## Selected clip set and generation decision

Selected source-native clips:

1. Old Hag threshold;
2. REM signal gate;
3. sensor macro;
4. six-episodes signal;
5. cause/shadow assembly;
6. blank-sketch-to-shadow;
7. feedback/entity loop;
8. Salem public transformation;
9. dawn aftermath.

The already submitted EN Hook Veo job failed visual QA (door action reversed and
mattress geometry deformed) and is excluded. The German selection fills every
remaining genuine motion/transform gap. **No new Veo submission is currently
justified.**

## In-episode reuse lock

- Each source still, document, painting and clip is assigned once.
- Full-context source assets and their guided crops are one continuous document
  reveal, not separate callbacks elsewhere.
- A callback uses a new source, state, perspective or material transformation.
- Old German final renders are never a source.
