# EP05 Jung & Pauli V4 — Audio / Stems Plan

**Status:** PRODUCTION LOCK  
**Referenz:** `01_GLOBAL/00_PRODUKTIONSSTANDARD.md`

## 1. Voice

### Voice Engine
- Voice ID: `JBFqnCBsd6RMkjVDRZzb`
- Name: `George - Warm, Captivating Storyteller`
- Model: `eleven_multilingual_v2`
- stability: `0.58`
- similarity_boost: `0.80`
- style: `0.08`
- speed: `1.06`
- speaker boost: `true`
- seed: `2402`

### Source Stems
1. `EP05_V4_S01_WELTUHR.txt`
2. `EP05_V4_S02_TRAEUME.txt`
3. `EP05_V4_S03_GEGENUEBER.txt`
4. `EP05_V4_S04_KAEFER.txt`
5. `EP05_V4_S05_GRENZE.txt`
6. `EP05_V4_S06_ZUFALL_ZEICHEN.txt`
7. `EP05_V4_S07_QUANTENFALLE.txt`
8. `EP05_V4_S08_WAS_BLEIBT.txt`

### Expected Raw Outputs
- `EP05_V4_S01_WELTUHR.mp3`
- `EP05_V4_S02_TRAEUME.mp3`
- `EP05_V4_S03_GEGENUEBER.mp3`
- `EP05_V4_S04_KAEFER.mp3`
- `EP05_V4_S05_GRENZE.mp3`
- `EP05_V4_S06_ZUFALL_ZEICHEN.mp3`
- `EP05_V4_S07_QUANTENFALLE.mp3`
- `EP05_V4_S08_WAS_BLEIBT.mp3`

### Voice Master
- normalize every stem to approx. `-18 LUFS integrated`
- true peak per VO stem/master: `<= -2 dBTP`
- 48 kHz mono PCM24 working files
- pre-roll: `0.35 s`
- between act stems: `0.65 s` starting point; shorten or extend only if the spoken thought needs it
- tail before endcard: `2.2 s` starting point
- final name: `EP05_JUNG_PAULI_V4_VO_MASTER.wav`

**Important:** timing follows the final spoken voice. No scene is forced to a target duration.

## 2. Music Stems

No licensed third-party music is required. Build the bed from NOESIS-style synthesis so rights remain clean.

### Deliverables
- `EP05_MX_LOW.wav` — low foundation, energy primarily below 520 Hz
- `EP05_MX_HARMONIC.wav` — audible harmonic/melodic texture mainly 700–2600 Hz so the bed survives phone speakers
- `EP05_MX_NOISE.wav` — restrained pink-noise / room-texture layer
- `EP05_MX_MASTER.wav` — combined premix before VO ducking

### Character
EP05 should sound less horror-oriented than EP06 and less technical than Gateway. Think: ordered mechanical mystery, paper, clockwork, quiet intellectual tension.

- low layer: slow dark pulse, no trailer bass hits
- harmonic layer: sparse glass/wood/soft-bell partials, never “cosmic meditation”
- noise layer: barely audible paper/air texture
- optional world-clock motif: irregular but musically controlled tick/pendulum figure; never constant through the whole episode

### Intensity by Act
Use the global NOESIS curve as a starting point:
- S1 World Clock: `0.85`
- S2 Biography / dreams: `0.58`
- S3 Correspondence: `0.70`
- S4 Beetle: `0.88`
- S5 Boundary debate: `0.74`
- S6 Viewer coincidence: `0.92`
- S7 Quantum trap / 1952 reveal: `1.00`
- S8 Residue / handoff: `0.66`

Do not automate these as hard numbers if the edit asks for a quieter moment. The curve defines relative energy, not exact seconds.

### Music Loudness
- bed premix around `-30 LUFS` under normal narration
- duck against VO, preferably smooth side-chain / automation, not audible pumping
- allow brief rises into pauses and document reveals
- no music peak should compete with a spoken proper name, source reveal or CTA

## 3. SFX / Atmosphere Stems

### Required
- `EP05_SFX_WORLD_CLOCK.wav` — subtle mechanical ticks, pendulum movement, faint layered rhythm; abstract, not a literal antique clock loop
- `EP05_SFX_PAPER_LETTERS.wav` — restrained paper handling / envelope / pencil texture for S2–S5
- `EP05_SFX_BEETLE_WINDOW.wav` — one small believable tap against glass plus optional very brief wing buzz; no horror sting
- `EP05_SFX_PHONE_NOTIFICATION.wav` — neutral non-branded notification, quiet and realistic
- `EP05_SFX_ROOMTONES.wav` — Zurich study / consulting-room / modern room tones as subtle edit glue
- `EP05_SFX_SLEEP_HANDOFF.wav` — dark bedroom room tone plus extremely restrained near/far floor or hallway sound for EP06 transition

### Optional
- `EP05_SFX_TYPE_MOTION.wav` — tiny restrained UI/paper ticks for typography reveals
- `EP05_SFX_1952_REVEAL.wav` — one low paper/tonal transition for the double-publication reveal

### Forbidden
- cinematic horror booms
- “mystical” reversed choir
- cosmic whooshes implying a force connecting events
- aggressive risers under skeptical/scientific corrections
- branded phone sounds

## 4. Final Mix

- output: stereo 48 kHz AAC 320 kbps for delivery master
- final integrated loudness: `-14 LUFS +/- 0.5`
- true peak: `<= -0.8 dBTP`
- dialogue remains the unquestioned foreground
- music and effects may open only in deliberate pauses
- no noise gate that clips natural word tails or breath

## 5. Stem Export Package

Deliver these separately before final render:
- `EP05_VO_MASTER.wav`
- `EP05_MX_LOW.wav`
- `EP05_MX_HARMONIC.wav`
- `EP05_MX_NOISE.wav`
- `EP05_SFX_WORLD_CLOCK.wav`
- `EP05_SFX_PAPER_LETTERS.wav`
- `EP05_SFX_BEETLE_WINDOW.wav`
- `EP05_SFX_PHONE_NOTIFICATION.wav`
- `EP05_SFX_ROOMTONES.wav`
- `EP05_SFX_SLEEP_HANDOFF.wav`

This is the handoff set. Final mix is derived from these stems, not baked into the voice master.